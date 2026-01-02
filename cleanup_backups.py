#!/usr/bin/env python3
"""
Cleanup Existing Backup Files
Run this to clean up all the backup files you currently have
"""

import os
import glob
from smart_backup_manager import clean_all_backups_in_directory

def main():
    print("🧹 Backup File Cleanup Utility")
    print("=" * 50)
    
    # Show current backup files
    backup_files = glob.glob("*_backup_*.xlsx")
    emergency_files = glob.glob("*_emergency_*.xlsx")
    
    print(f"📁 Found {len(backup_files)} backup files")
    print(f"🚨 Found {len(emergency_files)} emergency files")
    
    if backup_files:
        print("\nCurrent backup files:")
        for f in sorted(backup_files):
            size = os.path.getsize(f) / (1024*1024)  # MB
            print(f"  📄 {f} ({size:.1f} MB)")
    
    if emergency_files:
        print("\nEmergency files:")
        for f in sorted(emergency_files):
            size = os.path.getsize(f) / (1024*1024)  # MB
            print(f"  🚨 {f} ({size:.1f} MB)")
    
    if not backup_files and not emergency_files:
        print("✅ No backup files found to clean up!")
        return
    
    print("\n" + "=" * 50)
    print("Options:")
    print("1. Keep 3 most recent backups per file (recommended)")
    print("2. Keep 2 most recent backups per file")
    print("3. Keep 1 most recent backup per file")
    print("4. Delete ALL backup files (dangerous!)")
    print("5. Cancel")
    
    choice = input("\nEnter your choice (1-5): ").strip()
    
    if choice == "5":
        print("❌ Cancelled")
        return
    elif choice == "4":
        confirm = input("⚠️  Are you sure you want to delete ALL backups? (yes/no): ").strip().lower()
        if confirm == "yes":
            deleted = 0
            for f in backup_files + emergency_files:
                try:
                    os.remove(f)
                    deleted += 1
                    print(f"🗑️  Deleted: {f}")
                except Exception as e:
                    print(f"❌ Could not delete {f}: {e}")
            print(f"✅ Deleted {deleted} backup files")
        else:
            print("❌ Cancelled")
        return
    elif choice in ["1", "2", "3"]:
        max_backups = int(choice)
        print(f"\n🧹 Cleaning up, keeping {max_backups} most recent backups per file...")
        clean_all_backups_in_directory(".", max_backups=max_backups)
    else:
        print("❌ Invalid choice")
        return
    
    # Show results
    print("\n" + "=" * 50)
    remaining_backups = glob.glob("*_backup_*.xlsx")
    remaining_emergency = glob.glob("*_emergency_*.xlsx")
    
    print(f"📁 Remaining backup files: {len(remaining_backups)}")
    print(f"🚨 Remaining emergency files: {len(remaining_emergency)}")
    
    if remaining_backups:
        print("\nRemaining backups:")
        for f in sorted(remaining_backups):
            print(f"  📄 {f}")

if __name__ == "__main__":
    main()