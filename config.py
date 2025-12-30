#!/usr/bin/env python3
"""
Configuration management for Medicine Enricher
Handles loading environment variables from .env file
"""

import os
from pathlib import Path

def load_env_file(env_path=".env"):
    """
    Load environment variables from .env file
    Simple implementation without external dependencies
    """
    env_file = Path(env_path)
    
    if not env_file.exists():
        print(f"⚠️  Warning: {env_path} file not found")
        print(f"   Create {env_path} file with your API key:")
        print(f"   GROQ_API_KEY=your_actual_api_key_here")
        return False
    
    try:
        with open(env_file, 'r', encoding='utf-8') as f:
            for line in f:
                line = line.strip()
                
                # Skip empty lines and comments
                if not line or line.startswith('#'):
                    continue
                
                # Parse KEY=VALUE format
                if '=' in line:
                    key, value = line.split('=', 1)
                    key = key.strip()
                    value = value.strip()
                    
                    # Remove quotes if present
                    if value.startswith('"') and value.endswith('"'):
                        value = value[1:-1]
                    elif value.startswith("'") and value.endswith("'"):
                        value = value[1:-1]
                    
                    # Set environment variable
                    os.environ[key] = value
        
        return True
        
    except Exception as e:
        print(f"❌ Error loading {env_path}: {str(e)}")
        return False

def get_groq_api_key():
    """
    Get Groq API key from environment variables
    Tries multiple sources in order of preference
    """
    # Try to load from .env file first
    load_env_file()
    
    # Check environment variables
    api_key = os.getenv('GROQ_API_KEY')
    
    if not api_key or api_key == 'your_groq_api_key_here':
        print("❌ Groq API key not found!")
        print("📝 Please set your API key in one of these ways:")
        print("   1. Create .env file with: GROQ_API_KEY=your_actual_key")
        print("   2. Set environment variable: export GROQ_API_KEY=your_actual_key")
        print("   3. Copy .env.example to .env and edit it")
        print("🔑 Get your API key from: https://console.groq.com/")
        return None
    
    # Validate API key format
    if not api_key.startswith('gsk_'):
        print("⚠️  Warning: API key doesn't start with 'gsk_' - this might be incorrect")
    
    return api_key

def get_config():
    """
    Get all configuration values
    """
    load_env_file()
    
    return {
        'groq_api_key': get_groq_api_key(),
        'max_retries': int(os.getenv('MAX_RETRIES', '3')),
        'timeout_seconds': int(os.getenv('TIMEOUT_SECONDS', '30')),
        'rate_limit_delay': int(os.getenv('RATE_LIMIT_DELAY', '2')),
    }

if __name__ == "__main__":
    # Test the configuration
    print("🔧 Testing Configuration")
    print("=" * 30)
    
    config = get_config()
    
    if config['groq_api_key']:
        print(f"✅ Groq API Key: {config['groq_api_key'][:20]}...")
        print(f"✅ Max Retries: {config['max_retries']}")
        print(f"✅ Timeout: {config['timeout_seconds']}s")
        print(f"✅ Rate Limit Delay: {config['rate_limit_delay']}s")
    else:
        print("❌ Configuration incomplete")