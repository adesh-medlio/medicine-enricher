"""
Check the current state of your Downloads file and run enricher on it
"""

import pandas as pd
import os
from medicine_enricher import MedicineEnricher

def check_and_process_your_file():
    # Your file path
    input_file = r"C:\Users\adesh.shetty\Downloads\part_1_medicine_normalized_enriched.xlsx"
    output_file = r"C:\Users\adesh.shetty\Downloads\part_1_medicine_normalized_enriched_UPDATED.xlsx"
    
    print("🔍 Checking your current file...")
    print("=" * 60)
    
    try:
        # Read your current file
        df = pd.read_excel(input_file)
        
        print(f"📄 File: {input_file}")
        print(f"📊 Total rows: {len(df)}")
        print(f"📋 Columns: {list(df.columns)}")
        
        # Check if enrichment columns exist
        enrichment_columns = ['salt_composition', 'medicine_description', 'source_url', 'processing_status']
        existing_enrichment = [col for col in enrichment_columns if col in df.columns]
        
        if existing_enrichment:
            print(f"\n✅ Found existing enrichment columns: {existing_enrichment}")
            
            # Check processing status
            if 'processing_status' in df.columns:
                status_counts = df['processing_status'].value_counts()
                print(f"\n📈 Processing Status:")
                for status, count in status_counts.items():
                    print(f"   {status}: {count}")
                
                # Check how many are already processed
                processed = len(df[df['processing_status'] == 'SUCCESS'])
                total = len(df)
                print(f"\n🎯 Progress: {processed}/{total} medicines already processed ({processed/total*100:.1f}%)")
                
                if processed == total:
                    print(f"\n🎉 All medicines are already processed!")
                    print(f"✅ Your file is complete - no further processing needed.")
                    return
                elif processed > 0:
                    print(f"\n🔄 Found partial processing - can resume from where it left off")
            
        else:
            print(f"\n📝 No enrichment columns found - this will be a fresh enrichment")
        
        # Show sample data
        print(f"\n📋 Sample medicines in your file:")
        if 'name' in df.columns:
            sample_names = df['name'].head(5).tolist()
            for i, name in enumerate(sample_names, 1):
                print(f"   {i}. {name}")
        else:
            print("   ❌ No 'name' column found!")
            return
        
        # Ask if user wants to process
        print(f"\n" + "=" * 60)
        print(f"🚀 Ready to process your file!")
        print(f"📥 Input:  {input_file}")
        print(f"📤 Output: {output_file}")
        
        proceed = input(f"\nDo you want to start enrichment? (y/N): ").strip().lower()
        
        if proceed in ['y', 'yes']:
            # Get API key
            api_key = input("Enter your Groq API key: ").strip()
            
            if not api_key:
                print("❌ API key required!")
                return
            
            print(f"\n🔄 Starting enrichment process...")
            print(f"💡 Using optimized method: Targeted scraping + AI fallback")
            
            # Initialize enricher
            enricher = MedicineEnricher(api_key)
            
            # Run enrichment
            result_df = enricher.enrich_excel(input_file, output_file)
            
            print(f"\n✅ Enrichment completed!")
            print(f"📄 Results saved to: {output_file}")
            
            # Show final summary
            final_status = result_df['processing_status'].value_counts()
            print(f"\n📊 Final Results:")
            for status, count in final_status.items():
                print(f"   {status}: {count}")
                
        else:
            print("Operation cancelled.")
    
    except Exception as e:
        print(f"❌ Error: {str(e)}")

if __name__ == "__main__":
    check_and_process_your_file()