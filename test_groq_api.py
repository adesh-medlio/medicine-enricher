"""
Test Groq API connectivity and key validity
"""

import requests
import json

def test_groq_api():
    """Test if Groq API key is working"""
    
    api_key = input("Enter your Groq API key: ").strip()
    
    if not api_key:
        print("❌ No API key provided")
        return
    
    # Simple test request
    headers = {
        'Authorization': f'Bearer {api_key}',
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
        print("Testing Groq API...")
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
            
            # Test JSON parsing
            try:
                parsed = json.loads(content)
                print(f"✅ JSON parsing successful: {parsed}")
            except:
                print(f"⚠️ Response not valid JSON: {content}")
                
        else:
            print(f"❌ API Error: {response.status_code}")
            print(f"Response: {response.text}")
            
            if response.status_code == 401:
                print("🔑 This looks like an authentication error. Check your API key.")
            elif response.status_code == 400:
                print("📝 This looks like a request format error.")
                
    except Exception as e:
        print(f"❌ Request failed: {str(e)}")

def test_medicine_extraction():
    """Test medicine data extraction"""
    
    api_key = input("Enter your Groq API key: ").strip()
    
    if not api_key:
        print("❌ No API key provided")
        return
    
    # Sample medicine content
    sample_content = """
    Augmentin 625 Duo Tablet
    Salt Composition: Amoxycillin (500mg) + Clavulanic Acid (125mg)
    This medicine is used to treat bacterial infections.
    It is an antibiotic that works by stopping the growth of bacteria.
    """
    
    headers = {
        'Authorization': f'Bearer {api_key}',
        'Content-Type': 'application/json'
    }
    
    payload = {
        'model': 'llama-3.1-8b-instant',
        'messages': [
            {
                'role': 'user',
                'content': f"""Extract medicine info from: {sample_content}

Return ONLY JSON:
{{
    "salt_composition": "active ingredients",
    "medicine_description": "brief description"
}}"""
            }
        ],
        'temperature': 0.1,
        'max_tokens': 200
    }
    
    try:
        print("Testing medicine extraction...")
        response = requests.post(
            'https://api.groq.com/openai/v1/chat/completions',
            headers=headers,
            json=payload,
            timeout=30
        )
        
        if response.status_code == 200:
            result = response.json()
            content = result['choices'][0]['message']['content'].strip()
            print(f"✅ Raw response: {content}")
            
            # Clean and parse
            if content.startswith('```json'):
                content = content.replace('```json', '').replace('```', '').strip()
            
            try:
                parsed = json.loads(content)
                print(f"✅ Parsed successfully:")
                for key, value in parsed.items():
                    print(f"  {key}: {value}")
            except Exception as e:
                print(f"❌ JSON parsing failed: {str(e)}")
                
        else:
            print(f"❌ API Error: {response.status_code} - {response.text}")
            
    except Exception as e:
        print(f"❌ Request failed: {str(e)}")

if __name__ == "__main__":
    print("Groq API Tester")
    print("=" * 30)
    
    choice = input("\n1. Test API key\n2. Test medicine extraction\n3. Both\nChoose (1/2/3): ").strip()
    
    if choice in ['1', '3']:
        test_groq_api()
        print()
    
    if choice in ['2', '3']:
        test_medicine_extraction()