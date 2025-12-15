from typing import List, Dict, Any
from agents import SearchAgent, AnalysisAgent, ValidationAgent, Company
from data_sources import GoogleSearchAPI, PublicDataSources, WebScraper
from models import LLMManager
from config import Config
import json

class DiscoveryEngine:
    """Main engine for company discovery"""
    
    def __init__(self):
        self.config = Config()
        self.llm_manager = LLMManager(self.config.LLM_MODEL)
        self.search_agent = SearchAgent(self.llm_manager)
        self.analysis_agent = AnalysisAgent(self.llm_manager)
        self.validation_agent = ValidationAgent(self.llm_manager)
        
        # Initialize data sources
        self.google_api = GoogleSearchAPI(
            self.config.GOOGLE_API_KEY,
            self.config.GOOGLE_CSE_ID
        )
        self.public_data = PublicDataSources()
        self.scraper = WebScraper()
        
        # Cache for results
        self.cache = {}
    
    def discover(self, query_type: str, use_google: bool = False) -> List[Company]:
        """Main discovery method"""
        
        cache_key = f"{query_type}_{use_google}"
        if cache_key in self.cache:
            return self.cache[cache_key]
        
        print(f"Discovering {query_type} companies...")
        
        # Get sample companies as base
        sample_companies = self.public_data.get_sample_companies(query_type)
        
        # If Google API is available and requested, enhance with search
        if use_google and self.google_api.api_key and self.google_api.cse_id:
            print("Enhancing with Google search...")
            search_companies = self._enhance_with_search(query_type)
            # Merge with sample companies
            all_companies = sample_companies + search_companies[:5]
        else:
            all_companies = sample_companies
        
        # Enrich and analyze each company
        enriched_companies = []
        for company_data in all_companies[:self.config.MAX_RESULTS]:
            try:
                enriched = self.analysis_agent.enrich_company(company_data, query_type)
                enriched_companies.append(enriched)
            except Exception as e:
                print(f"Error enriching company {company_data.get('name')}: {e}")
                continue
        
        # Rank companies
        ranked_companies = self.analysis_agent.rank_companies(enriched_companies)
        
        # Cache results
        self.cache[cache_key] = ranked_companies
        
        return ranked_companies
    
    def _enhance_with_search(self, query_type: str) -> List[Dict]:
        """Enhance company list with Google search results"""
        
        if query_type.lower() == "customers":
            keywords = self.config.INDUSTRY_KEYWORDS['customers']
        else:
            keywords = self.config.INDUSTRY_KEYWORDS['partners']
        
        search_results = []
        for region in self.config.TARGET_REGIONS[:2]:  # Limit to 2 regions
            companies = self.google_api.find_companies(keywords, region)
            search_results.extend(companies)
        
        # Deduplicate
        unique_companies = []
        seen_names = set()
        
        for company in search_results:
            if company['name'] not in seen_names:
                seen_names.add(company['name'])
                unique_companies.append(company)
        
        return unique_companies
    
    def get_results_as_dict(self, companies: List[Company]) -> List[Dict]:
        """Convert Company objects to dictionaries"""
        return [
            {
                "Company Name": company.name,
                "Website URL": company.website,
                "Locations": company.locations,
                "Estimated Size": company.size,
                "Rationale": company.rationale,
                "Type": company.type,
                "Confidence": f"{company.confidence:.1%}"
            }
            for company in companies
        ]
    
    def export_results(self, companies: List[Company], format: str = "json") -> str:
        """Export results in specified format"""
        company_dicts = self.get_results_as_dict(companies)
        
        if format.lower() == "json":
            return json.dumps(company_dicts, indent=2)
        elif format.lower() == "csv":
            import csv
            import io
            
            output = io.StringIO()
            writer = csv.DictWriter(output, fieldnames=company_dicts[0].keys())
            writer.writeheader()
            writer.writerows(company_dicts)
            return output.getvalue()
        else:
            return str(company_dicts)