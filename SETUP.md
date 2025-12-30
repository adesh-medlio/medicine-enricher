# Setup Instructions for Medicine Enricher

## 🔧 Environment Setup

### 1. Clone/Download the Project
```bash
git clone https://github.com/your-username/medicine-enricher.git
cd medicine-enricher
```

### 2. Create Python Virtual Environment
```bash
# Create virtual environment
python -m venv medicine_env

# Activate it
# Windows:
medicine_env\Scripts\activate
# Linux/Mac:
source medicine_env/bin/activate
```

### 3. Install Dependencies
```bash
pip install -r requirements.txt
```

### 4. Configure API Key

#### Option A: Using .env file (Recommended)
```bash
# Copy the example file
copy .env.example .env

# Edit .env file and add your API key:
# GROQ_API_KEY=gsk_your_actual_api_key_here
```

#### Option B: Set Environment Variable
```bash
# Windows
set GROQ_API_KEY=gsk_your_actual_api_key_here

# Linux/Mac
export GROQ_API_KEY=gsk_your_actual_api_key_here
```

### 5. Test Configuration
```bash
python config.py
```

You should see:
```
✅ Groq API Key: gsk_your_key...
✅ Max Retries: 3
✅ Timeout: 30s
✅ Rate Limit Delay: 2s
```

## 🚀 Quick Start

### Test the Setup
```bash
python test_improved_search.py
```

### Run on Your Data
```bash
python run_with_file_path.py "path/to/your/excel/file.xlsx"
```

## 🔑 Getting Your Groq API Key

1. Go to https://console.groq.com/
2. Sign up or log in
3. Navigate to API Keys section
4. Create a new API key
5. Copy the key (starts with `gsk_`)

## 📁 File Structure

```
medicine-enricher/
├── .env                    # Your API keys (DO NOT COMMIT)
├── .env.example           # Template for API keys
├── config.py              # Configuration management
├── medicine_enricher.py   # Main enricher class
├── run_with_file_path.py  # Easy way to run with your file
├── test_*.py             # Test scripts
└── requirements.txt       # Python dependencies
```

## 🔒 Security Notes

- **Never commit `.env` file** - it contains your API keys
- The `.gitignore` file prevents accidental commits
- Use `.env.example` as a template for others
- API keys are loaded automatically from environment

## 🐛 Troubleshooting

### "API key not found" error
- Check if `.env` file exists
- Verify API key format (should start with `gsk_`)
- Run `python config.py` to test configuration

### "Module not found" error
- Make sure virtual environment is activated
- Run `pip install -r requirements.txt`

### Search accuracy issues
- Ensure your Excel has `manufacturer_name` column
- Check similarity warnings in output
- Use manufacturer information for better results