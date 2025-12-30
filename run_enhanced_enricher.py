#!/usr/bin/env python3
"""
Simple script to run the enhanced medicine enricher with manufacturer support
"""

import os
from medicine_enricher import MedicineEnricher

def main():
    print("🚀 Enhanced Medicine Enricher")
    print("=" * 40)
    
    from config import get_groq_api_key
    
    # Configuration
    GROQ_API_KEY = get_groq_api_key()
    if not GROQ_API_KEY:
        return
    
    # Find Excel files
    excel_files = [f for f in os.listdir('.') if f.endswith('.xlsx') and not f.startswith('~')]
    
    if not excel_files:
        print("❌ No Excel files found!")
        return
    
    print("📁 Available Excel files:")
    for i, f in enumerate(excel_files, 1):
        print(f"   {i}. {f}")
    
    # Get input file
    if len(excel_files) == 1:
        input_file = excel_files[0]
        print(f"\n📥 Using: {input_file}")
    else:
        choice = input(f"\nSelect input file (1-{len(excel_files)}): ").strip()
        try:
            input_file = excel_files[int(choice) - 1]
        except (ValueError, IndexError):
            input_file = excel_files[0]
            print(f"Using: {input_file}")
    
    # Set output file
    output_file = input_file.replace('.xlsx', '_enriched_with_manufacturer.xlsx')
    
    print(f"📤 Output will be: {output_file}")
    print(f"🔑 API Key: {GROQ_API_KEY[:20]}...")
    
    # Confirm before starting
    confirm = input("\nStart enrichment? (y/n): ").strip().lower()
    if confirm not in ['y', 'yes']:
        print("👋 Cancelled")
        return
    
    # Run enrichment
    try:
        enricher = MedicineEnricher(GROQ_API_KEY)
        enricher.enrich_excel(input_file, output_file)
        print(f"\n✅ Enrichment completed!")
        print(f"📄 Results saved to: {output_file}")
    except Exception as e:
        print(f"\n❌ Error: {str(e)}")

if __name__ == "__main__":
    main()