"""
Command-line interface for Medicine Enricher
Supports multiple ways to specify Excel file paths
"""

import argparse
import os
import sys
from medicine_enricher import MedicineEnricher

def main():
    parser = argparse.ArgumentParser(description='Enrich Excel file with medicine data from 1mg.com')
    
    parser.add_argument('--input', '-i', 
                       help='Path to input Excel file',
                       required=False)
    
    parser.add_argument('--output', '-o',
                       help='Path to output Excel file (optional)',
                       required=False)
    
    parser.add_argument('--api-key', '-k',
                       help='Groq API key',
                       required=False)
    
    args = parser.parse_args()
    
    # Get input file path
    if args.input:
        input_file = args.input
    else:
        input_file = input("Enter path to your Excel file: ").strip().strip('"')
    
    # Validate input file
    if not os.path.exists(input_file):
        print(f"❌ Error: File '{input_file}' not found!")
        print("Make sure the file path is correct and the file exists.")
        return
    
    if not input_file.lower().endswith(('.xlsx', '.xls')):
        print(f"❌ Error: '{input_file}' is not an Excel file!")
        print("Please provide a .xlsx or .xls file.")
        return
    
    # Generate output file path
    if args.output:
        output_file = args.output
    else:
        base_name = os.path.splitext(input_file)[0]
        output_file = f"{base_name}_enriched.xlsx"
    
    # Get API key
    if args.api_key:
        api_key = args.api_key
    else:
        api_key = input("Enter your Groq API key: ").strip()
    
    if not api_key:
        print("❌ Error: Groq API key is required!")
        print("Get your API key from: https://console.groq.com/")
        return
    
    print(f"\n📋 Configuration:")
    print(f"   Input file:  {input_file}")
    print(f"   Output file: {output_file}")
    print(f"   API key:     {'*' * (len(api_key) - 4) + api_key[-4:] if len(api_key) > 4 else '****'}")
    
    confirm = input(f"\nProceed with enrichment? (y/N): ").strip().lower()
    if confirm not in ['y', 'yes']:
        print("Operation cancelled.")
        return
    
    # Run enrichment
    try:
        print(f"\n🚀 Starting enrichment process...")
        enricher = MedicineEnricher(api_key)
        result_df = enricher.enrich_excel(input_file, output_file)
        
        print(f"\n✅ Enrichment completed successfully!")
        print(f"📄 Results saved to: {output_file}")
        
        # Show summary
        status_counts = result_df['processing_status'].value_counts()
        print(f"\n📊 Summary:")
        for status, count in status_counts.items():
            print(f"   {status}: {count}")
            
    except Exception as e:
        print(f"❌ Enrichment failed: {str(e)}")
        return 1
    
    return 0

if __name__ == "__main__":
    sys.exit(main())