"""
Quick test of the improved medicine enricher
"""

from medicine_enricher import MedicineEnricher
import logging

# Set up logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')

def test_with_groq():
    """Test the complete pipeline with Groq"""
    
    # Get API key
    api_key = input("Enter your Groq API key (or 'skip' to test without Groq): ").strip()
    
    if api_key.lower() == 'skip':
        print("Testing without Groq API...")
        enricher = MedicineEnricher("dummy_key")
        
        # Test just URL finding and page fetching
        test_medicine = "Augmentin 625 Duo Tablet"
        print(f"\nTesting: {test_medicine}")
        
        url = enricher.google_search_1mg(test_medicine)
        if url:
            print(f"✅ Found URL: {url}")
            
            content = enricher.fetch_1mg_page(url)
            if content:
                print(f"✅ Fetched content ({len(content)} chars)")
                print(f"Preview: {content[:200]}...")
            else:
                print("❌ Failed to fetch content")
        else:
            print("❌ No URL found")
    
    else:
        print("Testing complete pipeline with Groq...")
        enricher = MedicineEnricher(api_key)
        
        test_medicine = "Augmentin 625 Duo Tablet"
        print(f"\nTesting: {test_medicine}")
        
        result = enricher.process_medicine(test_medicine)
        if result:
            print("✅ Complete pipeline successful!")
            print(f"Salt composition: {result.get('salt_composition', 'N/A')}")
            print(f"Description: {result.get('medicine_description', 'N/A')}")
            print(f"Source URL: {result.get('source_url', 'N/A')}")
        else:
            print("❌ Pipeline failed")

if __name__ == "__main__":
    test_with_groq()