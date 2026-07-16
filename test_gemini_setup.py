"""Quick test script to verify Gemini API integration."""

import os
import sys

def test_gemini_setup():
    """Test Gemini API configuration."""
    
    print("=" * 60)
    print("🔍 Testing Gemini API Setup")
    print("=" * 60)
    print()
    
    # Step 1: Check environment variables
    print("Step 1: Checking environment variables...")
    llm_provider = os.getenv("LLM_PROVIDER", "not set")
    gemini_key = os.getenv("GEMINI_API_KEY", "not set")
    gemini_model = os.getenv("GEMINI_MODEL", "not set")
    
    print(f"  LLM_PROVIDER: {llm_provider}")
    print(f"  GEMINI_API_KEY: {'✅ Set' if gemini_key != 'not set' and gemini_key != 'your_gemini_api_key_here' else '❌ Not set'}")
    print(f"  GEMINI_MODEL: {gemini_model}")
    print()
    
    if llm_provider != "gemini":
        print("⚠️  Warning: LLM_PROVIDER is not set to 'gemini'")
        print("   Set LLM_PROVIDER=gemini in your .env file")
        print()
    
    if gemini_key == "not set" or gemini_key == "your_gemini_api_key_here":
        print("❌ Error: GEMINI_API_KEY is not configured")
        print()
        print("To fix this:")
        print("1. Get your API key from: https://makersuite.google.com/app/apikey")
        print("2. Create/edit .env file in project root")
        print("3. Add: GEMINI_API_KEY=your_actual_key_here")
        print()
        return False
    
    # Step 2: Check if google-generativeai is installed
    print("Step 2: Checking if google-generativeai is installed...")
    try:
        import google.generativeai as genai
        print("  ✅ google-generativeai package is installed")
        print()
    except ImportError:
        print("  ❌ google-generativeai package is NOT installed")
        print()
        print("To fix this:")
        print("  pip install google-generativeai")
        print()
        return False
    
    # Step 3: Test API connection
    print("Step 3: Testing Gemini API connection...")
    try:
        import google.generativeai as genai
        from google.generativeai.types import HarmCategory, HarmBlockThreshold
        
        genai.configure(api_key=gemini_key)
        model = genai.GenerativeModel(gemini_model)
        
        # Simple test prompt with safety settings
        response = model.generate_content(
            "Say hello",
            generation_config=genai.types.GenerationConfig(
                max_output_tokens=10,
                temperature=0.7,
            ),
            safety_settings={
                HarmCategory.HARM_CATEGORY_HARASSMENT: HarmBlockThreshold.BLOCK_NONE,
                HarmCategory.HARM_CATEGORY_HATE_SPEECH: HarmBlockThreshold.BLOCK_NONE,
                HarmCategory.HARM_CATEGORY_SEXUALLY_EXPLICIT: HarmBlockThreshold.BLOCK_NONE,
                HarmCategory.HARM_CATEGORY_DANGEROUS_CONTENT: HarmBlockThreshold.BLOCK_NONE,
            }
        )
        
        if response.text:
            print(f"  ✅ API connection successful!")
            print(f"  Test response: {response.text.strip()}")
            print()
        else:
            print("  ⚠️  API connected but returned empty response")
            print()
            return False
            
    except Exception as e:
        print(f"  ❌ API connection failed: {e}")
        print()
        print("Possible issues:")
        print("  - Invalid API key")
        print("  - Network connection problem")
        print("  - API quota exceeded")
        print()
        return False
    
    # Step 4: Test with chatbot engine
    print("Step 4: Testing with BoundedChatbotEngine...")
    try:
        from src.bounded_chatbot import BoundedChatbotEngine
        
        bot = BoundedChatbotEngine()
        
        print(f"  Provider: {bot.llm_provider}")
        print(f"  Model: {bot.gemini_model}")
        print(f"  Available: {'✅ Yes' if bot.llm_available else '❌ No'}")
        print()
        
        if not bot.llm_available:
            print("  ⚠️  Chatbot engine reports LLM not available")
            return False
            
    except Exception as e:
        print(f"  ❌ Chatbot engine test failed: {e}")
        print()
        return False
    
    # Success!
    print("=" * 60)
    print("✅ All tests passed! Gemini API is configured correctly.")
    print("=" * 60)
    print()
    print("Next steps:")
    print("  1. Start your backend: python src/main.py")
    print("  2. Start your frontend: cd frontend && npm run dev")
    print("  3. Test with real queries!")
    print()
    return True


if __name__ == "__main__":
    # Load .env file if it exists
    try:
        from dotenv import load_dotenv
        load_dotenv()
        print("📄 Loaded .env file")
        print()
    except ImportError:
        print("⚠️  python-dotenv not installed (optional)")
        print("   Install with: pip install python-dotenv")
        print()
    
    success = test_gemini_setup()
    sys.exit(0 if success else 1)
