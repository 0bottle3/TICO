"""
분석가 AI - 실행자들의 결과를 분석
"""
from typing import Dict, Any, List
from .base_agent import BaseAgent
from loguru import logger
import json


class AnalyzerAgent(BaseAgent):
    """분석가 AI - 실행 결과를 분석하고 인사이트 제공"""
    
    async def process(self, input_data: Dict[str, Any]) -> Dict[str, Any]:
        """실행자들의 결과를 분석"""
        
        execution_results = input_data.get('execution_results', [])
        target_url = input_data.get('target_url', '')
        
        if not execution_results:
            return {
                "status": "error",
                "error": "분석할 실행 결과가 없습니다."
            }
        
        try:
            # 실행 결과들을 종합하여 분석
            system_prompt = self.create_system_prompt() + f"""

당신은 {self.primary_provider} 기반의 보안 분석 전문가입니다.
여러 실행자 AI들이 수행한 보안 테스트 결과를 종합 분석하여:

1. 발견된 취약점들의 연관성 분석
2. 비즈니스 영향도 평가
3. 공격 시나리오 구성
4. 우선순위별 수정 방안 제시
5. 전체적인 보안 성숙도 평가

{self.primary_provider}의 특성을 활용하여 심층적이고 실용적인 분석을 제공하세요.
"""
            
            # 실행 결과 요약
            results_summary = self._summarize_execution_results(execution_results)
            
            user_prompt = f"""
대상 시스템: {target_url}

실행자들의 보안 테스트 결과:
{json.dumps(results_summary, indent=2, ensure_ascii=False)}

다음 관점에서 종합 분석해주세요:

1. **위험도 분석**: 발견된 취약점들의 실제 위험도
2. **공격 체인**: 취약점들을 연결한 가능한 공격 시나리오
3. **비즈니스 영향**: 각 취약점이 비즈니스에 미치는 영향
4. **수정 우선순위**: 즉시/단기/장기 수정 항목 분류
5. **보안 점수**: 100점 만점 기준 현재 보안 수준

JSON 형태로 구조화된 분석 결과를 제공해주세요.
"""
            
            messages = [
                {"role": "system", "content": system_prompt},
                {"role": "user", "content": user_prompt}
            ]
            
            # AI 분석 (적당한 토큰 사용)
            analysis_result = await self.call_llm(messages, max_tokens=1500)
            
            logger.info(f"{self.name}: 종합 분석 완료")
            
            return {
                "status": "success",
                "agent": self.name,
                "provider": self.primary_provider,
                "analysis_type": "comprehensive",
                "analysis_result": analysis_result,
                "processed_results": len(execution_results),
                "token_usage": "약 1000-1500 토큰 사용",
                "analysis_perspective": f"{self.primary_provider} 관점의 전문 분석"
            }
            
        except Exception as e:
            logger.error(f"{self.name}: 분석 실패 - {e}")
            return {
                "status": "error",
                "agent": self.name,
                "provider": self.primary_provider,
                "error": str(e)
            }
    
    def _summarize_execution_results(self, execution_results: List[Dict[str, Any]]) -> Dict[str, Any]:
        """실행 결과들을 요약"""
        
        summary = {
            "total_tests": len(execution_results),
            "successful_tests": 0,
            "failed_tests": 0,
            "vulnerabilities_found": [],
            "test_coverage": [],
            "execution_times": {}
        }
        
        for result in execution_results:
            if result.get("status") == "success":
                summary["successful_tests"] += 1
                
                # 실행 결과에서 취약점 추출
                exec_result = result.get("execution_result", {})
                if exec_result.get("status") == "completed":
                    test_type = exec_result.get("test_type", "unknown")
                    summary["test_coverage"].append(test_type)
                    
                    # 취약점 정보 추출 (결과 구조에 따라 조정 필요)
                    if "vulnerabilities" in str(exec_result):
                        summary["vulnerabilities_found"].append({
                            "test_type": test_type,
                            "executor": result.get("agent", "unknown"),
                            "details": "취약점 발견됨"
                        })
            else:
                summary["failed_tests"] += 1
        
        return summary


class ClaudeAnalyzer(AnalyzerAgent):
    """Claude 기반 분석가 - 안전성과 신중함 중심"""
    
    def create_system_prompt(self) -> str:
        base_prompt = super().create_system_prompt()
        return base_prompt + """

Claude 분석가로서 다음 특성을 강조하세요:
- 보수적이고 신중한 위험도 평가
- 안전성을 최우선으로 하는 권장사항
- 단계적이고 체계적인 수정 계획
- 규정 준수 및 컴플라이언스 고려
"""


class GeminiAnalyzer(AnalyzerAgent):
    """Gemini 기반 분석가 - 패턴 분석과 효율성 중심"""
    
    def create_system_prompt(self) -> str:
        base_prompt = super().create_system_prompt()
        return base_prompt + """

Gemini 분석가로서 다음 특성을 강조하세요:
- 대량 데이터에서 패턴 식별
- 효율적이고 실용적인 해결책 제시
- 자동화 가능한 수정 방안 우선 제안
- 성능과 보안의 균형점 고려
"""


class OpenAIAnalyzer(AnalyzerAgent):
    """OpenAI 기반 분석가 - 종합적 추론과 창의적 해결책"""
    
    def create_system_prompt(self) -> str:
        base_prompt = super().create_system_prompt()
        return base_prompt + """

OpenAI 분석가로서 다음 특성을 강조하세요:
- 복합적 취약점 간의 연관성 분석
- 창의적이고 혁신적인 보안 솔루션 제안
- 비즈니스 맥락을 고려한 전략적 권장사항
- 미래 위협에 대한 예측적 분석
"""