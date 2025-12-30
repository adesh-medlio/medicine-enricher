#!/usr/bin/env python3
"""
Test script to demonstrate manufacturer-enhanced medicine search
"""

import pandas as pd
from medicine_enricher import MedicineEnricher
import logging

# Set up logging to see what's happening
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')

def test_manufacturer_search():
    """Test the enhanced search with manufacturer information"""
    
    from config import get_groq_api_key
    
    # Get API key from environment
    GROQ_API_KEY = get_groq_api_key()
    if not GROQ_API_KEY:
        return
    
    # Initialize enricher
    enricher = MedicineEnricher(GROQ_API_KEY)
    
    # Test cases - your problematic example
    test_cases = [
        {
            'name': 'Glywohn MP 1mg/500mg/15mg Tablet',
            'manufacturer': 'Riyadh Pharmaceutical'
        },
        {
            'name': 'Glynamic MV 1 Tablet',
            'manufacturer': 'Fusion Healthcare Pvt Ltd'
        }
    ]
    
    print("🔍 Testing manufacturer-enhanced search...")
    print("=" * 60)
    
    for i, test_case in enumerate(test_cases, 1):
        medicine_name = test_case['name']
        manufacturer = test_case['manufacturer']
        
        print(f"\n📋 Test {i}: {medicine_name}")
        print(f"🏭 Manufacturer: {manufacturer}")
        print("-" * 40)
        
        # Test the search
        try:
            result = enricher.process_medicine(medicine_name, manufacturer)
            
            if result:
                print("✅ SUCCESS - Found data:")
                print(f"   Found Medicine: {result.get('found_medicine_name', 'N/A')}")
                print(f"   Found Manufacturer: {result.get('found_manufacturer', 'N/A')}")
                print(f"   Salt Composition: {result.get('salt_composition', 'N/A')[:100]}...")
                print(f"   Source URL: {result.get('source_url', 'N/A')}")
                
                # Check for warnings
                if result.get('similarity_warning'):
                    print(f"   ⚠️  {result['similarity_warning']}")
                if result.get('manufacturer_warning'):
                    print(f"   ⚠️  {result['manufacturer_warning']}")
            else:
                print("❌ FAILED - No data found")
                
        except Exception as e:
            print(f"❌ ERROR: {str(e)}")
    
    print("\n" + "=" * 60)
    print("🏁 Test completed!")

def create_sample_excel():
    """Create a sample Excel file with manufacturer information"""
    
    # Sample data with manufacturer column
    data = {
        'name': [
            'Glywohn MP 1mg/500mg/15mg Tablet',
            'Glynamic MV 1 Tablet',
            'Paracetamol 500mg Tablet',
            'Aspirin 75mg Tablet'
        ],
        'manufacturer_name': [
            'Riyadh Pharmaceutical',
            'Fusion Healthcare Pvt Ltd',
            'Cipla Ltd',
            'Bayer Pharmaceuticals'
        ]
    }
    
    df = pd.DataFrame(data)
    output_file = 'sample_medicines_with_manufacturer.xlsx'
    df.to_excel(output_file, index=False)
    
    print(f"📄 Created sample Excel file: {output_file}")
    print("Columns:", list(df.columns))
    print("\nSample data:")
    print(df.to_string(index=False))
    
    return output_file

def run_full_enrichment():
    """Run full enrichment on sample data"""
    
    # Create sample file
    input_file = create_sample_excel()
    output_file = 'enriched_medicines_with_manufacturer.xlsx'
    
    from config import get_groq_api_key
    
    # Get API key from environment
    GROQ_API_KEY = get_groq_api_key()
    if not GROQ_API_KEY:
        return
    
    # Initialize enricher
    enricher = MedicineEnricher(GROQ_API_KEY)
    
    print(f"\n🚀 Running full enrichment...")
    print(f"📥 Input: {input_file}")
    print(f"📤 Output: {output_file}")
    
    try:
        # Run enrichment
        result_df = enricher.enrich_excel(input_file, output_file)
        
        print(f"\n✅ Enrichment completed!")
        print(f"📊 Results saved to: {output_file}")
        
        # Show summary
        success_count = len(result_df[result_df['processing_status'] == 'SUCCESS'])
        total_count = len(result_df)
        print(f"📈 Success rate: {success_count}/{total_count}")
        
        # Show any warnings
        warnings = result_df[result_df['similarity_warning'] != '']
        if len(warnings) > 0:
            print(f"\n⚠️  {len(warnings)} medicines have similarity warnings:")
            for idx, row in warnings.iterrows():
                print(f"   - {row['name']}: {row['similarity_warning']}")
        
        manufacturer_warnings = result_df[result_df['manufacturer_warning'] != '']
        if len(manufacturer_warnings) > 0:
            print(f"\n⚠️  {len(manufacturer_warnings)} medicines have manufacturer warnings:")
            for idx, row in manufacturer_warnings.iterrows():
                print(f"   - {row['name']}: {row['manufacturer_warning']}")
        
    except Exception as e:
        print(f"❌ Enrichment failed: {str(e)}")

if __name__ == "__main__":
    print("🧪 Medicine Enricher - Manufacturer Search Test")
    print("=" * 50)
    
    # Choose what to run
    print("\nOptions:")
    print("1. Test manufacturer search only")
    print("2. Create sample Excel file")
    print("3. Run full enrichment on sample data")
    
    choice = input("\nEnter choice (1-3): ").strip()
    
    if choice == "1":
        test_manufacturer_search()
    elif choice == "2":
        create_sample_excel()
    elif choice == "3":
        run_full_enrichment()
    else:
        print("Invalid choice. Running test search...")
        test_manufacturer_search()