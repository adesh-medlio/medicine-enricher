"""
Check where output files are being stored
"""

import os
from pathlib import Path

def show_output_locations():
    """Show where output files will be stored"""
    
    print("📁 Output File Locations")
    print("=" * 50)
    
    # Current working directory
    current_dir = os.getcwd()
    print(f"Current working directory: {current_dir}")
    
    # Example input file paths and their corresponding outputs
    example_inputs = [
        "C:/Users/adesh.shetty/Downloads/medicine_normalized.xlsx",
        "medicine_data.xlsx",
        "./data/medicines.xlsx"
    ]
    
    print(f"\n📋 Output File Examples:")
    print("-" * 30)
    
    for input_path in example_inputs:
        # This is how the code generates output paths
        base_name = os.path.splitext(input_path)[0]
        output_path = f"{base_name}_enriched.xlsx"
        
        print(f"Input:  {input_path}")
        print(f"Output: {output_path}")
        print(f"Full path: {os.path.abspath(output_path) if not os.path.isabs(output_path) else output_path}")
        print()
    
    # Check for existing output files
    print(f"🔍 Looking for existing output files in current directory...")
    
    enriched_files = []
    for file in os.listdir(current_dir):
        if file.endswith('_enriched.xlsx'):
            enriched_files.append(file)
            file_path = os.path.join(current_dir, file)
            file_size = os.path.getsize(file_path)
            mod_time = os.path.getmtime(file_path)
            
            from datetime import datetime
            mod_time_str = datetime.fromtimestamp(mod_time).strftime('%Y-%m-%d %H:%M:%S')
            
            print(f"✅ Found: {file}")
            print(f"   Size: {file_size:,} bytes")
            print(f"   Modified: {mod_time_str}")
            print(f"   Full path: {file_path}")
            print()
    
    if not enriched_files:
        print("   No enriched files found yet.")
    
    print(f"\n💡 Key Points:")
    print(f"   • Output files are saved in the SAME FOLDER as your input file")
    print(f"   • They get '_enriched' added to the filename")
    print(f"   • If input is 'medicine_data.xlsx', output is 'medicine_data_enriched.xlsx'")
    print(f"   • Progress is saved every 10 medicines, so you can resume if interrupted")

def find_your_output_file():
    """Help find your specific output file"""
    
    print(f"\n🔍 Find Your Output File")
    print("=" * 30)
    
    input_file = input("What was your input file name? (e.g., medicine_normalized.xlsx): ").strip()
    
    if input_file:
        # Generate expected output name
        base_name = os.path.splitext(input_file)[0]
        expected_output = f"{base_name}_enriched.xlsx"
        
        print(f"\n📄 Your output file should be named: {expected_output}")
        
        # Check if it exists in current directory
        if os.path.exists(expected_output):
            full_path = os.path.abspath(expected_output)
            file_size = os.path.getsize(expected_output)
            
            print(f"✅ Found your file!")
            print(f"   Location: {full_path}")
            print(f"   Size: {file_size:,} bytes")
        else:
            # Check if input file path was absolute
            if os.path.isabs(input_file):
                input_dir = os.path.dirname(input_file)
                expected_in_input_dir = os.path.join(input_dir, f"{os.path.splitext(os.path.basename(input_file))[0]}_enriched.xlsx")
                
                print(f"   Not found in current directory.")
                print(f"   Check this location: {expected_in_input_dir}")
            else:
                print(f"   File not found. It may still be processing or there was an error.")

if __name__ == "__main__":
    show_output_locations()
    
    choice = input("\nWould you like help finding your specific output file? (y/n): ").strip().lower()
    if choice in ['y', 'yes']:
        find_your_output_file()