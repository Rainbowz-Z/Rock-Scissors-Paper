@echo off
cd /d "%~dp0"
title AI Gesture Game

if exist ".venv\Scripts\activate.bat" (
    call .venv\Scripts\activate.bat
) else (
    echo [ERROR] Virtual environment not found!
    echo Please run: uv venv --python 3.8
    pause
    exit /b 1
)

python pygame_rockscissorpaper.py
pause
