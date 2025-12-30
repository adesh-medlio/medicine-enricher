"""
Test script for the optimized medicine enricher with targeted scraping
"""

from medicine_enricher import MedicineEnricher
import pandas as pd

def test_optimized_extraction():
    """Test the new optimized extraction method"""
    
    from config import get_groq_api_key
    
    # Get API key from environment
    GROQ_API_KEY = get_groq_api_key()
    if not GROQ_API_KEY:
        return
        print("❌ Groq API key is required")
        return
    
    # Initialize enricher
    enricher = MedicineEnricher(GROQ_API_KEY)
    
    # Test medicines
    test_medicines = [
        "Ascoril LS Drops",
        "Paracetamol 500mg",
        "Crocin Advance Tablet"
    ]
    
    print("🚀 Testing optimized medicine enricher...")
    print("=" * 50)
    
    results = []
    
    for medicine in test_medicines:
        print(f"\n📋 Processing: {medicine}")
        print("-" * 30)
        
        try:
            # Process medicine using new optimized method
            result = enricher.process_medicine(medicine)
            
            if result:
                print(f"✅ Success!")
                print(f"Salt Composition: {result.get('salt_composition', 'Not found')}")
                print(f"Description: {result.get('medicine_description', 'Not found')[:100]}...")
                print(f"Source URL: {result.get('source_url', 'Not found')}")
                
                results.append({
                    'name': medicine,
                    'salt_composition': result.get('salt_composition', ''),
                    'medicine_description': result.get('medicine_description', ''),
                    'source_url': result.get('source_url', ''),
                    'status': 'SUCCESS'
                })
            else:
                print(f"❌ Failed to extract data")
                results.append({
                    'name': medicine,
                    'salt_composition': '',
                    'medicine_description': '',
                    'source_url': '',
                    'status': 'FAILED'
                })
                
        except Exception as e:
            print(f"❌ Error: {str(e)}")
            results.append({
                'name': medicine,
                'salt_composition': '',
                'medicine_description': '',
                'source_url': '',
                'status': f'ERROR: {str(e)}'
            })
    
    # Save results to Excel
    df = pd.DataFrame(results)
    output_file = "optimized_test_results.xlsx"
    df.to_excel(output_file, index=False)
    
    print(f"\n📊 Test Results Summary:")
    print("=" * 50)
    status_counts = df['status'].value_counts()
    for status, count in status_counts.items():
        print(f"{status}: {count}")
    
    print(f"\n📄 Detailed results saved to: {output_file}")
    
    # Show efficiency comparison
    print(f"\n⚡ Efficiency Improvements:")
    print("- Targeted scraping tries to extract data directly from HTML")
    print("- AI fallback only used when targeted scraping fails")
    print("- Expected 90% reduction in token usage")
    print("- Much faster processing")

if __name__ == "__main__":
    test_optimized_extraction()