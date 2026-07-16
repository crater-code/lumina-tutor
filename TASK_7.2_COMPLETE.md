# Task 7.2 Complete: Refusal Message Generation

## Summary

Task 7.2 has been successfully verified and completed. The `generate_refusal()` method was already implemented as part of Task 7.1 in the `ChatbotEngine` class, and it fully meets all requirements.

## Implementation Details

### Location
- **File**: `src/chatbot_engine.py`
- **Method**: `generate_refusal()` (lines 127-177)
- **Helper Method**: `_generate_refusal_text()` (lines 327-377)

### Features Implemented

1. **Polite, Age-Appropriate Messages**
   - Three age groups with tailored language:
     - Ages 4-7: Simple, friendly language
     - Ages 8-11: Clear, elementary-level language
     - Ages 12-15: More formal, middle-school appropriate

2. **Explains Answer Not in Book**
   - All messages explicitly state the information is not found in the book
   - Clear communication about the system's limitations

3. **Encourages Different Questions**
   - All messages encourage users to ask other questions about the book
   - Positive, supportive tone

4. **No External Resources**
   - Messages never suggest Google, Wikipedia, or other external sources
   - Keeps users focused on the book content

5. **Multilingual Support**
   - Full support for English and Urdu
   - Age-appropriate messages in both languages

## Requirements Validation

✅ **Requirement 4.4**: Generates refusal when no relevant chunks found
- Returns `Response` object with `is_refusal=True`
- Empty `chunk_ids` list

✅ **Requirement 12.1**: Generates polite refusal message
- All messages are respectful and supportive
- Age-appropriate tone

✅ **Requirement 12.2**: Explains that answer is not in the book
- All messages contain explicit statements about book limitations
- Clear communication: "couldn't find", "not in this book"

✅ **Requirement 12.4**: Does not suggest external resources
- No mentions of search engines, websites, or external sources
- Verified by test: `test_generate_refusal_no_external_resources`

✅ **Requirement 12.5**: Encourages asking different questions
- All messages include encouragement to ask about book content
- Positive framing: "ask something else", "other questions"

## Test Coverage

### Unit Tests (12 tests in `tests/test_chatbot_engine.py`)
- ✅ Basic refusal generation
- ✅ Age-appropriate messages (all three age groups)
- ✅ Multilingual support (English and Urdu)
- ✅ No external resource suggestions
- ✅ Encourages book questions
- ✅ Input validation (empty query, invalid age, invalid language)
- ✅ All ages (4-15) in both languages

### Integration Tests (2 tests in `tests/test_chatbot_integration.py`)
- ✅ Refusal for off-topic queries
- ✅ Refusal messages for all ages

**Total Tests Passing**: 36 unit tests + 9 integration tests = 45 tests ✓

## Example Output

### English Messages

**Young Child (Age 6)**:
```
I'm sorry, but I can't find the answer to your question in this book. 
Can you ask me something else about the book?
```

**Elementary Student (Age 10)**:
```
I couldn't find information about that in this book. The book doesn't 
seem to cover this topic. Would you like to ask me something else 
about what's in the book?
```

**Middle School Student (Age 14)**:
```
I couldn't find relevant information about that in this book. The 
content you're asking about doesn't appear to be covered in this book. 
Feel free to ask me other questions about the topics that are in the book.
```

### Urdu Messages

All age groups also have equivalent messages in Urdu with appropriate 
language complexity.

## Demonstration

Run the demonstration script to see the refusal messages in action:

```bash
python demo_refusal_messages.py
```

This script demonstrates:
- Refusal messages for all three age groups
- Both English and Urdu messages
- Verification of all requirements

## API Usage

```python
from src.chatbot_engine import ChatbotEngine

engine = ChatbotEngine()

# Generate refusal message
response = engine.generate_refusal(
    query="What is quantum mechanics?",
    user_age=10,
    language="en"
)

print(response.text)        # The refusal message
print(response.is_refusal)  # True
print(response.chunk_ids)   # []
```

## Conclusion

Task 7.2 is complete and fully functional. The implementation:
- ✅ Meets all specified requirements
- ✅ Passes all tests (45 tests)
- ✅ Supports both English and Urdu
- ✅ Provides age-appropriate messages
- ✅ Maintains strict content boundaries (no external resources)
- ✅ Encourages continued engagement with book content

The refusal message generation is a critical component of the bounded tutoring system, ensuring that when the chatbot cannot answer from the book, it communicates this limitation clearly and appropriately to users of all ages.
