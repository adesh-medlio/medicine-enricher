#!/usr/bin/env python3
"""
Test the improved search functionality
"""

import logging
from medicine_enricher import MedicineEnricher

# Set up detailed logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')

def test_improved_search():
    """Test the improved search with problematic cases"""
    
    from config import get_groq_api_key
    
    # Get API key from environment
    GROQ_API_KEY = get_groq_api_key()
    if not GROQ_API_KEY:
        return
    
    # Initialize enricher
    enricher = MedicineEnricher(GROQ_API_KEY)
    
    # Test cases that were problematic
    test_cases = [
        {
            'name': 'Actibile 300 Tablet',
            'manufacturer': 'Zydus Cadila',
            'expected_contains': 'actibile',
            'wrong_result': 'zedott'  # What we were getting before
        },
        {
            'name': 'Glywohn MP 1mg/500mg/15mg Tablet',
            'manufacturer': 'Riyadh Pharmaceutical',
            'expected_contains': 'glywohn',
            'wrong_result': 'glynamic'  # What we were getting before
        }
    ]
    
    print("🔬 Testing Improved Search Algorithm")
    print("=" * 50)
    
    for i, case in enumerate(test_cases, 1):
        print(f"\n📋 Test Case {i}: {case['name']}")
        print(f"🏭 Manufacturer: {case['manufacturer']}")
        print(f"✅ Should contain: '{case['expected_contains']}'")
        print(f"❌ Should NOT contain: '{case['wrong_result']}'")
        print("-" * 40)
        
        try:
            # Test search only first
            print("🔍 Step 1: Testing URL search...")
            found_url = enricher.google_search_1mg(case['name'], case['manufacturer'])
            
            if found_url:
                print(f"   Found URL: {found_url}")
                
                # Check if it's correct
                url_lower = found_url.lower()
                if case['expected_contains'] in url_lower:
                    print("   ✅ CORRECT URL - Contains expected medicine name!")
                elif case['wrong_result'] in url_lower:
                    print("   ❌ WRONG URL - Still getting the old wrong result")
                else:
                    print("   ⚠️  DIFFERENT URL - Not the expected one, but also not the wrong one")
            else:
                print("   ❌ No URL found")
                continue
            
            # Test full processing
            print("\n🔄 Step 2: Testing full processing...")
            result = enricher.process_medicine(case['name'], case['manufacturer'])
            
            if result:
                found_name = result.get('found_medicine_name', '').lower()
                found_mfg = result.get('found_manufacturer', '')
                
                print(f"   Found Medicine: {result.get('found_medicine_name', 'N/A')}")
                print(f"   Found Manufacturer: {found_mfg}")
                
                # Check accuracy
                if case['expected_contains'] in found_name:
                    print("   ✅ SUCCESS - Found correct medicine!")
                elif case['wrong_result'] in found_name:
                    print("   ❌ FAILURE - Still getting wrong medicine")
                else:
                    print("   ⚠️  UNCERTAIN - Different medicine found")
                
                # Check warnings
                if result.get('similarity_warning'):
                    print(f"   ⚠️  Similarity Warning: {result['similarity_warning']}")
                if result.get('manufacturer_warning'):
                    print(f"   ⚠️  Manufacturer Warning: {result['manufacturer_warning']}")
                    
            else:
                print("   ❌ Processing failed")
                
        except Exception as e:
            print(f"   ❌ Error: {str(e)}")
    
    print(f"\n" + "=" * 50)
    print("🏁 Test completed!")
    print("\n💡 If you're still getting wrong results:")
    print("   1. Check the similarity_warning and manufacturer_warning columns")
    print("   2. The improved algorithm should reject very low similarity matches")
    print("   3. Direct 1mg search is now tried first for better accuracy")

if __name__ == "__main__":
    test_improved_search()