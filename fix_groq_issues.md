# Fixing Groq API 400 Error

## Common Causes of 400 Bad Request

### 1. Invalid API Key
- Make sure you copied the full API key from https://console.groq.com/
- API key should start with `gsk_`
- No extra spaces or characters

### 2. Request Too Large
- Content might be too long
- Try reducing `max_content_length` in the code

### 3. Invalid Model Name
- Make sure `llama3-8b-8192` is available
- Try `mixtral-8x7b-32768` as alternative

### 4. Rate Limiting
- You might be hitting API limits
- Add longer delays between requests

## Quick Fixes

### Fix 1: Update API Key Format
Make sure your API key is valid:
```python
# Good: gsk_1234567890abcdef...
# Bad: missing gsk_ prefix or truncated
```

### Fix 2: Try Alternative Model
Edit `medicine_enricher.py` line with model name:
```python
'model': 'mixtral-8x7b-32768',  # Instead of llama3-8b-8192
```

### Fix 3: Reduce Content Size
Already implemented in the updated code:
- Reduced from 8000 to 6000 characters
- Reduced max_tokens from 500 to 300

### Fix 4: Add Error Recovery
The updated code now:
- Shows detailed error messages
- Handles different response formats
- Continues processing even if some medicines fail

## Test Your API Key

Run this simple test:
```bash
curl -X POST "https://api.groq.com/openai/v1/chat/completions" \
  -H "Authorization: Bearer YOUR_API_KEY" \
  -H "Content-Type: application/json" \
  -d '{
    "model": "llama3-8b-8192",
    "messages": [{"role": "user", "content": "Hello"}],
    "max_tokens": 10
  }'
```

## Continue Processing

Your pipeline is still working! Even with Groq errors:
- ✅ URLs are being found successfully
- ✅ Pages are being fetched
- ❌ Only the AI extraction is failing

The Excel file will still be updated with:
- `source_url` (working)
- `processing_status` (shows the error)
- Empty fields for AI-extracted data

You can fix the API issue and re-run just the failed medicines later.