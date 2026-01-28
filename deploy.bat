@echo off
echo ========================================
echo 🚀 Backend Deployment Script (Render.com)
echo ========================================
echo.

echo [1/4] Git repository kontrol ediliyor...
if not exist .git (
    echo Git repository olusturuluyor...
    git init
    echo ✓ Git repository olusturuldu
) else (
    echo ✓ Git repository mevcut
)

echo.
echo [2/4] .gitignore kontrol ediliyor...
if not exist .gitignore (
    echo ⚠️  .gitignore bulunamadi! Dosyayi olusturun.
) else (
    echo ✓ .gitignore mevcut
)

echo.
echo [3/4] Dosyalar commit ediliyor...
git add .
git commit -m "Backend deployment ready"
echo ✓ Commit tamamlandi

echo.
echo [4/4] GitHub'a push...
set /p REPO_URL="GitHub repository URL'inizi girin: "

if not "%REPO_URL%"=="" (
    git remote remove origin 2>nul
    git remote add origin %REPO_URL%
    git push -u origin main
    echo ✓ Push tamamlandi!
    
    echo.
    echo ==========================================
    echo ✅ Backend GitHub'a yuklendi!
    echo.
    echo 📋 Sirada Render.com'da deployment:
    echo 1. https://render.com adresine gidin
    echo 2. 'New +' → 'Web Service' secin
    echo 3. GitHub repo'nuzu secin
    echo 4. Ayarlar:
    echo    - Name: gecmisi-backend
    echo    - Environment: Python 3
    echo    - Build: pip install -r requirements.txt
    echo    - Start: gunicorn app:app
    echo    - Plan: Free
    echo 5. 'Create Web Service' tiklayin
    echo.
    echo 🌐 Deploy sonrasi URL'inizi not edin!
    echo ==========================================
) else (
    echo ⚠️  Repository URL girilmedi!
)

pause
