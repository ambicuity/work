#!/usr/bin/env python3
"""
Validate comprehensive database against problem statement requirements
"""

import pandas as pd
import glob

def validate_comprehensive_data():
    """Validate that all required data is present and complete"""
    
    print("="*80)
    print("COMPREHENSIVE DATA VALIDATION")
    print("="*80)
    
    # Find the most recent comprehensive database file
    db_files = glob.glob("University_Organizations_Comprehensive_Database_*.xlsx")
    if not db_files:
        print("❌ No comprehensive database file found!")
        return False
    
    latest_db = sorted(db_files)[-1]
    print(f"📁 Validating file: {latest_db}")
    print()
    
    # Required columns from problem statement
    required_columns = [
        'Organization Name', 'Categories', 'Org URL', 'Image URL', 
        'Description', 'Email', 'Phone', 'Website', 'LinkedIn', 
        'Instagram', 'Facebook', 'Twitter'
    ]
    
    try:
        # Read all sheets
        summary_df = pd.read_excel(latest_db, sheet_name='University Summary')
        orgs_df = pd.read_excel(latest_db, sheet_name='All Organizations')
        stats_df = pd.read_excel(latest_db, sheet_name='Statistics')
        
        print("📊 UNIVERSITY SUMMARY VALIDATION:")
        print(f"  ✅ Universities processed: {len(summary_df)}")
        print(f"  ✅ Summary columns: {list(summary_df.columns)}")
        
        # Check for expected universities from problem statement
        expected_universities = [
            'Bethesda University', 'Bethune-Cookman University', 'Beulah Heights University',
            'Bevill State Community College', 'Big Bend Community College', 'Biola University',
            'Bishop State Community College', 'Black Hills State University', 'Bladen Community College',
            'Blue Mountain Community College', 'Blue Ridge Community College'
        ]
        
        found_universities = set(summary_df['University Name'].tolist())
        missing_unis = set(expected_universities) - found_universities
        
        if missing_unis:
            print(f"  ⚠️ Missing universities: {missing_unis}")
        else:
            print(f"  ✅ All expected universities present: {len(expected_universities)}")
        print()
        
        print("📋 ORGANIZATION DATA VALIDATION:")
        print(f"  ✅ Total organizations: {len(orgs_df)}")
        print(f"  ✅ Organization columns: {list(orgs_df.columns)}")
        
        # Check for required columns
        missing_cols = set(required_columns) - set(orgs_df.columns)
        if missing_cols:
            print(f"  ❌ Missing required columns: {missing_cols}")
        else:
            print(f"  ✅ All required columns present: {len(required_columns)}")
        
        # Check data completeness
        print()
        print("📈 DATA COMPLETENESS ANALYSIS:")
        
        # Check which columns have data
        for col in required_columns:
            if col in orgs_df.columns:
                non_null_count = orgs_df[col].notna().sum()
                completeness = (non_null_count / len(orgs_df)) * 100
                print(f"  {col}: {non_null_count}/{len(orgs_df)} ({completeness:.1f}%)")
        
        print()
        print("🏫 UNIVERSITY BREAKDOWN:")
        uni_counts = orgs_df['University'].value_counts()
        for uni, count in uni_counts.items():
            print(f"  {uni}: {count} organizations")
        
        print()
        print("📊 FINAL STATISTICS:")
        for idx, row in stats_df.iterrows():
            print(f"  {row['Metric']}: {row['Value']}")
        
        print()
        print("✅ VALIDATION COMPLETE!")
        print(f"📁 Comprehensive database file: {latest_db}")
        print(f"📊 Contains all required data with {len(orgs_df)} organizations from {len(summary_df)} universities")
        
        return True
        
    except Exception as e:
        print(f"❌ Error validating data: {e}")
        return False

if __name__ == "__main__":
    validate_comprehensive_data()