# 🚀 Quick Start: Gemini API Integration

## TL;DR - 3 Steps to Get Running

### 1️⃣ Get Your API Key (2 minutes)
Visit: **https://makersuite.google.com/app/apikey**
- Sign in with Google
- Click "Create API Key"
- Copy the key

### 2️⃣ Configure (1 minute)
**Windows:**
```bash
setup_gemini.bat
```

**Mac/Linux:**
```bash
chmod +x setup_gemini.sh
./setup_gemini.sh
```

**Or manually:**
```bash
copy .env.template .env
# Edit .env and paste your API key
pip install google-generativeai
```

### 3️⃣ Test (30 seconds)
```bash
python test_gemini_setup.py
```

**That's it!** 🎉

---

## What You Need

### Required
- ✅ Google account (free)
- ✅ Gemini API key (free tier available)
- ✅ Internet connection

### NOT Required
- ❌ Powerful GPU
- ❌ Ollama installation
- ❌ Local AI models
- ❌ Lots of RAM

---

## Your `.env` File Should Look Like This

```env
LLM_PROVIDER=gemini
GEMINI_API_KEY=AIzaSyC...your_actual_key_here
GEMINI_MODEL=gemini-1.5-flash
```

**⚠️ Replace `AIzaSyC...your_actual_key_here` with your real API key!**

---

## Testing

### Automated Test
```bash
python test_gemini_setup.py
```

### Manual Test
```python
from src.bounded_chatbot import BoundedChatbotEngine

bot = BoundedChatbotEngine()
print(f"✅ Gemini is {'ready' if bot.llm_available else 'not configured'}")
```

---

## Common Issues

### ❌ "GEMINI_API_KEY is not configured"
**Fix:** Create `.env` file and add your API key

### ❌ "google-generativeai package is NOT installed"
**Fix:** `pip install google-generativeai`

### ❌ "API connection failed"
**Fix:** Check your API key is valid and you have internet

---

## Cost

### Free Tier (Perfect for Development)
- **15 requests per minute**
- **1,500 requests per day**
- **1 million tokens per month**

This is more than enough for testing and small-scale use!

### Paid Tier (If You Need More)
- **Gemini 1.5 Flash:** $0.075 per 1M input tokens
- Very affordable for production use

---

## Why Gemini > Ollama (For Your Case)

| Feature | Gemini API | Ollama |
|---------|-----------|--------|
| **Hardware** | ☁️ Cloud (none needed) | 💻 Local (GPU required) |
| **Speed** | ⚡ Fast | 🐌 Slow on weak hardware |
| **Setup** | 🎯 2 minutes | 🔧 Complex |
| **Cost** | 💰 Free tier + cheap | 🆓 Free but hardware cost |
| **Quality** | 🌟 State-of-the-art | 👍 Good |

**For your hardware limitations, Gemini is the clear winner!**

---

## Next Steps After Setup

1. **Start your backend:**
   ```bash
   python src/main.py
   ```

2. **Start your frontend:**
   ```bash
   cd frontend
   npm run dev
   ```

3. **Test with real queries!**
   - Upload a book
   - Ask questions
   - See Gemini-powered responses

---

## Files Reference

- **Setup Guide:** `GEMINI_SETUP_GUIDE.md` (detailed instructions)
- **Test Script:** `test_gemini_setup.py` (verify setup)
- **Migration Info:** `GEMINI_MIGRATION_COMPLETE.md` (what changed)
- **This File:** `QUICK_START_GEMINI.md` (quick reference)

---

## Support

### Get API Key
🔑 https://makersuite.google.com/app/apikey

### Documentation
📚 https://ai.google.dev/docs

### Test Your Setup
```bash
python test_gemini_setup.py
```

---

**Ready to go? Get your API key and run the setup script!** 🚀
