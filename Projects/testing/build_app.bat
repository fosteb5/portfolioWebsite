@echo off
echo Building UniTracker for Windows...
npm run electron:build
echo.
echo Build complete! You can find the app in dist-electron/win-unpacked
pause
