"""
멀티 AI 보안 테스트 시스템 메인 실행 파일
"""
import asyncio
from typing import Dict, Any
from loguru import logger

from config.settings import settings, AGENT_ROLES
from core.workflow import SecurityTestWorkflow
from agents.manager_agent import ManagerAgent


async def main():
    """메인 실행 함수"""
    
    logger.info("멀티 AI 보안 테스트 시스템 시작")
    
    # 테스트 대상 정보 (예시)
    target_info = {
        "project_name": "샘플 웹 애플리케이션",
        "project_type": "web_application",
        "language": "python",
        "framework": "fastapi",
        "source_path": "./sample_project"
    }
    
    test_scope = [
        "static_code_analysis",
        "dependency_vulnerability_scan", 
        "dynamic_security_testing",
        "authentication_testing",
        "authorization_testing"
    ]
    
    input_data = {
        "target_info": target_info,
        "test_scope": test_scope
    }
    
    # 워크플로우 실행
    workflow = SecurityTestWorkflow()
    result = await workflow.execute_workflow(input_data)
    
    logger.info("보안 테스트 완료")
    logger.info(f"결과: {result}")
    
    return result


async def test_manager_agent():
    """관리자 AI 테스트"""
    
    manager_config = AGENT_ROLES["manager"]
    manager = ManagerAgent(
        name=manager_config["name"],
        model=manager_config["model"],
        provider=manager_config["provider"],
        role_description=manager_config["description"]
    )
    
    test_input = {
        "target_info": {
            "project_name": "테스트 프로젝트",
            "project_type": "web_api"
        },
        "test_scope": ["static_analysis", "dynamic_testing"]
    }
    
    result = await manager.process(test_input)
    logger.info(f"관리자 AI 테스트 결과: {result}")


if __name__ == "__main__":
    # 환경 설정 확인
    if not settings.OPENAI_API_KEY:
        logger.warning("API 키가 설정되지 않았습니다. .env 파일을 확인해주세요.")
    
    # 메인 실행
    asyncio.run(main())
    
    # 개별 에이전트 테스트
    # asyncio.run(test_manager_agent())