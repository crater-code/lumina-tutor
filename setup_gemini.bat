@echo off
echo ============================================
echo Gemini API Setup Script
echo ============================================
echo.

REM Check if .env exists
if exist .env (
    echo [INFO] .env file already exists
    echo.
) else (
    echo [INFO] Creating .env file from template...
    copy .env.template .env
    echo.
    echo [ACTION REQUIRED] Please edit .env file and add your Gemini API key
    echo Get your key from: https://makersuite.google.com/app/apikey
    echo.
    pause
)

echo [INFO] Installing google-generativeai package...
pip install google-generativeai
echo.

echo [INFO] Installing python-dotenv (optional but recommended)...
pip install python-dotenv
echo.

echo [INFO] Running setup test...
python test_gemini_setup.py
echo.

echo ============================================
echo Setup Complete!
echo ============================================
echo.
echo Next steps:
echo   1. Make sure your .env file has your API key
echo   2. Start backend: python src/main.py
echo   3. Start frontend: cd frontend ^&^& npm run dev
echo.
pause
