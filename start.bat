@echo off
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

echo [2/4] Django o'rnatilmoqda...
venv\Scripts\python.exe -m pip install -r requirements.txt
if errorlevel 1 goto ERROR

echo [3/4] Database migration...
venv\Scripts\python.exe manage.py migrate --noinput
if errorlevel 1 goto ERROR

echo [4/4] Sayt ishga tushmoqda...
echo http://127.0.0.1:8000/
echo.
venv\Scripts\python.exe manage.py runserver
exit /b 0

:ERROR
echo.
echo XATOLIK. Yuqoridagi xabarni tekshiring.
pause
exit /b 1
