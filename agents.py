from typing import List, Dict, Any, Optional
from dataclasses import dataclass
import re
from models import LLMManager, EmbeddingManager, VectorStore
from config import Config

@dataclass
class Company:
    """Data class for company information"""
    name: str
    website: str
    locations: str
    size: str  # Small, Medium, Large
    rationale: str
    type: str  # customer or partner
    confidence: float = 0.0


class SearchAgent:
    """Agent responsible for finding companies"""
    
    def __init__(self, llm_manager: LLMManager):
        self.llm = llm_manager
        self.config = Config()
    
    def find_companies(self, company_type: str, industry_focus: str = None) -> List[Dict]:
        """Find companies based on type and industry focus"""
        
        if company_type.lower() == "customers":
            keywords = self.config.INDUSTRY_KEYWORDS['customers']
            prompt = f"""Find automotive dealership companies that would benefit from {self.config.get_axelwave_profile()['product']}.
            
            Target companies should:
            1. Be automotive retailers or dealership groups
            2. Operate in {', '.join(self.config.TARGET_REGIONS)}
            3. Likely use legacy DMS/CRM systems
            4. Have pain points around system integration
            
            Provide a list of potential companies."""
            
        else:  # partners
            keywords = self.config.INDUSTRY_KEYWORDS['partners']
            prompt = f"""Find technology companies that could partner with {self.config.get_axelwave_profile()['company']}.
            
            Target companies should:
            1. Provide software to automotive dealerships
            2. Have complementary products/services
            3. Operate in {', '.join(self.config.TARGET_REGIONS)}
            4. Benefit from integration with {self.config.get_axelwave_profile()['product']}
            
            Provide a list of potential partner companies."""
        
        # Use LLM to generate company names based on knowledge
        response = self.llm.generate(prompt, system_prompt="You are a business research assistant.")
        
        # Parse response to extract company names
        companies = self._parse_llm_response(response, company_type)
        
        return companies
    
    def _parse_llm_response(self, response: str, company_type: str) -> List[Dict]:
        """Parse LLM response to extract company information"""
        companies = []
        
        # Look for numbered lists or bullet points
        lines = response.split('\n')
        
        for line in lines:
            line = line.strip()
            
            # Skip empty lines and headers
            if not line or ':' in line and len(line.split(':')) > 2:
                continue
            
            # Check if line looks like a company entry
            if re.match(r'^\d+\.\s+', line) or re.match(r'^[-*•]\s+', line):
                # Remove numbering/bullets
                clean_line = re.sub(r'^\d+\.\s+', '', line)
                clean_line = re.sub(r'^[-*•]\s+', '', clean_line)
                
                # Try to extract company name (first part before common separators)
                name_parts = re.split(r'[–—:-]', clean_line, 1)
                company_name = name_parts[0].strip()
                
                if company_name and len(company_name) > 2:
                    companies.append({
                        'name': company_name,
                        'type': company_type,
                        'source': 'llm_generated'
                    })
        
        return companies[:10]  # Return top 10


class AnalysisAgent:
    """Agent responsible for analyzing and enriching company data"""
    
    def __init__(self, llm_manager: LLMManager):
        self.llm = llm_manager
        self.embedding_manager = EmbeddingManager()
        self.vector_store = VectorStore()
        self.config = Config()
    
    def enrich_company(self, company_data: Dict, company_type: str) -> Company:
        """Enrich company data with additional information"""
        
        # Generate rationale using LLM
        rationale = self._generate_rationale(company_data, company_type)
        
        # Estimate company size
        size = self._estimate_size(company_data)
        
        # Create Company object
        company = Company(
            name=company_data.get('name', 'Unknown'),
            website=company_data.get('website', ''),
            locations=company_data.get('locations', 'Not specified'),
            size=size,
            rationale=rationale,
            type=company_type,
            confidence=self._calculate_confidence(company_data)
        )
        
        return company
    
    def _generate_rationale(self, company_data: Dict, company_type: str) -> str:
        """Generate rationale for why this company is relevant"""
        
        axelwave_profile = self.config.get_axelwave_profile()
        
        if company_type.lower() == "customers":
            prompt = f"""Why would {company_data.get('name', 'this company')} be a good customer for {axelwave_profile['company']}?

            Axelwave Profile:
            - Product: {axelwave_profile['product']}
            - Industry: {axelwave_profile['industry']}
            - Key Features: {', '.join(axelwave_profile['key_features'][:3])}
            - Pain Points Solved: {', '.join(axelwave_profile['pain_points_solved'][:3])}

            Company: {company_data.get('name', 'Unknown')}
            Description: {company_data.get('description', 'Not available')}
            Locations: {company_data.get('locations', 'Not specified')}

            Provide a concise rationale (2-3 sentences)."""
        else:
            prompt = f"""Why would {company_data.get('name', 'this company')} be a good partner for {axelwave_profile['company']}?

            Axelwave Profile:
            - Product: {axelwave_profile['product']}
            - Industry: {axelwave_profile['industry']}
            - Key Features: {', '.join(axelwave_profile['key_features'][:3])}

            Company: {company_data.get('name', 'Unknown')}
            Description: {company_data.get('description', 'Not available')}
            Locations: {company_data.get('locations', 'Not specified')}

            Provide a concise rationale (2-3 sentences)."""
        
        rationale = self.llm.generate(prompt, max_tokens=200)
        return rationale or "Relevance analysis not available."
    
    def _estimate_size(self, company_data: Dict) -> str:
        """Estimate company size based on available data"""
        name = company_data.get('name', '').lower()
        description = company_data.get('description', '').lower()
        
        # Simple heuristics for size estimation
        size_keywords = {
            'Large': ['fortune 500', 'global', 'international', 'largest', 'nationwide', 'multinational'],
            'Medium': ['regional', 'multiple locations', 'growing', 'expanding'],
            'Small': ['local', 'family-owned', 'independent', 'boutique']
        }
        
        for size, keywords in size_keywords.items():
            for keyword in keywords:
                if keyword in name or keyword in description:
                    return size
        
        # Default to Medium if unknown
        return "Medium"
    
    def _calculate_confidence(self, company_data: Dict) -> float:
        """Calculate confidence score for company data"""
        confidence = 0.5  # Base confidence
        
        # Increase confidence based on data completeness
        if company_data.get('website'):
            confidence += 0.2
        if company_data.get('locations') and company_data['locations'] != 'Not specified':
            confidence += 0.15
        if company_data.get('description') and len(company_data['description']) > 20:
            confidence += 0.15
        
        return min(confidence, 1.0)
    
    def rank_companies(self, companies: List[Company]) -> List[Company]:
        """Rank companies by relevance"""
        # Simple ranking by confidence
        return sorted(companies, key=lambda x: x.confidence, reverse=True)


class ValidationAgent:
    """Agent responsible for validating company data"""
    
    def __init__(self, llm_manager: LLMManager):
        self.llm = llm_manager
    
    def validate_company(self, company: Company) -> Dict:
        """Validate company information"""
        
        prompt = f"""Validate this company information:
        
        Name: {company.name}
        Website: {company.website}
        Locations: {company.locations}
        Size: {company.size}
        Type: {company.type}
        
        Check if:
        1. This appears to be a real company
        2. The size classification seems reasonable
        3. The locations make sense for this type of business
        4. The company would realistically be in the target market
        
        Provide validation feedback."""
        
        validation = self.llm.generate(prompt, max_tokens=150)
        
        return {
            'is_valid': 'likely real' in validation.lower() or 'appears valid' in validation.lower(),
            'feedback': validation,
            'confidence': 0.7  # Default confidence
        }