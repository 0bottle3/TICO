#!/bin/bash

echo "🚀 멀티 AI 보안 테스트 시스템 시작"

# API 키 확인
if [ -z "$OPENAI_API_KEY" ] || [ "$OPENAI_API_KEY" = "your_openai_api_key_here" ]; then
    echo "⚠️  경고: .env 파일에서 실제 API 키를 설정해주세요"
    echo "   OPENAI_API_KEY, ANTHROPIC_API_KEY, GOOGLE_API_KEY"
    echo ""
fi

# Docker Compose로 전체 시스템 시작
echo "📦 Docker 컨테이너들을 시작합니다..."
docker-compose up -d

echo ""
echo "✅ 시스템이 시작되었습니다!"
echo ""
echo "🌐 서비스 접속 정보:"
echo "   - 관리자 API: http://localhost:8000"
echo "   - 대시보드: http://localhost:3000"
echo "   - PostgreSQL: localhost:5432"
echo "   - Redis: localhost:6379"
echo ""
echo "📊 상태 확인:"
echo "   docker-compose ps"
echo ""
echo "📝 로그 확인:"
echo "   docker-compose logs -f [서비스명]"
echo ""
echo "🛑 시스템 종료:"
echo "   docker-compose down"