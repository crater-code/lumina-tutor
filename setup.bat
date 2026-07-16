@echo off
REM Setup script for Book-Bounded Tutoring Chatbot (Windows)

echo Setting up Book-Bounded Tutoring Chatbot...

REM Backend setup
echo Creating Python virtual environment...
python -m venv venv

echo Activating virtual environment...
call venv\Scripts\activate.bat

echo Installing Python dependencies...
pip install -r requirements.txt

REM Frontend setup
echo Installing frontend dependencies...
cd frontend
call npm install
cd ..

echo Setup complete!
echo.
echo To start the backend:
echo   1. Activate virtual environment: venv\Scripts\activate.bat
echo   2. Run: python src\main.py
echo.
echo To start the frontend:
echo   1. cd frontend
echo   2. npm run dev
