#!/usr/bin/env python3
"""
University Organization Scraper for Cells 91-100
Scrapes organization data from universities and formats it according to Rice.edu format
"""

import pandas as pd
import requests
from bs4 import BeautifulSoup
import time
import re
from urllib.parse import urljoin, urlparse
from typing import List, Dict, Optional
import json

class UniversityOrganizationScraper:
    def __init__(self):
        self.session = requests.Session()
        self.session.headers.update({
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36'
        })
        self.scraped_data = []
        
    def extract_organizations_from_url(self, url: str, university_name: str) -> List[Dict]:
        """Extract organization data from a university URL"""
        print(f"Scraping {university_name}: {url}")
        
        try:
            response = self.session.get(url, timeout=30)
            response.raise_for_status()
            soup = BeautifulSoup(response.content, 'html.parser')
            
            organizations = []
            
            # Strategy 1: Look for common organization list patterns
            org_containers = self._find_organization_containers(soup)
            
            if not org_containers:
                # Strategy 2: Look for links, headings, or text that might represent organizations
                org_containers = self._find_alternative_patterns(soup)
            
            for container in org_containers:
                org_data = self._extract_organization_details(container, url, university_name)
                if org_data and org_data.get('Organization Name'):
                    organizations.append(org_data)
            
            # If still no organizations found, try to extract from general text
            if not organizations:
                organizations = self._extract_from_general_text(soup, url, university_name)
            
            print(f"Found {len(organizations)} organizations for {university_name}")
            return organizations
            
        except Exception as e:
            print(f"Error scraping {university_name} ({url}): {str(e)}")
            return []
    
    def _find_organization_containers(self, soup: BeautifulSoup) -> List:
        """Find containers that likely contain organization information"""
        containers = []
        
        # Common selectors for organization listings
        selectors = [
            '.organization', '.club', '.group', '.student-organization',
            '[class*="organization"]', '[class*="club"]', '[class*="group"]',
            'li', 'div.entry', 'div.item', 'div.card', 'div.listing',
            'tbody tr', 'table tr', '.accordion-item', '.tab-content div',
            'h2, h3, h4', '.title', '.name'
        ]
        
        for selector in selectors:
            elements = soup.select(selector)
            if elements and len(elements) > 2:  # Likely a list if multiple elements
                containers.extend(elements)
                break
        
        return containers[:50]  # Limit to avoid too many false positives
    
    def _find_alternative_patterns(self, soup: BeautifulSoup) -> List:
        """Alternative patterns to find organizations"""
        containers = []
        
        # Look for headings that might be organization names
        headings = soup.find_all(['h1', 'h2', 'h3', 'h4', 'h5', 'h6'])
        for heading in headings:
            text = heading.get_text(strip=True)
            if self._is_likely_organization_name(text):
                containers.append(heading)
        
        # Look for list items
        list_items = soup.find_all('li')
        for li in list_items:
            text = li.get_text(strip=True)
            if self._is_likely_organization_name(text):
                containers.append(li)
        
        return containers
    
    def _is_likely_organization_name(self, text: str) -> bool:
        """Determine if text is likely an organization name"""
        if not text or len(text) < 3 or len(text) > 200:
            return False
        
        # Skip common non-organization terms
        skip_terms = [
            'home', 'about', 'contact', 'login', 'search', 'menu', 'navigation',
            'footer', 'header', 'sidebar', 'main', 'content', 'page', 'site',
            'copyright', 'privacy', 'terms', 'policy', 'back to top', 'skip to',
            'student life', 'campus', 'university', 'college', 'school'
        ]
        
        text_lower = text.lower()
        if any(term in text_lower for term in skip_terms):
            return False
        
        # Look for organization-like patterns
        org_indicators = [
            'club', 'society', 'association', 'organization', 'group', 'team',
            'council', 'committee', 'union', 'fraternity', 'sorority', 'honor',
            'student', 'academic', 'professional', 'service', 'volunteer'
        ]
        
        return any(indicator in text_lower for indicator in org_indicators) or \
               (len(text.split()) >= 2 and len(text.split()) <= 8)
    
    def _extract_organization_details(self, container, base_url: str, university_name: str) -> Dict:
        """Extract organization details from a container element"""
        org_data = {
            'Organization Name': '',
            'Categories': '',
            'Org URL': '',
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
        
        # Extract organization name
        name = self._extract_name(container)
        if not name:
            return {}
        
        org_data['Organization Name'] = name
        
        # Extract description
        org_data['Description'] = self._extract_description(container)
        
        # Extract contact information
        org_data['Email'] = self._extract_email(container)
        org_data['Phone'] = self._extract_phone(container)
        
        # Extract URLs and social media
        links = container.find_all('a', href=True)
        for link in links:
            href = link.get('href', '').lower()
            full_url = urljoin(base_url, link.get('href', ''))
            
            if 'facebook' in href:
                org_data['Facebook'] = full_url
            elif 'twitter' in href or 'x.com' in href:
                org_data['Twitter'] = full_url
            elif 'instagram' in href:
                org_data['Instagram'] = full_url
            elif 'linkedin' in href:
                org_data['LinkedIn'] = full_url
            elif href and not href.startswith('#') and not href.startswith('javascript'):
                if not org_data['Website']:
                    org_data['Website'] = full_url
        
        # Extract image
        img = container.find('img')
        if img and img.get('src'):
            org_data['Image URL'] = urljoin(base_url, img.get('src'))
        
        # Set organization URL to the page we scraped from
        org_data['Org URL'] = base_url
        
        # Try to determine category from context
        org_data['Categories'] = self._determine_category(name, org_data['Description'])
        
        return org_data
    
    def _extract_name(self, container) -> str:
        """Extract organization name from container"""
        # Try different approaches to get the name
        name_selectors = ['h1', 'h2', 'h3', 'h4', 'h5', 'h6', '.title', '.name', 'strong', 'b']
        
        for selector in name_selectors:
            element = container.find(selector)
            if element:
                name = element.get_text(strip=True)
                if name and self._is_likely_organization_name(name):
                    return name
        
        # If no specific element found, use the container's text
        text = container.get_text(strip=True)
        lines = [line.strip() for line in text.split('\n') if line.strip()]
        
        if lines:
            # First line is usually the name
            first_line = lines[0]
            if self._is_likely_organization_name(first_line):
                return first_line
        
        return ""
    
    def _extract_description(self, container) -> str:
        """Extract organization description"""
        # Look for description-like elements
        desc_selectors = ['.description', '.summary', '.about', 'p']
        
        for selector in desc_selectors:
            element = container.find(selector)
            if element:
                desc = element.get_text(strip=True)
                if len(desc) > 20:  # Reasonable description length
                    return desc[:500]  # Limit length
        
        # Get all text and try to find description-like content
        full_text = container.get_text(strip=True)
        sentences = re.split(r'[.!?]+', full_text)
        
        # Look for sentences that seem descriptive
        for sentence in sentences:
            sentence = sentence.strip()
            if len(sentence) > 20 and len(sentence) < 300:
                return sentence
        
        return ""
    
    def _extract_email(self, container) -> str:
        """Extract email address"""
        text = container.get_text()
        email_pattern = r'\b[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Z|a-z]{2,}\b'
        emails = re.findall(email_pattern, text)
        return emails[0] if emails else ""
    
    def _extract_phone(self, container) -> str:
        """Extract phone number"""
        text = container.get_text()
        phone_patterns = [
            r'\(?\d{3}\)?[-.\s]?\d{3}[-.\s]?\d{4}',
            r'\d{3}[-.\s]?\d{3}[-.\s]?\d{4}'
        ]
        
        for pattern in phone_patterns:
            phones = re.findall(pattern, text)
            if phones:
                return phones[0]
        return ""
    
    def _determine_category(self, name: str, description: str) -> str:
        """Determine organization category based on name and description"""
        text = (name + " " + description).lower()
        
        category_keywords = {
            'Academic': ['academic', 'honor', 'scholarship', 'study', 'research', 'education'],
            'Arts': ['art', 'music', 'theater', 'theatre', 'dance', 'creative', 'band', 'choir'],
            'Athletic': ['sport', 'athletic', 'team', 'recreation', 'fitness', 'basketball', 'football'],
            'Cultural': ['cultural', 'international', 'heritage', 'ethnic', 'diversity'],
            'Greek': ['fraternity', 'sorority', 'greek', 'alpha', 'beta', 'gamma', 'delta'],
            'Professional': ['professional', 'career', 'business', 'engineering', 'medical', 'law'],
            'Religious': ['christian', 'muslim', 'jewish', 'faith', 'religious', 'ministry', 'chapel'],
            'Service': ['service', 'volunteer', 'community', 'outreach', 'charity', 'help'],
            'Special Interest': ['gaming', 'anime', 'technology', 'computer', 'environment', 'outdoor']
        }
        
        for category, keywords in category_keywords.items():
            if any(keyword in text for keyword in keywords):
                return category
        
        return 'General'
    
    def _extract_from_general_text(self, soup: BeautifulSoup, url: str, university_name: str) -> List[Dict]:
        """Extract organizations from general text when structured data isn't available"""
        organizations = []
        
        # Get all text content
        text_content = soup.get_text()
        
        # Split into potential organization entries
        lines = [line.strip() for line in text_content.split('\n') if line.strip()]
        
        for line in lines:
            if self._is_likely_organization_name(line) and len(line) < 100:
                org_data = {
                    'Organization Name': line,
                    'Categories': self._determine_category(line, ""),
                    'Org URL': url,
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
                organizations.append(org_data)
        
        # Limit to reasonable number
        return organizations[:20]
    
    def scrape_universities_91_100(self):
        """Main method to scrape universities 91-100"""
        # Read the Excel file
        df = pd.read_excel('/home/runner/work/work/work/Non Campus Labs Universities list.xlsx')
        target_rows = df.iloc[90:100]  # Rows 91-100 (0-indexed)
        
        all_organizations = []
        
        for idx, row in target_rows.iterrows():
            university_name = row.iloc[0]  # First column contains university name
            url = row['URL']
            
            if pd.isna(url) or not url:
                print(f"Skipping {university_name} - no URL provided")
                continue
            
            organizations = self.extract_organizations_from_url(url, university_name)
            all_organizations.extend(organizations)
            
            # Be respectful with requests
            time.sleep(2)
        
        # Convert to DataFrame and save
        if all_organizations:
            df_results = pd.DataFrame(all_organizations)
            
            # Clean and format data
            df_results = self._clean_data(df_results)
            
            # Save to Excel file
            output_file = '/home/runner/work/work/work/scraped_organizations_91_100.xlsx'
            df_results.to_excel(output_file, index=False)
            print(f"\nScraping complete! Saved {len(df_results)} organizations to {output_file}")
            
            # Print summary
            print(f"\nSummary:")
            print(f"Total organizations found: {len(df_results)}")
            print(f"Organizations by category:")
            print(df_results['Categories'].value_counts())
            
            return df_results
        else:
            print("No organizations found to save.")
            return pd.DataFrame()
    
    def _clean_data(self, df: pd.DataFrame) -> pd.DataFrame:
        """Clean and format the scraped data"""
        # Remove duplicates based on organization name
        df = df.drop_duplicates(subset=['Organization Name'], keep='first')
        
        # Clean organization names
        df['Organization Name'] = df['Organization Name'].apply(self._clean_text)
        
        # Clean descriptions
        df['Description'] = df['Description'].apply(lambda x: self._clean_text(x) if pd.notna(x) else "")
        
        # Ensure all required columns exist
        required_columns = [
            'Organization Name', 'Categories', 'Org URL', 'Image URL', 'Description',
            'Email', 'Phone', 'Website', 'LinkedIn', 'Instagram', 'Facebook', 'Twitter'
        ]
        
        for col in required_columns:
            if col not in df.columns:
                df[col] = ""
        
        # Reorder columns to match Rice format
        df = df[required_columns]
        
        # Remove rows with empty organization names
        df = df[df['Organization Name'].str.strip() != ""]
        
        return df
    
    def _clean_text(self, text: str) -> str:
        """Clean text content"""
        if pd.isna(text) or not text:
            return ""
        
        # Remove extra whitespace
        text = re.sub(r'\s+', ' ', text).strip()
        
        # Remove special characters that might cause issues
        text = re.sub(r'[^\w\s\-.,!?()&@]', '', text)
        
        return text

def main():
    scraper = UniversityOrganizationScraper()
    results = scraper.scrape_universities_91_100()
    
    if not results.empty:
        print("\nFirst few organizations:")
        print(results.head().to_string())

if __name__ == "__main__":
    main()