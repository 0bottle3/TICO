"""
정적 분석 실행자 AI
"""
from typing import Dict, Any
from .base_agent import BaseAgent
from loguru import logger


class StaticAnalysisExecutor(BaseAgent):
    """정적 분석 실행자 AI"""
    
    async def process(self, input_data: Dict[str, Any]) -> Dict[str, Any]:
        """관리자 AI가 생성한 코드를 실행"""
        
        from agents.code_executor import ExecutorAgent
        
        # 관리자 AI가 보낸 실행 패키지 확인
        execution_package = input_data.get('execution_package')
        
        if not execution_package:
            return {
                "status": "error",
                "error": "관리자 AI로부터 실행 패키지를 받지 못했습니다."
            }
        
        try:
            # 코드 실행자 생성
            executor = ExecutorAgent(
                executor_id=f"static_{self.primary_provider}",
                ai_provider=self.primary_provider
            )
            
            # 관리자 AI가 생성한 코드 실행
            execution_result = await executor.process(execution_package)
            
            logger.info(f"{self.name}: 코드 실행 완료")
            
            return {
                "status": "success",
                "agent": self.name,
                "provider": self.primary_provider,
                "analysis_type": "static",
                "execution_result": execution_result,
                "token_usage": "0 토큰 (코드 실행만 함)",
                "note": "관리자 AI가 생성한 코드를 실행했습니다"
            }
            
        except Exception as e:
            logger.error(f"{self.name}: 코드 실행 실패 - {e}")
            return {
                "status": "error",
                "agent": self.name,
                "provider": self.primary_provider,
                "analysis_type": "static",
                "error": str(e)
            }
    
    def _count_findings(self, response: str) -> int:
        """발견된 이슈 개수 추정"""
        # 실제로는 응답을 파싱하여 정확한 개수 계산
        return response.lower().count("취약점") + response.lower().count("vulnerability")