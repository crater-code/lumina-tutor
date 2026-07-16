# 🚀 How to Start Your Chatbot

## ✅ Setup Complete!

Your chatbot is now configured with **Gemini API** and ready to use!

- ✅ Gemini API key configured
- ✅ All dependencies installed
- ✅ API connection tested successfully
- ✅ Using model: `gemini-2.5-flash`

---

## 🎯 Start the Application

### Step 1: Start the Backend Server

Open a **new terminal/command prompt** and run:

```bash
start_backend.bat
```

Or manually:
```bash
python -m uvicorn src.main:app --host 0.0.0.0 --port 8000 --reload
```

You should see:
```
INFO:     Uvicorn running on http://0.0.0.0:8000 (Press CTRL+C to quit)
INFO:     Started reloader process
INFO:     Started server process
INFO:     Waiting for application startup.
INFO:     Application startup complete.
```

**Backend is now running at:** http://localhost:8000

**API Documentation:** http://localhost:8000/docs

---

### Step 2: Start the Frontend (Optional)

If you want to use the web interface:

Open **another terminal** and run:

```bash
cd frontend
npm install
npm run dev
```

**Frontend will run at:** http://localhost:5173 or http://localhost:3000

---

## 🧪 Test the API

### Option 1: Use the API Documentation
1. Open http://localhost:8000/docs in your browser
2. Try the `/health` endpoint to verify it's working
3. Upload a book using `/upload-book`
4. Ask questions using `/chat`

### Option 2: Use curl (Command Line)
```bash
# Test health endpoint
curl http://localhost:8000/health

# Upload a book
curl -X POST "http://localhost:8000/upload-book" -F "file=@path/to/your/book.pdf"

# Ask a question
curl -X POST "http://localhost:8000/chat" -H "Content-Type: application/json" -d "{\"query\":\"What is this book about?\",\"user_age\":10}"
```

---

## 📊 What's Different Now?

### Before (Ollama):
- ❌ Required powerful hardware
- ❌ Slow on weak systems
- ❌ 5.4GB RAM usage
- ❌ Model loading delays

### Now (Gemini API):
- ✅ No hardware requirements
- ✅ Fast responses
- ✅ Minimal RAM usage
- ✅ Instant availability
- ✅ Cloud-powered AI

---

## 🔧 Troubleshooting

### Backend won't start
**Error:** `ModuleNotFoundError: No module named 'src'`
**Fix:** Make sure you're in the project root directory

**Error:** `Address already in use`
**Fix:** Port 8000 is busy. Kill the process or use a different port:
```bash
python -m uvicorn src.main:app --host 0.0.0.0 --port 8001 --reload
```

### Gemini API errors
**Error:** `API key invalid`
**Fix:** Check your `.env` file has the correct API key

**Error:** `Quota exceeded`
**Fix:** You've hit the free tier limit. Wait or upgrade to paid tier

### Frontend won't connect
**Error:** `Network error`
**Fix:** Make sure backend is running on port 8000

---

## 📝 Quick Reference

### Backend Commands
```bash
# Start backend
start_backend.bat

# Or manually
python -m uvicorn src.main:app --host 0.0.0.0 --port 8000 --reload

# Test Gemini setup
python test_gemini_setup.py
```

### Frontend Commands
```bash
cd frontend
npm install
npm run dev
```

### Environment Variables (.env file)
```env
LLM_PROVIDER=gemini
GEMINI_API_KEY=AIzaSyCZqAgumXIoT2DPCr1VYMDPQ9LVnDDaitE
GEMINI_MODEL=gemini-2.5-flash
```

---

## 🎉 You're Ready!

1. **Start backend:** Run `start_backend.bat`
2. **Open browser:** Go to http://localhost:8000/docs
3. **Upload a book:** Use the `/upload-book` endpoint
4. **Ask questions:** Use the `/chat` endpoint
5. **Enjoy fast AI responses powered by Gemini!**

---

## 📚 Additional Resources

- **Gemini API Docs:** https://ai.google.dev/docs
- **Setup Guide:** See `GEMINI_SETUP_GUIDE.md`
- **Migration Info:** See `GEMINI_MIGRATION_COMPLETE.md`
- **Quick Start:** See `QUICK_START_GEMINI.md`

---

**Need help?** Check the troubleshooting section above or review the setup guides!
