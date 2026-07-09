@echo off
REM Biznex POS uchun Windows .exe yig'ish skripti
REM Talab: Windows + Python 3.11+ o'rnatilgan bo'lishi kerak

cd /d "%~dp0\.."

echo [1/3] Kerakli kutubxonalarni o'rnatish...
pip install -r desktop\requirements.txt
if errorlevel 1 goto :error

echo [2/3] Eski build fayllarini tozalash...
rmdir /s /q build 2>nul
rmdir /s /q dist 2>nul

echo [3/3] .exe fayl yig'ilmoqda (PyInstaller)...
pyinstaller desktop\biznex.spec --distpath desktop\dist --workpath desktop\build --noconfirm
if errorlevel 1 goto :error

copy /Y desktop\config.example.json desktop\dist\config.json >nul

echo.
echo TAYYOR! .exe fayl: desktop\dist\BiznexPOS.exe
echo Bu faylni istalgan Windows kompyuterga ko'chirib, ishga tushirishingiz mumkin.
echo Dastur HAR DOIM mahalliy (offline) rejimda ishlaydi.
echo.
echo Saytga fon rejimida sinxronlanishi uchun (internet bo'lganda):
echo   desktop\dist\config.json faylini oching va to'ldiring:
echo     "remote_url"     — Railway manzilingiz (masalan https://biznex.up.railway.app)
echo     "sync_api_key"   — saytdagi SYNC_API_KEY muhit o'zgaruvchisi bilan BIR XIL bo'lishi shart
pause
exit /b 0

:error
echo Xatolik yuz berdi. Yuqoridagi xabarni tekshiring.
pause
exit /b 1
