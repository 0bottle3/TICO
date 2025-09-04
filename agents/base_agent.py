"""
기본 AI 에이전트 클래스
"""
from abc import ABC, abstractmethod
from typing import Dict, Any, Optional
import litellm
from loguru import logger


class BaseAgent(ABC):
    """모든 AI 에이전트의 기본 클래스"""
    
    def __init__(self, name: str, model: str, primary_provider: str, fallback_providers: list, role_description: str):
        self.name = name
        self.model = model
        self.primary_provider = primary_provider
        self.fallback_providers = fallback_providers or []
        self.role_description = role_description
        
    async def call_llm(self, messages: list, **kwargs) -> str:
        """LLM API 호출 (다중 제공업체 지원 및 Fallback)"""
        
        from config.settings import AI_PROVIDERS
        
        # Primary provider 시도
        try:
            return await self._call_with_provider(self.primary_provider, messages, **kwargs)
        except Exception as primary_error:
            logger.warning(f"{self.name} Primary provider ({self.primary_provider}) 실패: {primary_error}")
            
            # Fallback providers 시도
            for fallback_provider in self.fallback_providers:
                try:
                    logger.info(f"{self.name} Fallback provider 시도: {fallback_provider}")
                    return await self._call_with_provider(fallback_provider, messages, **kwargs)
                except Exception as fallback_error:
                    logger.warning(f"{self.name} Fallback provider ({fallback_provider}) 실패: {fallback_error}")
                    continue
            
            # 모든 provider 실패
            raise Exception(f"모든 AI 제공업체 호출 실패. Primary: {primary_error}")
    
    async def _call_with_provider(self, provider_name: str, messages: list, **kwargs) -> str:
        """특정 제공업체로 LLM 호출"""
        
        from config.settings import AI_PROVIDERS
        
        provider_config = AI_PROVIDERS[provider_name]
        model_name = provider_config["models"][self.model]
        
        # 제공업체별 설정 적용
        call_kwargs = {**kwargs}
        
        if provider_config["type"] == "azure":
            call_kwargs.update({
                "api_key": provider_config["config"]["api_key"],
                "api_base": provider_config["config"]["api_base"],
                "api_version": provider_config["config"]["api_version"]
            })
        elif provider_config["type"] == "bedrock":
            call_kwargs.update({
                "aws_access_key_id": provider_config["config"]["aws_access_key_id"],
                "aws_secret_access_key": provider_config["config"]["aws_secret_access_key"],
                "aws_region_name": provider_config["config"]["aws_region_name"]
            })
        elif provider_config["type"] == "vertex_ai":
            call_kwargs.update({
                "vertex_project": provider_config["config"]["vertex_project"],
                "vertex_location": provider_config["config"]["vertex_location"]
            })
        else:
            # 직접 API 키 사용
            call_kwargs.update({
                "api_key": provider_config["config"]["api_key"]
            })
        
        response = await litellm.acompletion(
            model=model_name,
            messages=messages,
            **call_kwargs
        )
        
        return response.choices[0].message.content
    
    @abstractmethod
    async def process(self, input_data: Dict[str, Any]) -> Dict[str, Any]:
        """에이전트별 처리 로직"""
        pass
    
    def create_system_prompt(self) -> str:
        """시스템 프롬프트 생성"""
        return f"""
당신은 {self.name}입니다.
역할: {self.role_description}

다음 지침을 따라주세요:
1. 전문적이고 정확한 분석을 제공하세요
2. 결과는 구조화된 형태로 반환하세요
3. 보안 관련 이슈는 심각도별로 분류하세요
4. 실행 가능한 권장사항을 포함하세요
"""