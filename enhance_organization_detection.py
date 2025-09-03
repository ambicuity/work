#!/usr/bin/env python3
"""
Enhanced Organization Detection and Gap Analysis
Identifies missing organizations and ensures complete link processing
"""

import pandas as pd
import requests
from bs4 import BeautifulSoup
import time
import re
import os
from urllib.parse import urljoin, urlparse
from typing import List, Dict, Optional, Tuple
import json
from requests.adapters import HTTPAdapter
from urllib3.util.retry import Retry

class EnhancedOrganizationDetector:
    def __init__(self):
        # Setup session with retries
        self.session = requests.Session()
        retry_strategy = Retry(
            total=3,
            status_forcelist=[429, 500, 502, 503, 504],
            allowed_methods=["HEAD", "GET", "OPTIONS"]
        )
        adapter = HTTPAdapter(max_retries=retry_strategy)
        self.session.mount("http://", adapter)
        self.session.mount("https://", adapter)
        
        self.session.headers.update({
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36',
            'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,*/*;q=0.8',
            'Accept-Language': 'en-US,en;q=0.5',
            'Connection': 'keep-alive',
        })
        
        # University data with expected counts and URLs
        self.universities = {
            "Bethesda University": {
                "url": "https://www.buc.edu/student-services",
                "expected_count": 4,
                "alternate_urls": ["https://www.buc.edu/student-life", "https://www.buc.edu/"]
            },
            "Bethune-Cookman University": {
                "url": "https://www.cookman.edu/studentexperience/student-organizations.html", 
                "expected_count": 80,
                "alternate_urls": ["https://www.cookman.edu/student-life", "https://www.cookman.edu/"]
            },
            "Beulah Heights University": {
                "url": "https://beulah.edu/student-life/",
                "expected_count": 5,
                "alternate_urls": ["https://beulah.edu/"]
            },
            "Bevill State Community College": {
                "url": "https://www.bscc.edu/students/current-students/student-organizations",
                "expected_count": 19,
                "alternate_urls": ["https://www.bscc.edu/student-life"]
            },
            "Big Bend Community College": {
                "url": "https://www.bigbend.edu/student-center/clubs-and-community-list/",
                "expected_count": 14,
                "alternate_urls": ["https://www.bigbend.edu/student-life"]
            },
            "Biola University": {
                "url": "https://www.biola.edu/student-life/",
                "expected_count": 6,
                "alternate_urls": ["https://www.biola.edu/student-organizations"]
            },
            "Bishop State Community College": {
                "url": "https://www.bishop.edu/student-services/student-organizations",
                "expected_count": 16,
                "alternate_urls": ["https://www.bishop.edu/student-life"]
            },
            "Black Hills State University": {
                "url": "https://www.bhsu.edu/student-life/clubs-organizations/",
                "expected_count": 75,
                "alternate_urls": ["https://www.bhsu.edu/student-organizations"]
            },
            "Bladen Community College": {
                "url": "https://www.bladencc.edu/campus-resources/student-activities/",
                "expected_count": 10,
                "alternate_urls": ["https://www.bladencc.edu/student-life"]
            },
            "Blue Mountain Community College": {
                "url": "https://www.bluecc.edu/support-services/student-life/clubs",
                "expected_count": 15,
                "alternate_urls": ["https://www.bluecc.edu/student-organizations"]
            },
            "Blue Ridge Community College": {
                "url": "https://www.brcc.edu/services/clubs/",
                "expected_count": 18,
                "alternate_urls": ["https://www.brcc.edu/student-organizations"]
            }
        }
        
    def get_page_content(self, url: str) -> Optional[BeautifulSoup]:
        """Get page content with error handling"""
        try:
            print(f"  Fetching: {url}")
            response = self.session.get(url, timeout=30, allow_redirects=True)
            response.raise_for_status()
            
            if response.encoding is None or response.encoding == 'ISO-8859-1':
                response.encoding = response.apparent_encoding
            
            soup = BeautifulSoup(response.content, 'html.parser')
            return soup
            
        except requests.exceptions.RequestException as e:
            print(f"  Error fetching {url}: {str(e)}")
            return None
    
    def find_organization_links(self, soup: BeautifulSoup, base_url: str) -> List[Tuple[str, str]]:
        """Find links that might lead to individual organization pages"""
        org_links = []
        
        if not soup:
            return org_links
        
        # Look for organization-specific links
        links = soup.find_all('a', href=True)
        
        for link in links:
            href = link.get('href', '')
            link_text = link.get_text(strip=True)
            
            if not href or not link_text:
                continue
            
            # Skip external links
            if self._is_external_link(href, base_url):
                continue
            
            # Look for organization indicators in link text
            if self._is_likely_organization_link(link_text, href):
                full_url = urljoin(base_url, href)
                org_links.append((full_url, link_text))
        
        # Limit to reasonable number to avoid overwhelming
        return org_links[:30]
    
    def _is_likely_organization_link(self, link_text: str, href: str) -> bool:
        """Determine if a link likely leads to an organization page"""
        text_lower = link_text.lower().strip()
        href_lower = href.lower()
        
        # Skip common navigation items
        skip_terms = [
            'home', 'about', 'contact', 'admissions', 'academics', 'faculty',
            'staff', 'news', 'events', 'calendar', 'directory', 'search',
            'apply', 'tuition', 'financial aid', 'library', 'bookstore'
        ]
        
        if any(term in text_lower for term in skip_terms):
            return False
        
        # Look for organization indicators
        org_indicators = [
            'club', 'organization', 'society', 'association', 'fraternity',
            'sorority', 'honor society', 'student government', 'council',
            'committee', 'group', 'team', 'union', 'guild', 'fellowship'
        ]
        
        # Check link text
        has_org_indicator = any(indicator in text_lower for indicator in org_indicators)
        
        # Check if href suggests organization content
        href_indicators = ['org', 'club', 'society', 'student', 'group']
        has_href_indicator = any(indicator in href_lower for indicator in href_indicators)
        
        # Check if it's a reasonable organization name
        is_reasonable_name = (
            len(text_lower.split()) >= 2 and 
            len(text_lower.split()) <= 10 and
            len(text_lower) > 5 and
            len(text_lower) < 200
        )
        
        return has_org_indicator or (has_href_indicator and is_reasonable_name)
    
    def _is_external_link(self, href: str, base_url: str) -> bool:
        """Check if link is external to the university domain"""
        if not href:
            return True
        
        try:
            base_domain = urlparse(base_url).netloc.lower()
            href_parsed = urlparse(href)
            href_domain = href_parsed.netloc.lower()
            
            if not href_domain:  # Relative link
                return False
            
            return base_domain not in href_domain and href_domain not in base_domain
        except:
            return True
    
    def extract_organization_from_page(self, soup: BeautifulSoup, org_url: str, org_name: str) -> Optional[Dict]:
        """Extract detailed organization information from individual page"""
        if not soup:
            return None
        
        org_data = {
            'Organization Name': org_name,
            'Categories': 'General',
            'Org URL': org_url,
            'Image URL': '',
            'Description': '',
            'Email': '',
            'Phone': '',
            'Website': '',
            'LinkedIn': '',
            'Instagram': '',
            'Facebook': '',
            'Twitter': ''
        }
        
        # Extract description
        desc_selectors = ['.description', '.about', '.summary', '.content', 'p', 
                         '.mission', '.overview', '.info', '.details']
        
        for selector in desc_selectors:
            desc_elem = soup.select_one(selector)
            if desc_elem:
                desc_text = desc_elem.get_text(strip=True)
                if len(desc_text) > 20:
                    org_data['Description'] = desc_text[:800]
                    break
        
        # If no description found, use first paragraph
        if not org_data['Description']:
            paragraphs = soup.find_all('p')
            for p in paragraphs[:3]:
                text = p.get_text(strip=True)
                if len(text) > 20:
                    org_data['Description'] = text[:800]
                    break
        
        # Extract contact information
        page_text = soup.get_text()
        org_data['Email'] = self._extract_email_from_text(page_text)
        org_data['Phone'] = self._extract_phone_from_text(page_text)
        
        # Extract social media and website links
        links = soup.find_all('a', href=True)
        for link in links:
            href = link.get('href', '').lower()
            full_url = urljoin(org_url, link.get('href', ''))
            
            if 'facebook' in href and not org_data['Facebook']:
                org_data['Facebook'] = full_url
            elif ('twitter' in href or 'x.com' in href) and not org_data['Twitter']:
                org_data['Twitter'] = full_url
            elif 'instagram' in href and not org_data['Instagram']:
                org_data['Instagram'] = full_url
            elif 'linkedin' in href and not org_data['LinkedIn']:
                org_data['LinkedIn'] = full_url
            elif (href.startswith('http') and 
                  not any(social in href for social in ['facebook', 'twitter', 'instagram', 'linkedin']) and
                  not org_data['Website']):
                # Potential organization website
                org_data['Website'] = full_url
        
        # Extract logo/image
        img_selectors = ['img[alt*="logo"]', '.logo img', 'img', '.header img']
        for selector in img_selectors:
            img = soup.select_one(selector)
            if img and img.get('src'):
                org_data['Image URL'] = urljoin(org_url, img.get('src'))
                break
        
        # Determine category
        org_data['Categories'] = self._determine_category(org_name, org_data['Description'])
        
        return org_data
    
    def _extract_email_from_text(self, text: str) -> str:
        """Extract email from text"""
        email_pattern = r'\b[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Z|a-z]{2,}\b'
        emails = re.findall(email_pattern, text)
        for email in emails:
            if not any(skip in email.lower() for skip in ['noreply', 'webmaster', 'admin']):
                return email
        return ""
    
    def _extract_phone_from_text(self, text: str) -> str:
        """Extract phone number from text"""
        phone_patterns = [
            r'\(?\d{3}\)?[-.\s]?\d{3}[-.\s]?\d{4}',
            r'\+?1?[-.\s]?\(?\d{3}\)?[-.\s]?\d{3}[-.\s]?\d{4}',
        ]
        
        for pattern in phone_patterns:
            phones = re.findall(pattern, text)
            if phones:
                return phones[0]
        return ""
    
    def _determine_category(self, name: str, description: str) -> str:
        """Determine organization category"""
        text = (name + " " + description).lower()
        
        category_keywords = {
            'Academic': ['academic', 'honor society', 'scholarship', 'study', 'research', 'phi theta kappa'],
            'Arts': ['art', 'music', 'theater', 'theatre', 'dance', 'creative', 'band', 'choir'],
            'Athletics': ['sport', 'athletic', 'recreation', 'fitness', 'team'],
            'Cultural': ['cultural', 'international', 'heritage', 'diversity', 'multicultural'],
            'Greek Life': ['fraternity', 'sorority', 'greek', 'alpha', 'beta', 'gamma', 'delta'],
            'Professional': ['professional', 'career', 'business', 'engineering', 'medical'],
            'Religious': ['christian', 'muslim', 'jewish', 'faith', 'religious', 'ministry'],
            'Service': ['service', 'volunteer', 'community', 'outreach', 'charity'],
            'Student Government': ['student government', 'sga', 'student council', 'leadership']
        }
        
        for category, keywords in category_keywords.items():
            if any(keyword in text for keyword in keywords):
                return category
        
        return 'General'
    
    def analyze_university_gaps(self) -> Dict[str, Dict]:
        """Analyze gaps in scraped data compared to expected counts"""
        print("=== University Gap Analysis ===")
        
        gaps = {}
        university_files = {}
        
        # Map filenames to university names
        for filename in os.listdir('.'):
            if filename.endswith('_Organizations.xlsx'):
                uni_name = filename.replace('_Organizations.xlsx', '').replace('_', ' ')
                if uni_name in self.universities:
                    university_files[uni_name] = filename
        
        for uni_name, data in self.universities.items():
            expected = data['expected_count']
            
            # Get current count
            current_count = 0
            if uni_name in university_files:
                try:
                    df = pd.read_excel(university_files[uni_name])
                    current_count = len(df)
                except:
                    current_count = 0
            
            gap = expected - current_count if expected else 0
            
            gaps[uni_name] = {
                'expected': expected,
                'current': current_count,
                'gap': gap,
                'url': data['url'],
                'alternate_urls': data.get('alternate_urls', []),
                'needs_rescraping': gap > 0 or current_count == 0
            }
            
            print(f"{uni_name}:")
            print(f"  Expected: {expected}")
            print(f"  Current: {current_count}")
            print(f"  Gap: {gap}")
            print(f"  Status: {'NEEDS WORK' if gap > 0 or current_count == 0 else 'OK'}")
            print()
        
        total_expected = sum(data['expected'] for data in gaps.values() if data['expected'])
        total_current = sum(data['current'] for data in gaps.values())
        total_gap = total_expected - total_current
        
        print(f"OVERALL SUMMARY:")
        print(f"Total expected: {total_expected}")
        print(f"Total current: {total_current}")
        print(f"Total gap: {total_gap}")
        
        return gaps
    
    def enhance_organization_data(self, university_name: str, max_new_orgs: int = 10) -> List[Dict]:
        """Try to find additional organizations for a university by following links"""
        print(f"\n=== Enhancing data for {university_name} ===")
        
        if university_name not in self.universities:
            print(f"University {university_name} not found in database")
            return []
        
        uni_data = self.universities[university_name]
        urls_to_try = [uni_data['url']] + uni_data.get('alternate_urls', [])
        
        new_organizations = []
        
        for url in urls_to_try:
            if len(new_organizations) >= max_new_orgs:
                break
                
            print(f"Checking URL: {url}")
            soup = self.get_page_content(url)
            
            if not soup:
                continue
            
            # Find organization links
            org_links = self.find_organization_links(soup, url)
            print(f"Found {len(org_links)} potential organization links")
            
            # Follow a few links to get organization details
            for org_url, org_name in org_links[:max_new_orgs - len(new_organizations)]:
                print(f"  Checking: {org_name}")
                time.sleep(1)  # Be respectful
                
                org_soup = self.get_page_content(org_url)
                org_data = self.extract_organization_from_page(org_soup, org_url, org_name)
                
                if org_data and org_data['Organization Name']:
                    new_organizations.append(org_data)
                    print(f"    ✅ Added: {org_data['Organization Name']}")
                
                if len(new_organizations) >= max_new_orgs:
                    break
        
        print(f"Found {len(new_organizations)} new organizations for {university_name}")
        return new_organizations
    
    def save_enhanced_data(self, university_name: str, new_orgs: List[Dict]):
        """Save enhanced organization data to file"""
        if not new_orgs:
            return
        
        filename = f"{university_name.replace(' ', '_')}_Organizations.xlsx"
        
        # Load existing data
        existing_orgs = []
        if os.path.exists(filename):
            try:
                existing_df = pd.read_excel(filename)
                existing_orgs = existing_df.to_dict('records')
            except:
                pass
        
        # Combine and remove duplicates
        all_orgs = existing_orgs + new_orgs
        
        # Remove duplicates based on organization name
        seen_names = set()
        unique_orgs = []
        for org in all_orgs:
            name = org.get('Organization Name', '').strip().lower()
            if name and name not in seen_names:
                seen_names.add(name)
                unique_orgs.append(org)
        
        # Create DataFrame and save
        df = pd.DataFrame(unique_orgs)
        
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
        
        print(f"Saved {len(unique_orgs)} organizations to {filename}")

def main():
    detector = EnhancedOrganizationDetector()
    
    # Analyze current gaps
    gaps = detector.analyze_university_gaps()
    
    # Enhance data for universities with significant gaps
    for uni_name, gap_data in gaps.items():
        if gap_data['needs_rescraping'] and gap_data['gap'] > 5:
            print(f"\nEnhancing data for {uni_name} (gap: {gap_data['gap']})")
            try:
                new_orgs = detector.enhance_organization_data(uni_name, max_new_orgs=gap_data['gap'])
                if new_orgs:
                    detector.save_enhanced_data(uni_name, new_orgs)
                time.sleep(2)  # Rate limiting
            except Exception as e:
                print(f"Error enhancing data for {uni_name}: {e}")

if __name__ == "__main__":
    main()