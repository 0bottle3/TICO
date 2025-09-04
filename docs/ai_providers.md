# AI 제공업체 설정 가이드

## 지원하는 AI 제공업체

### 1. OpenAI
#### 직접 API 사용
```env
OPENAI_API_KEY=sk-your-openai-key
OPENAI_API_TYPE=openai
```

#### Azure OpenAI 사용
```env
OPENAI_API_KEY=your-azure-openai-key
OPENAI_API_TYPE=azure
AZURE_OPENAI_ENDPOINT=https://your-resource.openai.azure.com/
AZURE_OPENAI_API_VERSION=2024-02-15-preview
```

**장점:**
- **직접 API**: 최신 모델 빠른 접근, 간단한 설정
- **Azure**: 엔터프라이즈 보안, 데이터 거버넌스, SLA 보장

### 2. Claude (Anthropic)
#### 직접 API 사용
```env
ANTHROPIC_API_KEY=sk-ant-your-claude-key
CLAUDE_API_TYPE=anthropic
```

#### AWS Bedrock 사용
```env
CLAUDE_API_TYPE=bedrock
AWS_ACCESS_KEY_ID=your-aws-access-key
AWS_SECRET_ACCESS_KEY=your-aws-secret-key
AWS_REGION=us-east-1
```

**장점:**
- **직접 API**: 최신 Claude 모델, 빠른 응답
- **AWS Bedrock**: AWS 생태계 통합, 보안 강화, 비용 최적화

### 3. Google Gemini
#### 직접 API 사용
```env
GOOGLE_API_KEY=your-google-ai-key
GEMINI_API_TYPE=google
```

#### Vertex AI 사용
```env
GEMINI_API_TYPE=vertex
GOOGLE_PROJECT_ID=your-gcp-project-id
GOOGLE_LOCATION=us-central1
```

**장점:**
- **직접 API**: 간단한 설정, 빠른 시작
- **Vertex AI**: GCP 통합, MLOps 기능, 확장성

## 제공업체별 특징

### OpenAI GPT-4
- **강점**: 추론 능력, 코드 생성, 일반적 작업
- **보안 테스트 활용**: 관리 업무, 종합 분석, 의사결정

### Claude 3
- **강점**: 안전성, 긴 컨텍스트, 신중한 분석
- **보안 테스트 활용**: 코드 리뷰, 취약점 분석, 위험 평가

### Google Gemini
- **강점**: 멀티모달, 대용량 처리, 빠른 속도
- **보안 테스트 활용**: 대용량 로그 분석, 패턴 탐지

## Fallback 시스템

각 AI 에이전트는 Primary → Fallback 순서로 시도:

```python
"openai": {
    "primary_provider": "openai_direct",
    "fallback_providers": ["azure_openai"]
},
"claude": {
    "primary_provider": "claude_direct", 
    "fallback_providers": ["aws_bedrock"]
},
"gemini": {
    "primary_provider": "google_direct",
    "fallback_providers": ["vertex_ai"]
}
```

## 비용 최적화 전략

### 1. 모델 선택
- **관리자/결정자**: GPT-4 (높은 추론 능력 필요)
- **실행자**: GPT-3.5-turbo, Claude Haiku (비용 효율적)
- **분석가**: Claude Sonnet, Gemini Pro (균형잡힌 성능)

### 2. 제공업체 선택
- **개발/테스트**: 직접 API (유연성)
- **프로덕션**: 클라우드 서비스 (안정성, SLA)
- **대규모**: Bedrock, Vertex AI (볼륨 할인)

## 설정 예시

### 개발 환경
```env
# 간단한 직접 API 사용
OPENAI_API_KEY=sk-...
ANTHROPIC_API_KEY=sk-ant-...
GOOGLE_API_KEY=AI...
```

### 프로덕션 환경
```env
# 클라우드 서비스 사용
OPENAI_API_TYPE=azure
AZURE_OPENAI_ENDPOINT=https://company.openai.azure.com/

CLAUDE_API_TYPE=bedrock
AWS_ACCESS_KEY_ID=AKIA...
AWS_REGION=us-east-1

GEMINI_API_TYPE=vertex
GOOGLE_PROJECT_ID=company-security-ai
```

## 보안 고려사항

1. **API 키 관리**: AWS Secrets Manager, Azure Key Vault 사용
2. **네트워크 보안**: VPC, Private Endpoint 설정
3. **데이터 거버넌스**: 지역별 데이터 보관 정책 준수
4. **감사 로그**: 모든 AI 호출 로깅 및 모니터링

## 문제 해결

### 일반적인 오류
1. **API 키 오류**: 키 유효성 및 권한 확인
2. **할당량 초과**: 제공업체별 사용량 모니터링
3. **네트워크 오류**: Fallback 제공업체 자동 전환
4. **모델 버전**: 지원하는 모델 버전 확인