#!/usr/bin/env python3
"""
Smart Backup Manager - Automatically manages backup files
Keeps only the most recent backups and cleans up old ones
"""

import os
import glob
import shutil
from datetime import datetime
import pandas as pd

class SmartBackupManager:
    """Manages backup files intelligently - keeps only recent ones."""
    
    def __init__(self, max_backups=3):
        """
        Initialize backup manager.
        
        Args:
            max_backups: Maximum number of backup files to keep (default: 3)
        """
        self.max_backups = max_backups
    
    def create_backup_with_cleanup(self, file_path):
        """
        Create a backup and clean up old ones.
        
        Args:
            file_path: Path to the file to backup
            
        Returns:
            str: Path to the created backup file
        """
        if not os.path.exists(file_path):
            return None
            
        # Create new backup
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        backup_path = file_path.replace('.xlsx', f'_backup_{timestamp}.xlsx')
        
        try:
            shutil.copy2(file_path, backup_path)
            print(f"📁 Backup created: {os.path.basename(backup_path)}")
            
            # Clean up old backups
            self.cleanup_old_backups(file_path)
            
            return backup_path
            
        except Exception as e:
            print(f"❌ Backup creation failed: {e}")
            return None
    
    def cleanup_old_backups(self, original_file_path):
        """
        Remove old backup files, keeping only the most recent ones.
        
        Args:
            original_file_path: Path to the original file
        """
        try:
            # Get base filename without extension
            base_name = os.path.splitext(original_file_path)[0]
            directory = os.path.dirname(original_file_path) or '.'
            
            # Find all backup files for this base name
            backup_pattern = f"{base_name}_backup_*.xlsx"
            backup_files = glob.glob(os.path.join(directory, os.path.basename(backup_pattern)))
            
            if len(backup_files) <= self.max_backups:
                return  # No cleanup needed
            
            # Sort by modification time (newest first)
            backup_files.sort(key=os.path.getmtime, reverse=True)
            
            # Keep only the most recent backups
            files_to_keep = backup_files[:self.max_backups]
            files_to_delete = backup_files[self.max_backups:]
            
            # Delete old backup files
            deleted_count = 0
            for old_backup in files_to_delete:
                try:
                    os.remove(old_backup)
                    deleted_count += 1
                    print(f"🗑️  Deleted old backup: {os.path.basename(old_backup)}")
                except Exception as e:
                    print(f"⚠️  Could not delete {os.path.basename(old_backup)}: {e}")
            
            if deleted_count > 0:
                print(f"✅ Cleaned up {deleted_count} old backup files")
                print(f"📁 Keeping {len(files_to_keep)} most recent backups")
                
        except Exception as e:
            print(f"⚠️  Backup cleanup failed: {e}")
    
    def get_latest_backup(self, original_file_path):
        """
        Get the path to the most recent backup file.
        
        Args:
            original_file_path: Path to the original file
            
        Returns:
            str: Path to the latest backup file, or None if no backups exist
        """
        try:
            base_name = os.path.splitext(original_file_path)[0]
            directory = os.path.dirname(original_file_path) or '.'
            
            backup_pattern = f"{base_name}_backup_*.xlsx"
            backup_files = glob.glob(os.path.join(directory, os.path.basename(backup_pattern)))
            
            if not backup_files:
                return None
            
            # Return the most recent backup
            latest_backup = max(backup_files, key=os.path.getmtime)
            return latest_backup
            
        except Exception as e:
            print(f"⚠️  Could not find latest backup: {e}")
            return None
    
    def list_backups(self, original_file_path):
        """
        List all backup files for a given original file.
        
        Args:
            original_file_path: Path to the original file
            
        Returns:
            list: List of backup file paths, sorted by creation time (newest first)
        """
        try:
            base_name = os.path.splitext(original_file_path)[0]
            directory = os.path.dirname(original_file_path) or '.'
            
            backup_pattern = f"{base_name}_backup_*.xlsx"
            backup_files = glob.glob(os.path.join(directory, os.path.basename(backup_pattern)))
            
            # Sort by modification time (newest first)
            backup_files.sort(key=os.path.getmtime, reverse=True)
            
            return backup_files
            
        except Exception as e:
            print(f"⚠️  Could not list backups: {e}")
            return []

def clean_all_backups_in_directory(directory=".", max_backups=3):
    """
    Clean up all backup files in a directory, keeping only recent ones.
    
    Args:
        directory: Directory to clean (default: current directory)
        max_backups: Maximum backups to keep per file (default: 3)
    """
    manager = SmartBackupManager(max_backups)
    
    # Find all Excel files that might have backups
    excel_files = glob.glob(os.path.join(directory, "*.xlsx"))
    
    # Filter out backup files themselves
    original_files = [f for f in excel_files if '_backup_' not in f and '_emergency_' not in f]
    
    print(f"🧹 Cleaning backup files in: {os.path.abspath(directory)}")
    print(f"📁 Keeping maximum {max_backups} backups per file")
    
    total_cleaned = 0
    for original_file in original_files:
        print(f"\n📄 Processing: {os.path.basename(original_file)}")
        
        backups_before = len(manager.list_backups(original_file))
        if backups_before > 0:
            manager.cleanup_old_backups(original_file)
            backups_after = len(manager.list_backups(original_file))
            cleaned = backups_before - backups_after
            total_cleaned += cleaned
        else:
            print(f"   No backup files found")
    
    print(f"\n✅ Cleanup complete! Removed {total_cleaned} old backup files")

if __name__ == "__main__":
    print("🧹 Smart Backup Manager")
    print("=" * 50)
    
    # Clean up all backup files in current directory
    clean_all_backups_in_directory(".", max_backups=3)
    
    print("\n" + "=" * 50)
    print("💡 Usage in your code:")
    print("""
from smart_backup_manager import SmartBackupManager

# Create manager (keeps 3 most recent backups)
backup_manager = SmartBackupManager(max_backups=3)

# Create backup with automatic cleanup
backup_path = backup_manager.create_backup_with_cleanup("your_file.xlsx")

# Get latest backup
latest = backup_manager.get_latest_backup("your_file.xlsx")
""")