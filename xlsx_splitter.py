import pandas as pd
import os
import math
import sys
from pathlib import Path

def split_xlsx_file(input_file, output_prefix="part", num_parts=3):
    """
    Split an Excel file into specified number of parts.
    
    Args:
        input_file (str): Path to the input Excel file
        output_prefix (str): Prefix for output files (default: "part")
        num_parts (int): Number of parts to split into (default: 3)
    
    Returns:
        list: List of created file paths
    """
    try:
        # Read the Excel file
        print(f"Reading Excel file: {input_file}")
        df = pd.read_excel(input_file)
        
        total_rows = len(df)
        print(f"Total rows: {total_rows}")
        
        if total_rows == 0:
            print("Error: The Excel file is empty")
            return []
        
        # Calculate rows per part
        rows_per_part = math.ceil(total_rows / num_parts)
        print(f"Rows per part: {rows_per_part}")
        
        # Get the directory and filename without extension
        input_path = Path(input_file)
        output_dir = input_path.parent
        file_stem = input_path.stem
        
        created_files = []
        
        # Split the dataframe and save parts
        for i in range(num_parts):
            start_idx = i * rows_per_part
            end_idx = min((i + 1) * rows_per_part, total_rows)
            
            # Skip if no rows for this part
            if start_idx >= total_rows:
                break
            
            # Extract the part
            part_df = df.iloc[start_idx:end_idx]
            
            # Create output filename
            output_filename = f"{output_prefix}_{i+1}_{file_stem}.xlsx"
            output_path = output_dir / output_filename
            
            # Save the part
            part_df.to_excel(output_path, index=False)
            created_files.append(str(output_path))
            
            print(f"Created {output_filename} with {len(part_df)} rows (rows {start_idx+1}-{end_idx})")
        
        print(f"\nSuccessfully split into {len(created_files)} files:")
        for file_path in created_files:
            print(f"  - {file_path}")
        
        return created_files
        
    except FileNotFoundError:
        print(f"Error: File '{input_file}' not found")
        return []
    except Exception as e:
        print(f"Error processing file: {str(e)}")
        return []

def main():
    """
    Main function with example usage and user input.
    """
    print("Excel File Splitter")
    print("=" * 50)
    
    # Check if file path provided as command line argument
    if len(sys.argv) > 1:
        input_file = sys.argv[1]
        num_parts = int(sys.argv[2]) if len(sys.argv) > 2 else 3
        output_prefix = sys.argv[3] if len(sys.argv) > 3 else "part"
        
        print(f"Using command line arguments:")
        print(f"  File: {input_file}")
        print(f"  Parts: {num_parts}")
        print(f"  Prefix: {output_prefix}")
        
    else:
        # Get input file from user
        input_file = input("Enter the path to your Excel file: ").strip()
        
        # Remove quotes if present
        if input_file.startswith('"') and input_file.endswith('"'):
            input_file = input_file[1:-1]
        
        # Get number of parts (default to 3)
        try:
            num_parts = input("Enter number of parts (default 3): ").strip()
            num_parts = int(num_parts) if num_parts else 3
            
            if num_parts <= 0:
                print("Error: Number of parts must be positive")
                return
                
        except ValueError:
            print("Error: Invalid number entered, using default (3)")
            num_parts = 3
        
        # Get output prefix
        output_prefix = input("Enter output file prefix (default 'part'): ").strip()
        if not output_prefix:
            output_prefix = "part"
    
    # Check if file exists
    if not os.path.exists(input_file):
        print(f"Error: File '{input_file}' does not exist")
        return
    
    print(f"\nSplitting '{input_file}' into {num_parts} parts...")
    
    # Split the file
    created_files = split_xlsx_file(input_file, output_prefix, num_parts)
    
    if created_files:
        print(f"\n✅ Successfully created {len(created_files)} files!")
    else:
        print("\n❌ Failed to split the file")

if __name__ == "__main__":
    main()