#!/usr/bin/env python3
"""
Re-scrape all universities with enhanced algorithms to improve completeness
"""

import pandas as pd
import requests
from bs4 import BeautifulSoup
import time
import re
from urllib.parse import urljoin, urlparse
from typing import List, Dict, Optional
import os
from requests.adapters import HTTPAdapter
from urllib3.util.retry import Retry

class EnhancedScraper:
    def __init__(self):
        # Setup session with retries and proper headers
        self.session = requests.Session()
        
        # Add retry strategy
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
            'Accept-Encoding': 'gzip, deflate',
            'Connection': 'keep-alive',
            'Upgrade-Insecure-Requests': '1',
        })
    
    def enhance_existing_file(self, filename: str) -> bool:
        """Enhance an existing Excel file by re-scraping its organization page for more details"""
        try:
            print(f"\n🔍 Enhancing: {filename}")
            df = pd.read_excel(filename)
            print(f"Found {len(df)} organizations to enhance")
            
            enhanced_count = 0
            
            for idx, row in df.iterrows():
                org_name = row['Organization Name']
                org_link = row['Organization Link']
                
                print(f"  📝 Enhancing: {org_name}")
                
                # Get current completion status
                current_completion = sum(1 for col in ['Description', 'Email', 'Phone Number', 'Logo Link', 
                                                     'Linkedin Link', 'Instagram Link', 'Facebook Link', 
                                                     'Twitter Link', 'Youtube Link', 'Tiktok Link'] 
                                       if row[col] and str(row[col]).strip() != '')
                
                # Try to enhance if completion is low
                if current_completion < 5:  # Less than 5 fields completed
                    enhanced_data = self.scrape_organization_page(org_link, org_name)
                    
                    if enhanced_data:
                        # Update fields that are currently empty
                        for field, value in enhanced_data.items():
                            if value and (not row[field] or str(row[field]).strip() == ''):
                                df.at[idx, field] = value
                                enhanced_count += 1
                
                # Small delay to be respectful
                time.sleep(0.5)
            
            # Save enhanced file
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
            
            print(f"  ✅ Enhanced {enhanced_count} data points")
            return True
            
        except Exception as e:
            print(f"  ❌ Error enhancing {filename}: {e}")
            return False
    
    def scrape_organization_page(self, url: str, org_name: str) -> Dict:
        """Scrape a single organization page for enhanced details"""
        try:
            response = self.session.get(url, timeout=15)
            response.raise_for_status()
            
            if response.encoding is None or response.encoding == 'ISO-8859-1':
                response.encoding = response.apparent_encoding
            
            soup = BeautifulSoup(response.content, 'html.parser')
            
            # Extract enhanced data
            enhanced_data = {}
            
            # Extract description with multiple strategies
            enhanced_data['Description'] = self.extract_enhanced_description(soup, org_name)
            
            # Extract contact information
            page_text = soup.get_text()
            enhanced_data['Email'] = self.extract_enhanced_email(page_text, soup)
            enhanced_data['Phone Number'] = self.extract_enhanced_phone(page_text, soup)
            
            # Extract logo/image
            enhanced_data['Logo Link'] = self.extract_enhanced_logo(soup, url)
            
            # Extract social media links with comprehensive search
            social_links = self.extract_enhanced_social_media(soup, url)
            enhanced_data.update(social_links)
            
            return {k: v for k, v in enhanced_data.items() if v}
            
        except Exception as e:
            print(f"    Error scraping {url}: {e}")
            return {}
    
    def extract_enhanced_description(self, soup: BeautifulSoup, org_name: str) -> str:
        """Extract description with enhanced strategies"""
        # Strategy 1: Look for organization-specific content
        org_keywords = org_name.lower().split()
        
        # Try to find paragraphs or divs that mention the organization
        for element in soup.find_all(['p', 'div', 'section', 'article']):
            text = element.get_text(strip=True)
            if len(text) > 50 and any(keyword in text.lower() for keyword in org_keywords):
                if not any(skip in text.lower() for skip in ['click here', 'read more', 'contact us', 'home']):
                    return text[:1000]
        
        # Strategy 2: Look for description-related elements
        desc_selectors = [
            '[class*="description"]', '[class*="about"]', '[class*="mission"]',
            '[class*="overview"]', '[class*="summary"]', '[class*="info"]',
            '.content p', 'main p', 'article p', '.entry-content p'
        ]
        
        for selector in desc_selectors:
            elements = soup.select(selector)
            for element in elements:
                text = element.get_text(strip=True)
                if len(text) > 30 and len(text) < 2000:
                    # Skip navigation and boilerplate
                    if not any(skip in text.lower() for skip in ['navigation', 'menu', 'footer', 'header', 'cookie']):
                        return text[:1000]
        
        # Strategy 3: Get the first substantial paragraph
        paragraphs = soup.find_all('p')
        for p in paragraphs:
            text = p.get_text(strip=True)
            if len(text) > 50 and not text.lower().startswith(('click', 'read', 'learn', 'contact')):
                return text[:1000]
        
        return ""
    
    def extract_enhanced_email(self, page_text: str, soup: BeautifulSoup) -> str:
        """Extract email with enhanced strategies"""
        # Look for emails in mailto links first
        mailto_links = soup.find_all('a', href=re.compile(r'mailto:', re.I))
        for link in mailto_links:
            href = link.get('href', '')
            if href.startswith('mailto:'):
                email = href.replace('mailto:', '').split('?')[0]  # Remove query params
                if self.is_valid_email(email):
                    return email
        
        # Enhanced email patterns
        email_patterns = [
            r'\b[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Z|a-z]{2,}\b',  # Standard
            r'\b[A-Za-z0-9._%+-]+\s*\[at\]\s*[A-Za-z0-9.-]+\s*\[dot\]\s*[A-Za-z]{2,}\b',  # Obfuscated
            r'\b[A-Za-z0-9._%+-]+\s*@\s*[A-Za-z0-9.-]+\s*\.\s*[A-Za-z]{2,}\b',  # Spaced
        ]
        
        all_emails = []
        for pattern in email_patterns:
            emails = re.findall(pattern, page_text, re.IGNORECASE)
            all_emails.extend(emails)
        
        # Clean and prioritize emails
        for email in all_emails:
            cleaned = email.replace('[at]', '@').replace('[dot]', '.').replace(' ', '')
            if self.is_valid_email(cleaned):
                # Skip generic emails
                if not any(generic in cleaned.lower() for generic in ['noreply', 'webmaster', 'admin@university']):
                    return cleaned
        
        return ""
    
    def extract_enhanced_phone(self, page_text: str, soup: BeautifulSoup) -> str:
        """Extract phone with enhanced strategies"""
        # Look for tel: links first
        tel_links = soup.find_all('a', href=re.compile(r'tel:', re.I))
        for link in tel_links:
            href = link.get('href', '')
            if href.startswith('tel:'):
                phone = href.replace('tel:', '')
                cleaned = re.sub(r'[^\d]', '', phone)
                if len(cleaned) == 10:
                    return self.format_phone(phone)
        
        # Enhanced phone patterns
        phone_patterns = [
            r'\(?\d{3}\)?[-.\s]?\d{3}[-.\s]?\d{4}',  # Standard US format
            r'\+?1?[-.\s]?\(?\d{3}\)?[-.\s]?\d{3}[-.\s]?\d{4}',  # US with country code
            r'\b\d{3}[-.\s]?\d{3}[-.\s]?\d{4}\b',  # Simple format
        ]
        
        for pattern in phone_patterns:
            phones = re.findall(pattern, page_text)
            for phone in phones:
                cleaned = re.sub(r'[^\d]', '', phone)
                if len(cleaned) == 10:
                    return self.format_phone(phone)
        
        return ""
    
    def extract_enhanced_logo(self, soup: BeautifulSoup, base_url: str) -> str:
        """Extract logo with enhanced strategies"""
        # Strategy 1: Look for images with logo-related attributes
        logo_selectors = [
            'img[alt*="logo" i]',
            'img[src*="logo" i]',
            'img[class*="logo" i]',
            '.logo img',
            '.header img',
            '.brand img',
            '[class*="logo"] img'
        ]
        
        for selector in logo_selectors:
            img = soup.select_one(selector)
            if img and img.get('src'):
                src = img.get('src')
                # Skip placeholder and generic images
                if not any(skip in src.lower() for skip in ['placeholder', 'blank', 'spacer', 'pixel']):
                    return urljoin(base_url, src)
        
        # Strategy 2: Find the first reasonable image
        images = soup.find_all('img')
        for img in images[:5]:  # Check first 5 images
            src = img.get('src', '')
            alt = img.get('alt', '').lower()
            
            if src and not any(skip in src.lower() for skip in ['ad', 'banner', 'tracking', 'pixel']):
                # Prefer images with org-related alt text
                if any(term in alt for term in ['logo', 'emblem', 'seal', 'organization']):
                    return urljoin(base_url, src)
        
        return ""
    
    def extract_enhanced_social_media(self, soup: BeautifulSoup, base_url: str) -> Dict:
        """Extract social media links with comprehensive search"""
        social_links = {
            'Linkedin Link': '',
            'Instagram Link': '',
            'Facebook Link': '',
            'Twitter Link': '',
            'Youtube Link': '',
            'Tiktok Link': ''
        }
        
        # Find all links
        all_links = soup.find_all('a', href=True)
        
        for link in all_links:
            href = link.get('href', '').lower()
            full_url = urljoin(base_url, link.get('href', ''))
            
            # Check for each social media platform
            if 'linkedin.com' in href and not social_links['Linkedin Link']:
                social_links['Linkedin Link'] = full_url
            elif 'instagram.com' in href and not social_links['Instagram Link']:
                social_links['Instagram Link'] = full_url
            elif 'facebook.com' in href and not social_links['Facebook Link']:
                social_links['Facebook Link'] = full_url
            elif ('twitter.com' in href or 'x.com' in href) and not social_links['Twitter Link']:
                social_links['Twitter Link'] = full_url
            elif 'youtube.com' in href and not social_links['Youtube Link']:
                social_links['Youtube Link'] = full_url
            elif 'tiktok.com' in href and not social_links['Tiktok Link']:
                social_links['Tiktok Link'] = full_url
        
        # Also look in text for social media handles/usernames
        page_text = soup.get_text()
        
        # Look for @mentions that might indicate social media
        handle_patterns = [
            r'@[\w_]+(?=\s|\b)',  # @username
            r'instagram\.com/[\w_\.]+',
            r'twitter\.com/[\w_]+',
            r'facebook\.com/[\w_\.]+',
            r'linkedin\.com/[\w/_\.]+',
            r'youtube\.com/[\w/_\.]+',
            r'tiktok\.com/@?[\w_\.]+',
        ]
        
        for pattern in handle_patterns:
            matches = re.findall(pattern, page_text, re.IGNORECASE)
            for match in matches:
                if 'instagram' in match.lower() and not social_links['Instagram Link']:
                    social_links['Instagram Link'] = f"https://{match}" if not match.startswith('http') else match
                elif 'twitter' in match.lower() and not social_links['Twitter Link']:
                    social_links['Twitter Link'] = f"https://{match}" if not match.startswith('http') else match
                elif 'facebook' in match.lower() and not social_links['Facebook Link']:
                    social_links['Facebook Link'] = f"https://{match}" if not match.startswith('http') else match
                elif 'linkedin' in match.lower() and not social_links['Linkedin Link']:
                    social_links['Linkedin Link'] = f"https://{match}" if not match.startswith('http') else match
                elif 'youtube' in match.lower() and not social_links['Youtube Link']:
                    social_links['Youtube Link'] = f"https://{match}" if not match.startswith('http') else match
                elif 'tiktok' in match.lower() and not social_links['Tiktok Link']:
                    social_links['Tiktok Link'] = f"https://{match}" if not match.startswith('http') else match
        
        return {k: v for k, v in social_links.items() if v}
    
    def is_valid_email(self, email: str) -> bool:
        """Check if email is valid"""
        pattern = r'^[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Z|a-z]{2,}$'
        return re.match(pattern, email) is not None
    
    def format_phone(self, phone: str) -> str:
        """Format phone number consistently"""
        digits = re.sub(r'[^\d]', '', phone)
        if len(digits) == 10:
            return f"({digits[:3]}) {digits[3:6]}-{digits[6:]}"
        elif len(digits) == 11 and digits[0] == '1':
            return f"({digits[1:4]}) {digits[4:7]}-{digits[7:]}"
        return phone
    
    def enhance_all_files(self):
        """Enhance all organization Excel files"""
        print("🚀 Starting comprehensive enhancement of all organization files...")
        
        excel_files = sorted([f for f in os.listdir('.') if f.endswith('_Organizations.xlsx')])
        print(f"Found {len(excel_files)} files to enhance")
        
        success_count = 0
        
        for filename in excel_files:
            if self.enhance_existing_file(filename):
                success_count += 1
            
            # Delay between files to be respectful
            time.sleep(2)
        
        print(f"\n📊 ENHANCEMENT COMPLETE")
        print(f"✅ Successfully enhanced: {success_count}/{len(excel_files)} files")
        
        return success_count == len(excel_files)

def main():
    scraper = EnhancedScraper()
    success = scraper.enhance_all_files()
    
    if success:
        print("\n🎉 All files enhanced successfully!")
        print("📈 Running validation to check improvements...")
        
        # Run validation
        os.system('python3 comprehensive_validation.py')
    else:
        print("\n⚠️ Some files could not be enhanced. Check the output above for details.")

if __name__ == "__main__":
    main()