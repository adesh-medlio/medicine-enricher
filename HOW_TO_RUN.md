# How to Run Enhanced Medicine Enricher

## Prerequisites
1. Your Excel file with medicine names
2. Groq API key
3. Python environment activated

## Step-by-Step Instructions

### Step 1: Prepare Your Excel File
Your Excel file should have these columns:
- `name` - Medicine names (required)
- `manufacturer_name` - Manufacturer names (optional but recommended)

Example:
| name | manufacturer_name |
|------|-------------------|
| Glywohn MP 1mg/500mg/15mg Tablet | Riyadh Pharmaceutical |
| Paracetamol 500mg Tablet | Cipla Ltd |

## Step 2: Set Your API Key

### Option A: Using .env file (Recommended)
1. Copy the example file:
   ```bash
   copy .env.example .env
   ```
2. Edit `.env` file and replace `your_groq_api_key_here` with your actual API key:
   ```
   GROQ_API_KEY=gsk_your_actual_api_key_here
   ```

### Option B: Using environment variable
```bash
# Windows
set GROQ_API_KEY=gsk_your_actual_api_key_here

# Linux/Mac
export GROQ_API_KEY=gsk_your_actual_api_key_here
```

**Get your API key from**: https://console.groq.com/

### Step 3: Run the Enricher
```bash
python run_enhanced_enricher.py
```

### Alternative: Use Existing Scripts

#### Option A: Use your existing run_enricher.py
```bash
python run_enricher.py
```
(The enhanced medicine_enricher.py will automatically detect manufacturer columns)

#### Option B: Use interactive enricher
```bash
python interactive_enricher.py
```

#### Option C: Test first with sample data
```bash
python test_manufacturer_search.py
```

## What Happens During Enrichment

1. **File Detection**: Finds your Excel file
2. **Column Detection**: Automatically detects manufacturer column if present
3. **Enhanced Search**: Uses both medicine name + manufacturer for accurate results
4. **Data Extraction**: Gets salt composition, description, etc.
5. **Validation**: Checks if found medicine matches what you searched for
6. **Safe Saving**: Uses corruption-proof saving every 10 medicines

## Output Columns

Your enriched Excel will have these new columns:
- `salt_composition` - Active ingredients
- `medicine_description` - Medicine description
- `source_url` - 1mg.com URL
- `found_medicine_name` - What medicine was actually found
- `found_manufacturer` - What manufacturer was found
- `similarity_warning` - Warning if names don't match well
- `manufacturer_warning` - Warning if manufacturers don't match
- `processing_status` - SUCCESS/FAILED/ERROR

## Troubleshooting

### If you get wrong medicines:
- Make sure manufacturer_name column is filled
- Check similarity_warning and manufacturer_warning columns
- The enhanced search should be much more accurate

### If enrichment fails:
- Check your Groq API key
- Check internet connection
- Look for emergency backup files (auto-created)

### If you want to resume:
- Just run again - it will skip already processed medicines
- Look for processing_status = 'SUCCESS' to see what's done

## Example Commands

```bash
# Check your Excel structure first
python check_excel_columns.py

# Add manufacturer column if needed
python add_manufacturer_column.py

# Test the enhanced search
python test_manufacturer_search.py

# Run full enrichment
python run_enhanced_enricher.py
```

## Expected Results

**Before (without manufacturer):**
- Search: "Glywohn MP 1mg/500mg/15mg Tablet"
- Might find: "Glynamic MV 1 Tablet" (wrong!)

**After (with manufacturer):**
- Search: "Glywohn MP 1mg/500mg/15mg Tablet" + "Riyadh Pharmaceutical"
- Finds: "Glywohn MP 1mg/500mg/15mg Tablet" (correct!)

The manufacturer information makes searches much more precise! 🎯