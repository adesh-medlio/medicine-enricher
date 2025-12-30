"""
Example usage of the Medicine Enricher
"""

from medicine_enricher import MedicineEnricher
import pandas as pd

def create_sample_excel():
    """Create a sample Excel file for testing"""
    sample_data = {
        'name': [
            'Augmentin 625 Duo Tablet',
            'Azithral 500 Tablet',
            'Paracetamol 500mg',
            'Crocin Advance Tablet'
        ],
        'manufacturer_name': [
            'Glaxo SmithKline Pharmaceuticals Ltd',
            'Alembic Pharmaceuticals Ltd',
            'Generic Manufacturer',
            'GSK Consumer Healthcare'
        ],
        'strength': ['', '', '500mg', ''],
        'dosage_form': ['Tablet', 'Tablet', 'Tablet', 'Tablet'],
        'packaging': ['Strip', 'Strip', 'Strip', 'Strip'],
        'pack_size': ['10 tablets', '5 tablets', '10 tablets', '15 tablets']
    }
    
    df = pd.DataFrame(sample_data)
    df.to_excel('sample_medicines.xlsx', index=False)
    print("✅ Sample Excel file created: sample_medicines.xlsx")

def run_enrichment():
    """Run the enrichment process"""
    from config import get_groq_api_key
    
    # Get API key from environment
    GROQ_API_KEY = get_groq_api_key()
    if not GROQ_API_KEY:
        return
        print("❌ Groq API key is required")
        return
    
    # Initialize enricher
    enricher = MedicineEnricher(GROQ_API_KEY)
    
    # Run enrichment
    try:
        print("🚀 Starting enrichment process...")
        result_df = enricher.enrich_excel('sample_medicines.xlsx', 'enriched_medicines.xlsx')
        
        print("\n📊 Enrichment Results:")
        print("=" * 50)
        
        # Show summary
        status_counts = result_df['processing_status'].value_counts()
        for status, count in status_counts.items():
            print(f"{status}: {count}")
        
        print(f"\n📄 Detailed results saved to: enriched_medicines.xlsx")
        
        # Show sample of enriched data
        successful_rows = result_df[result_df['processing_status'] == 'SUCCESS']
        if not successful_rows.empty:
            print("\n🔍 Sample enriched data:")
            print("-" * 50)
            for _, row in successful_rows.head(2).iterrows():
                print(f"Medicine: {row['name']}")
                print(f"Salt Composition: {row['salt_composition']}")
                print(f"Description: {row['medicine_description']}")
                print(f"Source URL: {row['source_url']}")
                print("-" * 50)
        
    except Exception as e:
        print(f"❌ Enrichment failed: {str(e)}")

def main():
    """Main function"""
    print("Medicine Data Enricher")
    print("=" * 30)
    
    choice = input("\n1. Create sample Excel file\n2. Run enrichment\n3. Both\nChoose (1/2/3): ").strip()
    
    if choice in ['1', '3']:
        create_sample_excel()
    
    if choice in ['2', '3']:
        run_enrichment()

if __name__ == "__main__":
    main()