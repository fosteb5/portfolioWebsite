@echo off
echo ===================================================
echo Starting Polaroid App Server
echo ===================================================
echo.
echo 1. The app will open in your browser automatically.
echo 2. To test on your iPhone:
echo    - Make sure your phone and PC are on the same WiFi.
echo    - Find your PC's IP address (run 'ipconfig' in a new terminal).
echo    - On phone, go to: http://[YOUR-PC-IP]:8000
echo    - Tap Share -> Add to Home Screen.
echo.
echo Press Ctrl+C to stop the server.
echo.

start http://localhost:8000
python -m http.server 8000
