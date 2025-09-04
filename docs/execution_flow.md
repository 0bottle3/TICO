# 실행 흐름 상세 가이드

## 🔄 완전한 실행 흐름

### 1단계: 관리자 AI (코드 생성)
```python
# 사용자 요청: "example.com에 브루트포스 테스트"

관리자_AI.process({
    "target_url": "https://example.com",
    "test_scope": ["brute_force", "sql_injection"]
})

# 관리자 AI가 생성하는 것:
{
    "brute_force": {
        "execution_code": "완전한 Python 브루트포스 코드",
        "shell_commands": ["nmap -p 80,443 example.com"],
        "expected_runtime": "5-10분"
    },
    "sql_injection": {
        "execution_code": "완전한 SQL 인젝션 테스트 코드", 
        "shell_commands": ["sqlmap -u example.com --batch"],
        "expected_runtime": "10-15분"
    }
}
```

### 2단계: 실행자 AI들 (코드 실행)
```python
# 6개 실행자가 병렬로 코드 실행

실행자_OpenAI_정적.execute(브루트포스_코드)
실행자_Claude_정적.execute(브루트포스_코드)  
실행자_Gemini_정적.execute(브루트포스_코드)

실행자_OpenAI_동적.execute(SQL인젝션_코드)
실행자_Claude_동적.execute(SQL인젝션_코드)
실행자_Gemini_동적.execute(SQL인젝션_코드)

# 각 실행자는 토큰 사용 없이 코드만 실행
# 실제 시간: 5-15분 (도구 실행 시간)
```

### 3단계: 분석가 AI들 (결과 분석)
```python
# 3개 분석가가 실행 결과를 받아서 분석

분석가_Claude.analyze({
    "execution_results": [실행자1_결과, 실행자2_결과, ...]
})

분석가_Gemini.analyze({
    "execution_results": [실행자1_결과, 실행자2_결과, ...]
})

분석가_OpenAI.analyze({
    "execution_results": [실행자1_결과, 실행자2_결과, ...]
})

# 각 분석가는 1000-1500 토큰 사용
# 분석 시간: 10-20초
```

### 4단계: 결정자 AI (최종 판단)
```python
결정자_AI.decide({
    "analysis_results": [분석가1_결과, 분석가2_결과, 분석가3_결과]
})

# 최종 리포트 생성: 1500-2000 토큰 사용
# 결정 시간: 15-30초
```

---

## 💰 토큰 사용량 분석

### 관리자 AI (코드 생성)
- **입력**: 사용자 요청 (100-200 토큰)
- **출력**: 완전한 실행 코드 (2000-4000 토큰)
- **총 사용량**: 2100-4200 토큰

### 실행자 AI들 (6개)
- **토큰 사용량**: 0 토큰 (코드 실행만)
- **실행 시간**: 5-15분 (실제 보안 테스트)

### 분석가 AI들 (3개)
- **각각**: 1000-1500 토큰
- **총 사용량**: 3000-4500 토큰

### 결정자 AI
- **사용량**: 1500-2000 토큰

### 전체 토큰 사용량
- **총합**: 6600-10700 토큰
- **비용**: 약 $0.10-0.20 (GPT-4 기준)

---

## ⏱️ 시간 분석

### 병렬 처리 시간
```
관리자 AI (코드 생성): 30-60초
    ↓
실행자들 (병렬 실행): 5-15분  ← 가장 오래 걸림
    ↓
분석가들 (병렬 분석): 10-20초
    ↓
결정자 AI (최종 판단): 15-30초

총 소요 시간: 6-17분
```

### 기존 방식 vs 하이브리드 방식
```
기존 방식 (AI가 모든 것 추측):
- 시간: 5-10분
- 토큰: 15000-25000개
- 정확도: 낮음 (실제 테스트 없음)
- 비용: $0.30-0.50

하이브리드 방식 (우리 시스템):
- 시간: 6-17분
- 토큰: 6600-10700개  
- 정확도: 높음 (실제 테스트 기반)
- 비용: $0.10-0.20
```

---

## 🔧 브루트포스 테스트 실제 예시

### 관리자 AI가 생성하는 코드
```python
# 완전한 브루트포스 테스트 코드
class BruteForceExecutor:
    def __init__(self, target_url):
        self.target_url = target_url
        # ... 완전한 구현
    
    def find_login_endpoints(self):
        # 로그인 페이지 탐지 로직
        
    def test_common_credentials(self):
        # 일반적인 자격증명 테스트
        
    def analyze_timing_attacks(self):
        # 타이밍 공격 분석
        
    def execute(self):
        # 전체 실행 로직
        return json_results
```

### 실행자 AI가 하는 일
```python
# 1. 코드 받기
execution_package = {
    "test_type": "brute_force",
    "execution_code": "위의 완전한 코드",
    "target_url": "https://example.com"
}

# 2. 코드 실행 (토큰 사용 없음)
executor = CodeExecutor()
result = executor.execute_code(execution_package)

# 3. 결과 반환
return {
    "status": "completed",
    "execution_time": "8분 30초",
    "results": {
        "login_endpoints": [...],
        "successful_logins": [...],
        "recommendations": [...]
    }
}
```

### 분석가 AI가 하는 일
```python
# 실행 결과를 받아서 분석 (1000-1500 토큰 사용)
analysis_prompt = f"""
브루트포스 테스트 결과:
{execution_results}

다음을 분석해주세요:
1. 발견된 취약점의 심각도
2. 비즈니스 영향도
3. 수정 우선순위
"""

# AI 분석 결과
return {
    "risk_level": "High",
    "business_impact": "Critical",
    "recommendations": [...],
    "security_score": 45
}
```

---

## 🎯 핵심 장점

### 1. 비용 효율성
- **실행자들**: 토큰 사용 없음 (코드만 실행)
- **관리자**: 한 번만 코드 생성
- **분석가들**: 결과만 분석 (최소 토큰)

### 2. 정확성
- **실제 테스트**: 진짜 브루트포스, SQL 인젝션 수행
- **실제 결과**: 추측이 아닌 실제 발견된 취약점
- **검증된 코드**: 관리자 AI가 생성한 완전한 코드

### 3. 확장성
- **새로운 테스트**: 관리자 AI가 새 코드 생성
- **새로운 도구**: 쉽게 통합 가능
- **병렬 처리**: 실행자들이 동시에 작업

### 4. 안전성
- **제한된 권한**: 실행자들은 안전한 코드만 실행
- **시간 제한**: 각 테스트별 최대 실행 시간 설정
- **샌드박스**: 격리된 환경에서 실행

이제 정말로 **관리자 AI가 완벽한 코드를 생성**하고, **실행자들은 그 코드를 실행만** 하는 효율적인 시스템이 완성되었습니다! 🚀