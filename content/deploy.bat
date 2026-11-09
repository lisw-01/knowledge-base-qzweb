@echo off
rem One-click: sync notes -> Quartz build -> SSH deploy to your own server.
cd /d "%~dp0"
git deploy %*
if errorlevel 1 (
  echo.
  echo Deploy failed. Please read the messages above.
  pause
)
