#!/usr/bin/env python3
"""
Quick script to check what columns are in your Excel file
"""

import pandas as pd
import os

def check_excel_columns(file_path):
    """Check columns in Excel file"""
    try:
        if not os.path.exists(file_path):
            print(f"❌ File not found: {file_path}")
            return
        
        print(f"📄 Checking file: {file_path}")
        
        # Read just the first few rows to check structure
        df = pd.read_excel(file_path, nrows=5)
        
        print(f"📊 File info:")
        print(f"   - Total columns: {len(df.columns)}")
        print(f"   - Sample rows read: {len(df)}")
        
        print(f"\n📋 Columns found:")
        for i, col in enumerate(df.columns, 1):
            print(f"   {i:2d}. {col}")
        
        print(f"\n🔍 Sample data (first 3 rows):")
        print(df.head(3).to_string(index=False))
        
        # Check for manufacturer-related columns
        manufacturer_cols = [col for col in df.columns if 'manufacturer' in col.lower() or 'company' in col.lower() or 'marketer' in col.lower()]
        
        if manufacturer_cols:
            print(f"\n🏭 Found manufacturer-related columns:")
            for col in manufacturer_cols:
                print(f"   - {col}")
                # Show sample values
                sample_values = df[col].dropna().head(3).tolist()
                if sample_values:
                    print(f"     Sample values: {sample_values}")
        else:
            print(f"\n⚠️  No manufacturer-related columns found")
            print(f"   Consider adding a 'manufacturer_name' column for better search accuracy")
        
        return df.columns.tolist()
        
    except Exception as e:
        print(f"❌ Error reading file: {str(e)}")
        return None

def main():
    """Main function"""
    print("📋 Excel Column Checker")
    print("=" * 30)
    
    # Common file names to check
    common_files = [
        'medicines_input.xlsx',
        'medicines.xlsx',
        'input.xlsx',
        'data.xlsx',
        'optimized_test_results.xlsx'  # From your file list
    ]
    
    # Check if any common files exist
    found_files = [f for f in common_files if os.path.exists(f)]
    
    if found_files:
        print(f"📁 Found these Excel files:")
        for i, f in enumerate(found_files, 1):
            print(f"   {i}. {f}")
        
        if len(found_files) == 1:
            file_to_check = found_files[0]
            print(f"\n🔍 Checking: {file_to_check}")
        else:
            choice = input(f"\nEnter number to check (1-{len(found_files)}): ").strip()
            try:
                file_to_check = found_files[int(choice) - 1]
            except (ValueError, IndexError):
                file_to_check = found_files[0]
                print(f"Invalid choice, using: {file_to_check}")
    else:
        file_to_check = input("Enter Excel file path: ").strip()
    
    print()
    columns = check_excel_columns(file_to_check)
    
    if columns:
        print(f"\n💡 Tips for better search accuracy:")
        print(f"   - If you have manufacturer data, add it to a column named 'manufacturer_name'")
        print(f"   - The enricher will automatically use it for more precise searches")
        print(f"   - This helps avoid getting wrong medicines with similar names")

if __name__ == "__main__":
    main()