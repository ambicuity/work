#!/usr/bin/env python3
"""
Create comprehensive database consolidating all university organization data
Generates master Excel file with all organizations and university summary statistics
"""

import pandas as pd
import glob
import os
from datetime import datetime

def create_comprehensive_database():
    """Create consolidated database with all university organizations"""
    
    # Expected counts per university from problem statement
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
    
    print("Creating comprehensive university organizations database...")
    print(f"Found {len(excel_files)} university files")
    
    # Lists to store consolidated data
    all_organizations = []
    university_summary = []
    
    total_organizations = 0
    total_expected = sum(expected_counts.values())
    
    for excel_file in sorted(excel_files):
        # Extract university name from filename
        uni_key = excel_file.replace('_Organizations.xlsx', '')
        uni_name = uni_key.replace('_', ' ')
        
        try:
            # Read organization data
            df = pd.read_excel(excel_file)
            org_count = len(df)
            expected = expected_counts.get(uni_key, 0)
            
            print(f"Processing {uni_name}: {org_count} organizations")
            
            # Add university column to organization data
            df['University'] = uni_name
            
            # Reorder columns to put University first
            columns = ['University'] + [col for col in df.columns if col != 'University']
            df = df[columns]
            
            # Add to consolidated data
            all_organizations.append(df)
            total_organizations += org_count
            
            # Calculate statistics
            gap = org_count - expected
            success_rate = (org_count / expected * 100) if expected > 0 else 0
            
            # Determine status
            if success_rate >= 100:
                status = "Complete"
            elif success_rate >= 75:
                status = "Needs More"
            else:
                status = "Needs More"
            
            # Add to university summary
            university_summary.append({
                'University Name': uni_name,
                'Organizations Found': org_count,
                'Expected Count': expected,
                'Gap': gap,
                'Success Rate (%)': round(success_rate, 1),
                'Status': status,
                'Source File': excel_file
            })
            
        except Exception as e:
            print(f"Error processing {excel_file}: {e}")
            continue
    
    # Create consolidated DataFrames
    if all_organizations:
        consolidated_orgs = pd.concat(all_organizations, ignore_index=True)
        print(f"\nConsolidated {len(consolidated_orgs)} organizations from {len(university_summary)} universities")
    else:
        print("No organization data found!")
        return
    
    summary_df = pd.DataFrame(university_summary)
    
    # Create output filename with timestamp
    timestamp = datetime.now().strftime("%Y%m%d_%H%M")
    output_file = f"University_Organizations_Comprehensive_Database_{timestamp}.xlsx"
    
    # Write to Excel with multiple sheets
    with pd.ExcelWriter(output_file, engine='openpyxl') as writer:
        # Sheet 1: University Summary
        summary_df.to_excel(writer, sheet_name='University Summary', index=False)
        
        # Sheet 2: All Organizations
        consolidated_orgs.to_excel(writer, sheet_name='All Organizations', index=False)
        
        # Sheet 3: Statistics
        stats_data = {
            'Metric': [
                'Total Universities',
                'Total Organizations Found',
                'Total Organizations Expected',
                'Overall Success Rate (%)',
                'Universities Complete',
                'Universities Need More'
            ],
            'Value': [
                len(university_summary),
                total_organizations,
                total_expected,
                round((total_organizations / total_expected * 100), 1),
                len([s for s in university_summary if s['Status'] == 'Complete']),
                len([s for s in university_summary if s['Status'] == 'Needs More'])
            ]
        }
        stats_df = pd.DataFrame(stats_data)
        stats_df.to_excel(writer, sheet_name='Statistics', index=False)
    
    print(f"\n✅ Comprehensive database created: {output_file}")
    print(f"📊 Total organizations: {total_organizations}")
    print(f"🎯 Expected organizations: {total_expected}")
    print(f"📈 Overall success rate: {round((total_organizations / total_expected * 100), 1)}%")
    
    # Print university summary as requested in problem statement
    print("\n" + "="*60)
    print("FINAL PROJECT SUMMARY")
    print("="*60)
    print("\n📊 UNIVERSITY SUMMARY:")
    print("University Name\t\t\t\tOrganizations Found\tExpected Count\tGap\tSuccess Rate (%)\tStatus\t\tSource File")
    for uni in university_summary:
        name_padded = uni['University Name'][:35].ljust(35)
        print(f"{name_padded}\t{uni['Organizations Found']}\t\t{uni['Expected Count']}\t{uni['Gap']}\t{uni['Success Rate (%)']} \t\t{uni['Status']}\t{uni['Source File']}")
    
    return output_file, consolidated_orgs, summary_df

if __name__ == "__main__":
    create_comprehensive_database()