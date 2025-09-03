#!/usr/bin/env python3
"""
University Organization Scraper Demo with Mock Data
Since network access is limited, this demonstrates the expected output format
"""

import pandas as pd
import json
from typing import List, Dict

def create_mock_organizations_data() -> List[Dict]:
    """Create realistic mock data for universities 91-100 organizations"""
    
    mock_organizations = [
        # Beulah Heights University
        {
            'Organization Name': 'Student Government Association',
            'Categories': 'Leadership',
            'Org URL': 'https://beulah.edu/student-life/',
            'Image URL': '',
            'Description': 'The Student Government Association serves as the voice of the student body and works to improve campus life.',
            'Email': 'sga@beulah.edu',
            'Phone': '(404) 627-2681',
            'Website': 'https://beulah.edu/student-government',
            'LinkedIn': '',
            'Instagram': '',
            'Facebook': 'https://facebook.com/BeulahHeightsSGA',
            'Twitter': ''
        },
        {
            'Organization Name': 'Campus Ministry Team',
            'Categories': 'Religious',
            'Org URL': 'https://beulah.edu/student-life/',
            'Image URL': '',
            'Description': 'Campus Ministry provides spiritual guidance and organizes faith-based activities for students.',
            'Email': 'ministry@beulah.edu',
            'Phone': '',
            'Website': '',
            'LinkedIn': '',
            'Instagram': '',
            'Facebook': '',
            'Twitter': ''
        },
        
        # Bevill State Community College
        {
            'Organization Name': 'Phi Theta Kappa Honor Society',
            'Categories': 'Academic',
            'Org URL': 'https://www.bscc.edu/students/current-students/student-organizations',
            'Image URL': '',
            'Description': 'International honor society recognizing academic achievement of community college students.',
            'Email': 'ptk@bscc.edu',
            'Phone': '(256) 898-3000',
            'Website': 'https://www.ptk.org',
            'LinkedIn': '',
            'Instagram': '',
            'Facebook': '',
            'Twitter': ''
        },
        {
            'Organization Name': 'Student Government Association',
            'Categories': 'Leadership',
            'Org URL': 'https://www.bscc.edu/students/current-students/student-organizations',
            'Image URL': '',
            'Description': 'Represents student interests and organizes campus events and activities.',
            'Email': 'sga@bscc.edu',
            'Phone': '',
            'Website': '',
            'LinkedIn': '',
            'Instagram': '',
            'Facebook': '',
            'Twitter': ''
        },
        
        # Big Bend Community College
        {
            'Organization Name': 'Associated Students of Big Bend',
            'Categories': 'Leadership',
            'Org URL': 'https://www.bigbend.edu/student-center/clubs-and-community-list/',
            'Image URL': '',
            'Description': 'Student government organization representing the interests of all Big Bend students.',
            'Email': 'asbb@bigbend.edu',
            'Phone': '(509) 793-2061',
            'Website': '',
            'LinkedIn': '',
            'Instagram': '',
            'Facebook': '',
            'Twitter': ''
        },
        {
            'Organization Name': 'Drama Club',
            'Categories': 'Arts',
            'Org URL': 'https://www.bigbend.edu/student-center/clubs-and-community-list/',
            'Image URL': '',
            'Description': 'Students interested in theater, acting, and dramatic arts performances.',
            'Email': 'drama@bigbend.edu',
            'Phone': '',
            'Website': '',
            'LinkedIn': '',
            'Instagram': '',
            'Facebook': '',
            'Twitter': ''
        },
        
        # Biola University
        {
            'Organization Name': 'Digital Media Club',
            'Categories': 'Professional',
            'Org URL': 'https://www.biola.edu/digital-journalism-media-department/student-organizations',
            'Image URL': '',
            'Description': 'Students passionate about digital media, journalism, and multimedia storytelling.',
            'Email': 'digitalmedia@biola.edu',
            'Phone': '(562) 903-4816',
            'Website': 'https://www.biola.edu/digitalmedia',
            'LinkedIn': 'https://linkedin.com/company/biola-digital-media',
            'Instagram': 'https://instagram.com/biola_digitalmedia',
            'Facebook': 'https://facebook.com/BiolaDigitalMedia',
            'Twitter': 'https://twitter.com/biola_dm'
        },
        {
            'Organization Name': 'Journalism Society',
            'Categories': 'Academic',
            'Org URL': 'https://www.biola.edu/digital-journalism-media-department/student-organizations',
            'Image URL': '',
            'Description': 'Promotes excellence in journalism and provides networking opportunities for aspiring journalists.',
            'Email': 'journalism@biola.edu',
            'Phone': '',
            'Website': '',
            'LinkedIn': '',
            'Instagram': '',
            'Facebook': '',
            'Twitter': ''
        },
        
        # Bishop State Community College
        {
            'Organization Name': 'Student Activities Council',
            'Categories': 'Leadership',
            'Org URL': 'https://www.bishop.edu/student-services/student-organizations',
            'Image URL': '',
            'Description': 'Plans and coordinates student activities, events, and social programs on campus.',
            'Email': 'activities@bishop.edu',
            'Phone': '(251) 405-7000',
            'Website': '',
            'LinkedIn': '',
            'Instagram': '',
            'Facebook': '',
            'Twitter': ''
        },
        {
            'Organization Name': 'Nursing Club',
            'Categories': 'Professional',
            'Org URL': 'https://www.bishop.edu/student-services/student-organizations',
            'Image URL': '',
            'Description': 'Supporting nursing students through academic and professional development activities.',
            'Email': 'nursing@bishop.edu',
            'Phone': '',
            'Website': '',
            'LinkedIn': '',
            'Instagram': '',
            'Facebook': '',
            'Twitter': ''
        },
        
        # Black Hills State University
        {
            'Organization Name': 'Biology Club',
            'Categories': 'Academic',
            'Org URL': 'https://www.bhsu.edu/student-life/clubs-organizations/#tab_1-academic',
            'Image URL': '',
            'Description': 'Students interested in biological sciences, research, and environmental conservation.',
            'Email': 'biology@bhsu.edu',
            'Phone': '(605) 642-6343',
            'Website': '',
            'LinkedIn': '',
            'Instagram': '',
            'Facebook': '',
            'Twitter': ''
        },
        {
            'Organization Name': 'Pre-Med Society',
            'Categories': 'Academic',
            'Org URL': 'https://www.bhsu.edu/student-life/clubs-organizations/#tab_1-academic',
            'Image URL': '',
            'Description': 'Preparing students for medical school and healthcare careers through mentorship and activities.',
            'Email': 'premed@bhsu.edu',
            'Phone': '',
            'Website': '',
            'LinkedIn': '',
            'Instagram': '',
            'Facebook': '',
            'Twitter': ''
        },
        
        # Blackfeet Community College
        {
            'Organization Name': 'Native American Student Association',
            'Categories': 'Cultural',
            'Org URL': 'https://bfcc.edu/2021-spring-registration/',
            'Image URL': '',
            'Description': 'Celebrating and preserving Native American culture and traditions on campus.',
            'Email': 'nasa@bfcc.edu',
            'Phone': '(406) 338-5441',
            'Website': '',
            'LinkedIn': '',
            'Instagram': '',
            'Facebook': '',
            'Twitter': ''
        },
        
        # Bladen Community College
        {
            'Organization Name': 'Student Ambassador Program',
            'Categories': 'Leadership',
            'Org URL': 'https://www.bladencc.edu/campus-resources/student-activities/',
            'Image URL': '',
            'Description': 'Student representatives who assist with campus tours, recruitment, and community outreach.',
            'Email': 'ambassadors@bladencc.edu',
            'Phone': '(910) 879-5500',
            'Website': '',
            'LinkedIn': '',
            'Instagram': '',
            'Facebook': '',
            'Twitter': ''
        },
        {
            'Organization Name': 'Veterans Club',
            'Categories': 'Service',
            'Org URL': 'https://www.bladencc.edu/campus-resources/student-activities/',
            'Image URL': '',
            'Description': 'Supporting military veterans in their educational and career transitions.',
            'Email': 'veterans@bladencc.edu',
            'Phone': '',
            'Website': '',
            'LinkedIn': '',
            'Instagram': '',
            'Facebook': '',
            'Twitter': ''
        },
        
        # Blue Mountain Community College
        {
            'Organization Name': 'Outdoor Recreation Club',
            'Categories': 'Recreation',
            'Org URL': 'https://www.bluecc.edu/support-services/student-life/clubs',
            'Image URL': '',
            'Description': 'Organizes hiking, camping, and outdoor adventure activities for students.',
            'Email': 'outdoor@bluecc.edu',
            'Phone': '(541) 278-5400',
            'Website': '',
            'LinkedIn': '',
            'Instagram': 'https://instagram.com/bluecc_outdoor',
            'Facebook': '',
            'Twitter': ''
        },
        {
            'Organization Name': 'Art Club',
            'Categories': 'Arts',
            'Org URL': 'https://www.bluecc.edu/support-services/student-life/clubs',
            'Image URL': '',
            'Description': 'Creative students exploring various art forms and techniques.',
            'Email': 'art@bluecc.edu',
            'Phone': '',
            'Website': '',
            'LinkedIn': '',
            'Instagram': '',
            'Facebook': '',
            'Twitter': ''
        },
        
        # Blue Ridge Community College
        {
            'Organization Name': 'Student Government Association',
            'Categories': 'Leadership',
            'Org URL': 'https://www.brcc.edu/services/clubs/',
            'Image URL': '',
            'Description': 'Representing student interests and organizing campus events and initiatives.',
            'Email': 'sga@brcc.edu',
            'Phone': '(828) 694-1700',
            'Website': '',
            'LinkedIn': '',
            'Instagram': '',
            'Facebook': '',
            'Twitter': ''
        },
        {
            'Organization Name': 'Culinary Arts Club',
            'Categories': 'Professional',
            'Org URL': 'https://www.brcc.edu/services/clubs/',
            'Image URL': '',
            'Description': 'Students in culinary programs practicing skills and competing in cooking competitions.',
            'Email': 'culinary@brcc.edu',
            'Phone': '',
            'Website': '',
            'LinkedIn': '',
            'Instagram': '',
            'Facebook': '',
            'Twitter': ''
        },
        {
            'Organization Name': 'Environmental Sustainability Club',
            'Categories': 'Special Interest',
            'Org URL': 'https://www.brcc.edu/services/clubs/',
            'Image URL': '',
            'Description': 'Promoting environmental awareness and sustainable practices on campus and in the community.',
            'Email': 'environment@brcc.edu',
            'Phone': '',
            'Website': '',
            'LinkedIn': '',
            'Instagram': '',
            'Facebook': '',
            'Twitter': ''
        }
    ]
    
    return mock_organizations

def main():
    """Generate mock data and save in Rice format"""
    print("Generating mock organization data for universities 91-100...")
    
    # Create mock data
    organizations = create_mock_organizations_data()
    
    # Convert to DataFrame
    df = pd.DataFrame(organizations)
    
    # Ensure all required columns are present (matching Rice format)
    required_columns = [
        'Organization Name', 'Categories', 'Org URL', 'Image URL', 'Description',
        'Email', 'Phone', 'Website', 'LinkedIn', 'Instagram', 'Facebook', 'Twitter'
    ]
    
    for col in required_columns:
        if col not in df.columns:
            df[col] = ""
    
    # Reorder columns to match Rice format
    df = df[required_columns]
    
    # Save to Excel file
    output_file = '/home/runner/work/work/work/scraped_organizations_91_100_demo.xlsx'
    df.to_excel(output_file, index=False)
    
    print(f"Mock data generated successfully!")
    print(f"Saved {len(df)} organizations to {output_file}")
    print(f"\nSummary:")
    print(f"Total organizations: {len(df)}")
    print(f"Organizations by category:")
    print(df['Categories'].value_counts().to_string())
    
    print(f"\nSample organizations:")
    print(df.head().to_string())
    
    return df

if __name__ == "__main__":
    main()