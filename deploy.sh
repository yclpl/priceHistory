#!/bin/bash

echo "🚀 Backend Deployment Script (Render.com)"
echo "=========================================="

# Renklendirme
GREEN='\033[0;32m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

echo ""
echo -e "${BLUE}1/4${NC} Git repository kontrol ediliyor..."
if [ ! -d .git ]; then
    echo "Git repository oluşturuluyor..."
    git init
    echo -e "${GREEN}✓${NC} Git repository oluşturuldu"
else
    echo -e "${GREEN}✓${NC} Git repository mevcut"
fi

echo ""
echo -e "${BLUE}2/4${NC} .gitignore kontrol ediliyor..."
if [ ! -f .gitignore ]; then
    echo "⚠️  .gitignore bulunamadı! Dosyayı oluşturun."
else
    echo -e "${GREEN}✓${NC} .gitignore mevcut"
fi

echo ""
echo -e "${BLUE}3/4${NC} Dosyalar commit ediliyor..."
git add .
git commit -m "Backend deployment ready"
echo -e "${GREEN}✓${NC} Commit tamamlandı"

echo ""
echo -e "${BLUE}4/4${NC} GitHub'a push..."
echo "GitHub repository URL'inizi girin:"
read REPO_URL

if [ ! -z "$REPO_URL" ]; then
    git remote remove origin 2>/dev/null
    git remote add origin $REPO_URL
    git push -u origin main
    echo -e "${GREEN}✓${NC} Push tamamlandı!"
    
    echo ""
    echo "=========================================="
    echo "✅ Backend GitHub'a yüklendi!"
    echo ""
    echo "📋 Sırada Render.com'da deployment:"
    echo "1. https://render.com adresine gidin"
    echo "2. 'New +' → 'Web Service' seçin"
    echo "3. GitHub repo'nuzu seçin"
    echo "4. Ayarlar:"
    echo "   - Name: gecmisi-backend"
    echo "   - Environment: Python 3"
    echo "   - Build: pip install -r requirements.txt"
    echo "   - Start: gunicorn app:app"
    echo "   - Plan: Free"
    echo "5. 'Create Web Service' tıklayın"
    echo ""
    echo "🌐 Deploy sonrası URL'inizi not edin!"
    echo "=========================================="
else
    echo "⚠️  Repository URL girilmedi!"
fi
