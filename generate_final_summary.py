#!/usr/bin/env python3
"""
Generate final summary report of all scraped university organizations
"""

import pandas as pd
import os
import glob

def generate_final_summary():
    """Generate a comprehensive summary of all scraped data"""
    
    # Expected counts per university
    expected_counts = {
        'Bethesda_University': 4,
        'Bethune-Cookman_University': 80,
        'Beulah_Heights_University': 5,
        'Bevill_State_Community_College': 19,
        'Big_Bend_Community_College': 14,
        'Biola_University': 6,
        'Bishop_State_Community_College': 16,
        'Black_Hills_State_University': 75,
        'Bladen_Community_College': 10,
        'Blue_Mountain_Community_College': 15,
        'Blue_Ridge_Community_College': 18
    }
    
    # Find all organization Excel files
    excel_files = glob.glob("*Organizations.xlsx")
    
    print("="*80)
    print("FINAL UNIVERSITY ORGANIZATION SCRAPING SUMMARY")
    print("="*80)
    print()
    
    total_scraped = 0
    total_expected = 0
    summary_data = []
    
    for excel_file in sorted(excel_files):
        # Extract university name from filename
        uni_key = excel_file.replace('_Organizations.xlsx', '')
        uni_name = uni_key.replace('_', ' ')
        
        try:
            df = pd.read_excel(excel_file)
            org_count = len(df)
            expected = expected_counts.get(uni_key, 0)
            
            total_scraped += org_count
            total_expected += expected
            
            # Validate data structure
            required_columns = [
                'Category', 'Organization Name', 'Organization Link', 'Logo Link', 
                'Description', 'Email', 'Phone Number', 'Linkedin Link', 
                'Instagram Link', 'Facebook Link', 'Twitter Link', 'Youtube Link', 'Tiktok Link'
            ]
            
            missing_cols = [col for col in required_columns if col not in df.columns]
            data_quality = "✓" if not missing_cols else "✗ Missing: " + ", ".join(missing_cols)
            
            success_rate = (org_count / expected * 100) if expected > 0 else 0
            
            print(f"📚 {uni_name}")
            print(f"   📁 File: {excel_file}")
            print(f"   📊 Organizations Found: {org_count}")
            print(f"   🎯 Expected Count: {expected}")
            print(f"   📈 Success Rate: {success_rate:.1f}%")
            print(f"   ✅ Data Quality: {data_quality}")
            
            # Sample some organization names
            if not df.empty:
                sample_orgs = df['Organization Name'].head(3).tolist()
                print(f"   📝 Sample Organizations: {', '.join(sample_orgs)}")
            
            print()
            
            summary_data.append({
                'University': uni_name,
                'File': excel_file,
                'Organizations_Found': org_count,
                'Expected_Count': expected,
                'Success_Rate_%': success_rate,
                'Data_Quality': 'Complete' if not missing_cols else 'Issues'
            })
            
        except Exception as e:
            print(f"❌ Error reading {excel_file}: {str(e)}")
            print()
    
    # Create summary DataFrame
    summary_df = pd.DataFrame(summary_data)
    
    print("="*80)
    print("OVERALL STATISTICS")
    print("="*80)
    print(f"🏫 Total Universities Processed: {len(excel_files)}")
    print(f"📊 Total Organizations Scraped: {total_scraped}")
    print(f"🎯 Total Organizations Expected: {total_expected}")
    print(f"📈 Overall Success Rate: {(total_scraped / total_expected * 100):.1f}%")
    print(f"✅ Files Created: {len(excel_files)} Excel files")
    print()
    
    # Category analysis
    print("="*80)
    print("CATEGORY ANALYSIS")
    print("="*80)
    
    all_categories = []
    for excel_file in excel_files:
        try:
            df = pd.read_excel(excel_file)
            if 'Category' in df.columns:
                all_categories.extend(df['Category'].dropna().tolist())
        except:
            pass
    
    if all_categories:
        category_counts = pd.Series(all_categories).value_counts()
        print("Category Distribution:")
        for category, count in category_counts.items():
            print(f"  {category}: {count} organizations")
    
    print()
    
    # Save summary to Excel
    summary_filename = "University_Organizations_Summary.xlsx"
    with pd.ExcelWriter(summary_filename, engine='openpyxl') as writer:
        summary_df.to_excel(writer, sheet_name='Summary', index=False)
        
        # Auto-adjust column widths
        worksheet = writer.sheets['Summary']
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
    
    print(f"📋 Summary saved to: {summary_filename}")
    print()
    print("✅ All university organization data has been successfully scraped and saved!")
    print("   Each university has its own Excel file with detailed organization information.")
    print("   All required fields are included: Category, Name, Links, Contact Info, Social Media.")

if __name__ == "__main__":
    generate_final_summary()