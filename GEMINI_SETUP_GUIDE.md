# Gemini API Integration Setup Guide

## Overview
Your chatbot now supports **Google Gemini API** as an alternative to Ollama. This is perfect for systems with limited hardware since all processing happens in the cloud.

## What Changed

### 1. **Multi-Provider Support**
The system now supports:
- **Gemini API** (recommended for limited hardware) ✅
- **Ollama** (local, requires powerful hardware)
- **Fallback mode** (simple responses without AI)

### 2. **Updated Files**
- `src/bounded_chatbot.py` - Now supports both Gemini and Ollama
- `.env.example` - Added Gemini configuration
- `requirements.txt` - Added `google-generativeai` package

## Setup Instructions

### Step 1: Get Your Gemini API Key

1. Go to [Google AI Studio](https://makersuite.google.com/app/apikey)
2. Sign in with your Google account
3. Click "Create API Key"
4. Copy your API key (keep it secret!)

### Step 2: Install Dependencies

```bash
pip install google-generativeai
```

Or install all requirements:
```bash
pip install -r requirements.txt
```

### Step 3: Configure Environment Variables

1. **Create a `.env` file** in your project root (if you don't have one):
   ```bash
   copy .env.example .env
   ```

2. **Edit the `.env` file** and add your Gemini API key:
   ```env
   # LLM Configuration
   LLM_PROVIDER=gemini
   GEMINI_API_KEY=your_actual_api_key_here
   GEMINI_MODEL=gemini-1.5-flash
   ```

   **Important:** Replace `your_actual_api_key_here` with your real API key!

### Step 4: Test the Integration

Run a quick test:
```bash
python -c "import os; os.environ['LLM_PROVIDER']='gemini'; os.environ['GEMINI_API_KEY']='YOUR_KEY'; from src.bounded_chatbot import BoundedChatbotEngine; bot = BoundedChatbotEngine(); print('✅ Gemini configured!' if bot.llm_available else '❌ Configuration failed')"
```

## Model Options

### Gemini 1.5 Flash (Recommended)
- **Fast** and cost-effective
- Good for educational chatbots
- Default model: `gemini-1.5-flash`

### Gemini 1.5 Pro
- More powerful but slower
- Better for complex explanations
- Set: `GEMINI_MODEL=gemini-1.5-pro`

## Pricing (as of 2024)

### Gemini 1.5 Flash
- **Free tier:** 15 requests per minute
- **Paid:** $0.075 per 1M input tokens, $0.30 per 1M output tokens
- Very affordable for educational use!

### Gemini 1.5 Pro
- **Free tier:** 2 requests per minute
- **Paid:** $1.25 per 1M input tokens, $5.00 per 1M output tokens

## Configuration Examples

### Example 1: Gemini (Recommended for you)
```env
LLM_PROVIDER=gemini
GEMINI_API_KEY=AIzaSyC...your_key_here
GEMINI_MODEL=gemini-1.5-flash
```

### Example 2: Ollama (If you have powerful hardware)
```env
LLM_PROVIDER=ollama
LLM_MODEL=llama3.1:8b
LLM_API_URL=http://localhost:11434/api/generate
```

### Example 3: Fallback Mode (No AI)
```env
LLM_PROVIDER=none
```

## Testing Your Setup

### Test 1: Check Configuration
```python
from src.bounded_chatbot import BoundedChatbotEngine

bot = BoundedChatbotEngine()
print(f"Provider: {bot.llm_provider}")
print(f"Available: {bot.llm_available}")
```

### Test 2: Generate a Response
```python
from src.bounded_chatbot import BoundedChatbotEngine
from src.models import Chunk

bot = BoundedChatbotEngine()

# Create a test chunk
chunk = Chunk(
    chunk_id="test_1",
    text="Photosynthesis is the process by which plants make food using sunlight.",
    page_numbers=[1],
    book_id="test_book"
)

# Generate response
response = bot._handle_content_query(
    query="What is photosynthesis?",
    chunks=[chunk],
    user_age=10,
    language="en"
)

print(response.text)
```

## Troubleshooting

### Error: "Gemini API key not configured"
- Make sure you created a `.env` file
- Check that `GEMINI_API_KEY` is set correctly
- Verify the key doesn't have extra spaces

### Error: "google-generativeai package not installed"
```bash
pip install google-generativeai
```

### Error: "API key invalid"
- Get a new API key from [Google AI Studio](https://makersuite.google.com/app/apikey)
- Make sure you copied the entire key

### Slow responses
- Switch to `gemini-1.5-flash` (faster)
- Check your internet connection
- Verify you're not hitting rate limits

## Security Best Practices

1. **Never commit your API key to Git**
   - The `.env` file is already in `.gitignore`
   - Never share your `.env` file

2. **Use environment variables**
   - Don't hardcode API keys in your code
   - Always use `os.getenv()`

3. **Rotate keys regularly**
   - Generate new keys periodically
   - Delete old keys from Google AI Studio

## Next Steps

1. ✅ Get your Gemini API key
2. ✅ Update your `.env` file
3. ✅ Install dependencies
4. ✅ Test the integration
5. ✅ Start your server and enjoy fast AI responses!

## Support

If you encounter issues:
1. Check the logs for error messages
2. Verify your API key is valid
3. Test with a simple prompt first
4. Check [Google AI documentation](https://ai.google.dev/docs)

---

**You're all set!** Your chatbot will now use Gemini API for generating responses, which should work much better on your hardware than Ollama. 🚀
