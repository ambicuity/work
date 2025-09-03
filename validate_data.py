#!/usr/bin/env python3
"""
Data Validation Script
Compares the scraped data format with Rice format and validates data quality
"""

import pandas as pd
import numpy as np

def validate_data_format():
    """Validate that scraped data matches Rice format"""
    
    print("=== Data Format Validation ===\n")
    
    # Load Rice format reference
    rice_df = pd.read_excel('/home/runner/work/work/work/owlnest.rice.edu_organizations_merged.xlsx')
    
    # Load our scraped data
    scraped_df = pd.read_excel('/home/runner/work/work/work/scraped_organizations_91_100_demo.xlsx')
    
    print("Rice format reference:")
    print(f"Columns: {rice_df.columns.tolist()}")
    print(f"Shape: {rice_df.shape}")
    
    print("\nOur scraped data:")
    print(f"Columns: {scraped_df.columns.tolist()}")
    print(f"Shape: {scraped_df.shape}")
    
    # Check if columns match
    rice_columns = set(rice_df.columns)
    scraped_columns = set(scraped_df.columns)
    
    if rice_columns == scraped_columns:
        print("\n✅ COLUMN MATCH: All columns match Rice format exactly!")
    else:
        missing_cols = rice_columns - scraped_columns
        extra_cols = scraped_columns - rice_columns
        
        if missing_cols:
            print(f"\n❌ MISSING COLUMNS: {missing_cols}")
        if extra_cols:
            print(f"\n❌ EXTRA COLUMNS: {extra_cols}")
    
    # Data quality checks
    print("\n=== Data Quality Analysis ===")
    
    print(f"\nTotal organizations scraped: {len(scraped_df)}")
    print(f"Organizations with names: {scraped_df['Organization Name'].notna().sum()}")
    print(f"Organizations with descriptions: {scraped_df['Description'].apply(lambda x: len(str(x).strip()) > 0).sum()}")
    print(f"Organizations with emails: {scraped_df['Email'].apply(lambda x: len(str(x).strip()) > 0 and x != 'nan').sum()}")
    print(f"Organizations with phone numbers: {scraped_df['Phone'].apply(lambda x: len(str(x).strip()) > 0 and x != 'nan').sum()}")
    print(f"Organizations with websites: {scraped_df['Website'].apply(lambda x: len(str(x).strip()) > 0 and x != 'nan').sum()}")
    
    # Category distribution
    print(f"\nCategory distribution:")
    category_counts = scraped_df['Categories'].value_counts()
    for category, count in category_counts.items():
        print(f"  {category}: {count}")
    
    # Sample comparison with Rice data
    print(f"\n=== Format Comparison ===")
    print(f"Rice sample organization:")
    rice_sample = rice_df.iloc[0]
    for col in rice_df.columns:
        value = rice_sample[col]
        if pd.isna(value):
            value = "[Empty]"
        print(f"  {col}: {str(value)[:100]}...")
    
    print(f"\nOur scraped sample organization:")
    scraped_sample = scraped_df.iloc[0]
    for col in scraped_df.columns:
        value = scraped_sample[col]
        if pd.isna(value) or str(value).strip() == '':
            value = "[Empty]"
        print(f"  {col}: {str(value)[:100]}...")

def create_data_summary():
    """Create a summary of scraped data"""
    df = pd.read_excel('/home/runner/work/work/work/scraped_organizations_91_100_demo.xlsx')
    
    print("\n=== University Organizations Summary (Cells 91-100) ===")
    
    # Group by source URL to see organizations per university
    university_counts = df['Org URL'].value_counts()
    
    # Map URLs to university names
    url_to_university = {
        'https://beulah.edu/student-life/': 'Beulah Heights University',
        'https://www.bscc.edu/students/current-students/student-organizations': 'Bevill State Community College',
        'https://www.bigbend.edu/student-center/clubs-and-community-list/': 'Big Bend Community College',
        'https://www.biola.edu/digital-journalism-media-department/student-organizations': 'Biola University',
        'https://www.bishop.edu/student-services/student-organizations': 'Bishop State Community College',
        'https://www.bhsu.edu/student-life/clubs-organizations/#tab_1-academic': 'Black Hills State University',
        'https://bfcc.edu/2021-spring-registration/': 'Blackfeet Community College',
        'https://www.bladencc.edu/campus-resources/student-activities/': 'Bladen Community College',
        'https://www.bluecc.edu/support-services/student-life/clubs': 'Blue Mountain Community College',
        'https://www.brcc.edu/services/clubs/': 'Blue Ridge Community College'
    }
    
    print("Organizations found per university:")
    for url, count in university_counts.items():
        university_name = url_to_university.get(url, 'Unknown University')
        print(f"  {university_name}: {count} organizations")
    
    print(f"\nData completeness:")
    total_orgs = len(df)
    for col in df.columns:
        if col not in ['Organization Name', 'Categories', 'Org URL']:  # Skip mandatory fields
            non_empty = df[col].apply(lambda x: len(str(x).strip()) > 0 and str(x) != 'nan').sum()
            percentage = (non_empty / total_orgs) * 100
            print(f"  {col}: {non_empty}/{total_orgs} ({percentage:.1f}%)")

def main():
    validate_data_format()
    create_data_summary()

if __name__ == "__main__":
    main()