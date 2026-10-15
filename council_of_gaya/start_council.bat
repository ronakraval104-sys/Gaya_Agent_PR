@echo off
title Council of Gaya Web Console
cd /d "%~dp0"
echo ==========================================================
echo   Council of Gaya - Operator Dashboard (:4200)
echo ==========================================================
echo.
if not exist "node_modules" (
    echo [*] Installing npm dependencies...
    npm install
)
echo [*] Launching Next.js console on http://localhost:4200 ...
npm run dev
pause
