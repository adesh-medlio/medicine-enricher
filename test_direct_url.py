#!/usr/bin/env python3
"""
Test direct URL access to verify the correct medicine page exists
"""

import requests
from bs4 import BeautifulSoup
from medicine_enricher import MedicineEnricher

def test_direct_url_access():
    """Test if we can directly access the correct Actibile URL"""
    
    correct_url = "https://www.1mg.com/drugs/actibile-300-tablet-121415"
    
    print("🔗 Testing Direct URL Access")
    print("=" * 40)
    print(f"URL: {correct_url}")
    
    try:
        # Try to fetch the page directly
        headers = {
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36'
        }
        
        response = requests.get(correct_url, headers=headers, timeout=15)
        response.raise_for_status()
        
        print(f"✅ Successfully accessed the page")
        print(f"   Status code: {response.status_code}")
        print(f"   Content length: {len(response.content)} bytes")
        
        # Parse and extract basic info
        soup = BeautifulSoup(response.content, 'html.parser')
        
        # Get medicine name
        title_elem = soup.find('h1', class_='DrugHeader__title-content___2ZaPo')
        if title_elem:
            found_name = title_elem.get_text().strip()
            print(f"   Medicine name: {found_name}")
            
            if "actibile" in found_name.lower():
                print("   ✅ Correct medicine confirmed!")
            else:
                print("   ❌ Wrong medicine found")
        
        # Get manufacturer
        meta_sections = soup.find_all('div', class_='DrugHeader__meta___B3BcU')
        for section in meta_sections:
            title_elem = section.find('div', class_='DrugHeader__meta-title___22zXC')
            if title_elem and 'marketer' in title_elem.get_text().lower():
                value_elem = section.find('div', class_='DrugHeader__meta-value___vqYM0')
                if value_elem:
                    found_manufacturer = value_elem.get_text().strip()
                    print(f"   Manufacturer: {found_manufacturer}")
                    
                    if "zydus" in found_manufacturer.lower():
                        print("   ✅ Correct manufacturer confirmed!")
                    else:
                        print("   ⚠️  Different manufacturer found")
                break
        
        # Get salt composition
        salt_elem = soup.find('div', class_='saltInfo')
        if salt_elem:
            salt_text = salt_elem.get_text().strip()
            print(f"   Salt composition: {salt_text}")
        
        return True
        
    except Exception as e:
        print(f"❌ Failed to access URL: {str(e)}")
        return False

def test_search_vs_direct():
    """Compare search results vs direct URL access"""
    
    print("\n🔍 Comparing Search Results vs Direct Access")
    print("=" * 50)
    
    # Test data
    medicine_name = "Actibile 300 Tablet"
    manufacturer_name = "Zydus Cadila"
    correct_url = "https://www.1mg.com/drugs/actibile-300-tablet-121415"
    
    from config import get_groq_api_key
    
    # Get API key from environment
    GROQ_API_KEY = get_groq_api_key()
    if not GROQ_API_KEY:
        return
        
    # Initialize enricher
    enricher = MedicineEnricher(GROQ_API_KEY)
    
    print(f"Searching for: {medicine_name} by {manufacturer_name}")
    
    # Test search
    try:
        found_url = enricher.google_search_1mg(medicine_name, manufacturer_name)
        
        print(f"\n🔎 Search Result:")
        if found_url:
            print(f"   Found URL: {found_url}")
            
            if found_url == correct_url:
                print("   ✅ PERFECT MATCH!")
            elif "actibile" in found_url.lower():
                print("   ✅ Correct medicine, different URL format")
            else:
                print("   ❌ Wrong medicine found")
                print(f"   Expected: {correct_url}")
        else:
            print("   ❌ No URL found")
            
    except Exception as e:
        print(f"   ❌ Search failed: {str(e)}")
    
    # Test direct access
    print(f"\n🔗 Direct Access Test:")
    success = test_direct_url_access()
    
    if success:
        print("\n💡 Recommendations:")
        print("   1. The correct URL exists and is accessible")
        print("   2. If search is not finding it, we need to:")
        print("      - Improve search query specificity")
        print("      - Add more validation in URL selection")
        print("      - Consider direct 1mg site search as primary method")

if __name__ == "__main__":
    test_search_vs_direct()