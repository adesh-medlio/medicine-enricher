#!/usr/bin/env python3
"""
Run enhanced medicine enricher with custom file path
"""

import os
import sys
from medicine_enricher import MedicineEnricher

def main():
    print("🚀 Enhanced Medicine Enricher - Custom File Path")
    print("=" * 50)
    
    # Get file path from user
    if len(sys.argv) > 1:
        input_file = sys.argv[1]
        print(f"📥 Using file from command line: {input_file}")
    else:
        input_file = input("Enter the full path to your Excel file: ").strip()
        # Remove quotes if user added them
        input_file = input_file.strip('"').strip("'")
    
    # Check if file exists
    if not os.path.exists(input_file):
        print(f"❌ File not found: {input_file}")
        return
    
    # Set output file (same directory as input)
    input_dir = os.path.dirname(input_file)
    input_name = os.path.basename(input_file)
    output_name = input_name.replace('.xlsx', '_enriched_with_manufacturer.xlsx')
    output_file = os.path.join(input_dir, output_name)
    
    print(f"📄 Input file: {input_file}")
    print(f"📤 Output file: {output_file}")
    
    from config import get_groq_api_key
    
    # Get API key from environment
    GROQ_API_KEY = get_groq_api_key()
    if not GROQ_API_KEY:
        return
    
    print(f"🔑 API Key: {GROQ_API_KEY[:20]}...")
    
    # Quick file check
    try:
        import pandas as pd
        df = pd.read_excel(input_file, nrows=3)
        print(f"\n📊 File info:")
        print(f"   - Columns: {list(df.columns)}")
        print(f"   - Has 'name' column: {'name' in df.columns}")
        print(f"   - Has 'manufacturer_name' column: {'manufacturer_name' in df.columns}")
        
        if 'manufacturer_name' in df.columns:
            print("✅ Great! Manufacturer column found - searches will be more accurate")
        else:
            print("⚠️  No manufacturer column - will use medicine name only")
        
    except Exception as e:
        print(f"⚠️  Could not preview file: {str(e)}")
    
    # Confirm before starting
    confirm = input(f"\nStart enrichment? (y/n): ").strip().lower()
    if confirm not in ['y', 'yes']:
        print("👋 Cancelled")
        return
    
    # Run enrichment
    print(f"\n🔄 Starting enrichment...")
    print(f"💡 This will use manufacturer names for more accurate searches!")
    
    try:
        enricher = MedicineEnricher(GROQ_API_KEY)
        result_df = enricher.enrich_excel(input_file, output_file)
        
        print(f"\n✅ Enrichment completed successfully!")
        print(f"📄 Results saved to: {output_file}")
        
        # Show summary
        if result_df is not None:
            success_count = len(result_df[result_df['processing_status'] == 'SUCCESS'])
            total_count = len(result_df)
            print(f"📊 Success rate: {success_count}/{total_count}")
            
            # Show warnings if any
            if 'similarity_warning' in result_df.columns:
                warnings = result_df[result_df['similarity_warning'] != '']
                if len(warnings) > 0:
                    print(f"⚠️  {len(warnings)} medicines have similarity warnings (check output file)")
            
            if 'manufacturer_warning' in result_df.columns:
                mfg_warnings = result_df[result_df['manufacturer_warning'] != '']
                if len(mfg_warnings) > 0:
                    print(f"⚠️  {len(mfg_warnings)} medicines have manufacturer warnings (check output file)")
        
    except Exception as e:
        print(f"\n❌ Enrichment failed: {str(e)}")
        print(f"💡 Check for emergency backup files in the same directory")

if __name__ == "__main__":
    main()