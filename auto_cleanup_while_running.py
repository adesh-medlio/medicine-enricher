#!/usr/bin/env python3
"""
Auto Cleanup Backup Files While Enricher is Running
Run this in a separate terminal to continuously clean backup files
"""

import os
import glob
import time
import threading
from datetime import datetime, timedelta

class BackgroundCleaner:
    """Continuously cleans backup files while enricher runs."""
    
    def __init__(self, max_backups_per_file=2, cleanup_interval=300):  # 5 minutes
        self.max_backups_per_file = max_backups_per_file
        self.cleanup_interval = cleanup_interval
        self.running = True
        
    def cleanup_old_backups(self):
        """Clean up old backup files."""
        try:
            # Find all backup files
            backup_files = glob.glob("*_backup_*.xlsx")
            emergency_files = glob.glob("*_emergency_*.xlsx")
            
            if not backup_files and not emergency_files:
                return 0
            
            # Group backup files by base name
            backup_groups = {}
            for backup_file in backup_files:
                # Extract base name (remove _backup_timestamp.xlsx)
                base_name = backup_file.split('_backup_')[0]
                if base_name not in backup_groups:
                    backup_groups[base_name] = []
                backup_groups[base_name].append(backup_file)
            
            deleted_count = 0
            
            # Clean up each group
            for base_name, files in backup_groups.items():
                if len(files) > self.max_backups_per_file:
                    # Sort by modification time (newest first)
                    files.sort(key=os.path.getmtime, reverse=True)
                    
                    # Keep only the most recent ones
                    files_to_delete = files[self.max_backups_per_file:]
                    
                    for file_to_delete in files_to_delete:
                        try:
                            os.remove(file_to_delete)
                            deleted_count += 1
                            print(f"🗑️  Deleted: {file_to_delete}")
                        except Exception as e:
                            print(f"⚠️  Could not delete {file_to_delete}: {e}")
            
            # Delete emergency files older than 1 hour
            for emergency_file in emergency_files:
                try:
                    file_time = datetime.fromtimestamp(os.path.getmtime(emergency_file))
                    if datetime.now() - file_time > timedelta(hours=1):
                        os.remove(emergency_file)
                        deleted_count += 1
                        print(f"🗑️  Deleted old emergency: {emergency_file}")
                except Exception as e:
                    print(f"⚠️  Could not delete {emergency_file}: {e}")
            
            if deleted_count > 0:
                print(f"✅ Cleaned up {deleted_count} backup files")
                
                # Show remaining files
                remaining = len(glob.glob("*_backup_*.xlsx")) + len(glob.glob("*_emergency_*.xlsx"))
                print(f"📁 Remaining backup files: {remaining}")
            
            return deleted_count
            
        except Exception as e:
            print(f"❌ Cleanup error: {e}")
            return 0
    
    def run_continuous_cleanup(self):
        """Run cleanup in a loop."""
        print(f"🧹 Starting continuous backup cleanup...")
        print(f"📁 Keeping max {self.max_backups_per_file} backups per file")
        print(f"⏰ Cleanup interval: {self.cleanup_interval} seconds")
        print("Press Ctrl+C to stop")
        
        while self.running:
            try:
                current_time = datetime.now().strftime("%H:%M:%S")
                print(f"\n🔄 [{current_time}] Running cleanup...")
                
                deleted = self.cleanup_old_backups()
                if deleted == 0:
                    print("✅ No cleanup needed")
                
                # Wait for next cleanup
                time.sleep(self.cleanup_interval)
                
            except KeyboardInterrupt:
                print("\n🛑 Cleanup stopped by user")
                self.running = False
                break
            except Exception as e:
                print(f"❌ Cleanup loop error: {e}")
                time.sleep(60)  # Wait 1 minute before retrying

def immediate_cleanup():
    """Perform immediate cleanup of all backup files."""
    print("🚨 IMMEDIATE CLEANUP - Deleting ALL backup files")
    
    backup_files = glob.glob("*_backup_*.xlsx")
    emergency_files = glob.glob("*_emergency_*.xlsx")
    
    total_size = 0
    deleted_count = 0
    
    # Calculate total size
    for f in backup_files + emergency_files:
        try:
            total_size += os.path.getsize(f)
        except:
            pass
    
    print(f"📁 Found {len(backup_files)} backup files")
    print(f"🚨 Found {len(emergency_files)} emergency files")
    print(f"💾 Total size: {total_size / (1024*1024*1024):.2f} GB")
    
    confirm = input("\n⚠️  Delete ALL backup files? (yes/no): ").strip().lower()
    if confirm != 'yes':
        print("❌ Cancelled")
        return
    
    # Delete all backup files
    for f in backup_files + emergency_files:
        try:
            os.remove(f)
            deleted_count += 1
            print(f"🗑️  Deleted: {f}")
        except Exception as e:
            print(f"❌ Could not delete {f}: {e}")
    
    print(f"\n✅ Deleted {deleted_count} files")
    print(f"💾 Freed up ~{total_size / (1024*1024*1024):.2f} GB")

def main():
    print("🧹 Backup File Auto-Cleaner")
    print("=" * 50)
    
    print("Options:")
    print("1. Immediate cleanup (delete ALL backup files now)")
    print("2. Continuous cleanup (keep cleaning while enricher runs)")
    print("3. Cancel")
    
    choice = input("\nEnter choice (1-3): ").strip()
    
    if choice == "1":
        immediate_cleanup()
    elif choice == "2":
        cleaner = BackgroundCleaner(max_backups_per_file=2, cleanup_interval=300)
        cleaner.run_continuous_cleanup()
    else:
        print("❌ Cancelled")

if __name__ == "__main__":
    main()