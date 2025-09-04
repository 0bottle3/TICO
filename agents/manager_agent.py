"""
관리자 AI 에이전트
전체 보안 테스트 프로세스를 관리하고 조율
"""
from typing import Dict, Any, List
from .base_agent import BaseAgent
from loguru import logger


class ManagerAgent(BaseAgent):
    """관리자 AI - 전체 프로세스 관리 및 조율"""
    
    async def process(self, input_data: Dict[str, Any]) -> Dict[str, Any]:
        """보안 테스트 계획 수립 및 실행 코드 생성"""
        
        target_info = input_data.get("target_info", {})
        test_scope = input_data.get("test_scope", [])
        target_url = target_info.get("target_url", "")
        
        system_prompt = self.create_system_prompt() + """

당신은 보안 테스트 관리자로서 실행자 AI들이 바로 실행할 수 있는 완벽한 코드를 생성해야 합니다.

각 테스트 유형별로 다음을 생성하세요:
1. 완전한 Python 실행 코드
2. 필요한 도구 명령어
3. 결과 파싱 로직
4. 에러 처리 코드

실행자들은 이 코드를 받아서 그대로 실행만 하면 됩니다.
"""
        
        user_prompt = f"""
보안 테스트 대상: {target_url}
테스트 유형: {', '.join(test_scope)}

다음 테스트들에 대해 완벽한 실행 코드를 생성해주세요:

{self._generate_test_requirements(test_scope)}

각 테스트별로 다음 형식으로 제공하세요:
{{
    "test_type": "브루트포스",
    "execution_code": "완전한 Python 코드",
    "shell_commands": ["필요한 쉘 명령어들"],
    "expected_output": "예상 결과 형식",
    "parsing_logic": "결과 파싱 코드"
}}
"""
        
        messages = [
            {"role": "system", "content": system_prompt},
            {"role": "user", "content": user_prompt}
        ]
        
        try:
            response = await self.call_llm(messages, max_tokens=4000)
            logger.info(f"{self.name}: 실행 코드 생성 완료")
            
            return {
                "status": "success",
                "agent": self.name,
                "execution_codes": response,
                "target_url": target_url,
                "test_scope": test_scope,
                "next_step": "distribute_to_executors"
            }
            
        except Exception as e:
            logger.error(f"{self.name}: 코드 생성 실패 - {e}")
            return {
                "status": "error",
                "agent": self.name,
                "error": str(e)
            }
    
    def _generate_test_requirements(self, test_scope: list) -> str:
        """테스트 유형별 요구사항 생성"""
        
        requirements = {
            "brute_force": """
브루트포스 테스트:
- 로그인 페이지 탐지 (/login, /admin, /wp-admin 등)
- 일반적인 패스워드 리스트로 테스트 (admin/admin, admin/password 등)
- 계정 잠금 정책 확인
- 응답 시간 분석으로 유효한 사용자명 탐지
- 실행 시간: 최대 10분
""",
            "sql_injection": """
SQL 인젝션 테스트:
- GET/POST 파라미터에 SQL 페이로드 삽입
- Error-based, Boolean-based, Time-based 테스트
- sqlmap 도구 사용 또는 커스텀 페이로드
- 데이터베이스 정보 추출 시도
- 실행 시간: 최대 15분
""",
            "xss_testing": """
XSS 테스트:
- Reflected, Stored, DOM-based XSS 테스트
- 다양한 XSS 페이로드 시도
- 입력 필드, URL 파라미터, 헤더 테스트
- WAF 우회 기법 적용
- 실행 시간: 최대 5분
""",
            "port_scan": """
포트 스캔:
- nmap을 사용한 포트 스캔
- 서비스 버전 탐지
- OS 핑거프린팅
- 취약한 서비스 식별
- 실행 시간: 최대 3분
""",
            "ssl_tls_test": """
SSL/TLS 테스트:
- 인증서 유효성 검사
- 암호화 강도 확인
- 프로토콜 버전 테스트
- 취약한 암호화 알고리즘 탐지
- 실행 시간: 최대 2분
"""
        }
        
        result = []
        for test_type in test_scope:
            if test_type in requirements:
                result.append(requirements[test_type])
        
        return "\n".join(result)
    
    async def coordinate_workflow(self, workflow_data: Dict[str, Any]) -> Dict[str, Any]:
        """워크플로우 조율"""
        
        system_prompt = f"""
{self.create_system_prompt()}

당신은 보안 테스트 워크플로우를 조율하는 관리자입니다.
현재 진행 상황을 분석하고 다음 단계를 결정해주세요.
"""
        
        user_prompt = f"""
현재 워크플로우 상태:
{workflow_data}

다음을 결정해주세요:
1. 현재 단계의 완료 여부
2. 다음 실행할 단계
3. 필요한 재작업 여부
4. 전체 진행률

JSON 형태로 응답해주세요.
"""
        
        messages = [
            {"role": "system", "content": system_prompt},
            {"role": "user", "content": user_prompt}
        ]
        
        try:
            response = await self.call_llm(messages)
            return {
                "status": "success",
                "coordination_result": response
            }
        except Exception as e:
            logger.error(f"워크플로우 조율 실패: {e}")
            return {
                "status": "error",
                "error": str(e)
            }