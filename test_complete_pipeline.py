"""
Test the complete medicine enrichment pipeline
"""

from medicine_enricher import MedicineEnricher
import logging

# Set up logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')

def test_complete_pipeline():
    """Test the complete pipeline with one medicine"""
    
    API_KEY = "your_groq_api_key_here"  # Replace with your actual API key
    
    enricher = MedicineEnricher(API_KEY)
    
    test_medicine = "Augmentin 625 Duo Tablet"
    print(f"Testing complete pipeline for: {test_medicine}")
    print("=" * 50)
    
    try:
        result = enricher.process_medicine(test_medicine)
        
        if result:
            print("✅ SUCCESS! Complete pipeline worked!")
            print("\nExtracted Data:")
            print("-" * 30)
            print(f"Salt Composition: {result.get('salt_composition', 'N/A')}")
            print(f"Description: {result.get('medicine_description', 'N/A')}")
            print(f"Source URL: {result.get('source_url', 'N/A')}")
            
            print(f"\n🎉 Your pipeline is ready for the full dataset!")
            print(f"You can now run: python interactive_enricher.py")
            
        else:
            print("❌ Pipeline failed - check the logs above for details")
            
    except Exception as e:
        print(f"❌ Error: {str(e)}")

if __name__ == "__main__":
    test_complete_pipeline()