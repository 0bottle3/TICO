"""
관리자 AI 마이크로서비스
"""
import asyncio
import os
from fastapi import FastAPI, BackgroundTasks
from pydantic import BaseModel
import redis.asyncio as redis
import json
from typing import Dict, Any

from agents.manager_agent import ManagerAgent
from config.settings import AGENT_ROLES

app = FastAPI(title="Manager AI Service", version="1.0.0")

# Redis 연결
redis_client = None

class TestRequest(BaseModel):
    target_info: Dict[str, Any]
    test_scope: list


@app.on_event("startup")
async def startup():
    global redis_client
    redis_url = os.getenv("REDIS_URL", "redis://localhost:6379")
    redis_client = redis.from_url(redis_url)
    print("관리자 AI 서비스 시작됨")


@app.on_event("shutdown")
async def shutdown():
    if redis_client:
        await redis_client.close()


@app.post("/start-security-test")
async def start_security_test(request: TestRequest, background_tasks: BackgroundTasks):
    """보안 테스트 시작"""
    
    # 관리자 AI 초기화
    manager_config = AGENT_ROLES["manager"]
    manager = ManagerAgent(
        name=manager_config["name"],
        model=manager_config["model"],
        primary_provider=manager_config["primary_provider"],
        fallback_providers=manager_config["fallback_providers"],
        role_description=manager_config["description"]
    )
    
    # 백그라운드에서 테스트 실행
    background_tasks.add_task(execute_security_test, manager, request.dict())
    
    return {
        "status": "started",
        "message": "보안 테스트가 시작되었습니다",
        "test_id": "test_" + str(hash(str(request.dict())))
    }


async def execute_security_test(manager: ManagerAgent, test_data: Dict[str, Any]):
    """보안 테스트 실행"""
    
    try:
        # 1. 테스트 계획 수립
        plan_result = await manager.process(test_data)
        
        if plan_result["status"] == "success":
            # 2. 실행자들에게 작업 분배
            await distribute_tasks_to_executors(plan_result)
            
        print(f"테스트 계획 완료: {plan_result}")
        
    except Exception as e:
        print(f"테스트 실행 중 오류: {e}")


async def distribute_tasks_to_executors(plan_result: Dict[str, Any]):
    """실행자들에게 작업 분배"""
    
    # 정적 분석 작업 큐에 추가
    static_task = {
        "type": "static_analysis",
        "plan": plan_result["test_plan"],
        "timestamp": asyncio.get_event_loop().time()
    }
    
    await redis_client.lpush("static_analysis_queue", json.dumps(static_task))
    
    # 동적 테스트 작업 큐에 추가
    dynamic_task = {
        "type": "dynamic_testing", 
        "plan": plan_result["test_plan"],
        "timestamp": asyncio.get_event_loop().time()
    }
    
    await redis_client.lpush("dynamic_testing_queue", json.dumps(dynamic_task))
    
    print("작업이 실행자 큐에 분배되었습니다")


@app.get("/health")
async def health_check():
    """헬스 체크"""
    return {"status": "healthy", "service": "manager-ai"}


@app.get("/status")
async def get_status():
    """현재 상태 조회"""
    
    # Redis에서 큐 상태 확인
    static_queue_size = await redis_client.llen("static_analysis_queue")
    dynamic_queue_size = await redis_client.llen("dynamic_testing_queue")
    
    return {
        "service": "manager-ai",
        "queues": {
            "static_analysis": static_queue_size,
            "dynamic_testing": dynamic_queue_size
        }
    }


if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)