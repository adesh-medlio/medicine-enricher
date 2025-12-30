"""
Debug script to test medicine search functionality
"""

from medicine_enricher import MedicineEnricher
import logging

# Enable debug logging
logging.basicConfig(level=logging.DEBUG, format='%(asctime)s - %(levelname)s - %(message)s')

def test_single_medicine():
    """Test search for a single medicine"""
    enricher = MedicineEnricher("dummy_key")  # We won't call Groq for this test
    
    test_medicines = [
        "Augmentin 625 Duo Tablet",
        "Paracetamol 500mg",
        "Crocin",
        "Dolo 650"
    ]
    
    for medicine in test_medicines:
        print(f"\n{'='*50}")
        print(f"Testing: {medicine}")
        print(f"{'='*50}")
        
        try:
            url = enricher.google_search_1mg(medicine)
            if url:
                print(f"✅ SUCCESS: Found URL: {url}")
                
                # Test fetching the page
                print("Testing page fetch...")
                content = enricher.fetch_1mg_page(url)
                if content:
                    print(f"✅ Page fetched successfully ({len(content)} characters)")
                    print(f"Preview: {content[:200]}...")
                else:
                    print("❌ Failed to fetch page content")
            else:
                print(f"❌ FAILED: No URL found for {medicine}")
                
        except Exception as e:
            print(f"❌ ERROR: {str(e)}")
        
        print("\nWaiting 3 seconds before next test...")
        import time
        time.sleep(3)

def test_manual_url():
    """Test with a known 1mg URL"""
    enricher = MedicineEnricher("dummy_key")
    
    # Try a known medicine URL pattern
    test_url = "https://www.1mg.com/drugs/paracetamol-500mg-tablet-138629"
    
    print(f"Testing manual URL: {test_url}")
    
    if enricher._is_valid_1mg_url(test_url):
        print("✅ URL validation passed")
        
        content = enricher.fetch_1mg_page(test_url)
        if content:
            print(f"✅ Page fetched successfully ({len(content)} characters)")
            print(f"Preview: {content[:300]}...")
        else:
            print("❌ Failed to fetch page")
    else:
        print("❌ URL validation failed")

if __name__ == "__main__":
    print("Medicine Search Debug Tool")
    print("=" * 40)
    
    choice = input("\n1. Test single medicine search\n2. Test manual URL\n3. Both\nChoose (1/2/3): ").strip()
    
    if choice in ['1', '3']:
        test_single_medicine()
    
    if choice in ['2', '3']:
        test_manual_url()