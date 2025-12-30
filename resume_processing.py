"""
Resume medicine processing - skips already processed medicines
"""

from medicine_enricher import MedicineEnricher
import pandas as pd
import logging

# Set up logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')

def check_progress(file_path):
    """Check current progress in the Excel file"""
    try:
        df = pd.read_excel(file_path)
        
        if 'processing_status' not in df.columns:
            print("❌ No processing_status column found - this file hasn't been processed yet")
            return None
        
        total = len(df)
        success = len(df[df['processing_status'] == 'SUCCESS'])
        failed = len(df[df['processing_status'].str.startswith('FAILED', na=False)])
        errors = len(df[df['processing_status'].str.startswith('ERROR', na=False)])
        pending = len(df[(df['processing_status'] == '') | (df['processing_status'].isna())])
        
        print(f"📊 Current Progress:")
        print(f"   Total medicines: {total:,}")
        print(f"   ✅ Successful: {success:,}")
        print(f"   ❌ Failed: {failed:,}")
        print(f"   ⚠️  Errors: {errors:,}")
        print(f"   ⏳ Pending: {pending:,}")
        print(f"   📈 Progress: {((success + failed + errors) / total * 100):.1f}%")
        
        return {
            'total': total,
            'success': success,
            'failed': failed,
            'errors': errors,
            'pending': pending,
            'df': df
        }
        
    except FileNotFoundError:
        print(f"❌ File not found: {file_path}")
        return None
    except Exception as e:
        print(f"❌ Error reading file: {str(e)}")
        return None

def resume_processing():
    """Resume processing from where it left off"""
    
    print("🔄 Medicine Processing Resumer")
    print("=" * 40)
    
    # Get file path
    file_path = input("Enter path to your enriched Excel file: ").strip().strip('"')
    
    if not file_path:
        file_path = "C:/Users/adesh.shetty/Downloads/medicine_normalized_enriched.xlsx"
        print(f"Using default path: {file_path}")
    
    # Check current progress
    progress = check_progress(file_path)
    if not progress:
        return
    
    if progress['pending'] == 0:
        print("🎉 All medicines have been processed!")
        return
    
    print(f"\n⏳ {progress['pending']:,} medicines still need processing")
    
    # Get API key
    api_key = input("\nEnter your Groq API key: ").strip()
    if not api_key:
        print("❌ API key required")
        return
    
    # Confirm resume
    confirm = input(f"\nResume processing {progress['pending']:,} medicines? (y/N): ").strip().lower()
    if confirm not in ['y', 'yes']:
        print("Operation cancelled")
        return
    
    # Important: Close Excel warning
    print("\n⚠️  IMPORTANT: Please close the Excel file if it's open!")
    input("Press Enter when Excel file is closed...")
    
    # Resume processing
    try:
        print(f"\n🚀 Resuming processing...")
        enricher = MedicineEnricher(api_key)
        result_df = enricher.enrich_excel(file_path, file_path)  # Same file for input/output
        
        print(f"\n✅ Processing completed!")
        
        # Show final summary
        final_success = len(result_df[result_df['processing_status'] == 'SUCCESS'])
        print(f"📊 Final Results:")
        print(f"   Total successful: {final_success:,}")
        print(f"   Success rate: {(final_success / progress['total'] * 100):.1f}%")
        
    except Exception as e:
        print(f"❌ Error during processing: {str(e)}")
        
        if "Permission denied" in str(e):
            print("\n💡 The Excel file is probably still open.")
            print("   Close Excel and try again.")

if __name__ == "__main__":
    resume_processing()