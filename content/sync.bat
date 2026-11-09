@echo off
rem Double-click entry point for knowledge-base sync.
rem Usage: double click (auto message), or: sync.bat "your commit message"
cd /d "%~dp0"
git sync %*
if errorlevel 1 (
  echo.
  echo Sync failed. Please read the messages above.
  pause
)
