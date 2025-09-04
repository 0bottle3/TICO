"""
Pydantic 스키마
"""
from pydantic import BaseModel
from typing import Optional, Dict, Any
from datetime import datetime


class TestResult(BaseModel):
    """테스트 결과 스키마"""
    id: int
    target_url: str
    target_type: str
    status: str
    progress: Optional[int] = 0
    results: Optional[Dict[str, Any]] = None
    error_message: Optional[str] = None
    created_at: datetime
    
    class Config:
        from_attributes = True