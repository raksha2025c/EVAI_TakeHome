import requests
import json
from bs4 import BeautifulSoup
from typing import List, Dict, Any, Optional
import time
from urllib.parse import quote_plus

class GoogleSearchAPI:
    """Google Custom Search JSON API wrapper (free tier)"""
    
    BASE_URL = "https://www.googleapis.com/customsearch/v1"
    
    def __init__(self, api_key: str, cse_id: str):
        self.api_key = api_key
        self.cse_id = cse_id
        
    def search(self, query: str, num_results: int = 10) -> List[Dict]:
        """Perform Google search"""
        if not self.api_key or not self.cse_id:
            print("Warning: Google API credentials not set")
            return []
        
        try:
            params = {
                'key': self.api_key,
                'cx': self.cse_id,
                'q': query,
                'num': min(num_results, 10),  # Max 10 for free tier
                'start': 1
            }
            
            response = requests.get(self.BASE_URL, params=params, timeout=30)
            response.raise_for_status()
            
            data = response.json()
            results = []
            
            if 'items' in data:
                for item in data['items']:
                    result = {
                        'title': item.get('title', ''),
                        'link': item.get('link', ''),
                        'snippet': item.get('snippet', '')
                    }
                    results.append(result)
            
            return results
            
        except Exception as e:
            print(f"Google search error: {e}")
            return []
    
    def find_companies(self, industry_keywords: List[str], location: str = "") -> List[Dict]:
        """Find companies using industry keywords"""
        all_results = []
        
        for keyword in industry_keywords[:3]:  # Limit to 3 keywords to save quota
            query = f"{keyword} {location} company"
            results = self.search(query, num_results=5)
            
            for result in results:
                company_info = self._extract_company_info(result)
                if company_info:
                    all_results.append(company_info)
            
            time.sleep(1)  # Rate limiting
        
        return all_results[:10]  # Return top 10
    
    def _extract_company_info(self, search_result: Dict) -> Optional[Dict]:
        """Extract company info from search result"""
        title = search_result.get('title', '')
        snippet = search_result.get('snippet', '')
        url = search_result.get('link', '')
        
        # Simple heuristic to identify company names
        # Remove common suffixes from title
        company_name = title
        suffixes = [' - Home', ' | Official Site', ' - Official Website', 
                   ' Inc.', ' LLC', ' Corp.', ' Ltd.']
        
        for suffix in suffixes:
            if suffix in company_name:
                company_name = company_name.split(suffix)[0]
        
        # Extract location from snippet
        location = ""
        location_keywords = ['based in', 'headquartered in', 'located in', 'operates in']
        
        for keyword in location_keywords:
            if keyword in snippet.lower():
                start_idx = snippet.lower().find(keyword) + len(keyword)
                location_text = snippet[start_idx:start_idx+50]
                location = location_text.split('.')[0].strip()
                break
        
        if company_name and len(company_name) > 3:
            return {
                'name': company_name.strip(),
                'website': url,
                'description': snippet,
                'location': location or 'Not specified'
            }
        
        return None


class PublicDataSources:
    """Use publicly available data sources"""
    
    @staticmethod
    def get_sample_companies(company_type: str) -> List[Dict]:
        """Get sample companies from embedded knowledge"""
        
        # Sample customer companies (automotive dealerships)
        customers = [
            {
                "name": "AutoNation",
                "website": "https://www.autonation.com",
                "locations": "United States (300+ locations nationwide)",
                "size": "Large",
                "description": "Largest automotive retailer in the US"
            },
            {
                "name": "Penske Automotive Group",
                "website": "https://www.penskeautomotive.com",
                "locations": "US, UK, Germany, Japan",
                "size": "Large",
                "description": "International automotive retailer with diverse brand portfolio"
            },
            {
                "name": "Lithia Motors",
                "website": "https://www.lithia.com",
                "locations": "United States",
                "size": "Large",
                "description": "One of the largest automotive retailers in North America"
            },
            {
                "name": "Sonic Automotive",
                "website": "https://www.sonicautomotive.com",
                "locations": "United States",
                "size": "Large",
                "description": "Fortune 500 automotive retailer"
            },
            {
                "name": "Group 1 Automotive",
                "website": "https://www.group1auto.com",
                "locations": "US, UK, Brazil",
                "size": "Large",
                "description": "International automotive retailer"
            },
            {
                "name": "Asbury Automotive Group",
                "website": "https://www.asburyauto.com",
                "locations": "United States",
                "size": "Large",
                "description": "Automotive retail and service company"
            },
            {
                "name": "CarMax",
                "website": "https://www.carmax.com",
                "locations": "United States",
                "size": "Large",
                "description": "Used car retailer with focus on technology"
            },
            {
                "name": "Carvana",
                "website": "https://www.carvana.com",
                "locations": "United States",
                "locations": "Online + physical locations",
                "size": "Large",
                "description": "Online used car retailer"
            },
            {
                "name": "Van Tuyl Group",
                "website": "https://www.vantuylgroup.com",
                "locations": "United States",
                "size": "Medium",
                "description": "Privately held automotive retailer"
            },
            {
                "name": "Hendrick Automotive Group",
                "website": "https://www.hendrickauto.com",
                "locations": "United States",
                "size": "Large",
                "description": "One of the largest privately owned dealer groups"
            }
        ]
        
        # Sample partner companies (technology providers)
        partners = [
            {
                "name": "CDK Global",
                "website": "https://www.cdkglobal.com",
                "locations": "Global (focus North America)",
                "size": "Large",
                "description": "Legacy DMS provider with deep OEM integrations"
            },
            {
                "name": "Tekion",
                "website": "https://www.tekion.com",
                "locations": "USA, India",
                "size": "Medium",
                "description": "Cloud-native automotive retail platform"
            },
            {
                "name": "DealerSocket",
                "website": "https://www.dealersocket.com",
                "locations": "United States",
                "size": "Medium",
                "description": "Dealership CRM and management software"
            },
            {
                "name": "Reynolds & Reynolds",
                "website": "https://www.reyrey.com",
                "locations": "United States, Canada",
                "size": "Large",
                "description": "Automotive retail software and services"
            },
            {
                "name": "Dealertrack",
                "website": "https://www.dealertrack.com",
                "locations": "United States",
                "size": "Large",
                "description": "Dealership management solutions"
            },
            {
                "name": "Auto/Mate",
                "website": "https://www.automate.com",
                "locations": "United States",
                "size": "Small",
                "description": "Dealer management systems"
            },
            {
                "name": "VinSolutions",
                "website": "https://www.vinsolutions.com",
                "locations": "United States",
                "size": "Medium",
                "description": "Cox Automotive dealership software"
            },
            {
                "name": "Dealer-FX",
                "website": "https://www.dealer-fx.com",
                "locations": "North America",
                "size": "Medium",
                "description": "Service lane technology solutions"
            },
            {
                "name": "ECU Communications",
                "website": "https://www.ecu.com",
                "locations": "United States",
                "size": "Small",
                "description": "Automotive digital marketing"
            },
            {
                "name": "Gubagoo",
                "website": "https://www.gubagoo.com",
                "locations": "United States",
                "size": "Small",
                "description": "Digital retailing and chat solutions"
            }
        ]
        
        if company_type.lower() == "customers":
            return customers
        elif company_type.lower() == "partners":
            return partners
        else:
            return []
    
    @staticmethod
    def search_public_directory(query: str) -> List[Dict]:
        """Simulate search in public business directories"""
        # This would integrate with real APIs in production
        # For now, return sample data based on query
        return []


class WebScraper:
    """Simple web scraper for company websites (respects robots.txt)"""
    
    @staticmethod
    def get_company_info(url: str) -> Dict:
        """Extract basic info from company website"""
        try:
            headers = {
                'User-Agent': 'Mozilla/5.0 (compatible; DiscoveryBot/1.0; +http://example.com/bot)'
            }
            response = requests.get(url, headers=headers, timeout=10)
            response.raise_for_status()
            
            soup = BeautifulSoup(response.content, 'html.parser')
            
            # Extract title
            title = soup.title.string if soup.title else ""
            
            # Try to find company description
            description = ""
            meta_desc = soup.find('meta', attrs={'name': 'description'})
            if meta_desc:
                description = meta_desc.get('content', '')
            
            return {
                'title': title,
                'description': description[:200]  # Truncate
            }
            
        except Exception as e:
            print(f"Web scraping error for {url}: {e}")
            return {}