"""
멀티 AI 보안 테스트 시스템 설정
"""
import os
from typing import Dict, List
from pydantic import BaseSettings


class Settings(BaseSettings):
    """시스템 설정"""
    
    # OpenAI API 설정 (직접 또는 Azure)
    OPENAI_API_KEY: str = ""
    OPENAI_API_TYPE: str = "openai"  # "openai" or "azure"
    AZURE_OPENAI_ENDPOINT: str = ""
    AZURE_OPENAI_API_VERSION: str = "2024-02-15-preview"
    
    # Claude API 설정 (직접 또는 AWS Bedrock)
    ANTHROPIC_API_KEY: str = ""
    CLAUDE_API_TYPE: str = "anthropic"  # "anthropic" or "bedrock"
    AWS_ACCESS_KEY_ID: str = ""
    AWS_SECRET_ACCESS_KEY: str = ""
    AWS_REGION: str = "us-east-1"
    
    # Google API 설정 (직접 또는 Vertex AI)
    GOOGLE_API_KEY: str = ""
    GEMINI_API_TYPE: str = "google"  # "google" or "vertex"
    GOOGLE_PROJECT_ID: str = ""
    GOOGLE_LOCATION: str = "us-central1"
    
    # 데이터베이스
    DATABASE_URL: str = "sqlite:///./security_test.db"
    
    # Redis (큐 시스템)
    REDIS_URL: str = "redis://localhost:6379"
    
    # 테스트 설정
    MAX_RETRY_COUNT: int = 3
    QUALITY_THRESHOLD: float = 0.7
    
    # 로깅
    LOG_LEVEL: str = "INFO"
    
    class Config:
        env_file = ".env"


# 전역 설정 인스턴스
settings = Settings()


# AI 제공업체별 모델 설정
AI_PROVIDERS = {
    "openai_direct": {
        "type": "openai",
        "models": {
            "gpt-4": "gpt-4",
            "gpt-4-turbo": "gpt-4-turbo-preview",
            "gpt-3.5-turbo": "gpt-3.5-turbo"
        },
        "config": {
            "api_key": settings.OPENAI_API_KEY,
            "api_type": "openai"
        }
    },
    "azure_openai": {
        "type": "azure",
        "models": {
            "gpt-4": "azure/gpt-4",
            "gpt-4-turbo": "azure/gpt-4-turbo",
            "gpt-3.5-turbo": "azure/gpt-35-turbo"
        },
        "config": {
            "api_key": settings.OPENAI_API_KEY,
            "api_base": settings.AZURE_OPENAI_ENDPOINT,
            "api_version": settings.AZURE_OPENAI_API_VERSION,
            "api_type": "azure"
        }
    },
    "claude_direct": {
        "type": "anthropic",
        "models": {
            "claude-3-opus": "claude-3-opus-20240229",
            "claude-3-sonnet": "claude-3-sonnet-20240229",
            "claude-3-haiku": "claude-3-haiku-20240307"
        },
        "config": {
            "api_key": settings.ANTHROPIC_API_KEY
        }
    },
    "aws_bedrock": {
        "type": "bedrock",
        "models": {
            "claude-3-opus": "bedrock/anthropic.claude-3-opus-20240229-v1:0",
            "claude-3-sonnet": "bedrock/anthropic.claude-3-sonnet-20240229-v1:0",
            "claude-3-haiku": "bedrock/anthropic.claude-3-haiku-20240307-v1:0"
        },
        "config": {
            "aws_access_key_id": settings.AWS_ACCESS_KEY_ID,
            "aws_secret_access_key": settings.AWS_SECRET_ACCESS_KEY,
            "aws_region_name": settings.AWS_REGION
        }
    },
    "google_direct": {
        "type": "google",
        "models": {
            "gemini-pro": "gemini-pro",
            "gemini-pro-vision": "gemini-pro-vision"
        },
        "config": {
            "api_key": settings.GOOGLE_API_KEY
        }
    },
    "vertex_ai": {
        "type": "vertex_ai",
        "models": {
            "gemini-pro": "vertex_ai/gemini-pro",
            "gemini-pro-vision": "vertex_ai/gemini-pro-vision"
        },
        "config": {
            "vertex_project": settings.GOOGLE_PROJECT_ID,
            "vertex_location": settings.GOOGLE_LOCATION
        }
    }
}

# AI 에이전트 역할 정의 (다중 제공업체 지원)
AGENT_ROLES = {
    "manager": {
        "name": "관리자 AI",
        "description": "전체 보안 테스트 프로세스를 관리하고 조율",
        "primary_provider": "openai_direct",
        "fallback_providers": ["azure_openai"],
        "model": "gpt-4"
    },
    "static_executors": {
        "openai": {
            "name": "정적분석 실행자 (OpenAI)",
            "description": "OpenAI를 사용한 정적 코드 분석",
            "primary_provider": "openai_direct",
            "fallback_providers": ["azure_openai"],
            "model": "gpt-4"
        },
        "claude": {
            "name": "정적분석 실행자 (Claude)",
            "description": "Claude를 사용한 정적 코드 분석",
            "primary_provider": "claude_direct",
            "fallback_providers": ["aws_bedrock"],
            "model": "claude-3-sonnet"
        },
        "gemini": {
            "name": "정적분석 실행자 (Gemini)",
            "description": "Gemini를 사용한 정적 코드 분석",
            "primary_provider": "google_direct",
            "fallback_providers": ["vertex_ai"],
            "model": "gemini-pro"
        }
    },
    "dynamic_executors": {
        "openai": {
            "name": "동적테스트 실행자 (OpenAI)",
            "description": "OpenAI를 사용한 동적 보안 테스트",
            "primary_provider": "openai_direct",
            "fallback_providers": ["azure_openai"],
            "model": "gpt-4"
        },
        "claude": {
            "name": "동적테스트 실행자 (Claude)",
            "description": "Claude를 사용한 동적 보안 테스트",
            "primary_provider": "claude_direct",
            "fallback_providers": ["aws_bedrock"],
            "model": "claude-3-sonnet"
        },
        "gemini": {
            "name": "동적테스트 실행자 (Gemini)",
            "description": "Gemini를 사용한 동적 보안 테스트",
            "primary_provider": "google_direct",
            "fallback_providers": ["vertex_ai"],
            "model": "gemini-pro"
        }
    },
    "analyzers": {
        "claude": {
            "name": "분석가 AI (Claude)",
            "description": "Claude를 사용한 보안 테스트 결과 분석",
            "primary_provider": "claude_direct",
            "fallback_providers": ["aws_bedrock"],
            "model": "claude-3-sonnet"
        },
        "gemini": {
            "name": "분석가 AI (Gemini)",
            "description": "Gemini를 사용한 보안 테스트 결과 분석",
            "primary_provider": "google_direct",
            "fallback_providers": ["vertex_ai"],
            "model": "gemini-pro"
        },
        "openai": {
            "name": "분석가 AI (OpenAI)",
            "description": "OpenAI를 사용한 보안 테스트 결과 분석",
            "primary_provider": "openai_direct",
            "fallback_providers": ["azure_openai"],
            "model": "gpt-4"
        }
    },
    "decision": {
        "name": "결정자 AI",
        "description": "최종 보안 평가 및 리포트 생성",
        "primary_provider": "openai_direct",
        "fallback_providers": ["azure_openai"],
        "model": "gpt-4"
    }
}