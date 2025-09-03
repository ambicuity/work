#!/usr/bin/env python3
"""
Generate final project summary report in the exact format requested
"""

import pandas as pd
import glob

def generate_final_report():
    """Generate final report matching the problem statement format"""
    
    # Find the comprehensive database
    db_files = glob.glob("University_Organizations_Comprehensive_Database_*.xlsx")
    if not db_files:
        print("❌ No comprehensive database file found!")
        return
    
    latest_db = sorted(db_files)[-1]
    
    # Read the data
    summary_df = pd.read_excel(latest_db, sheet_name='University Summary')
    orgs_df = pd.read_excel(latest_db, sheet_name='All Organizations')
    
    print("=" * 70)
    print("FINAL PROJECT SUMMARY")
    print("=" * 70)
    print()
    
    # Print university summary in exact format from problem statement
    print("📊 UNIVERSITY SUMMARY:")
    print("University Name\t\t\t\tOrganizations Found\tExpected Count\tGap\tSuccess Rate (%)\tStatus\t\tSource File")
    
    for _, row in summary_df.iterrows():
        name = row['University Name']
        found = row['Organizations Found']
        expected = row['Expected Count'] 
        gap = row['Gap']
        success_rate = row['Success Rate (%)']
        status = row['Status']
        source = row['Source File']
        
        # Format name to fit in column
        name_display = name[:35] + "..." if len(name) > 35 else name
        print(f"{name_display.ljust(40)}\t{found}\t\t\t{expected}\t\t{gap}\t{success_rate}\t\t\t{status}\t{source}")
    
    print()
    print("=" * 70)
    print("ORGANIZATION DATA SUMMARY")
    print("=" * 70)
    print()
    
    # Display column information as requested
    print("📋 ALL ORGANIZATION DATA INCLUDES:")
    columns = ['Organization Name', 'Categories', 'Org URL', 'Image URL', 'Description', 'Email', 'Phone', 'Website', 'LinkedIn', 'Instagram', 'Facebook', 'Twitter']
    for col in columns:
        print(f"  ✅ {col}")
    
    print()
    print("📊 DATA STATISTICS:")
    print(f"  • Total Universities: {len(summary_df)}")
    print(f"  • Total Organizations: {len(orgs_df)}")
    print(f"  • Complete Universities: {len(summary_df[summary_df['Status'] == 'Complete'])}")
    print(f"  • Universities Needing More: {len(summary_df[summary_df['Status'] == 'Needs More'])}")
    
    # Show sample organization data
    print()
    print("📋 SAMPLE ORGANIZATION DATA:")
    sample_orgs = orgs_df.head(5)
    for _, org in sample_orgs.iterrows():
        print(f"  🏫 {org['University']}")
        print(f"     📛 Name: {org['Organization Name']}")
        print(f"     📂 Category: {org['Categories']}")
        print(f"     🌐 URL: {org['Org URL'] if pd.notna(org['Org URL']) else 'N/A'}")
        print(f"     📧 Email: {org['Email'] if pd.notna(org['Email']) else 'N/A'}")
        print(f"     📱 Phone: {org['Phone'] if pd.notna(org['Phone']) else 'N/A'}")
        print()
    
    print("=" * 70)
    print("✅ COMPREHENSIVE DATABASE READY!")
    print(f"📁 File: {latest_db}")
    print("📋 Contains 3 sheets:")
    print("   1. University Summary - Overview of all universities")
    print("   2. All Organizations - Complete organization database") 
    print("   3. Statistics - Overall project statistics")
    print("=" * 70)

if __name__ == "__main__":
    generate_final_report()