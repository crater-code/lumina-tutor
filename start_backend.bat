@echo off
echo ============================================
echo Starting Book-Bounded Tutoring Chatbot Backend
echo ============================================
echo.
echo Backend will run on: http://localhost:8000
echo API Documentation: http://localhost:8000/docs
echo.
echo Press Ctrl+C to stop the server
echo.

python -m uvicorn src.main:app --host 0.0.0.0 --port 8000 --reload
