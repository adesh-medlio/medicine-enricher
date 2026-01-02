#!/usr/bin/env python3
"""
Run enhanced medicine enricher with custom file path + Auto Backup Cleanup
Automatically cleans backup files while enricher is running
"""

import os
import sys
import threading
import time
import glob
from datetime import datetime
from medicine_enricher import MedicineEnricher

class BackupCleaner:
    """Cleans backup files automatically while enricher runs."""
    
    def __init__(self, target_directory, max_backups=2, cleanup_interval=300):
        self.target_directory = target_directory
        self.max_backups = max_backups
        self.cleanup_interval = cleanup_interval
        self.running = True
        self.thread = None
        
    def start_cleanup(self):
        """Start the cleanup thread."""
        self.running = True
        self.thread = threading.Thread(target=self._cleanup_loop, daemon=True)
        self.thread.start()
        print(f"🧹 Auto-cleanup started (keeps {self.max_backups} backups, cleans every {self.cleanup_interval//60} min)")
        
    def stop_cleanup(self):
        """Stop the cleanup thread."""
        self.running = False
        if self.thread:
            self.thread.join(timeout=5)
        
    def _cleanup_loop(self):
        """Main cleanup loop running in background."""
        while self.running:
            try:
                self._perform_cleanup()
                time.sleep(self.cleanup_interval)
            except Exception as e:
                print(f"⚠️  Cleanup error: {e}")
                time.sleep(60)  # Wait 1 minute before retrying
                
    def _perform_cleanup(self):
        """Perform the actual cleanup."""
        try:
            # Change to target directory for cleanup
            original_dir = os.getcwd()
            os.chdir(self.target_directory)
            
            # Find backup files
            backup_files = glob.glob("*_backup_*.xlsx")
            emergency_files = glob.glob("*_emergency_*.xlsx")
            
            if not backup_files and not emergency_files:
                return
            
            # Group backup files by base name
            backup_groups = {}
            for backup_file in backup_files:
                base_name = backup_file.split('_backup_')[0]
                if base_name not in backup_groups:
                    backup_groups[base_name] = []
                backup_groups[base_name].append(backup_file)
            
            deleted_count = 0
            
            # Clean up each group
            for base_name, files in backup_groups.items():
                if len(files) > self.max_backups:
                    # Sort by modification time (newest first)
                    files.sort(key=os.path.getmtime, reverse=True)
                    
                    # Delete old backups
                    files_to_delete = files[self.max_backups:]
                    for file_to_delete in files_to_delete:
                        try:
                            os.remove(file_to_delete)
                            deleted_count += 1
                            print(f"🗑️  Auto-deleted old backup: {file_to_delete}")
                        except Exception as e:
                            print(f"⚠️  Could not delete {file_to_delete}: {e}")
            
            # Delete emergency files older than 30 minutes
            for emergency_file in emergency_files:
                try:
                    file_age = time.time() - os.path.getmtime(emergency_file)
                    if file_age > 1800:  # 30 minutes
                        os.remove(emergency_file)
                        deleted_count += 1
                        print(f"🗑️  Auto-deleted old emergency: {emergency_file}")
                except Exception as e:
                    print(f"⚠️  Could not delete {emergency_file}: {e}")
            
            if deleted_count > 0:
                remaining = len(glob.glob("*_backup_*.xlsx")) + len(glob.glob("*_emergency_*.xlsx"))
                print(f"✅ Auto-cleanup: Removed {deleted_count} files, {remaining} remaining")
                
        except Exception as e:
            print(f"❌ Cleanup error: {e}")
        finally:
            # Return to original directory
            try:
                os.chdir(original_dir)
            except:
                pass

def main():
    print("🚀 Enhanced Medicine Enricher - Auto Cleanup Edition")
    print("=" * 60)
    
    # Get file path from user
    if len(sys.argv) > 1:
        input_file = sys.argv[1]
        print(f"📥 Using file from command line: {input_file}")
    else:
        input_file = input("Enter the full path to your Excel file: ").strip()
        # Remove quotes if user added them
        input_file = input_file.strip('"').strip("'")
    
    # Check if file exists
    if not os.path.exists(input_file):
        print(f"❌ File not found: {input_file}")
        return
    
    # Set output file (same directory as input)
    input_dir = os.path.dirname(input_file)
    input_name = os.path.basename(input_file)
    output_name = input_name.replace('.xlsx', '_enriched_with_manufacturer.xlsx')
    output_file = os.path.join(input_dir, output_name)
    
    print(f"📄 Input file: {input_file}")
    print(f"📤 Output file: {output_file}")
    print(f"📁 Working directory: {input_dir}")
    
    from config import get_groq_api_key
    
    # Get API key from environment
    GROQ_API_KEY = get_groq_api_key()
    if not GROQ_API_KEY:
        return
    
    print(f"🔑 API Key: {GROQ_API_KEY[:20]}...")
    
    # Quick file check
    try:
        import pandas as pd
        df = pd.read_excel(input_file, nrows=3)
        print(f"\n📊 File info:")
        print(f"   - Columns: {list(df.columns)}")
        print(f"   - Has 'name' column: {'name' in df.columns}")
        print(f"   - Has 'manufacturer_name' column: {'manufacturer_name' in df.columns}")
        
        if 'manufacturer_name' in df.columns:
            print("✅ Great! Manufacturer column found - searches will be more accurate")
        else:
            print("⚠️  No manufacturer column - will use medicine name only")
        
    except Exception as e:
        print(f"⚠️  Could not preview file: {str(e)}")
    
    # Show cleanup settings
    print(f"\n🧹 Auto-cleanup settings:")
    print(f"   - Keeps 2 most recent backups per file")
    print(f"   - Cleans up every 5 minutes")
    print(f"   - Removes emergency files older than 30 minutes")
    
    # Confirm before starting
    confirm = input(f"\nStart enrichment with auto-cleanup? (y/n): ").strip().lower()
    if confirm not in ['y', 'yes']:
        print("👋 Cancelled")
        return
    
    # Initialize backup cleaner
    cleaner = BackupCleaner(input_dir, max_backups=2, cleanup_interval=300)
    
    try:
        # Start auto-cleanup
        cleaner.start_cleanup()
        
        # Run enrichment
        print(f"\n🔄 Starting enrichment with auto-cleanup...")
        print(f"💡 This will use manufacturer names for more accurate searches!")
        print(f"🧹 Backup files will be automatically cleaned while running")
        
        enricher = MedicineEnricher(GROQ_API_KEY)
        result_df = enricher.enrich_excel(input_file, output_file)
        
        print(f"\n✅ Enrichment completed successfully!")
        print(f"📄 Results saved to: {output_file}")
        
        # Show summary
        if result_df is not None:
            success_count = len(result_df[result_df['processing_status'] == 'SUCCESS'])
            total_count = len(result_df)
            print(f"📊 Success rate: {success_count}/{total_count}")
            
            # Show warnings if any
            if 'similarity_warning' in result_df.columns:
                warnings = result_df[result_df['similarity_warning'] != '']
                if len(warnings) > 0:
                    print(f"⚠️  {len(warnings)} medicines have similarity warnings (check output file)")
            
            if 'manufacturer_warning' in result_df.columns:
                mfg_warnings = result_df[result_df['manufacturer_warning'] != '']
                if len(mfg_warnings) > 0:
                    print(f"⚠️  {len(mfg_warnings)} medicines have manufacturer warnings (check output file)")
        
    except KeyboardInterrupt:
        print(f"\n🛑 Enrichment interrupted by user")
        print(f"💡 Check for emergency backup files in: {input_dir}")
    except Exception as e:
        print(f"\n❌ Enrichment failed: {str(e)}")
        print(f"💡 Check for emergency backup files in: {input_dir}")
    finally:
        # Stop cleanup thread
        print(f"\n🧹 Stopping auto-cleanup...")
        cleaner.stop_cleanup()
        
        # Final cleanup
        print(f"🧹 Performing final cleanup...")
        cleaner._perform_cleanup()
        
        print(f"✅ Auto-cleanup stopped")

if __name__ == "__main__":
    main()