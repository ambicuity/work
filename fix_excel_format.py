#!/usr/bin/env python3
"""
Update existing Excel files to match the problem statement format exactly
"""

import pandas as pd
import os
from pathlib import Path

def convert_excel_file_to_correct_format(filename):
    """Convert a single Excel file to the correct format"""
    try:
        # Load the existing file
        df = pd.read_excel(filename)
        print(f"\nProcessing: {filename}")
        print(f"Original shape: {df.shape}")
        print(f"Original columns: {list(df.columns)}")
        
        # Create new DataFrame with correct column names and order
        new_df = pd.DataFrame()
        
        # Map old columns to new columns
        column_mapping = {
            'Categories': 'Category',
            'Organization Name': 'Organization Name',  # Same
            'Org URL': 'Organization Link', 
            'Image URL': 'Logo Link',
            'Description': 'Description',  # Same
            'Email': 'Email',  # Same
            'Phone': 'Phone Number',
            'LinkedIn': 'Linkedin Link',
            'Instagram': 'Instagram Link',
            'Facebook': 'Facebook Link',
            'Twitter': 'Twitter Link'
        }
        
        # Problem statement column order
        target_columns = [
            'Category', 'Organization Name', 'Organization Link', 'Logo Link', 
            'Description', 'Email', 'Phone Number', 'Linkedin Link', 
            'Instagram Link', 'Facebook Link', 'Twitter Link', 'Youtube Link', 'Tiktok Link'
        ]
        
        # Create new dataframe with correct columns
        for target_col in target_columns:
            if target_col in ['Youtube Link', 'Tiktok Link']:
                # Add missing columns as empty
                new_df[target_col] = ''
            else:
                # Find the corresponding old column
                old_col = None
                for old, new in column_mapping.items():
                    if new == target_col:
                        old_col = old
                        break
                
                if old_col and old_col in df.columns:
                    new_df[target_col] = df[old_col]
                else:
                    new_df[target_col] = ''  # Default to empty if not found
        
        # Clean up data - fill NaN with empty strings
        new_df = new_df.fillna('')
        
        print(f"New shape: {new_df.shape}")
        print(f"New columns: {list(new_df.columns)}")
        
        # Save the updated file
        with pd.ExcelWriter(filename, engine='openpyxl') as writer:
            new_df.to_excel(writer, sheet_name='Organizations', index=False)
            
            # Auto-adjust column widths
            worksheet = writer.sheets['Organizations']
            for column in worksheet.columns:
                max_length = 0
                column_letter = column[0].column_letter
                
                for cell in column:
                    try:
                        if len(str(cell.value)) > max_length:
                            max_length = len(str(cell.value))
                    except:
                        pass
                
                adjusted_width = min(max_length + 2, 50)
                worksheet.column_dimensions[column_letter].width = adjusted_width
        
        print(f"✅ Successfully updated: {filename}")
        
        # Show field completeness
        print("Field completeness:")
        for col in new_df.columns:
            non_empty = sum(1 for val in new_df[col] if val and str(val).strip() != '')
            percentage = (non_empty / len(new_df)) * 100
            print(f'  {col}: {non_empty}/{len(new_df)} ({percentage:.1f}%)')
            
        return True
        
    except Exception as e:
        print(f"❌ Error processing {filename}: {e}")
        return False

def main():
    """Update all Excel files to correct format"""
    print("🔄 Converting all Excel files to match problem statement format...")
    
    # Find all organization Excel files
    excel_files = [f for f in os.listdir('.') if f.endswith('_Organizations.xlsx')]
    
    print(f"Found {len(excel_files)} files to update:")
    for f in excel_files:
        print(f"  - {f}")
    
    success_count = 0
    
    for filename in excel_files:
        if convert_excel_file_to_correct_format(filename):
            success_count += 1
    
    print(f"\n📊 SUMMARY:")
    print(f"✅ Successfully updated: {success_count}/{len(excel_files)} files")
    
    if success_count == len(excel_files):
        print("🎉 All files have been updated to match the problem statement format!")
        print("\nFormat now includes:")
        print("✅ Category (instead of Categories)")
        print("✅ Organization Link (instead of Org URL)")  
        print("✅ Logo Link (instead of Image URL)")
        print("✅ Phone Number (instead of Phone)")
        print("✅ Linkedin Link (instead of LinkedIn)")
        print("✅ Youtube Link (added)")
        print("✅ Tiktok Link (added)")
        print("❌ Website column (removed as not in problem statement)")
    
    return success_count == len(excel_files)

if __name__ == "__main__":
    main()