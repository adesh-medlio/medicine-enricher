#!/usr/bin/env python3
"""
Safe Excel Saver - Prevents file corruption during saves
Now with smart backup management!
"""

import pandas as pd
import os
import tempfile
import shutil
import time
from datetime import datetime
from smart_backup_manager import SmartBackupManager

class SafeExcelSaver:
    """A safe Excel file saver that prevents corruption."""
    
    def __init__(self, output_path, max_backups=3):
        self.output_path = output_path
        self.temp_dir = tempfile.mkdtemp()
        self.backup_manager = SmartBackupManager(max_backups)
        
    def safe_save(self, df, progress_count=None):
        """
        Safely save DataFrame to Excel with corruption protection.
        
        Args:
            df: DataFrame to save
            progress_count: Optional progress counter for backup naming
        
        Returns:
            bool: True if save successful, False otherwise
        """
        try:
            # Create temporary file first
            temp_filename = f"temp_save_{int(time.time())}.xlsx"
            temp_path = os.path.join(self.temp_dir, temp_filename)
            
            # Save to temporary location first
            df.to_excel(temp_path, index=False)
            
            # Verify the temporary file is valid
            try:
                test_df = pd.read_excel(temp_path)
                if len(test_df) != len(df):
                    raise ValueError("Saved file has different row count")
            except Exception as e:
                print(f"❌ Temporary file validation failed: {e}")
                return False
            
            # Create backup of existing file if it exists (with smart cleanup)
            if os.path.exists(self.output_path):
                backup_path = self.backup_manager.create_backup_with_cleanup(self.output_path)
                if backup_path:
                    print(f"📁 Smart backup created: {os.path.basename(backup_path)}")
                else:
                    print("⚠️  Could not create backup")
            
            # Atomic move from temp to final location
            shutil.move(temp_path, self.output_path)
            print(f"✅ File saved successfully: {self.output_path}")
            
            return True
            
        except Exception as e:
            print(f"❌ Save failed: {e}")
            
            # Try to save to backup location
            if progress_count:
                backup_path = self.output_path.replace('.xlsx', f'_emergency_backup_{progress_count}.xlsx')
                try:
                    df.to_excel(backup_path, index=False)
                    print(f"💾 Emergency backup saved: {backup_path}")
                    return True
                except Exception as backup_error:
                    print(f"❌ Emergency backup also failed: {backup_error}")
            
            return False
    
    def cleanup(self):
        """Clean up temporary directory."""
        try:
            shutil.rmtree(self.temp_dir)
        except:
            pass

def patch_medicine_enricher():
    """Create a patched version of the save mechanism."""
    
    patch_code = '''
# Add this to your medicine_enricher.py imports:
from safe_excel_saver import SafeExcelSaver

# Replace the save logic in enrich_excel method with:
def enrich_excel_safe(self, input_path, output_path):
    """Enhanced version with safe saving."""
    
    # ... (existing code until the save parts) ...
    
    # Initialize safe saver
    saver = SafeExcelSaver(output_path)
    
    try:
        # ... (existing processing code) ...
        
        # Replace the progress save section:
        if processed_count % 10 == 0:
            success = saver.safe_save(df, processed_count)
            if success:
                logger.info(f"Progress saved: {processed_count}/{unprocessed_count} processed")
            else:
                logger.warning(f"Could not save progress at {processed_count}")
        
        # Replace the final save section:
        final_success = saver.safe_save(df)
        if final_success:
            logger.info(f"Enrichment complete. Results saved to: {output_path}")
        else:
            logger.error("Final save failed - check backup files")
            
    finally:
        saver.cleanup()
    
    return df
'''
    
    with open('medicine_enricher_patch.py', 'w') as f:
        f.write(patch_code)
    
    print("📝 Patch file created: medicine_enricher_patch.py")

if __name__ == "__main__":
    print("🛡️ Safe Excel Saver utility created")
    print("This prevents file corruption during saves by:")
    print("  • Using temporary files")
    print("  • Validating saves before committing")
    print("  • Creating automatic backups")
    print("  • Atomic file operations")
    
    patch_medicine_enricher()