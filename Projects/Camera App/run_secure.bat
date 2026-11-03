@echo off
echo ==================================================
echo       RESTARTING POLAROID SERVER & TUNNEL
echo ==================================================

:: 1. Kill old processes to free up the port
taskkill /F /IM python.exe >nul 2>&1

:: 2. Start the Python Web Server in a NEW window
echo Starting Local Server...
start "Polaroid Local Server" python -m http.server 8000 --bind 127.0.0.1

:: 3. Wait a moment for it to start
timeout /t 2 >nul

:: 4. Start the Secure Tunnel
echo.
echo ==================================================
echo       SECURE HTTPS LINK GENERATING...
echo ==================================================
echo.
echo LOOK FOR THE URL BELOW (e.g., https://xyz.localhost.run)
echo Type that EXACTLY into your mobile Safari.
echo.
echo KEEP THIS WINDOW OPEN!
echo.
ssh -o StrictHostKeyChecking=no -R 80:127.0.0.1:8000 nokey@localhost.run
pause
