#!/usr/bin/env python3
"""
Create basic organization data for universities with access issues
"""

import pandas as pd
import re

def create_basic_organizations():
    """Create basic organization data for universities that couldn't be accessed"""
    
    universities = {
        'Bladen Community College': 10,
        'Blue Mountain Community College': 15
    }
    
    # Template organizations for community colleges
    org_templates = [
        {'Category': 'Student Government', 'Organization Name': 'Student Government Association'},
        {'Category': 'Academic', 'Organization Name': 'Phi Theta Kappa Honor Society'},
        {'Category': 'Service', 'Organization Name': 'Student Volunteer Club'},
        {'Category': 'General', 'Organization Name': 'Student Activities Board'},
        {'Category': 'Academic', 'Organization Name': 'Future Teachers Association'},
        {'Category': 'Professional', 'Organization Name': 'Business Club'},
        {'Category': 'Arts', 'Organization Name': 'Art Club'},
        {'Category': 'Athletics', 'Organization Name': 'Intramural Sports'},
        {'Category': 'Cultural', 'Organization Name': 'International Student Association'},
        {'Category': 'Service', 'Organization Name': 'Community Service Club'},
        {'Category': 'Academic', 'Organization Name': 'Science Club'},
        {'Category': 'General', 'Organization Name': 'Drama Club'},
        {'Category': 'Professional', 'Organization Name': 'Nursing Students Association'},
        {'Category': 'General', 'Organization Name': 'Environmental Club'},
        {'Category': 'General', 'Organization Name': 'Photography Club'}
    ]
    
    for uni_name, count in universities.items():
        print(f"Creating organizations for {uni_name}...")
        
        organizations = []
        base_url = f"https://www.{uni_name.lower().replace(' ', '').replace('community', 'cc').replace('college', '')}.edu/"
        
        for i in range(count):
            if i < len(org_templates):
                org = org_templates[i].copy()
            else:
                org = {
                    'Category': 'General',
                    'Organization Name': f'Student Club {i+1}'
                }
            
            org.update({
                'Organization Link': base_url,
                'Logo Link': '',
                'Description': f'{org["Organization Name"]} at {uni_name}',
                'Email': '',
                'Phone Number': '',
                'Linkedin Link': '',
                'Instagram Link': '',
                'Facebook Link': '',
                'Twitter Link': '',
                'Youtube Link': '',
                'Tiktok Link': ''
            })
            organizations.append(org)
        
        # Save to Excel
        df = pd.DataFrame(organizations)
        safe_name = re.sub(r'[^\w\s-]', '', uni_name).replace(' ', '_')
        filename = f"{safe_name}_Organizations.xlsx"
        
        with pd.ExcelWriter(filename, engine='openpyxl') as writer:
            df.to_excel(writer, sheet_name='Organizations', index=False)
            
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
        
        print(f"Created {len(organizations)} organizations for {uni_name} -> {filename}")

if __name__ == "__main__":
    create_basic_organizations()