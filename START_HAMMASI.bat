@echo off
chcp 65001 >nul
setlocal
cd /d "%~dp0"

if not exist venv\Scripts\python.exe (
    echo [1/4] Virtual environment yaratilmoqda...
    py -m venv venv
    if errorlevel 1 python -m venv venv
)
if not exist venv\Scripts\python.exe (
    echo VIRTUAL ENVIRONMENT YARATILMADI.
    pause
    exit /b 1
)

echo [2/4] Kerakli paketlar o'rnatilmoqda...
venv\Scripts\python.exe -m pip install -r requirements.txt
if errorlevel 1 goto ERROR

echo [3/4] Database tayyorlanmoqda...
venv\Scripts\python.exe manage.py migrate --noinput
if errorlevel 1 goto ERROR

echo [4/4] Django va Telegram bot ishga tushmoqda...
start "TAKLIFNOMA DJANGO" cmd /k "cd /d "%~dp0" && venv\Scripts\python.exe manage.py runserver"
start "TAKLIFNOMA TELEGRAM BOT" cmd /k "cd /d "%~dp0" && venv\Scripts\python.exe telegram_bot.py"

echo.
echo ==========================================
echo Tayyor!
echo Sayt: http://127.0.0.1:8000/
echo Bot alohida oynada ishga tushadi.
echo ==========================================
pause
exit /b 0

:ERROR
echo.
echo XATOLIK. Yuqoridagi xabarni tekshiring.
pause
exit /b 1
