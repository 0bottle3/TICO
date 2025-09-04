"""
관리자 AI가 생성하는 브루트포스 테스트 코드 예시
실행자 AI는 이 코드를 받아서 그대로 실행만 함
"""
import requests
import time
import json
from urllib.parse import urljoin, urlparse
from concurrent.futures import ThreadPoolExecutor
import threading

class BruteForceExecutor:
    def __init__(self, target_url):
        self.target_url = target_url
        self.session = requests.Session()
        self.results = {
            "target": target_url,
            "login_endpoints": [],
            "successful_logins": [],
            "account_lockout_detected": False,
            "timing_attack_results": [],
            "recommendations": []
        }
        self.lock = threading.Lock()
    
    def find_login_endpoints(self):
        """로그인 엔드포인트 탐지"""
        common_paths = [
            '/login', '/admin', '/wp-admin', '/signin', '/auth',
            '/administrator', '/user/login', '/account/login',
            '/panel', '/dashboard', '/cp', '/manage'
        ]
        
        found_endpoints = []
        
        for path in common_paths:
            try:
                url = urljoin(self.target_url, path)
                response = self.session.get(url, timeout=10, allow_redirects=True)
                
                if response.status_code == 200:
                    # 로그인 폼 키워드 확인
                    login_indicators = [
                        'password', 'login', 'username', 'email',
                        'signin', 'log in', 'user', 'pass'
                    ]
                    
                    content_lower = response.text.lower()
                    if any(indicator in content_lower for indicator in login_indicators):
                        found_endpoints.append({
                            'url': url,
                            'status_code': response.status_code,
                            'title': self._extract_title(response.text),
                            'form_detected': True
                        })
                        
            except Exception as e:
                continue
        
        self.results['login_endpoints'] = found_endpoints
        return found_endpoints
    
    def test_common_credentials(self, endpoint_url, max_attempts=10):
        """일반적인 자격증명 테스트"""
        common_creds = [
            ('admin', 'admin'),
            ('admin', 'password'),
            ('admin', '123456'),
            ('administrator', 'administrator'),
            ('root', 'root'),
            ('user', 'user'),
            ('test', 'test'),
            ('guest', 'guest'),
            ('demo', 'demo'),
            ('admin', '')  # 빈 패스워드
        ]
        
        successful_logins = []
        attempt_count = 0
        
        for username, password in common_creds[:max_attempts]:
            if attempt_count >= max_attempts:
                break
                
            try:
                # POST 요청으로 로그인 시도
                login_data = {
                    'username': username,
                    'password': password,
                    'user': username,
                    'pass': password,
                    'email': username,
                    'login': 'Login'
                }
                
                start_time = time.time()
                response = self.session.post(
                    endpoint_url, 
                    data=login_data, 
                    timeout=15,
                    allow_redirects=False
                )
                response_time = time.time() - start_time
                
                # 성공 지표 확인
                success_indicators = [
                    response.status_code in [302, 301],  # 리다이렉트
                    'dashboard' in response.text.lower(),
                    'welcome' in response.text.lower(),
                    'logout' in response.text.lower()
                ]
                
                # 실패 지표 확인
                failure_indicators = [
                    'invalid' in response.text.lower(),
                    'incorrect' in response.text.lower(),
                    'failed' in response.text.lower(),
                    'error' in response.text.lower()
                ]
                
                if any(success_indicators) and not any(failure_indicators):
                    successful_logins.append({
                        'username': username,
                        'password': password,
                        'endpoint': endpoint_url,
                        'response_code': response.status_code,
                        'response_time': response_time
                    })
                
                # 계정 잠금 감지
                if 'locked' in response.text.lower() or 'blocked' in response.text.lower():
                    self.results['account_lockout_detected'] = True
                    break
                
                # 타이밍 공격 데이터 수집
                with self.lock:
                    self.results['timing_attack_results'].append({
                        'username': username,
                        'response_time': response_time,
                        'status_code': response.status_code
                    })
                
                attempt_count += 1
                time.sleep(1)  # 요청 간격 조절
                
            except Exception as e:
                continue
        
        return successful_logins
    
    def analyze_timing_attacks(self):
        """타이밍 공격 분석"""
        if len(self.results['timing_attack_results']) < 5:
            return
        
        timing_data = self.results['timing_attack_results']
        avg_time = sum(r['response_time'] for r in timing_data) / len(timing_data)
        
        # 평균보다 현저히 긴 응답시간을 가진 사용자명 식별
        potential_valid_users = []
        for data in timing_data:
            if data['response_time'] > avg_time * 1.5:
                potential_valid_users.append(data['username'])
        
        if potential_valid_users:
            self.results['recommendations'].append(
                f"타이밍 공격으로 유효한 사용자명 추정 가능: {potential_valid_users}"
            )
    
    def generate_recommendations(self):
        """보안 권장사항 생성"""
        recommendations = []
        
        if self.results['login_endpoints']:
            recommendations.append("로그인 페이지가 발견되었습니다. 다음 보안 조치를 권장합니다:")
            recommendations.append("- 강력한 패스워드 정책 적용")
            recommendations.append("- 계정 잠금 정책 설정 (5회 실패 시 15분 잠금)")
            recommendations.append("- 2단계 인증(2FA) 도입")
            recommendations.append("- CAPTCHA 적용")
            recommendations.append("- 로그인 시도 로깅 및 모니터링")
        
        if self.results['successful_logins']:
            recommendations.append("⚠️ 약한 자격증명이 발견되었습니다!")
            recommendations.append("- 즉시 패스워드 변경 필요")
            recommendations.append("- 기본 계정 비활성화")
        
        if not self.results['account_lockout_detected']:
            recommendations.append("계정 잠금 정책이 없는 것으로 보입니다")
            recommendations.append("- 브루트포스 공격 방어를 위한 계정 잠금 정책 필요")
        
        self.results['recommendations'] = recommendations
    
    def _extract_title(self, html_content):
        """HTML에서 제목 추출"""
        try:
            start = html_content.lower().find('<title>') + 7
            end = html_content.lower().find('</title>')
            if start > 6 and end > start:
                return html_content[start:end].strip()
        except:
            pass
        return "Unknown"
    
    def execute(self):
        """브루트포스 테스트 실행"""
        print(f"브루트포스 테스트 시작: {self.target_url}")
        
        # 1. 로그인 엔드포인트 탐지
        endpoints = self.find_login_endpoints()
        print(f"발견된 로그인 엔드포인트: {len(endpoints)}개")
        
        # 2. 각 엔드포인트에 대해 자격증명 테스트
        all_successful = []
        for endpoint in endpoints:
            print(f"테스트 중: {endpoint['url']}")
            successful = self.test_common_credentials(endpoint['url'])
            all_successful.extend(successful)
        
        self.results['successful_logins'] = all_successful
        
        # 3. 타이밍 공격 분석
        self.analyze_timing_attacks()
        
        # 4. 권장사항 생성
        self.generate_recommendations()
        
        print("브루트포스 테스트 완료")
        return self.results


if __name__ == "__main__":
    import sys
    
    if len(sys.argv) != 2:
        print("사용법: python brute_force_code.py <target_url>")
        sys.exit(1)
    
    target_url = sys.argv[1]
    
    # 브루트포스 테스트 실행
    executor = BruteForceExecutor(target_url)
    results = executor.execute()
    
    # JSON 형태로 결과 출력 (실행자 AI가 파싱)
    print(json.dumps(results, indent=2, ensure_ascii=False))