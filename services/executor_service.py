"""
실행자 AI 마이크로서비스
"""
import asyncio
import os
import json
import redis.asyncio as redis
from typing import Dict, Any

from agents.base_agent import BaseAgent


class ExecutorService:
    """실행자 서비스"""
    
    def __init__(self):
        self.ai_provider = os.getenv("AI_PROVIDER", "openai")
        self.executor_type = os.getenv("EXECUTOR_TYPE", "static")  # static or dynamic
        self.redis_client = None
        self.agent = None
        
    async def initialize(self):
        """서비스 초기화"""
        
        # Redis 연결
        redis_url = os.getenv("REDIS_URL", "redis://localhost:6379")
        self.redis_client = redis.from_url(redis_url)
        
        # AI 에이전트 초기화
        self.agent = self.create_agent()
        
        print(f"{self.executor_type} 실행자 ({self.ai_provider}) 서비스 시작됨")
    
    def create_agent(self) -> BaseAgent:
        """AI 에이전트 생성"""
        
        if self.executor_type == "static":
            from agents.static_executor import StaticAnalysisExecutor
            return StaticAnalysisExecutor(
                name=f"정적분석 실행자 ({self.ai_provider})",
                model=self.get_model_name(),
                provider=self.ai_provider,
                role_description=f"{self.ai_provider}를 사용한 정적 코드 분석"
            )
        else:
            from agents.dynamic_executor import DynamicTestExecutor
            return DynamicTestExecutor(
                name=f"동적테스트 실행자 ({self.ai_provider})",
                model=self.get_model_name(),
                provider=self.ai_provider,
                role_description=f"{self.ai_provider}를 사용한 동적 보안 테스트"
            )
    
    def get_model_name(self) -> str:
        """AI 모델명 반환"""
        model_map = {
            "openai": "gpt-4",
            "claude": "claude-3-sonnet-20240229",
            "gemini": "gemini-pro"
        }
        return model_map.get(self.ai_provider, "gpt-4")
    
    async def start_worker(self):
        """워커 시작"""
        
        queue_name = f"{self.executor_type}_analysis_queue"
        
        while True:
            try:
                # 큐에서 작업 가져오기 (블로킹)
                task_data = await self.redis_client.brpop(queue_name, timeout=10)
                
                if task_data:
                    _, task_json = task_data
                    task = json.loads(task_json)
                    
                    print(f"작업 수신: {task['type']}")
                    
                    # 작업 실행
                    result = await self.execute_task(task)
                    
                    # 결과를 분석가 큐에 전송
                    await self.send_to_analyzers(result)
                    
            except Exception as e:
                print(f"작업 처리 중 오류: {e}")
                await asyncio.sleep(5)
    
    async def execute_task(self, task: Dict[str, Any]) -> Dict[str, Any]:
        """작업 실행"""
        
        try:
            # AI 에이전트로 작업 처리
            result = await self.agent.process(task)
            
            # 실행 시간 시뮬레이션 (실제 보안 테스트는 시간이 오래 걸림)
            if self.executor_type == "dynamic":
                print("동적 테스트 실행 중... (시간이 오래 걸릴 수 있습니다)")
                await asyncio.sleep(30)  # 30초 시뮬레이션
            else:
                await asyncio.sleep(10)  # 10초 시뮬레이션
            
            return {
                "executor_type": self.executor_type,
                "ai_provider": self.ai_provider,
                "result": result,
                "timestamp": asyncio.get_event_loop().time()
            }
            
        except Exception as e:
            return {
                "executor_type": self.executor_type,
                "ai_provider": self.ai_provider,
                "error": str(e),
                "timestamp": asyncio.get_event_loop().time()
            }
    
    async def send_to_analyzers(self, result: Dict[str, Any]):
        """분석가들에게 결과 전송"""
        
        result_json = json.dumps(result)
        await self.redis_client.lpush("analysis_queue", result_json)
        
        print(f"결과를 분석가 큐에 전송: {self.executor_type} ({self.ai_provider})")


async def main():
    """메인 실행 함수"""
    
    service = ExecutorService()
    await service.initialize()
    
    # 워커 시작
    await service.start_worker()


if __name__ == "__main__":
    asyncio.run(main())