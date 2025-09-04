"""
보안 테스트 웹 대시보드
"""
from fastapi import FastAPI, Request, Form, Depends
from fastapi.templating import Jinja2Templates
from fastapi.staticfiles import StaticFiles
from fastapi.responses import HTMLResponse, RedirectResponse
from sqlalchemy.orm import Session
import httpx
from typing import Optional

from .database import get_db, init_db
from .models import APIKey, SecurityTest
from .schemas import TestResult

app = FastAPI(title="AI 보안 테스트 대시보드", version="1.0.0")

# 정적 파일 및 템플릿 설정
app.mount("/static", StaticFiles(directory="web/static"), name="static")
templates = Jinja2Templates(directory="web/templates")

# 데이터베이스 초기화
init_db()

@app.get("/", response_class=HTMLResponse)
async def dashboard(request: Request, db: Session = Depends(get_db)):
    """메인 대시보드"""
    
    # 최근 테스트 결과 조회
    recent_tests = db.query(SecurityTest).order_by(SecurityTest.created_at.desc()).limit(5).all()
    
    # API 키 설정 상태 확인
    api_keys = db.query(APIKey).all()
    api_status = {
        "openai": any(key.provider == "openai" and key.is_active for key in api_keys),
        "claude": any(key.provider == "claude" and key.is_active for key in api_keys),
        "gemini": any(key.provider == "gemini" and key.is_active for key in api_keys)
    }
    
    return templates.TemplateResponse("dashboard.html", {
        "request": request,
        "recent_tests": recent_tests,
        "api_status": api_status
    })


@app.get("/settings", response_class=HTMLResponse)
async def settings_page(request: Request, db: Session = Depends(get_db)):
    """설정 페이지"""
    
    api_keys = db.query(APIKey).all()
    
    return templates.TemplateResponse("settings.html", {
        "request": request,
        "api_keys": api_keys
    })


@app.post("/settings/api-keys")
async def save_api_keys(
    request: Request,
    openai_key: str = Form(""),
    openai_type: str = Form("direct"),
    azure_endpoint: str = Form(""),
    claude_key: str = Form(""),
    claude_type: str = Form("direct"),
    aws_access_key: str = Form(""),
    aws_secret_key: str = Form(""),
    aws_region: str = Form("us-east-1"),
    gemini_key: str = Form(""),
    gemini_type: str = Form("direct"),
    gcp_project: str = Form(""),
    db: Session = Depends(get_db)
):
    """API 키 저장"""
    
    # 기존 키 삭제
    db.query(APIKey).delete()
    
    # OpenAI 설정 저장
    if openai_key:
        openai_config = {
            "api_key": openai_key,
            "type": openai_type
        }
        if openai_type == "azure" and azure_endpoint:
            openai_config["endpoint"] = azure_endpoint
            
        db.add(APIKey(
            provider="openai",
            config=openai_config,
            is_active=True
        ))
    
    # Claude 설정 저장
    if claude_key or (claude_type == "bedrock" and aws_access_key):
        claude_config = {
            "type": claude_type
        }
        if claude_type == "direct":
            claude_config["api_key"] = claude_key
        else:
            claude_config.update({
                "aws_access_key": aws_access_key,
                "aws_secret_key": aws_secret_key,
                "aws_region": aws_region
            })
            
        db.add(APIKey(
            provider="claude",
            config=claude_config,
            is_active=True
        ))
    
    # Gemini 설정 저장
    if gemini_key or (gemini_type == "vertex" and gcp_project):
        gemini_config = {
            "type": gemini_type
        }
        if gemini_type == "direct":
            gemini_config["api_key"] = gemini_key
        else:
            gemini_config["gcp_project"] = gcp_project
            
        db.add(APIKey(
            provider="gemini",
            config=gemini_config,
            is_active=True
        ))
    
    db.commit()
    
    return RedirectResponse(url="/settings?saved=true", status_code=303)


@app.get("/security-test", response_class=HTMLResponse)
async def security_test_page(request: Request):
    """보안 테스트 페이지"""
    
    return templates.TemplateResponse("security_test.html", {
        "request": request
    })


@app.post("/security-test/start")
async def start_security_test(
    request: Request,
    target_url: str = Form(...),
    target_type: str = Form("web_application"),
    test_types: list = Form([]),
    db: Session = Depends(get_db)
):
    """보안 테스트 시작"""
    
    # 테스트 기록 생성
    test_record = SecurityTest(
        target_url=target_url,
        target_type=target_type,
        test_types=",".join(test_types),
        status="running"
    )
    db.add(test_record)
    db.commit()
    
    # 관리자 AI 서비스에 테스트 요청
    test_request = {
        "target_info": {
            "target_url": target_url,
            "target_type": target_type,
            "test_id": test_record.id
        },
        "test_scope": test_types
    }
    
    try:
        async with httpx.AsyncClient() as client:
            response = await client.post(
                "http://manager-ai:8000/start-security-test",
                json=test_request,
                timeout=30.0
            )
            
        if response.status_code == 200:
            test_record.status = "started"
            test_record.test_id = response.json().get("test_id")
        else:
            test_record.status = "failed"
            test_record.error_message = f"API 호출 실패: {response.status_code}"
            
    except Exception as e:
        test_record.status = "failed"
        test_record.error_message = str(e)
    
    db.commit()
    
    return RedirectResponse(url=f"/test-result/{test_record.id}", status_code=303)


@app.get("/test-result/{test_id}", response_class=HTMLResponse)
async def test_result_page(request: Request, test_id: int, db: Session = Depends(get_db)):
    """테스트 결과 페이지"""
    
    test = db.query(SecurityTest).filter(SecurityTest.id == test_id).first()
    
    if not test:
        return templates.TemplateResponse("error.html", {
            "request": request,
            "error": "테스트를 찾을 수 없습니다."
        })
    
    return templates.TemplateResponse("test_result.html", {
        "request": request,
        "test": test
    })


@app.get("/api/test-status/{test_id}")
async def get_test_status(test_id: int, db: Session = Depends(get_db)):
    """테스트 상태 API"""
    
    test = db.query(SecurityTest).filter(SecurityTest.id == test_id).first()
    
    if not test:
        return {"error": "테스트를 찾을 수 없습니다."}
    
    return {
        "id": test.id,
        "status": test.status,
        "progress": test.progress or 0,
        "results": test.results,
        "error_message": test.error_message
    }


if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=3000)