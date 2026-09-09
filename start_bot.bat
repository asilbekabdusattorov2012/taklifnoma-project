@echo off
chcp 65001 >nul
cd /d "%~dp0"

if not exist venv\Scripts\python.exe (
    echo Virtual environment yaratilmoqda...
    py -m venv venv
)
venv\Scripts\python.exe -m pip install -r requirements.txt
if errorlevel 1 goto ERROR
venv\Scripts\python.exe manage.py migrate --noinput
if errorlevel 1 goto ERROR
echo Telegram bot ishga tushmoqda...
venv\Scripts\python.exe telegram_bot.py
pause
exit /b 0
:ERROR
echo XATOLIK. Yuqoridagi xabarni tekshiring.
pause
exit /b 1
