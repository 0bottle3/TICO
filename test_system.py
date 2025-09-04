"""
시스템 테스트 스크립트
"""
import asyncio
import httpx
import json


async def test_security_system():
    """보안 테스트 시스템 테스트"""
    
    print("🧪 멀티 AI 보안 테스트 시스템 테스트 시작")
    
    # 테스트 데이터
    test_request = {
        "target_info": {
            "project_name": "샘플 웹 애플리케이션",
            "project_type": "web_application",
            "language": "python",
            "framework": "fastapi",
            "source_path": "./sample_project"
        },
        "test_scope": [
            "static_code_analysis",
            "dependency_vulnerability_scan",
            "dynamic_security_testing",
            "authentication_testing",
            "authorization_testing"
        ]
    }
    
    try:
        async with httpx.AsyncClient() as client:
            # 헬스 체크
            print("1. 헬스 체크...")
            health_response = await client.get("http://localhost:8000/health")
            print(f"   상태: {health_response.json()}")
            
            # 보안 테스트 시작
            print("2. 보안 테스트 시작...")
            test_response = await client.post(
                "http://localhost:8000/start-security-test",
                json=test_request
            )
            print(f"   응답: {test_response.json()}")
            
            # 상태 확인
            print("3. 시스템 상태 확인...")
            await asyncio.sleep(5)  # 5초 대기
            
            status_response = await client.get("http://localhost:8000/status")
            print(f"   상태: {status_response.json()}")
            
            print("✅ 테스트 완료!")
            
    except Exception as e:
        print(f"❌ 테스트 실패: {e}")
        print("💡 시스템이 실행 중인지 확인하세요: docker-compose ps")


if __name__ == "__main__":
    asyncio.run(test_security_system())