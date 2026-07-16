#!/bin/bash
# Setup script for Book-Bounded Tutoring Chatbot

echo "Setting up Book-Bounded Tutoring Chatbot..."

# Backend setup
echo "Creating Python virtual environment..."
python -m venv venv

echo "Activating virtual environment..."
source venv/bin/activate

echo "Installing Python dependencies..."
pip install -r requirements.txt

# Frontend setup
echo "Installing frontend dependencies..."
cd frontend
npm install
cd ..

echo "Setup complete!"
echo ""
echo "To start the backend:"
echo "  1. Activate virtual environment: source venv/bin/activate"
echo "  2. Run: python src/main.py"
echo ""
echo "To start the frontend:"
echo "  1. cd frontend"
echo "  2. npm run dev"
