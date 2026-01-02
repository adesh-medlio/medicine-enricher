#!/usr/bin/env python3
"""
Test the Smart Backup System
"""

import pandas as pd
import os
from smart_backup_manager import SmartBackupManager

def test_smart_backups():
    """Test the smart backup system with a sample file."""
    
    print("🧪 Testing Smart Backup System")
    print("=" * 50)
    
    # Create a test Excel file
    test_file = "test_backup_demo.xlsx"
    df = pd.DataFrame({
        'name': ['Medicine A', 'Medicine B', 'Medicine C'],
        'manufacturer': ['Company 1', 'Company 2', 'Company 3']
    })
    df.to_excel(test_file, index=False)
    print(f"📄 Created test file: {test_file}")
    
    # Initialize backup manager (keep only 2 backups)
    backup_manager = SmartBackupManager(max_backups=2)
    
    # Simulate multiple saves (like during enrichment)
    for i in range(5):
        print(f"\n🔄 Simulation {i+1}: Updating file...")
        
        # Modify the file
        df_updated = df.copy()
        df_updated['update_count'] = i + 1
        df_updated.to_excel(test_file, index=False)
        
        # Create backup with smart cleanup
        backup_path = backup_manager.create_backup_with_cleanup(test_file)
        
        # Show current backups
        backups = backup_manager.list_backups(test_file)
        print(f"   📁 Current backups: {len(backups)}")
        for backup in backups:
            print(f"      • {os.path.basename(backup)}")
    
    print("\n" + "=" * 50)
    print("✅ Test complete!")
    print("Notice how old backups were automatically deleted")
    print("Only the 2 most recent backups are kept")
    
    # Cleanup test files
    try:
        os.remove(test_file)
        for backup in backup_manager.list_backups(test_file):
            os.remove(backup)
        print("\n🧹 Test files cleaned up")
    except:
        pass

if __name__ == "__main__":
    test_smart_backups()