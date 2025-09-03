#!/usr/bin/env python3
"""
Data Format Standardization Script
Converts all scraped university files to match Rice University format exactly
"""

import pandas as pd
import os
import glob
from typing import List, Dict
import re

class DataFormatFixer:
    def __init__(self):
        # Rice University reference format
        self.rice_columns = [
            'Organization Name', 'Categories', 'Org URL', 'Image URL', 
            'Description', 'Email', 'Phone', 'Website', 'LinkedIn', 
            'Instagram', 'Facebook', 'Twitter'
        ]
        
        # Current format to Rice format mapping
        self.column_mapping = {
            'Category': 'Categories',
            'Organization Name': 'Organization Name',  # Same
            'Organization Link': 'Org URL',
            'Logo Link': 'Image URL',
            'Description': 'Description',  # Same
            'Email': 'Email',  # Same
            'Phone Number': 'Phone',
            'Linkedin Link': 'LinkedIn',
            'Instagram Link': 'Instagram',
            'Facebook Link': 'Facebook',
            'Twitter Link': 'Twitter',
            # These will be dropped as they're not in Rice format
            'Youtube Link': None,
            'Tiktok Link': None
        }
    
    def is_valid_organization(self, org_name: str, description: str = "") -> bool:
        """
        Filter out navigation items and non-organizations
        """
        if not org_name or len(org_name.strip()) < 3:
            return False
        
        org_lower = org_name.lower().strip()
        
        # Common navigation/administrative items to exclude
        invalid_terms = [
            'faculty & staff', 'faculty and staff', 'my apps', 'student services',
            'academic programs', 'admissions', 'financial aid', 'library', 
            'bookstore', 'dining', 'parking', 'campus map', 'directory',
            'calendar', 'news', 'events', 'about us', 'contact us', 'home',
            'search', 'menu', 'navigation', 'login', 'register', 'apply now',
            'tuition', 'scholarships', 'degrees', 'certificates', 'programs',
            'campus life', 'athletics', 'alumni', 'giving', 'foundation',
            'president', 'administration', 'board', 'trustees', 'welcome',
            'overview', 'mission', 'history', 'accreditation', 'catalog',
            'handbook', 'policies', 'procedures', 'emergency', 'safety',
            'security', 'health center', 'counseling', 'disability',
            'career services', 'job placement', 'internships', 'study abroad',
            'continuing education', 'professional development', 'training'
        ]
        
        # Check if it's a common non-organization term
        for term in invalid_terms:
            if term in org_lower:
                return False
        
        # Check if it's too generic or short
        if len(org_lower.split()) < 2 and not any(indicator in org_lower for indicator in [
            'club', 'society', 'association', 'organization', 'fraternity', 'sorority'
        ]):
            return False
        
        # Valid organization indicators
        valid_indicators = [
            'club', 'society', 'association', 'organization', 'fraternity', 'sorority',
            'honor society', 'student government', 'council', 'committee', 'union',
            'team', 'group', 'honor', 'phi', 'alpha', 'beta', 'gamma', 'delta',
            'sigma', 'theta', 'kappa', 'lambda', 'mu', 'nu', 'pi', 'rho', 'tau',
            'upsilon', 'chi', 'psi', 'omega', 'service', 'volunteer', 'ministry',
            'fellowship', 'guild', 'league', 'society', 'coalition'
        ]
        
        # Check if it contains valid organization indicators
        has_valid_indicator = any(indicator in org_lower for indicator in valid_indicators)
        
        # Also check description for context
        desc_lower = description.lower() if description else ""
        has_desc_indicator = any(indicator in desc_lower for indicator in valid_indicators)
        
        return has_valid_indicator or has_desc_indicator or (
            len(org_lower.split()) >= 2 and 
            not any(skip in org_lower for skip in ['welcome', 'about', 'overview', 'information'])
        )
    
    def standardize_university_file(self, filepath: str) -> bool:
        """
        Standardize a single university file to Rice format
        """
        try:
            print(f"\nProcessing: {filepath}")
            df = pd.read_excel(filepath)
            
            print(f"  Original: {len(df)} organizations")
            
            # Filter out invalid organizations
            valid_orgs = []
            for _, row in df.iterrows():
                org_name = str(row.get('Organization Name', '')).strip()
                description = str(row.get('Description', '')).strip()
                
                if self.is_valid_organization(org_name, description):
                    valid_orgs.append(row)
            
            if not valid_orgs:
                print(f"  WARNING: No valid organizations found in {filepath}")
                return False
            
            # Create new DataFrame with valid organizations
            filtered_df = pd.DataFrame(valid_orgs)
            print(f"  After filtering: {len(filtered_df)} organizations")
            
            # Create new DataFrame with Rice format columns
            rice_df = pd.DataFrame(columns=self.rice_columns)
            
            # Map columns from current format to Rice format
            for current_col, rice_col in self.column_mapping.items():
                if rice_col and current_col in filtered_df.columns:
                    rice_df[rice_col] = filtered_df[current_col]
            
            # Add missing 'Website' column (empty for now)
            if 'Website' not in rice_df.columns:
                rice_df['Website'] = ''
            
            # Clean and validate data
            rice_df = self.clean_data(rice_df)
            
            # Save the standardized file
            with pd.ExcelWriter(filepath, engine='openpyxl') as writer:
                rice_df.to_excel(writer, sheet_name='Organizations', index=False)
                
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
            
            print(f"  ✅ Standardized: {len(rice_df)} valid organizations")
            return True
            
        except Exception as e:
            print(f"  ❌ Error processing {filepath}: {str(e)}")
            return False
    
    def clean_data(self, df: pd.DataFrame) -> pd.DataFrame:
        """
        Clean and validate the data
        """
        # Remove rows with empty organization names
        df = df[df['Organization Name'].notna() & (df['Organization Name'].str.strip() != '')]
        
        # Clean organization names
        df['Organization Name'] = df['Organization Name'].str.strip()
        
        # Clean descriptions
        df['Description'] = df['Description'].fillna('').str.strip()
        
        # Clean and validate URLs
        df['Org URL'] = df['Org URL'].fillna('')
        df['Image URL'] = df['Image URL'].fillna('')
        df['Website'] = df['Website'].fillna('')
        
        # Clean contact information
        df['Email'] = df['Email'].fillna('')
        df['Phone'] = df['Phone'].fillna('')
        
        # Clean social media links
        df['LinkedIn'] = df['LinkedIn'].fillna('')
        df['Instagram'] = df['Instagram'].fillna('')
        df['Facebook'] = df['Facebook'].fillna('')
        df['Twitter'] = df['Twitter'].fillna('')
        
        # Clean categories
        df['Categories'] = df['Categories'].fillna('General')
        
        # Remove duplicates based on organization name
        df = df.drop_duplicates(subset=['Organization Name'], keep='first')
        
        return df
    
    def process_all_university_files(self) -> Dict[str, int]:
        """
        Process all university Excel files in the current directory
        """
        print("=== Data Format Standardization ===")
        
        # Find all university organization files
        university_files = glob.glob("*_Organizations.xlsx")
        
        if not university_files:
            print("No university organization files found!")
            return {}
        
        print(f"Found {len(university_files)} university files to process")
        
        results = {}
        total_before = 0
        total_after = 0
        
        for filepath in sorted(university_files):
            # Count organizations before processing
            try:
                df_before = pd.read_excel(filepath)
                before_count = len(df_before)
                total_before += before_count
            except:
                before_count = 0
            
            # Process the file
            success = self.standardize_university_file(filepath)
            
            if success:
                # Count organizations after processing
                try:
                    df_after = pd.read_excel(filepath)
                    after_count = len(df_after)
                    total_after += after_count
                    results[filepath] = {'before': before_count, 'after': after_count}
                except:
                    results[filepath] = {'before': before_count, 'after': 0}
        
        # Print summary
        print(f"\n{'='*60}")
        print("STANDARDIZATION SUMMARY")
        print(f"{'='*60}")
        
        for filepath, counts in results.items():
            uni_name = filepath.replace('_Organizations.xlsx', '').replace('_', ' ')
            print(f"{uni_name}:")
            print(f"  Before: {counts['before']} items")
            print(f"  After: {counts['after']} valid organizations")
            print(f"  Filtered out: {counts['before'] - counts['after']} invalid items")
            print()
        
        print(f"OVERALL SUMMARY:")
        print(f"Total items before: {total_before}")
        print(f"Total valid organizations after: {total_after}")
        print(f"Items filtered out: {total_before - total_after}")
        print(f"Retention rate: {(total_after / total_before * 100):.1f}%" if total_before > 0 else "N/A")
        
        return results

def main():
    fixer = DataFormatFixer()
    results = fixer.process_all_university_files()
    
    if results:
        print("\n✅ Data format standardization completed!")
        print("All files now match Rice University format exactly.")
    else:
        print("\n❌ No files were processed.")

if __name__ == "__main__":
    main()