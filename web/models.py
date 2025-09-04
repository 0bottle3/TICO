"""
데이터베이스 모델
"""
from sqlalchemy import Column, Integer, String, Text, DateTime, Boolean, JSON
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.sql import func

Base = declarative_base()


class APIKey(Base):
    """AI API 키 설정"""
    __tablename__ = "api_keys"
    
    id = Column(Integer, primary_key=True, index=True)
    provider = Column(String(50), nullable=False)  # openai, claude, gemini
    config = Column(JSON, nullable=False)  # API 키 및 설정 정보
    is_active = Column(Boolean, default=True)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())


class SecurityTest(Base):
    """보안 테스트 기록"""
    __tablename__ = "security_tests"
    
    id = Column(Integer, primary_key=True, index=True)
    target_url = Column(String(500), nullable=False)
    target_type = Column(String(100), nullable=False)  # web_application, api, mobile_app
    test_types = Column(Text, nullable=False)  # 쉼표로 구분된 테스트 유형
    test_id = Column(String(100))  # 관리자 AI에서 생성한 테스트 ID
    status = Column(String(50), default="pending")  # pending, running, completed, failed
    progress = Column(Integer, default=0)  # 진행률 (0-100)
    results = Column(JSON)  # 테스트 결과
    error_message = Column(Text)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())