"""
Merge backup files and choose the best one to continue processing
"""

import pandas as pd
import os
from datetime import datetime

def analyze_file(file_path):
    """Analyze a file and return progress statistics"""
    try:
        if not os.path.exists(file_path):
            return None
            
        df = pd.read_excel(file_path)
        
        if 'processing_status' not in df.columns:
            return {
                'file': file_path,
                'total': len(df),
                'success': 0,
                'failed': 0,
                'errors': 0,
                'pending': len(df),
                'valid': False,
                'error': 'No processing_status column'
            }
        
        total = len(df)
        success = len(df[df['processing_status'] == 'SUCCESS'])
        failed = len(df[df['processing_status'].str.startswith('FAILED', na=False)])
        errors = len(df[df['processing_status'].str.startswith('ERROR', na=False)])
        pending = len(df[(df['processing_status'] == '') | (df['processing_status'].isna())])
        
        # Get file modification time
        mod_time = os.path.getmtime(file_path)
        mod_time_str = datetime.fromtimestamp(mod_time).strftime('%Y-%m-%d %H:%M:%S')
        
        return {
            'file': file_path,
            'total': total,
            'success': success,
            'failed': failed,
            'errors': errors,
            'pending': pending,
            'progress_pct': (success / total * 100) if total > 0 else 0,
            'modified': mod_time_str,
            'valid': True,
            'df': df
        }
        
    except Exception as e:
        return {
            'file': file_path,
            'valid': False,
            'error': str(e)
        }

def find_backup_files():
    """Find all potential backup files"""
    current_dir = os.getcwd()
    downloads_dir = "C:/Users/adesh.shetty/Downloads"
    
    potential_files = []
    
    # Look in current directory
    for file in os.listdir(current_dir):
        if 'enriched' in file.lower() and file.endswith('.xlsx'):
            potential_files.append(os.path.join(current_dir, file))
    
    # Look in downloads directory
    if os.path.exists(downloads_dir):
        for file in os.listdir(downloads_dir):
            if 'enriched' in file.lower() and file.endswith('.xlsx'):
                potential_files.append(os.path.join(downloads_dir, file))
    
    return potential_files

def merge_files(file1_info, file2_info):
    """Merge two files, keeping the best data from each"""
    
    print(f"\n🔄 Merging files...")
    print(f"   File 1: {file1_info['success']} successful")
    print(f"   File 2: {file2_info['success']} successful")
    
    df1 = file1_info['df']
    df2 = file2_info['df']
    
    # Start with the file that has more successful entries
    if file1_info['success'] >= file2_info['success']:
        base_df = df1.copy()
        other_df = df2
        print(f"   Using File 1 as base")
    else:
        base_df = df2.copy()
        other_df = df1
        print(f"   Using File 2 as base")
    
    # Merge successful entries from the other file
    merged_count = 0
    for idx in other_df.index:
        if other_df.at[idx, 'processing_status'] == 'SUCCESS':
            # If base doesn't have this as success, copy it over
            if base_df.at[idx, 'processing_status'] != 'SUCCESS':
                base_df.at[idx, 'salt_composition'] = other_df.at[idx, 'salt_composition']
                base_df.at[idx, 'medicine_description'] = other_df.at[idx, 'medicine_description']
                base_df.at[idx, 'source_url'] = other_df.at[idx, 'source_url']
                base_df.at[idx, 'processing_status'] = 'SUCCESS'
                merged_count += 1
    
    print(f"   Merged {merged_count} additional successful entries")
    
    return base_df

def main():
    print("🔍 Backup File Merger & Analyzer")
    print("=" * 50)
    
    # Find all potential files
    files = find_backup_files()
    
    if not files:
        print("❌ No enriched Excel files found!")
        return
    
    print(f"📁 Found {len(files)} potential files:")
    
    # Analyze each file
    file_analyses = []
    for i, file_path in enumerate(files, 1):
        print(f"\n{i}. Analyzing: {os.path.basename(file_path)}")
        analysis = analyze_file(file_path)
        
        if analysis and analysis['valid']:
            print(f"   ✅ Total: {analysis['total']:,}")
            print(f"   ✅ Success: {analysis['success']:,}")
            print(f"   ❌ Failed: {analysis['failed']:,}")
            print(f"   ⚠️  Errors: {analysis['errors']:,}")
            print(f"   ⏳ Pending: {analysis['pending']:,}")
            print(f"   📈 Progress: {analysis['progress_pct']:.1f}%")
            print(f"   🕒 Modified: {analysis['modified']}")
            file_analyses.append(analysis)
        else:
            print(f"   ❌ Error: {analysis.get('error', 'Unknown error')}")
    
    if len(file_analyses) < 2:
        if len(file_analyses) == 1:
            print(f"\n✅ Only one valid file found. Use this one:")
            print(f"   {file_analyses[0]['file']}")
        else:
            print(f"\n❌ No valid files found to work with.")
        return
    
    # Sort by success count
    file_analyses.sort(key=lambda x: x['success'], reverse=True)
    
    print(f"\n🏆 Best files ranked by progress:")
    for i, analysis in enumerate(file_analyses[:3], 1):  # Show top 3
        print(f"   {i}. {os.path.basename(analysis['file'])}: {analysis['success']:,} successful ({analysis['progress_pct']:.1f}%)")
    
    # Ask user what to do
    print(f"\n🤔 What would you like to do?")
    print(f"   1. Use the best file (most successful entries)")
    print(f"   2. Merge the top 2 files (combine their successful entries)")
    print(f"   3. Choose a specific file")
    print(f"   4. Show detailed comparison")
    
    choice = input("Choose (1/2/3/4): ").strip()
    
    if choice == '1':
        # Use the best file
        best_file = file_analyses[0]
        print(f"\n✅ Using best file: {best_file['file']}")
        print(f"   Continue processing with: python resume_processing.py")
        print(f"   Use this path: {best_file['file']}")
        
    elif choice == '2':
        # Merge top 2 files
        if len(file_analyses) < 2:
            print("❌ Need at least 2 files to merge")
            return
            
        merged_df = merge_files(file_analyses[0], file_analyses[1])
        
        # Save merged file
        merged_path = "medicine_normalized_enriched_merged.xlsx"
        merged_df.to_excel(merged_path, index=False)
        
        success_count = len(merged_df[merged_df['processing_status'] == 'SUCCESS'])
        print(f"\n✅ Merged file created: {merged_path}")
        print(f"   Total successful entries: {success_count:,}")
        print(f"   Continue processing with: python resume_processing.py")
        print(f"   Use this path: {merged_path}")
        
    elif choice == '3':
        # Choose specific file
        print(f"\nAvailable files:")
        for i, analysis in enumerate(file_analyses, 1):
            print(f"   {i}. {os.path.basename(analysis['file'])} ({analysis['success']:,} successful)")
        
        try:
            file_choice = int(input("Choose file number: ")) - 1
            if 0 <= file_choice < len(file_analyses):
                chosen_file = file_analyses[file_choice]
                print(f"\n✅ Using: {chosen_file['file']}")
                print(f"   Continue processing with: python resume_processing.py")
            else:
                print("❌ Invalid choice")
        except ValueError:
            print("❌ Invalid input")
            
    elif choice == '4':
        # Detailed comparison
        print(f"\n📊 Detailed Comparison:")
        print("-" * 80)
        print(f"{'File':<30} {'Success':<8} {'Failed':<8} {'Errors':<8} {'Pending':<10} {'Progress':<10}")
        print("-" * 80)
        
        for analysis in file_analyses:
            filename = os.path.basename(analysis['file'])[:28]
            print(f"{filename:<30} {analysis['success']:<8} {analysis['failed']:<8} {analysis['errors']:<8} {analysis['pending']:<10} {analysis['progress_pct']:<10.1f}%")
    
    print(f"\n💡 Recommendation:")
    print(f"   • If files have different successful medicines → Merge them")
    print(f"   • If one file is clearly better → Use the best one")
    print(f"   • Always backup your files before continuing!")

if __name__ == "__main__":
    main()