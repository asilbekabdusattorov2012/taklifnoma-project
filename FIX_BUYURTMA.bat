@echo off
setlocal
cd /d "%~dp0"
echo TAKLIFNOMA BUYURTMA TUZATISH
if not exist venv\Scripts\python.exe py -m venv venv
venv\Scripts\python.exe -m pip install -r requirements.txt
venv\Scripts\python.exe manage.py migrate --noinput
if errorlevel 1 goto ERROR
echo Tayyor. Endi start.bat ni ishga tushiring.
pause
exit /b 0
:ERROR
echo Migration bajarilmadi. Yuqoridagi xatoni tekshiring.
pause
exit /b 1
