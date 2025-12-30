#!/usr/bin/env python3
"""
Demo to show what .strip() does with medicine names
"""

def demo_strip_function():
    """Demonstrate the strip() function with medicine names"""
    
    print("🧹 Demonstrating .strip() function")
    print("=" * 40)
    
    # Examples of messy medicine names (like you might get from Excel)
    messy_names = [
        "  Actibile 300 Tablet  ",           # Leading/trailing spaces
        "\tParacetamol 500mg\t",             # Tabs
        "\nCrocin Advance\n",                # Newlines
        "   Glywohn MP 1mg/500mg/15mg   ",   # Multiple spaces
        "Aspirin 75mg",                      # Already clean
        "  \t\n  Zedott 30 DT  \n\t  ",     # Mixed whitespace
    ]
    
    print("Examples of cleaning medicine names:\n")
    
    for i, messy_name in enumerate(messy_names, 1):
        clean_name = messy_name.strip()
        
        print(f"Example {i}:")
        print(f"  Original: '{messy_name}' (length: {len(messy_name)})")
        print(f"  Cleaned:  '{clean_name}' (length: {len(clean_name)})")
        
        # Show if there was a change
        if messy_name != clean_name:
            print(f"  ✅ Cleaned! Removed {len(messy_name) - len(clean_name)} characters")
        else:
            print(f"  ✨ Already clean!")
        print()
    
    # Show how this affects search queries
    print("Impact on search queries:")
    print("-" * 25)
    
    messy_example = "  Actibile 300 Tablet  "
    clean_example = messy_example.strip()
    
    print(f"Without .strip():")
    messy_query = f'site:1mg.com/drugs "{messy_example}"'
    print(f"  Query: {messy_query}")
    print(f"  Notice the extra spaces inside the quotes!")
    
    print(f"\nWith .strip():")
    clean_query = f'site:1mg.com/drugs "{clean_example}"'
    print(f"  Query: {clean_query}")
    print(f"  Much cleaner and more likely to work!")
    
    # Show character representation
    print(f"\nCharacter-by-character view:")
    print(f"  Messy:  {repr(messy_example)}")
    print(f"  Clean:  {repr(clean_example)}")

def show_real_world_example():
    """Show how this might look in the actual medicine enricher"""
    
    print("\n" + "=" * 50)
    print("🔍 Real-world example in medicine enricher")
    print("=" * 50)
    
    # Simulate reading from Excel (with extra whitespace)
    excel_data = [
        "  Actibile 300 Tablet  ",
        "\tGlywohn MP 1mg/500mg/15mg\n",
        "Paracetamol 500mg",  # Clean one
    ]
    
    print("Processing medicine names from Excel:\n")
    
    for medicine_name in excel_data:
        print(f"Raw from Excel: {repr(medicine_name)}")
        
        # This is what happens in the code
        clean_name = medicine_name.strip()
        print(f"After .strip(): {repr(clean_name)}")
        
        # Show the search query that would be created
        search_query = f'site:1mg.com/drugs "{clean_name}"'
        print(f"Search query:   {search_query}")
        print("-" * 40)

if __name__ == "__main__":
    demo_strip_function()
    show_real_world_example()