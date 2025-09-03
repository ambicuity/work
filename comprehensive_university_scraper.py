#!/usr/bin/env python3
"""
Comprehensive University Organization Scraper
Scrapes organization data from universities 89-100 and creates individual Excel files
"""

import pandas as pd
import requests
from bs4 import BeautifulSoup
import time
import re
from urllib.parse import urljoin, urlparse
from typing import List, Dict, Optional
import json
import os
from requests.adapters import HTTPAdapter
from urllib3.util.retry import Retry

class ComprehensiveUniversityScraper:
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
        
        # Universities data from rows 89-100
        self.universities = {
            "Bethesda University": {
                "url": "https://www.buc.edu/student-services",
                "expected_count": 4
            },
            "Bethune-Cookman University": {
                "url": "https://www.cookman.edu/studentexperience/student-organizations.html", 
                "expected_count": 80
            },
            "Beulah Heights University": {
                "url": "https://beulah.edu/student-life/",
                "expected_count": 5
            },
            "Bevill State Community College": {
                "url": "https://www.bscc.edu/students/current-students/student-organizations",
                "expected_count": 19
            },
            "Big Bend Community College": {
                "url": "https://www.bigbend.edu/student-center/clubs-and-community-list/",
                "expected_count": 14
            },
            "Biola University": {
                "url": "https://www.biola.edu/digital-journalism-media-department/student-organizations",
                "expected_count": 6
            },
            "Bishop State Community College": {
                "url": "https://www.bishop.edu/student-services/student-organizations",
                "expected_count": 16
            },
            "Black Hills State University": {
                "url": "https://www.bhsu.edu/student-life/clubs-organizations/#tab_1-academic",
                "expected_count": 75
            },
            "Blackfeet Community College": {
                "url": "https://bfcc.edu/2021-spring-registration/",
                "expected_count": None  # N/A
            },
            "Bladen Community College": {
                "url": "https://www.bladencc.edu/campus-resources/student-activities/",
                "expected_count": 10
            },
            "Blue Mountain Community College": {
                "url": "https://www.bluecc.edu/support-services/student-life/clubs",
                "expected_count": 15
            },
            "Blue Ridge Community College": {
                "url": "https://www.brcc.edu/services/clubs/",
                "expected_count": 18
            }
        }
    
    def get_page_content(self, url: str) -> Optional[BeautifulSoup]:
        """Get page content with error handling and retries"""
        try:
            print(f"Fetching: {url}")
            response = self.session.get(url, timeout=30, allow_redirects=True)
            response.raise_for_status()
            
            # Try to detect encoding
            if response.encoding is None or response.encoding == 'ISO-8859-1':
                response.encoding = response.apparent_encoding
            
            soup = BeautifulSoup(response.content, 'html.parser')
            return soup
            
        except requests.exceptions.RequestException as e:
            print(f"Error fetching {url}: {str(e)}")
            return None
    
    def extract_organizations_from_page(self, soup: BeautifulSoup, base_url: str, university_name: str, expected_count: int) -> List[Dict]:
        """Extract organizations using multiple strategies"""
        organizations = []
        
        # Strategy 1: Look for structured organization listings
        orgs = self._find_structured_organizations(soup, base_url, university_name)
        if orgs:
            organizations.extend(orgs)
        
        # Strategy 2: Look for list items that might be organizations
        if len(organizations) < expected_count * 0.5:  # If we haven't found enough
            list_orgs = self._find_list_based_organizations(soup, base_url, university_name)
            organizations.extend(list_orgs)
        
        # Strategy 3: Look for heading-based organization listings
        if len(organizations) < expected_count * 0.5:
            heading_orgs = self._find_heading_based_organizations(soup, base_url, university_name)
            organizations.extend(heading_orgs)
        
        # Strategy 4: Try to find organization links and follow them
        if len(organizations) < expected_count * 0.3:
            linked_orgs = self._find_linked_organizations(soup, base_url, university_name)
            organizations.extend(linked_orgs)
        
        # Remove duplicates based on organization name
        seen_names = set()
        unique_organizations = []
        for org in organizations:
            name = org.get('Organization Name', '').strip().lower()
            if name and name not in seen_names:
                seen_names.add(name)
                unique_organizations.append(org)
        
        # If we still don't have enough, try to extract from general content
        if len(unique_organizations) < expected_count * 0.3:
            general_orgs = self._extract_from_general_content(soup, base_url, university_name)
            for org in general_orgs:
                name = org.get('Organization Name', '').strip().lower() 
                if name and name not in seen_names:
                    seen_names.add(name)
                    unique_organizations.append(org)
        
        print(f"Found {len(unique_organizations)} organizations for {university_name}")
        return unique_organizations
    
    def _find_structured_organizations(self, soup: BeautifulSoup, base_url: str, university_name: str) -> List[Dict]:
        """Find organizations in structured containers"""
        organizations = []
        
        # Common selectors for organization containers
        selectors = [
            '.organization', '.club', '.student-org', '.group',
            '.accordion-item', '.card', '.listing-item', 
            '.org-item', '.student-organization',
            '[class*="organization"]', '[class*="club"]', '[class*="group"]',
            '.entry', '.item', '.member'
        ]
        
        for selector in selectors:
            containers = soup.select(selector)
            if len(containers) > 2:  # Likely a meaningful list
                for container in containers:
                    org = self._extract_organization_details(container, base_url, university_name)
                    if org and org.get('Organization Name'):
                        organizations.append(org)
                break  # Use first successful selector
        
        return organizations
    
    def _find_list_based_organizations(self, soup: BeautifulSoup, base_url: str, university_name: str) -> List[Dict]:
        """Find organizations in list structures"""
        organizations = []
        
        # Look for lists that might contain organizations
        lists = soup.find_all(['ul', 'ol'])
        for ul in lists:
            items = ul.find_all('li')
            if len(items) > 3:  # Likely an organization list
                for li in items:
                    text = li.get_text(strip=True)
                    if self._is_likely_organization_name(text):
                        org = self._extract_organization_details(li, base_url, university_name)
                        if org and org.get('Organization Name'):
                            organizations.append(org)
        
        return organizations
    
    def _find_heading_based_organizations(self, soup: BeautifulSoup, base_url: str, university_name: str) -> List[Dict]:
        """Find organizations based on headings"""
        organizations = []
        
        headings = soup.find_all(['h1', 'h2', 'h3', 'h4', 'h5', 'h6'])
        for heading in headings:
            text = heading.get_text(strip=True)
            if self._is_likely_organization_name(text):
                org = self._extract_organization_details(heading.parent or heading, base_url, university_name)
                if org and org.get('Organization Name'):
                    organizations.append(org)
        
        return organizations
    
    def _find_linked_organizations(self, soup: BeautifulSoup, base_url: str, university_name: str) -> List[Dict]:
        """Find organizations by following links to individual organization pages"""
        organizations = []
        
        # Look for links that might lead to individual organization pages
        links = soup.find_all('a', href=True)
        org_links = []
        
        for link in links:
            href = link.get('href', '')
            link_text = link.get_text(strip=True)
            
            # Skip external links and common navigation
            if self._is_external_link(href, base_url) or not self._is_likely_organization_name(link_text):
                continue
            
            full_url = urljoin(base_url, href)
            org_links.append((full_url, link_text))
        
        # Follow a limited number of promising links
        for org_url, org_name in org_links[:20]:  # Limit to avoid too many requests
            try:
                time.sleep(1)  # Be respectful
                org_soup = self.get_page_content(org_url)
                if org_soup:
                    org = self._extract_detailed_organization_info(org_soup, org_url, org_name, university_name)
                    if org:
                        organizations.append(org)
            except Exception as e:
                print(f"Error following org link {org_url}: {e}")
                continue
        
        return organizations
    
    def _extract_from_general_content(self, soup: BeautifulSoup, base_url: str, university_name: str) -> List[Dict]:
        """Extract organizations from general text content as last resort"""
        organizations = []
        
        # Get all text and look for organization-like patterns
        text_content = soup.get_text()
        lines = [line.strip() for line in text_content.split('\n') if line.strip()]
        
        for line in lines:
            if self._is_likely_organization_name(line) and len(line) < 150:
                org = {
                    'Category': self._determine_category(line, ""),
                    'Organization Name': line,
                    'Organization Link': base_url,
                    'Logo Link': '',
                    'Description': '',
                    'Email': '',
                    'Phone Number': '',
                    'Linkedin Link': '',
                    'Instagram Link': '',
                    'Facebook Link': '',
                    'Twitter Link': '',
                    'Youtube Link': '',
                    'Tiktok Link': ''
                }
                organizations.append(org)
        
        return organizations[:50]  # Limit to reasonable number
    
    def _extract_organization_details(self, container, base_url: str, university_name: str) -> Dict:
        """Extract detailed organization information from a container"""
        org_data = {
            'Category': '',
            'Organization Name': '',
            'Organization Link': '',
            'Logo Link': '',
            'Description': '',
            'Email': '',
            'Phone Number': '',
            'Linkedin Link': '',
            'Instagram Link': '',
            'Facebook Link': '',
            'Twitter Link': '',
            'Youtube Link': '',
            'Tiktok Link': ''
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
        org_data['Phone Number'] = self._extract_phone(container)
        
        # If no contact info found in container, try broader search in surrounding content
        if not org_data['Email'] or not org_data['Phone Number']:
            parent_container = container.parent if hasattr(container, 'parent') and container.parent else container
            if hasattr(parent_container, 'get_text'):
                broader_text = parent_container.get_text()
                if not org_data['Email']:
                    org_data['Email'] = self._extract_email_from_text(broader_text)
                if not org_data['Phone Number']:
                    org_data['Phone Number'] = self._extract_phone_from_text(broader_text)
        
        # Extract links and social media
        links = container.find_all('a', href=True) if hasattr(container, 'find_all') else []
        # Also look in surrounding content for additional links
        if hasattr(container, 'parent') and container.parent:
            parent_links = container.parent.find_all('a', href=True) if hasattr(container.parent, 'find_all') else []
            links.extend(parent_links)
        
        for link in links:
            href = link.get('href', '').lower()
            full_url = urljoin(base_url, link.get('href', ''))
            
            if 'facebook' in href and not org_data['Facebook Link']:
                org_data['Facebook Link'] = full_url
            elif ('twitter' in href or 'x.com' in href) and not org_data['Twitter Link']:
                org_data['Twitter Link'] = full_url  
            elif 'instagram' in href and not org_data['Instagram Link']:
                org_data['Instagram Link'] = full_url
            elif 'linkedin' in href and not org_data['Linkedin Link']:
                org_data['Linkedin Link'] = full_url
            elif 'youtube' in href and not org_data['Youtube Link']:
                org_data['Youtube Link'] = full_url
            elif 'tiktok' in href and not org_data['Tiktok Link']:
                org_data['Tiktok Link'] = full_url
            elif href and not href.startswith('#') and not href.startswith('javascript') and not org_data['Organization Link']:
                if not self._is_external_link(href, base_url):
                    org_data['Organization Link'] = full_url
        
        # If no specific org link found, use the base URL
        if not org_data['Organization Link']:
            org_data['Organization Link'] = base_url
        
        # Extract image/logo - try multiple strategies
        img = container.find('img') if hasattr(container, 'find') else None
        if img and img.get('src'):
            org_data['Logo Link'] = urljoin(base_url, img.get('src'))
        else:
            # Try finding images in parent container
            if hasattr(container, 'parent') and container.parent:
                parent_img = container.parent.find('img') if hasattr(container.parent, 'find') else None
                if parent_img and parent_img.get('src'):
                    org_data['Logo Link'] = urljoin(base_url, parent_img.get('src'))
            
            # Look for common logo patterns
            if not org_data['Logo Link'] and hasattr(container, 'find'):
                logo_selectors = ['img[alt*="logo"]', '.logo img', '.icon img', 'img[src*="logo"]']
                for selector in logo_selectors:
                    logo_img = container.find(selector)
                    if logo_img and logo_img.get('src'):
                        org_data['Logo Link'] = urljoin(base_url, logo_img.get('src'))
                        break
        
        # Determine category
        org_data['Category'] = self._determine_category(name, org_data['Description'])
        
        return org_data
    
    def _extract_detailed_organization_info(self, soup: BeautifulSoup, org_url: str, org_name: str, university_name: str) -> Dict:
        """Extract detailed information from an individual organization page"""
        org_data = {
            'Category': '',
            'Organization Name': org_name,
            'Organization Link': org_url,
            'Logo Link': '',
            'Description': '',
            'Email': '',
            'Phone Number': '',
            'Linkedin Link': '',
            'Instagram Link': '',
            'Facebook Link': '',
            'Twitter Link': '',
            'Youtube Link': '',
            'Tiktok Link': ''
        }
        
        # Extract description from various possible locations
        desc_selectors = ['.description', '.about', '.summary', '.content', 'p', '.mission', '.overview']
        for selector in desc_selectors:
            desc_elem = soup.select_one(selector)
            if desc_elem:
                desc = desc_elem.get_text(strip=True)
                if len(desc) > 20:
                    org_data['Description'] = desc[:1000]  # Limit length
                    break
        
        # Extract contact information from the entire page
        page_text = soup.get_text()
        org_data['Email'] = self._extract_email_from_text(page_text)
        org_data['Phone Number'] = self._extract_phone_from_text(page_text)
        
        # Extract social media links
        all_links = soup.find_all('a', href=True)
        for link in all_links:
            href = link.get('href', '').lower()
            full_url = urljoin(org_url, link.get('href', ''))
            
            if 'facebook' in href and not org_data['Facebook Link']:
                org_data['Facebook Link'] = full_url
            elif ('twitter' in href or 'x.com' in href) and not org_data['Twitter Link']:
                org_data['Twitter Link'] = full_url
            elif 'instagram' in href and not org_data['Instagram Link']:
                org_data['Instagram Link'] = full_url
            elif 'linkedin' in href and not org_data['Linkedin Link']:
                org_data['Linkedin Link'] = full_url
            elif 'youtube' in href and not org_data['Youtube Link']:
                org_data['Youtube Link'] = full_url
            elif 'tiktok' in href and not org_data['Tiktok Link']:
                org_data['Tiktok Link'] = full_url
        
        # Extract logo/image
        img_selectors = ['img[alt*="logo"]', '.logo img', 'img', '.header img']
        for selector in img_selectors:
            img = soup.select_one(selector)
            if img and img.get('src'):
                org_data['Logo Link'] = urljoin(org_url, img.get('src'))
                break
        
        # Determine category
        org_data['Category'] = self._determine_category(org_name, org_data['Description'])
        
        return org_data
    
    def _extract_name(self, container) -> str:
        """Extract organization name from container"""
        if isinstance(container, str):
            return container.strip()
        
        # Try different approaches to get the name
        name_selectors = ['h1', 'h2', 'h3', 'h4', 'h5', 'h6', '.title', '.name', 'strong', 'b', '.org-name']
        
        for selector in name_selectors:
            element = container.find(selector) if hasattr(container, 'find') else None
            if element:
                name = element.get_text(strip=True)
                if name and self._is_likely_organization_name(name):
                    return name
        
        # Try getting the first link text
        first_link = container.find('a') if hasattr(container, 'find') else None
        if first_link:
            name = first_link.get_text(strip=True)
            if name and self._is_likely_organization_name(name):
                return name
        
        # Use container text
        text = container.get_text(strip=True) if hasattr(container, 'get_text') else str(container)
        lines = [line.strip() for line in text.split('\n') if line.strip()]
        
        if lines:
            first_line = lines[0]
            if self._is_likely_organization_name(first_line):
                return first_line
        
        return ""
    
    def _extract_description(self, container) -> str:
        """Extract organization description with enhanced strategies"""
        if not hasattr(container, 'find'):
            return ""
        
        # Look for description elements with more selectors
        desc_selectors = [
            '.description', '.summary', '.about', '.overview', '.content', 
            '.details', '.info', '.mission', '.purpose', 'p', '.text',
            '.excerpt', '.intro', '.profile'
        ]
        
        # Try each selector in order of preference
        for selector in desc_selectors:
            elements = container.find_all(selector)
            for element in elements:
                desc = element.get_text(strip=True)
                # Look for substantial descriptions
                if len(desc) > 20 and len(desc) < 1000:
                    # Skip if it looks like navigation or boilerplate
                    if not any(skip in desc.lower() for skip in ['click here', 'read more', 'learn more', 'contact', 'home', 'about us']):
                        return desc[:800]  # Limit length
        
        # Get text from container, skip the first line (likely name)
        full_text = container.get_text(strip=True)
        lines = [line.strip() for line in full_text.split('\n') if line.strip()]
        
        if len(lines) > 1:
            # Join lines after the first one, looking for substantial content
            desc_lines = []
            for line in lines[1:]:
                # Skip lines that are just links or navigation
                if len(line) > 10 and not line.lower().startswith(('http', 'www', 'click', 'read more')):
                    desc_lines.append(line)
                if len(' '.join(desc_lines)) > 100:  # Stop when we have enough
                    break
            
            desc = ' '.join(desc_lines)
            if len(desc) > 20:
                return desc[:800]
        
        return ""
    
    def _extract_email(self, container) -> str:
        """Extract email address"""
        text = container.get_text() if hasattr(container, 'get_text') else str(container)
        return self._extract_email_from_text(text)
    
    def _extract_email_from_text(self, text: str) -> str:
        """Extract email from text with enhanced patterns"""
        # Multiple email patterns to catch different formats
        email_patterns = [
            r'\b[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Z|a-z]{2,}\b',  # Standard email
            r'\b[A-Za-z0-9._%+-]+\s*\[at\]\s*[A-Za-z0-9.-]+\s*\[dot\]\s*[A-Za-z]{2,}\b',  # Obfuscated email
            r'\b[A-Za-z0-9._%+-]+\s*@\s*[A-Za-z0-9.-]+\s*\.\s*[A-Za-z]{2,}\b',  # Spaced email
        ]
        
        all_emails = []
        for pattern in email_patterns:
            emails = re.findall(pattern, text, re.IGNORECASE)
            all_emails.extend(emails)
        
        # Clean up obfuscated emails
        cleaned_emails = []
        for email in all_emails:
            # Convert obfuscated format back to normal
            cleaned = email.replace('[at]', '@').replace('[dot]', '.').replace(' ', '')
            cleaned_emails.append(cleaned)
        
        # Filter out common non-organizational emails and prioritize
        filtered_emails = []
        skip_patterns = ['noreply', 'webmaster', 'admin@university', 'support@university', 'info@example']
        
        for email in cleaned_emails:
            if not any(skip in email.lower() for skip in skip_patterns):
                # Prioritize organization-specific emails
                if any(term in email.lower() for term in ['student', 'club', 'org', 'group', 'society']):
                    filtered_emails.insert(0, email)  # Put at front
                else:
                    filtered_emails.append(email)
        
        return filtered_emails[0] if filtered_emails else ""
    
    def _extract_phone(self, container) -> str:
        """Extract phone number"""
        text = container.get_text() if hasattr(container, 'get_text') else str(container)
        return self._extract_phone_from_text(text)
    
    def _extract_phone_from_text(self, text: str) -> str:
        """Extract phone number from text with enhanced patterns"""
        phone_patterns = [
            r'\(?\d{3}\)?[-.\s]?\d{3}[-.\s]?\d{4}',  # Standard US format
            r'\+?1?[-.\s]?\(?\d{3}\)?[-.\s]?\d{3}[-.\s]?\d{4}',  # US with country code
            r'\d{3}[-.\s]?\d{3}[-.\s]?\d{4}',  # Simple format
            r'\d{3}\.\d{3}\.\d{4}',  # Dot separated
            r'\d{10}',  # Just digits (if exactly 10)
        ]
        
        for pattern in phone_patterns:
            phones = re.findall(pattern, text)
            if phones:
                # Clean up the phone number
                phone = phones[0].strip()
                # Skip obviously invalid numbers
                if len(re.sub(r'[^\d]', '', phone)) == 10:
                    return phone
        return ""
    
    def _is_likely_organization_name(self, text: str) -> bool:
        """Determine if text is likely an organization name"""
        if not text or len(text) < 3 or len(text) > 300:
            return False
        
        # Skip common non-organization terms
        skip_terms = [
            'home', 'about', 'contact', 'login', 'search', 'menu', 'navigation', 'footer', 'header', 'sidebar',
            'main', 'content', 'page', 'site', 'copyright', 'privacy', 'terms', 'policy', 'back to top',
            'skip to', 'click here', 'read more', 'learn more', 'see more', 'view all', 'show all',
            'campus', 'university', 'college', 'school', 'education', 'academic', 'student services'
        ]
        
        text_lower = text.lower().strip()
        if any(term in text_lower for term in skip_terms):
            return False
        
        # Skip if it's just numbers or too short
        if text.isdigit() or len(text.split()) < 1:
            return False
        
        # Look for organization indicators
        org_indicators = [
            'club', 'society', 'association', 'organization', 'group', 'team', 'council', 'committee',
            'union', 'fraternity', 'sorority', 'honor', 'student', 'academic', 'professional',
            'service', 'volunteer', 'honor society', 'student government'
        ]
        
        return any(indicator in text_lower for indicator in org_indicators) or \
               (len(text.split()) >= 2 and len(text.split()) <= 12)
    
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
    
    def _determine_category(self, name: str, description: str) -> str:
        """Determine organization category based on name and description"""
        text = (name + " " + description).lower()
        
        category_keywords = {
            'Academic': ['academic', 'honor society', 'honor', 'scholarship', 'study', 'research', 'education', 'phi theta kappa', 'national honor', 'dean\'s list'],
            'Arts': ['art', 'music', 'theater', 'theatre', 'dance', 'creative', 'band', 'choir', 'drama', 'visual', 'performing'],
            'Athletics': ['sport', 'athletic', 'team', 'recreation', 'fitness', 'basketball', 'football', 'soccer', 'baseball', 'volleyball'],
            'Cultural': ['cultural', 'international', 'heritage', 'ethnic', 'diversity', 'multicultural', 'african american', 'hispanic', 'asian'],
            'Greek Life': ['fraternity', 'sorority', 'greek', 'alpha', 'beta', 'gamma', 'delta', 'theta', 'phi', 'sigma'],
            'Professional': ['professional', 'career', 'business', 'engineering', 'medical', 'law', 'nursing', 'education', 'technology'],
            'Religious': ['christian', 'muslim', 'jewish', 'faith', 'religious', 'ministry', 'chapel', 'church', 'bible', 'spiritual'],
            'Service': ['service', 'volunteer', 'community', 'outreach', 'charity', 'help', 'support', 'humanitarian', 'social service'],
            'Student Government': ['student government', 'sga', 'student association', 'student council', 'government', 'leadership'],
            'Special Interest': ['gaming', 'anime', 'technology', 'computer', 'environment', 'outdoor', 'photography', 'cooking', 'debate']
        }
        
        for category, keywords in category_keywords.items():
            if any(keyword in text for keyword in keywords):
                return category
        
        return 'General'
    
    def scrape_university(self, university_name: str, url: str, expected_count: int) -> List[Dict]:
        """Scrape a single university"""
        print(f"\n{'='*60}")
        print(f"Scraping {university_name}")
        print(f"URL: {url}")
        print(f"Expected organizations: {expected_count}")
        print(f"{'='*60}")
        
        soup = self.get_page_content(url)
        if not soup:
            print(f"Failed to get content for {university_name}")
            return []
        
        organizations = self.extract_organizations_from_page(soup, url, university_name, expected_count or 10)
        
        print(f"Successfully scraped {len(organizations)} organizations for {university_name}")
        return organizations
    
    def save_university_excel(self, university_name: str, organizations: List[Dict]):
        """Save university data to individual Excel file"""
        if not organizations:
            print(f"No organizations to save for {university_name}")
            return
        
        # Create DataFrame
        df = pd.DataFrame(organizations)
        
        # Clean university name for filename
        safe_name = re.sub(r'[^\w\s-]', '', university_name).replace(' ', '_')
        filename = f"{safe_name}_Organizations.xlsx"
        
        # Create Excel writer with formatting
        with pd.ExcelWriter(filename, engine='openpyxl') as writer:
            df.to_excel(writer, sheet_name='Organizations', index=False)
            
            # Get the worksheet
            worksheet = writer.sheets['Organizations']
            
            # Auto-adjust column widths
            for column in worksheet.columns:
                max_length = 0
                column_letter = column[0].column_letter
                
                for cell in column:
                    try:
                        if len(str(cell.value)) > max_length:
                            max_length = len(str(cell.value))
                    except:
                        pass
                
                adjusted_width = min(max_length + 2, 50)  # Cap at 50 characters
                worksheet.column_dimensions[column_letter].width = adjusted_width
        
        print(f"Saved {len(organizations)} organizations to {filename}")
        return filename
    
    def run_comprehensive_scraping(self):
        """Run the comprehensive scraping for all universities"""
        print("Starting comprehensive university organization scraping...")
        print(f"Total universities to scrape: {len(self.universities)}")
        
        results = {}
        
        for university_name, data in self.universities.items():
            try:
                url = data["url"]
                expected_count = data["expected_count"]
                
                # Skip if expected count is None (N/A)
                if expected_count is None:
                    print(f"Skipping {university_name} - No expected organization count")
                    continue
                
                organizations = self.scrape_university(university_name, url, expected_count)
                
                if organizations:
                    filename = self.save_university_excel(university_name, organizations)
                    results[university_name] = {
                        'organizations': len(organizations),
                        'expected': expected_count,
                        'filename': filename
                    }
                
                # Be respectful with delays
                time.sleep(3)
                
            except Exception as e:
                print(f"Error processing {university_name}: {str(e)}")
                continue
        
        # Print summary
        print(f"\n{'='*80}")
        print("SCRAPING SUMMARY")
        print(f"{'='*80}")
        
        for university, data in results.items():
            print(f"{university}:")
            print(f"  - Found: {data['organizations']} organizations")
            print(f"  - Expected: {data['expected']} organizations")
            print(f"  - File: {data['filename']}")
            print(f"  - Success Rate: {(data['organizations'] / data['expected'] * 100):.1f}%")
            print()
        
        total_found = sum(data['organizations'] for data in results.values())
        total_expected = sum(data['expected'] for data in results.values())
        
        print(f"OVERALL SUMMARY:")
        print(f"Total organizations found: {total_found}")
        print(f"Total organizations expected: {total_expected}")
        print(f"Overall success rate: {(total_found / total_expected * 100):.1f}%")
        
        return results

def main():
    scraper = ComprehensiveUniversityScraper()
    results = scraper.run_comprehensive_scraping()
    
    if results:
        print("\nScraping completed successfully!")
        print("Individual Excel files created for each university with detailed organization data.")
    else:
        print("No results obtained. Please check the URLs and try again.")

if __name__ == "__main__":
    main()