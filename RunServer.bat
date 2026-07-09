@echo off
title Clash SL Server Launcher
color 0A

echo ===================================================
echo         Clash of SL - Server Launcher
echo ===================================================
echo.

echo [1] Checking Database (MySQL)...
tasklist /FI "IMAGENAME eq mysqld.exe" 2>NUL | find /I /N "mysqld.exe">NUL
if "%ERRORLEVEL%"=="0" (
    echo Database is already running.
) else (
    echo Starting MySQL Database...
    start "MySQL Server" cmd /c "C:\wamp64\bin\mysql\mysql8.4.7\bin\mysqld.exe --defaults-file=C:\wamp64\bin\mysql\mysql8.4.7\my.ini --console"
    timeout /t 3 /nobreak >nul
)

echo.
echo [2] Starting Clash SL Server...
cd /d "D:\Clash-Of-SL\Clash SL Server\bin\Debug"
start "Clash SL Server" "Clash SL Server.exe"

echo.
echo Server started successfully! 
echo You can now open the Clash of SL app on your phone or emulator.
echo (Keep the black server windows open while playing)
echo.
exit
