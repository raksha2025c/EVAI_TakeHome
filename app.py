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

import streamlit as st
from discovery_engine import DiscoveryEngine
from config import Config
import pandas as pd
import json

# Page configuration - KEEP THIS AT MODULE LEVEL
st.set_page_config(
    page_title="Axelwave Company Discovery",
    page_icon="🚗",
    layout="wide"
)

st.markdown("""
<style>
    .main-header { font-size: 2.5rem; color: #2563eb; text-align: center; margin-bottom: 2rem; }
    .company-card { background-color: #f8fafc; padding: 1rem; border-radius: 0.5rem; border-left: 4px solid #2563eb; margin-bottom: 1rem; }
</style>
""", unsafe_allow_html=True)

if 'discovery_engine' not in st.session_state:
    st.session_state.discovery_engine = None
if 'results' not in st.session_state:
    st.session_state.results = None
if 'search_type' not in st.session_state:
    st.session_state.search_type = "customers"

# Helper functions
def initialize_engine():
    """Initialize DiscoveryEngine once and cache it"""
    if st.session_state.discovery_engine is None:
        with st.spinner("Initializing AI engine..."):
            st.session_state.discovery_engine = DiscoveryEngine()
    return st.session_state.discovery_engine

def perform_search(search_type, use_google=False):
    """Perform search and cache results"""
    engine = initialize_engine()
    
    with st.spinner(f"Discovering {search_type}..."):
        companies = engine.discover(search_type, use_google=use_google)
        st.session_state.results = engine.get_results_as_dict(companies)
    
    return st.session_state.results

def main():
    """Main Streamlit app"""
    
    # Header
    st.markdown('<h1 class="main-header">Axelwave Company Discovery</h1>', unsafe_allow_html=True)
    st.markdown("Discover potential customers and partners for Axelwave Technologies")
    
    # Sidebar
    with st.sidebar:
        st.image("https://img.icons8.com/color/96/000000/car--v1.png", width=80)
        st.markdown("### Discovery Settings")
        
        # Radio buttons for search type
        search_type = st.radio(
            "Discover:",
            ["Potential Customers", "Potential Partners"],
            index=0 if st.session_state.search_type == "customers" else 1
        )
        
        # Simple interface
        if st.button("Discover Companies", type="primary", use_container_width=True):
            # Convert to simple type
            simple_type = "customers" if "Customers" in search_type else "partners"
            st.session_state.search_type = simple_type
            
            # Perform search
            results = perform_search(simple_type, use_google=False)
            
            if results:
                st.success(f"Found {len(results)} companies!")
    
    # Main content
    if st.session_state.results:
        st.markdown(f"### Results: {len(st.session_state.results)} Companies Found")
        
        # Display as table
        df = pd.DataFrame(st.session_state.results)
        st.dataframe(df, use_container_width=True)
        
        # Export options
        col1, col2 = st.columns(2)
        with col1:
            if st.button("Export as JSON"):
                json_data = json.dumps(st.session_state.results, indent=2)
                st.download_button(
                    label="Download JSON",
                    data=json_data,
                    file_name=f"axelwave_{st.session_state.search_type}.json",
                    mime="application/json"
                )
        
        # Display as cards
        st.markdown("### Company Details")
        for idx, company in enumerate(st.session_state.results):
            with st.expander(f"{idx+1}. {company['Company Name']}"):
                st.markdown(f"**Website:** {company['Website URL']}")
                st.markdown(f"**Locations:** {company['Locations']}")
                st.markdown(f"**Size:** {company['Estimated Size']}")
                st.markdown(f"**Rationale:** {company['Rationale']}")
    else:
        # Welcome screen
        st.markdown("""
        ### Welcome to Axelwave Company Discovery
        
        This AI-powered tool helps identify:
        - **Potential Customers**: Automotive dealerships that could benefit from DealerFlow Cloud
        - **Potential Partners**: Technology companies that could integrate with Axelwave's platform
        
        **How to use:**
        1. Select "Potential Customers" or "Potential Partners" in the sidebar
        2. Click "Discover Companies"
        3. View and export the results
        
        **Sample companies you'll discover:**
        - AutoNation, Penske Automotive, Lithia Motors (Customers)
        - CDK Global, Tekion, Dealertrack (Partners)
        """)

if __name__ == "__main__":
    main()
