@echo off
REM ============================================================
REM  Biznex — sokin chop etishni Chrome'da sinash uchun ishga tushirgich
REM
REM  Oddiy Chrome'da "Chek chiqarish" tugmasi bosilganda doim
REM  Windows chop etish oynasi chiqadi — bu brauzerning xavfsizlik
REM  cheklovi, kodga bog'liq emas.
REM
REM  Bu skript Chrome'ni --kiosk-printing bayrog'i bilan ochadi —
REM  aynan .exe (desktop) dasturda ishlatiladigan usul bilan bir xil.
REM  Shu oynada chek chiqarilganda hech qanday oyna chiqmasdan,
REM  to'g'ridan-to'g'ri standart printerga yuboriladi.
REM
REM  ESLATMA: Django serverini ("python manage.py runserver") avval
REM  alohida oynada ishga tushirib qo'ying, keyin shu faylni ishga tushiring.
REM ============================================================

set CHROME_PATH="%ProgramFiles%\Google\Chrome\Application\chrome.exe"
if not exist %CHROME_PATH% set CHROME_PATH="%ProgramFiles(x86)%\Google\Chrome\Application\chrome.exe"

start "" %CHROME_PATH% --kiosk-printing --new-window "http://127.0.0.1:8000/"
