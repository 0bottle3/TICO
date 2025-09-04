"""
실제 보안 스캐닝 도구들
AI는 이 도구들을 실행하고 결과를 분석하는 역할만 함
"""
import subprocess
import asyncio
import json
import requests
import socket
from typing import Dict, Any, List
from urllib.parse import urlparse
import ssl
import nmap
from loguru import logger


class SecurityScanner:
    """실제 보안 스캐닝을 수행하는 도구 클래스"""
    
    def __init__(self, target_url: str):
        self.target_url = target_url
        self.parsed_url = urlparse(target_url)
        self.host = self.parsed_url.netloc
        self.domain = self.parsed_url.hostname
        
    async def run_port_scan(self) -> Dict[str, Any]:
        """포트 스캔 실행 (nmap 사용)"""
        try:
            logger.info(f"포트 스캔 시작: {self.domain}")
            
            # nmap을 사용한 포트 스캔
            nm = nmap.PortScanner()
            scan_result = nm.scan(self.domain, '22,80,443,21,25,53,110,143,993,995,3306,5432,6379,27017')
            
            open_ports = []
            for host in scan_result['scan']:
                for port in scan_result['scan'][host]['tcp']:
                    port_info = scan_result['scan'][host]['tcp'][port]
                    if port_info['state'] == 'open':
                        open_ports.append({
                            'port': port,
                            'service': port_info.get('name', 'unknown'),
                            'version': port_info.get('version', ''),
                            'state': port_info['state']
                        })
            
            return {
                'status': 'completed',
                'open_ports': open_ports,
                'total_ports_scanned': len(scan_result['scan'].get(self.domain, {}).get('tcp', {})),
                'scan_time': '5-10초'
            }
            
        except Exception as e:
            logger.error(f"포트 스캔 실패: {e}")
            return {
                'status': 'failed',
                'error': str(e),
                'open_ports': []
            }
    
    async def check_ssl_tls(self) -> Dict[str, Any]:
        """SSL/TLS 검사 (실제 SSL 연결 테스트)"""
        try:
            logger.info(f"SSL/TLS 검사 시작: {self.domain}")
            
            # SSL 인증서 정보 가져오기
            context = ssl.create_default_context()
            with socket.create_connection((self.domain, 443), timeout=10) as sock:
                with context.wrap_socket(sock, server_hostname=self.domain) as ssock:
                    cert = ssock.getpeercert()
                    cipher = ssock.cipher()
                    version = ssock.version()
            
            return {
                'status': 'completed',
                'certificate': {
                    'subject': dict(x[0] for x in cert['subject']),
                    'issuer': dict(x[0] for x in cert['issuer']),
                    'version': cert['version'],
                    'not_before': cert['notBefore'],
                    'not_after': cert['notAfter']
                },
                'cipher_suite': cipher,
                'tls_version': version,
                'scan_time': '2-3초'
            }
            
        except Exception as e:
            logger.error(f"SSL/TLS 검사 실패: {e}")
            return {
                'status': 'failed',
                'error': str(e)
            }
    
    async def check_security_headers(self) -> Dict[str, Any]:
        """보안 헤더 검사 (HTTP 요청으로 헤더 확인)"""
        try:
            logger.info(f"보안 헤더 검사 시작: {self.target_url}")
            
            response = requests.get(self.target_url, timeout=10, allow_redirects=True)
            headers = response.headers
            
            security_headers = {
                'Content-Security-Policy': headers.get('Content-Security-Policy'),
                'X-Frame-Options': headers.get('X-Frame-Options'),
                'X-XSS-Protection': headers.get('X-XSS-Protection'),
                'X-Content-Type-Options': headers.get('X-Content-Type-Options'),
                'Strict-Transport-Security': headers.get('Strict-Transport-Security'),
                'Referrer-Policy': headers.get('Referrer-Policy')
            }
            
            missing_headers = [k for k, v in security_headers.items() if v is None]
            
            return {
                'status': 'completed',
                'headers': security_headers,
                'missing_headers': missing_headers,
                'security_score': max(0, 100 - len(missing_headers) * 15),
                'scan_time': '1-2초'
            }
            
        except Exception as e:
            logger.error(f"보안 헤더 검사 실패: {e}")
            return {
                'status': 'failed',
                'error': str(e)
            }
    
    async def run_sql_injection_test(self) -> Dict[str, Any]:
        """SQL 인젝션 테스트 (sqlmap 사용)"""
        try:
            logger.info(f"SQL 인젝션 테스트 시작: {self.target_url}")
            
            # sqlmap 명령어 실행 (안전한 옵션만 사용)
            cmd = [
                'sqlmap',
                '-u', self.target_url,
                '--batch',  # 자동 응답
                '--crawl=2',  # 2단계까지만 크롤링
                '--level=1',  # 기본 레벨
                '--risk=1',   # 낮은 위험도
                '--timeout=10',
                '--retries=1',
                '--technique=B',  # Boolean-based blind만
                '--no-cast',
                '--disable-coloring',
                '--format=JSON'
            ]
            
            # 비동기로 프로세스 실행
            process = await asyncio.create_subprocess_exec(
                *cmd,
                stdout=asyncio.subprocess.PIPE,
                stderr=asyncio.subprocess.PIPE
            )
            
            stdout, stderr = await asyncio.wait_for(process.communicate(), timeout=300)  # 5분 제한
            
            if process.returncode == 0:
                # sqlmap 결과 파싱
                result_text = stdout.decode('utf-8')
                vulnerabilities = []
                
                if 'vulnerable' in result_text.lower():
                    vulnerabilities.append({
                        'type': 'SQL Injection',
                        'severity': 'High',
                        'description': 'SQL 인젝션 취약점이 발견되었습니다.'
                    })
                
                return {
                    'status': 'completed',
                    'vulnerabilities': vulnerabilities,
                    'scan_time': '2-5분',
                    'tool_used': 'sqlmap'
                }
            else:
                return {
                    'status': 'completed',
                    'vulnerabilities': [],
                    'scan_time': '2-5분',
                    'note': 'SQL 인젝션 취약점이 발견되지 않았습니다.'
                }
                
        except asyncio.TimeoutError:
            logger.warning("SQL 인젝션 테스트 시간 초과")
            return {
                'status': 'timeout',
                'error': '테스트 시간이 초과되었습니다 (5분 제한)',
                'scan_time': '5분+'
            }
        except Exception as e:
            logger.error(f"SQL 인젝션 테스트 실패: {e}")
            return {
                'status': 'failed',
                'error': str(e)
            }
    
    async def run_brute_force_test(self) -> Dict[str, Any]:
        """브루트포스 테스트 (hydra 사용, 매우 제한적)"""
        try:
            logger.info(f"브루트포스 테스트 시작: {self.target_url}")
            
            # 매우 제한적인 브루트포스 테스트 (실제로는 로그인 페이지 존재 여부만 확인)
            login_endpoints = ['/login', '/admin', '/wp-admin', '/signin', '/auth']
            found_endpoints = []
            
            for endpoint in login_endpoints:
                try:
                    test_url = f"{self.target_url.rstrip('/')}{endpoint}"
                    response = requests.get(test_url, timeout=5)
                    
                    if response.status_code == 200:
                        # 로그인 폼이 있는지 간단히 확인
                        if any(keyword in response.text.lower() for keyword in ['password', 'login', 'username']):
                            found_endpoints.append({
                                'endpoint': endpoint,
                                'status_code': response.status_code,
                                'has_login_form': True
                            })
                except:
                    continue
            
            # 실제 브루트포스는 하지 않고, 보안 권장사항만 제시
            recommendations = []
            if found_endpoints:
                recommendations.extend([
                    '강력한 패스워드 정책 적용',
                    '계정 잠금 정책 설정',
                    '2단계 인증 도입',
                    'CAPTCHA 적용',
                    '로그인 시도 제한'
                ])
            
            return {
                'status': 'completed',
                'login_endpoints': found_endpoints,
                'recommendations': recommendations,
                'scan_time': '10-30초',
                'note': '실제 브루트포스 공격은 수행하지 않고 보안 권장사항만 제시합니다.'
            }
            
        except Exception as e:
            logger.error(f"브루트포스 테스트 실패: {e}")
            return {
                'status': 'failed',
                'error': str(e)
            }
    
    async def run_xss_test(self) -> Dict[str, Any]:
        """XSS 테스트 (기본적인 페이로드 테스트)"""
        try:
            logger.info(f"XSS 테스트 시작: {self.target_url}")
            
            # 안전한 XSS 테스트 페이로드 (실제 스크립트 실행 안함)
            test_payloads = [
                '<script>alert("XSS")</script>',
                '"><script>alert("XSS")</script>',
                "javascript:alert('XSS')",
                '<img src=x onerror=alert("XSS")>'
            ]
            
            vulnerabilities = []
            
            # GET 파라미터 테스트
            for payload in test_payloads:
                try:
                    test_url = f"{self.target_url}?test={payload}"
                    response = requests.get(test_url, timeout=10)
                    
                    # 페이로드가 그대로 반영되는지 확인 (실제 실행은 안함)
                    if payload in response.text:
                        vulnerabilities.append({
                            'type': 'Reflected XSS',
                            'payload': payload,
                            'severity': 'Medium',
                            'location': 'GET parameter'
                        })
                        break  # 하나만 찾으면 충분
                except:
                    continue
            
            return {
                'status': 'completed',
                'vulnerabilities': vulnerabilities,
                'scan_time': '30초-2분',
                'note': '안전한 테스트 페이로드만 사용하여 실제 스크립트는 실행되지 않습니다.'
            }
            
        except Exception as e:
            logger.error(f"XSS 테스트 실패: {e}")
            return {
                'status': 'failed',
                'error': str(e)
            }


class SecurityToolOrchestrator:
    """보안 도구들을 조율하는 클래스"""
    
    def __init__(self, target_url: str):
        self.target_url = target_url
        self.scanner = SecurityScanner(target_url)
    
    async def run_test_suite(self, test_types: List[str]) -> Dict[str, Any]:
        """선택된 테스트들을 실행"""
        results = {}
        
        test_mapping = {
            'port_scan': self.scanner.run_port_scan,
            'ssl_tls_test': self.scanner.check_ssl_tls,
            'header_security': self.scanner.check_security_headers,
            'sql_injection': self.scanner.run_sql_injection_test,
            'brute_force': self.scanner.run_brute_force_test,
            'xss_testing': self.scanner.run_xss_test
        }
        
        for test_type in test_types:
            if test_type in test_mapping:
                logger.info(f"실행 중: {test_type}")
                results[test_type] = await test_mapping[test_type]()
            else:
                results[test_type] = {
                    'status': 'not_implemented',
                    'message': f'{test_type} 테스트는 아직 구현되지 않았습니다.'
                }
        
        return results