#!/usr/bin/env python3
"""
Excel File Recovery Script
Recovers corrupted Excel files using backup files created by the medicine enricher.
"""

import pandas as pd
import os
import shutil
from datetime import datetime

def recover_excel_file():
    """Recover the corrupted Excel file using the backup."""
    
    # File paths
    corrupted_file = r"C:\Users\adesh.shetty\Downloads\part_2_medicine_normalized_enriched_enriched.xlsx"
    backup_file = r"C:\Users\adesh.shetty\Downloads\part_2_medicine_normalized_enriched_enriched_backup_18560.xlsx"
    recovered_file = r"C:\Users\adesh.shetty\Downloads\part_2_medicine_normalized_enriched_enriched_RECOVERED.xlsx"
    
    print("🔧 Excel File Recovery Tool")
    print("=" * 50)
    
    # Check if files exist
    print(f"📁 Checking files...")
    print(f"   Corrupted file: {os.path.exists(corrupted_file)} ({os.path.getsize(corrupted_file) if os.path.exists(corrupted_file) else 0} bytes)")
    print(f"   Backup file: {os.path.exists(backup_file)} ({os.path.getsize(backup_file) if os.path.exists(backup_file) else 0} bytes)")
    
    if not os.path.exists(backup_file):
        print("❌ Backup file not found! Cannot recover.")
        return False
    
    try:
        # Test if backup file is readable
        print(f"\n🔍 Testing backup file...")
        df = pd.read_excel(backup_file)
        print(f"✅ Backup file is readable!")
        print(f"   Rows: {len(df)}")
        print(f"   Columns: {len(df.columns)}")
        print(f"   Columns: {list(df.columns)}")
        
        # Show sample data
        print(f"\n📊 Sample data from backup:")
        print(df.head(3).to_string())
        
        # Copy backup to recovered file
        print(f"\n💾 Creating recovered file...")
        shutil.copy2(backup_file, recovered_file)
        
        # Verify recovered file
        df_recovered = pd.read_excel(recovered_file)
        print(f"✅ Recovery successful!")
        print(f"   Recovered file: {recovered_file}")
        print(f"   Rows recovered: {len(df_recovered)}")
        
        # Optional: Replace the corrupted file
        replace = input(f"\n🔄 Replace corrupted file with recovered data? (y/n): ").lower().strip()
        if replace == 'y':
            # Backup the corrupted file first
            corrupted_backup = corrupted_file.replace('.xlsx', '_CORRUPTED_BACKUP.xlsx')
            if os.path.exists(corrupted_file):
                shutil.move(corrupted_file, corrupted_backup)
                print(f"   Corrupted file backed up to: {corrupted_backup}")
            
            # Replace with recovered data
            shutil.copy2(recovered_file, corrupted_file)
            print(f"✅ File replaced successfully!")
        
        return True
        
    except Exception as e:
        print(f"❌ Error during recovery: {str(e)}")
        return False

def check_all_backups():
    """Check all backup files in the Downloads folder."""
    
    downloads_dir = r"C:\Users\adesh.shetty\Downloads"
    print(f"\n🔍 Checking all backup files in {downloads_dir}")
    print("=" * 60)
    
    backup_files = []
    for file in os.listdir(downloads_dir):
        if 'backup' in file.lower() and file.endswith('.xlsx'):
            file_path = os.path.join(downloads_dir, file)
            size = os.path.getsize(file_path)
            backup_files.append((file, size, file_path))
    
    if not backup_files:
        print("❌ No backup files found.")
        return
    
    # Sort by size (larger files likely have more data)
    backup_files.sort(key=lambda x: x[1], reverse=True)
    
    print(f"Found {len(backup_files)} backup files:")
    for i, (filename, size, path) in enumerate(backup_files, 1):
        print(f"{i}. {filename}")
        print(f"   Size: {size:,} bytes ({size/1024/1024:.1f} MB)")
        
        try:
            df = pd.read_excel(path)
            print(f"   Status: ✅ Readable ({len(df)} rows, {len(df.columns)} columns)")
        except Exception as e:
            print(f"   Status: ❌ Error - {str(e)}")
        print()

if __name__ == "__main__":
    print("🚀 Starting Excel file recovery...")
    
    # First, check all backups
    check_all_backups()
    
    # Then attempt recovery
    success = recover_excel_file()
    
    if success:
        print(f"\n🎉 Recovery completed successfully!")
        print(f"💡 Tips to prevent corruption:")
        print(f"   • Don't close the process while it's saving")
        print(f"   • Close Excel before running the enricher")
        print(f"   • Use the resume feature if interrupted")
    else:
        print(f"\n❌ Recovery failed. Check the error messages above.")