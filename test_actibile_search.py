#!/usr/bin/env python3
"""
Test script for the specific Actibile 300 Tablet issue
"""

import logging
from medicine_enricher import MedicineEnricher

# Set up detailed logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')

def test_actibile_search():
    """Test the specific problematic case"""
    
    from config import get_groq_api_key
    
    # Get API key from environment
    GROQ_API_KEY = get_groq_api_key()
    if not GROQ_API_KEY:
        return
    
    # Initialize enricher
    enricher = MedicineEnricher(GROQ_API_KEY)
    
    # Test case - your problematic example
    medicine_name = "Actibile 300 Tablet"
    manufacturer_name = "Zydus Cadila"
    
    print("🔍 Testing Enhanced Search for Actibile 300 Tablet")
    print("=" * 60)
    print(f"Medicine: {medicine_name}")
    print(f"Manufacturer: {manufacturer_name}")
    print(f"Expected URL: https://www.1mg.com/drugs/actibile-300-tablet-121415")
    print("-" * 60)
    
    # Test just the search part first
    print("\n🔎 Step 1: Testing Google Search...")
    try:
        found_url = enricher.google_search_1mg(medicine_name, manufacturer_name)
        
        if found_url:
            print(f"✅ Found URL: {found_url}")
            
            # Check if it's the correct URL
            if "actibile-300-tablet" in found_url.lower():
                print("✅ CORRECT! Found the right medicine URL")
            else:
                print("❌ WRONG! Found different medicine")
                print("   This indicates the search strategy needs more refinement")
        else:
            print("❌ No URL found")
            
    except Exception as e:
        print(f"❌ Search failed: {str(e)}")
        return
    
    # Test full processing
    print(f"\n🔄 Step 2: Testing Full Processing...")
    try:
        result = enricher.process_medicine(medicine_name, manufacturer_name)
        
        if result:
            print("✅ Processing completed")
            print(f"   Found Medicine: {result.get('found_medicine_name', 'N/A')}")
            print(f"   Found Manufacturer: {result.get('found_manufacturer', 'N/A')}")
            print(f"   Source URL: {result.get('source_url', 'N/A')}")
            print(f"   Salt Composition: {result.get('salt_composition', 'N/A')[:100]}...")
            
            # Check warnings
            if result.get('similarity_warning'):
                print(f"   ⚠️  Similarity Warning: {result['similarity_warning']}")
            if result.get('manufacturer_warning'):
                print(f"   ⚠️  Manufacturer Warning: {result['manufacturer_warning']}")
                
            # Final verdict
            if "actibile" in result.get('found_medicine_name', '').lower():
                print("\n🎯 SUCCESS: Found the correct medicine!")
            else:
                print("\n❌ FAILURE: Still getting wrong medicine")
                print("   Need to further refine search strategy")
        else:
            print("❌ Processing failed - no data returned")
            
    except Exception as e:
        print(f"❌ Processing failed: {str(e)}")

def test_multiple_cases():
    """Test multiple problematic cases"""
    
    from config import get_groq_api_key
    
    GROQ_API_KEY = get_groq_api_key()
    if not GROQ_API_KEY:
        return
        
    enricher = MedicineEnricher(GROQ_API_KEY)
    
    test_cases = [
        {
            'name': 'Actibile 300 Tablet',
            'manufacturer': 'Zydus Cadila',
            'expected_url_contains': 'actibile-300-tablet'
        },
        {
            'name': 'Glywohn MP 1mg/500mg/15mg Tablet',
            'manufacturer': 'Riyadh Pharmaceutical',
            'expected_url_contains': 'glywohn-mp'
        }
    ]
    
    print("🧪 Testing Multiple Problematic Cases")
    print("=" * 50)
    
    for i, case in enumerate(test_cases, 1):
        print(f"\n📋 Test Case {i}: {case['name']}")
        print(f"🏭 Manufacturer: {case['manufacturer']}")
        print("-" * 30)
        
        try:
            # Test search only
            found_url = enricher.google_search_1mg(case['name'], case['manufacturer'])
            
            if found_url:
                if case['expected_url_contains'] in found_url.lower():
                    print(f"✅ CORRECT URL: {found_url}")
                else:
                    print(f"❌ WRONG URL: {found_url}")
                    print(f"   Expected to contain: {case['expected_url_contains']}")
            else:
                print("❌ No URL found")
                
        except Exception as e:
            print(f"❌ Error: {str(e)}")

if __name__ == "__main__":
    print("🔬 Actibile Search Test")
    print("=" * 30)
    
    choice = input("1. Test Actibile case only\n2. Test multiple cases\nChoice (1-2): ").strip()
    
    if choice == "2":
        test_multiple_cases()
    else:
        test_actibile_search()