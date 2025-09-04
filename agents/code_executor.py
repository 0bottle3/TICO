"""
코드 실행자 - 관리자 AI가 생성한 코드를 실행만 함
"""
import asyncio
import subprocess
import json
import tempfile
import os
from typing import Dict, Any
from loguru import logger


class CodeExecutor:
    """관리자 AI가 생성한 코드를 실행하는 클래스"""
    
    def __init__(self, executor_id: str):
        self.executor_id = executor_id
        
    async def execute_code(self, execution_package: Dict[str, Any]) -> Dict[str, Any]:
        """관리자 AI가 생성한 실행 패키지를 실행"""
        
        test_type = execution_package.get("test_type", "unknown")
        execution_code = execution_package.get("execution_code", "")
        shell_commands = execution_package.get("shell_commands", [])
        
        logger.info(f"실행자 {self.executor_id}: {test_type} 테스트 시작")
        
        try:
            # 1. Python 코드 실행
            if execution_code:
                python_result = await self._execute_python_code(execution_code)
            else:
                python_result = {}
            
            # 2. 쉘 명령어 실행
            shell_results = []
            for cmd in shell_commands:
                shell_result = await self._execute_shell_command(cmd)
                shell_results.append(shell_result)
            
            # 3. 결과 수집
            return {
                "status": "completed",
                "executor_id": self.executor_id,
                "test_type": test_type,
                "python_result": python_result,
                "shell_results": shell_results,
                "execution_time": "실제 측정 필요"
            }
            
        except Exception as e:
            logger.error(f"실행자 {self.executor_id}: {test_type} 실행 실패 - {e}")
            return {
                "status": "failed",
                "executor_id": self.executor_id,
                "test_type": test_type,
                "error": str(e)
            }
    
    async def _execute_python_code(self, code: str) -> Dict[str, Any]:
        """Python 코드 실행"""
        
        try:
            # 임시 파일에 코드 저장
            with tempfile.NamedTemporaryFile(mode='w', suffix='.py', delete=False) as f:
                f.write(code)
                temp_file = f.name
            
            # Python 코드 실행
            process = await asyncio.create_subprocess_exec(
                'python', temp_file,
                stdout=asyncio.subprocess.PIPE,
                stderr=asyncio.subprocess.PIPE
            )
            
            stdout, stderr = await asyncio.wait_for(process.communicate(), timeout=600)  # 10분 제한
            
            # 임시 파일 삭제
            os.unlink(temp_file)
            
            if process.returncode == 0:
                try:
                    # JSON 결과 파싱 시도
                    result = json.loads(stdout.decode('utf-8'))
                    return {"status": "success", "result": result}
                except json.JSONDecodeError:
                    # 일반 텍스트 결과
                    return {"status": "success", "result": stdout.decode('utf-8')}
            else:
                return {
                    "status": "error",
                    "error": stderr.decode('utf-8')
                }
                
        except asyncio.TimeoutError:
            return {
                "status": "timeout",
                "error": "코드 실행 시간 초과 (10분)"
            }
        except Exception as e:
            return {
                "status": "error", 
                "error": str(e)
            }
    
    async def _execute_shell_command(self, command: str) -> Dict[str, Any]:
        """쉘 명령어 실행"""
        
        try:
            # 안전한 명령어인지 확인
            if not self._is_safe_command(command):
                return {
                    "status": "blocked",
                    "error": f"안전하지 않은 명령어: {command}"
                }
            
            # 명령어 실행
            process = await asyncio.create_subprocess_shell(
                command,
                stdout=asyncio.subprocess.PIPE,
                stderr=asyncio.subprocess.PIPE
            )
            
            stdout, stderr = await asyncio.wait_for(process.communicate(), timeout=300)  # 5분 제한
            
            if process.returncode == 0:
                return {
                    "status": "success",
                    "command": command,
                    "output": stdout.decode('utf-8')
                }
            else:
                return {
                    "status": "error",
                    "command": command,
                    "error": stderr.decode('utf-8')
                }
                
        except asyncio.TimeoutError:
            return {
                "status": "timeout",
                "command": command,
                "error": "명령어 실행 시간 초과 (5분)"
            }
        except Exception as e:
            return {
                "status": "error",
                "command": command,
                "error": str(e)
            }
    
    def _is_safe_command(self, command: str) -> bool:
        """안전한 명령어인지 확인"""
        
        # 허용된 보안 도구들
        allowed_tools = [
            'nmap', 'sqlmap', 'nikto', 'dirb', 'gobuster',
            'curl', 'wget', 'openssl', 'dig', 'nslookup',
            'python', 'python3', 'pip', 'pip3'
        ]
        
        # 금지된 명령어들
        forbidden_commands = [
            'rm', 'del', 'format', 'fdisk', 'mkfs',
            'dd', 'shutdown', 'reboot', 'halt',
            'su', 'sudo', 'passwd', 'chown', 'chmod'
        ]
        
        command_lower = command.lower()
        
        # 금지된 명령어 확인
        for forbidden in forbidden_commands:
            if forbidden in command_lower:
                return False
        
        # 허용된 도구로 시작하는지 확인
        for tool in allowed_tools:
            if command_lower.startswith(tool):
                return True
        
        return False


class ExecutorAgent:
    """실행자 AI - 코드를 받아서 실행만 함"""
    
    def __init__(self, executor_id: str, ai_provider: str):
        self.executor_id = executor_id
        self.ai_provider = ai_provider
        self.code_executor = CodeExecutor(executor_id)
    
    async def process(self, execution_package: Dict[str, Any]) -> Dict[str, Any]:
        """관리자 AI가 보낸 실행 패키지를 처리"""
        
        logger.info(f"실행자 {self.executor_id} ({self.ai_provider}): 작업 수신")
        
        # 실행 패키지 검증
        if not self._validate_package(execution_package):
            return {
                "status": "invalid_package",
                "executor_id": self.executor_id,
                "error": "실행 패키지가 유효하지 않습니다"
            }
        
        # 코드 실행
        result = await self.code_executor.execute_code(execution_package)
        
        # 실행자 정보 추가
        result["executor_id"] = self.executor_id
        result["ai_provider"] = self.ai_provider
        
        return result
    
    def _validate_package(self, package: Dict[str, Any]) -> bool:
        """실행 패키지 유효성 검증"""
        
        required_fields = ["test_type"]
        
        for field in required_fields:
            if field not in package:
                return False
        
        # 실행 코드나 쉘 명령어 중 하나는 있어야 함
        if not package.get("execution_code") and not package.get("shell_commands"):
            return False
        
        return True