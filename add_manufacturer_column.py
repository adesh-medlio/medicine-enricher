#!/usr/bin/env python3
"""
Script to add manufacturer column to existing Excel file
"""

import pandas as pd
import os
from datetime import datetime

def add_manufacturer_column(input_file, output_file=None):
    """Add manufacturer column to Excel file"""
    try:
        if not os.path.exists(input_file):
            print(f"❌ File not found: {input_file}")
            return False
        
        print(f"📄 Reading file: {input_file}")
        df = pd.read_excel(input_file)
        
        print(f"📊 Original file info:")
        print(f"   - Rows: {len(df)}")
        print(f"   - Columns: {len(df.columns)}")
        
        # Check if manufacturer column already exists
        manufacturer_cols = [col for col in df.columns if 'manufacturer' in col.lower()]
        
        if manufacturer_cols:
            print(f"✅ Manufacturer column already exists: {manufacturer_cols}")
            return True
        
        # Add manufacturer column
        df['manufacturer_name'] = ''  # Empty column for user to fill
        
        # Create output filename if not provided
        if output_file is None:
            base_name = input_file.replace('.xlsx', '')
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            output_file = f"{base_name}_with_manufacturer_{timestamp}.xlsx"
        
        # Save the file
        df.to_excel(output_file, index=False)
        
        print(f"✅ Added manufacturer_name column")
        print(f"📤 Saved to: {output_file}")
        print(f"📊 New file info:")
        print(f"   - Rows: {len(df)}")
        print(f"   - Columns: {len(df.columns)}")
        
        print(f"\n📋 New columns:")
        for i, col in enumerate(df.columns, 1):
            marker = " (NEW)" if col == 'manufacturer_name' else ""
            print(f"   {i:2d}. {col}{marker}")
        
        print(f"\n💡 Next steps:")
        print(f"   1. Open {output_file} in Excel")
        print(f"   2. Fill in the 'manufacturer_name' column with manufacturer data")
        print(f"   3. Save the file")
        print(f"   4. Use the updated file with the medicine enricher")
        
        return True
        
    except Exception as e:
        print(f"❌ Error: {str(e)}")
        return False

def suggest_manufacturers_from_names(input_file):
    """Try to extract manufacturer info from medicine names"""
    try:
        df = pd.read_excel(input_file)
        
        if 'name' not in df.columns:
            print("❌ No 'name' column found")
            return
        
        print(f"\n🔍 Analyzing medicine names for manufacturer clues...")
        
        # Common patterns that might indicate manufacturer
        potential_manufacturers = []
        
        for idx, name in enumerate(df['name']):
            if pd.isna(name):
                continue
                
            name_str = str(name).strip()
            
            # Look for patterns like "by Company" or "Company Ltd"
            words = name_str.split()
            
            # Simple heuristics - you can improve these
            manufacturer_hints = []
            
            # Look for "Ltd", "Pvt", "Pharma", "Pharmaceutical" etc.
            pharma_keywords = ['ltd', 'pvt', 'pharma', 'pharmaceutical', 'pharmaceuticals', 'labs', 'laboratory']
            
            for i, word in enumerate(words):
                word_lower = word.lower().replace(',', '').replace('.', '')
                if word_lower in pharma_keywords:
                    # Take this word and maybe 1-2 words before it
                    start_idx = max(0, i-2)
                    manufacturer_hint = ' '.join(words[start_idx:i+1])
                    manufacturer_hints.append(manufacturer_hint)
            
            if manufacturer_hints:
                potential_manufacturers.append({
                    'row': idx + 1,
                    'medicine': name_str,
                    'potential_manufacturer': manufacturer_hints[0]
                })
        
        if potential_manufacturers:
            print(f"📋 Found {len(potential_manufacturers)} potential manufacturer hints:")
            for item in potential_manufacturers[:10]:  # Show first 10
                print(f"   Row {item['row']}: {item['medicine']}")
                print(f"      → Possible manufacturer: {item['potential_manufacturer']}")
                print()
            
            if len(potential_manufacturers) > 10:
                print(f"   ... and {len(potential_manufacturers) - 10} more")
        else:
            print(f"❌ No manufacturer hints found in medicine names")
            
    except Exception as e:
        print(f"❌ Error analyzing names: {str(e)}")

def main():
    """Main function"""
    print("🏭 Manufacturer Column Manager")
    print("=" * 35)
    
    # Find Excel files
    excel_files = [f for f in os.listdir('.') if f.endswith('.xlsx') and not f.startswith('~')]
    
    if not excel_files:
        print("❌ No Excel files found in current directory")
        return
    
    print(f"📁 Found Excel files:")
    for i, f in enumerate(excel_files, 1):
        print(f"   {i}. {f}")
    
    # Get user choice
    if len(excel_files) == 1:
        input_file = excel_files[0]
        print(f"\n🔍 Using: {input_file}")
    else:
        choice = input(f"\nEnter number to process (1-{len(excel_files)}): ").strip()
        try:
            input_file = excel_files[int(choice) - 1]
        except (ValueError, IndexError):
            input_file = excel_files[0]
            print(f"Invalid choice, using: {input_file}")
    
    print()
    
    # Check current structure
    try:
        df = pd.read_excel(input_file)
        print(f"📊 Current file structure:")
        print(f"   - Rows: {len(df)}")
        print(f"   - Columns: {df.columns.tolist()}")
        
        # Check if manufacturer column exists
        manufacturer_cols = [col for col in df.columns if 'manufacturer' in col.lower()]
        
        if manufacturer_cols:
            print(f"\n✅ Manufacturer column already exists: {manufacturer_cols[0]}")
            
            # Check how many are filled
            filled_count = df[manufacturer_cols[0]].notna().sum()
            print(f"   - Filled entries: {filled_count}/{len(df)}")
            
            if filled_count == 0:
                print(f"   ⚠️  Column is empty - you may want to fill it manually")
        else:
            print(f"\n❌ No manufacturer column found")
            
            # Ask if user wants to add one
            add_col = input("Add manufacturer_name column? (y/n): ").strip().lower()
            
            if add_col in ['y', 'yes']:
                success = add_manufacturer_column(input_file)
                
                if success:
                    # Try to suggest manufacturers from names
                    suggest_manufacturers_from_names(input_file)
            else:
                print("👍 No changes made")
        
    except Exception as e:
        print(f"❌ Error reading file: {str(e)}")

if __name__ == "__main__":
    main()