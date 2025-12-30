"""
Simple Groq API test with the updated model
"""

import requests
import json

# Your API key
API_KEY = "your_groq_api_key_here"  # Replace with your actual API key

def test_api():
    headers = {
        'Authorization': f'Bearer {API_KEY}',
        'Content-Type': 'application/json'
    }
    
    payload = {
        'model': 'llama-3.1-8b-instant',
        'messages': [
            {
                'role': 'user',
                'content': 'Return only this JSON: {"test": "success"}'
            }
        ],
        'temperature': 0.1,
        'max_tokens': 50
    }
    
    try:
        print("Testing Groq API with llama-3.1-8b-instant...")
        response = requests.post(
            'https://api.groq.com/openai/v1/chat/completions',
            headers=headers,
            json=payload,
            timeout=30
        )
        
        print(f"Status Code: {response.status_code}")
        
        if response.status_code == 200:
            result = response.json()
            content = result['choices'][0]['message']['content'].strip()
            print(f"✅ API working! Response: {content}")
            return True
        else:
            print(f"❌ API Error: {response.status_code}")
            print(f"Response: {response.text}")
            return False
            
    except Exception as e:
        print(f"❌ Request failed: {str(e)}")
        return False

if __name__ == "__main__":
    if test_api():
        print("\n🎉 Groq API is working! Your medicine enricher should work now.")
        print("You can resume your processing with the interactive_enricher.py")
    else:
        print("\n❌ API still not working. Check the error above.")