@echo off
title Launch Gaya Council & Mini Gaya
echo ==========================================================
echo   Launching Gaya Command Ecosystem (Update 0.5.2610)
echo   1. Council of Gaya Dashboard (Port 4200)
echo   2. Mini Gaya Desktop Companion & Voice Suite
echo ==========================================================

cd /d "%~dp0\..\council_of_gaya"
start "Council of Gaya" cmd /c "npm run dev"

cd /d "%~dp0\..\mini_gaya"
start "Mini Gaya" cmd /c "python launch_mini_gaya.py"

echo Ecosystem launched successfully!
exit /b 0
