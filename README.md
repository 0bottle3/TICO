# TICO - 멀티 AI 보안 테스트 자동화 시스템

## 프로젝트 개요
서비스 출시 전 보안 테스트를 자동화하는 멀티 AI 에이전트 시스템

## 시스템 아키텍처

```
슈퍼 관리자 (사용자)
    ↓
관리자 AI (OpenAI) - 전체 프로세스 관리 및 조율
    ↓
실행자 그룹:
├── 정적분석팀: Claude, Gemini, OpenAI
└── 동적테스트팀: Claude, Gemini, OpenAI
    ↓ (총 6개 테스트 결과)
분석가 그룹:
├── 분석가-Claude (6개 결과 → 분석리포트1)
├── 분석가-Gemini (6개 결과 → 분석리포트2)  
└── 분석가-OpenAI (6개 결과 → 분석리포트3)
    ↓ (3개 분석리포트)
결정자 AI (OpenAI) - 최종 판단 및 종합 리포트
```

## 핵심 기능
- **다중 AI 검증**: 같은 테스트를 여러 AI가 수행하여 누락 방지
- **품질 제어**: 분석가 AI가 결과 품질을 검증하고 재실행 명령 가능
- **다각도 분석**: 각 AI 업체별 특성을 활용한 종합적 분석
- **자동화된 워크플로우**: 회사 조직 구조와 유사한 계층적 처리

## 기술 스택
- **컨테이너화**: Docker + Docker Compose
- **API 통합**: LiteLLM (멀티 LLM 통합 관리)
- **백엔드**: FastAPI (마이크로서비스)
- **데이터베이스**: PostgreSQL
- **메시지 큐**: Redis
- **AI 모델**: OpenAI GPT-4, Claude, Gemini

## 마이크로서비스 아키텍처
```
┌─────────────────┐    ┌─────────────────┐    ┌─────────────────┐
│   관리자 AI     │    │  실행자 AI x6   │    │  분석가 AI x3   │
│   (OpenAI)      │    │  (각 컨테이너)   │    │  (각 컨테이너)   │
└─────────────────┘    └─────────────────┘    └─────────────────┘
         │                       │                       │
         └───────────────────────┼───────────────────────┘
                                 │
                    ┌─────────────────┐
                    │   Redis Queue   │
                    │   PostgreSQL    │
                    └─────────────────┘
```

## AI 제공업체 지원

### 다중 제공업체 지원
각 AI 모델을 여러 경로로 접근 가능:

**OpenAI:**
- 직접 API: `OPENAI_API_KEY`
- Azure OpenAI: `AZURE_OPENAI_ENDPOINT`

**Claude:**
- 직접 API: `ANTHROPIC_API_KEY`  
- AWS Bedrock: `AWS_ACCESS_KEY_ID`

**Gemini:**
- 직접 API: `GOOGLE_API_KEY`
- Vertex AI: `GOOGLE_PROJECT_ID`

### Fallback 시스템
Primary 제공업체 실패시 자동으로 Fallback 제공업체로 전환

## 빠른 시작

### 1. 환경 설정
```bash
# .env 파일에서 사용할 제공업체 설정
# 직접 API 사용 (간단)
OPENAI_API_KEY=sk-your-key
ANTHROPIC_API_KEY=sk-ant-your-key
GOOGLE_API_KEY=your-key

# 또는 클라우드 서비스 사용 (프로덕션)
OPENAI_API_TYPE=azure
AZURE_OPENAI_ENDPOINT=https://your.openai.azure.com/
CLAUDE_API_TYPE=bedrock
AWS_ACCESS_KEY_ID=your-aws-key
```

### 2. 시스템 시작
```bash
# 전체 시스템 시작
docker-compose up -d

# 또는 스크립트 사용
chmod +x start.sh
./start.sh
```

### 3. 테스트 실행
```bash
python test_system.py
```

## 서비스 접속 정보
- **웹 대시보드**: http://localhost:3000 ⭐ (메인 사용자 인터페이스)
- **관리자 API**: http://localhost:8000
- **PostgreSQL**: localhost:5432
- **Redis**: localhost:6379

## 사용법 (비개발자도 쉽게!)

### 1단계: 시스템 시작
```bash
docker-compose up -d
```

### 2단계: 웹 브라우저에서 접속
- http://localhost:3000 접속

### 3단계: AI API 키 설정
- 설정 메뉴에서 API 키 입력
- OpenAI, Claude, Gemini 중 원하는 것만 설정해도 OK

### 4단계: 보안 테스트 실행
- 보안 테스트 메뉴 클릭
- 도메인 입력 (예: https://example.com)
- 원하는 테스트 유형 선택
- 시작 버튼 클릭!

### 5단계: 결과 확인
- 실시간으로 진행 상황 확인
- AI들이 분석한 보안 리포트 확인
- PDF/Excel로 다운로드 가능

## 디렉토리 구조
```
security_project/
├── agents/          # AI 에이전트 구현
├── services/        # 마이크로서비스
├── docker/          # Docker 설정
├── core/           # 핵심 로직
├── config/         # 설정 파일
├── docs/           # 문서
├── docker-compose.yml
├── start.sh        # 시작 스크립트
└── test_system.py  # 시스템 테스트
```

## AI 제공업체별 특징

| 제공업체 | 직접 API | 클라우드 서비스 | 특징 |
|---------|---------|---------------|------|
| **OpenAI** | OpenAI API | Azure OpenAI | 뛰어난 추론 능력, 관리 업무 최적화 |
| **Claude** | Anthropic API | AWS Bedrock | 안전성 중심, 코드 리뷰 특화 |
| **Gemini** | Google AI API | Vertex AI | 대용량 처리, 빠른 속도 |

## 비용 최적화

### 모델 선택 전략
- **관리자/결정자**: GPT-4 (고급 추론)
- **실행자**: GPT-3.5-turbo, Claude Haiku (비용 효율)
- **분석가**: Claude Sonnet, Gemini Pro (균형)

### 제공업체 선택
- **개발**: 직접 API (유연성)
- **프로덕션**: 클라우드 서비스 (안정성)
- **대규모**: Bedrock, Vertex AI (볼륨 할인)

## 상세 문서
- [AI 제공업체 설정 가이드](docs/ai_providers.md)
- [시스템 아키텍처](docs/architecture.md)
- [보안 테스트 상세 가이드](docs/security_tests.md)
- [AI vs 보안 도구 역할 분담](docs/ai_vs_tools.md)
## 🎯 누구나 쉽게 사용하는 방법

### 📝 간단한 3단계
1. **웹사이트 접속**: http://localhost:3000
2. **도메인 입력**: 테스트하고 싶은 웹사이트 주소 입력
3. **결과 확인**: AI가 분석한 보안 리포트 확인

### 🔧 처음 사용할 때만 (1회)
- **설정 메뉴**에서 AI API 키 입력 (OpenAI, Claude, Gemini 중 하나만 있어도 OK)
- 모르겠으면 OpenAI API 키만 입력해도 충분!

### 💡 이런 상황에서 사용하세요
- **웹사이트 런칭 전**: 보안 문제 미리 확인
- **정기 점검**: 월 1회 보안 상태 체크  
- **경쟁사 분석**: 다른 회사 웹사이트 보안 수준 파악
- **문제 해결**: 보안 이슈 발생시 원인 분석
- **학습 목적**: 보안에 대해 배우고 싶을 때

### 🎯 모든 테스트를 누구나 사용 가능
- **정적 분석**: 코드 보안 검사, 의존성 취약점, 시크릿 키 탐지
- **동적 테스트**: SQL 인젝션, XSS, 인증 테스트, 브루트포스
- **웹 취약점**: CSRF, 디렉토리 트래버설, 파일 업로드
- **네트워크 보안**: 포트 스캔, SSL/TLS, 보안 헤더

> 💡 **팁**: 웹사이트 유형을 선택하면 추천 테스트가 자동으로 체크됩니다!

## 🚀 주요 특징

### 🤖 멀티 AI 시스템
- **6개 실행자 AI**: 병렬로 다양한 보안 테스트 수행
- **3개 분석가 AI**: 서로 다른 관점에서 결과 분석
- **1개 결정자 AI**: 최종 종합 판단 및 리포트 생성

### 🎨 직관적인 웹 인터페이스
- **드래그 앤 드롭**: 파일 업로드로 간편한 테스트
- **실시간 진행률**: 테스트 진행 상황을 실시간으로 확인
- **시각적 리포트**: 차트와 그래프로 결과를 쉽게 이해

### 🔒 포괄적인 보안 테스트
- **정적 분석**: 코드 레벨의 보안 취약점 탐지
- **동적 테스트**: 실제 공격 시나리오 시뮬레이션
- **네트워크 보안**: 포트 스캔, SSL/TLS 검사
- **웹 취약점**: OWASP Top 10 기반 테스트

### 📊 상세한 분석 리포트
- **위험도별 분류**: 위험/주의/정보 수준으로 구분
- **해결 방안 제시**: 구체적인 수정 방법 안내
- **다양한 형식**: PDF, Excel, JSON 형태로 다운로드