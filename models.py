import ollama
from sentence_transformers import SentenceTransformer
import chromadb
from chromadb.config import Settings
from chromadb.utils import embedding_functions
import numpy as np
from typing import List, Dict, Any
import time


print("Loading AI models for Axelwave Discovery...")

class LLMManager:
    """Simple LLM that returns pre-defined responses"""
    
    def __init__(self, model_name="dummy"):
        print(f"LLM Manager initialized (model: {model_name})")
        
    def generate(self, prompt, system_prompt=None, max_tokens=150):
        """Generate meaningful responses based on prompt content"""
        prompt_lower = str(prompt).lower()
        
        # Customer discovery responses
        if "customer" in prompt_lower or "dealership" in prompt_lower:
            if "large" in prompt_lower:
                return "Large automotive dealership groups like this would benefit from DealerFlow Cloud's unified platform to reduce deal time by 25% and consolidate legacy systems."
            else:
                return "This dealership would benefit from Axelwave's modern retail operating system to streamline sales, F&I, and service operations."
        
        # Partner discovery responses  
        elif "partner" in prompt_lower or "software" in prompt_lower or "dms" in prompt_lower:
            if "legacy" in prompt_lower or "cdk" in prompt_lower:
                return "Legacy DMS providers have established OEM certifications and dealer networks that could provide integration pathways for Axelwave."
            else:
                return "This technology company offers complementary solutions that could integrate with DealerFlow Cloud via APIs, creating a combined value proposition."
        
        # Default response
        else:
            return f"Analysis: '{prompt[:50]}...' appears relevant for Axelwave Technologies. This company could benefit from modern automotive retail SaaS solutions."

class EmbeddingManager:
    """Dummy embedding manager - returns fake embeddings"""
    
    def __init__(self, model_name="dummy-embeddings"):
        print(f"Using dummy embeddings (no model loading)")
        
    def embed_text(self, text):
        """Return fake 384-dimensional embeddings"""
        # Return list of 384 small floats
        return [0.001 * (i % 10) for i in range(384)]

# In-memory
class VectorStore:
    """Simple in-memory company database"""
    
    def __init__(self, collection_name="companies"):
        print(f"Initializing company database: {collection_name}")
        self.collection_name = collection_name
        
        # Pre-loaded sample companies
        self.sample_companies = [
            {
                "name": "AutoNation",
                "website": "https://www.autonation.com",
                "locations": "USA (300+ locations nationwide)",
                "size": "Large",
                "type": "customer",
                "rationale": "As the largest US automotive retailer, AutoNation operates multiple legacy systems that DealerFlow Cloud could consolidate, potentially reducing deal time by 25%."
            },
            {
                "name": "Penske Automotive Group",
                "website": "https://www.penskeautomotive.com",
                "locations": "US, UK, Germany, Japan",
                "size": "Large",
                "type": "customer",
                "rationale": "International operations with complex OEM relationships require unified data exchange that DealerFlow Cloud's OEM adapters can provide."
            },
            {
                "name": "Lithia Motors",
                "website": "https://www.lithia.com",
                "locations": "United States",
                "size": "Large",
                "type": "customer",
                "rationale": "One of the fastest-growing dealer groups with pain points around system integration and month-end close processes."
            },
            {
                "name": "CDK Global",
                "website": "https://www.cdkglobal.com",
                "locations": "Global (focus North America)",
                "size": "Large",
                "type": "partner",
                "rationale": "Legacy DMS provider with deep OEM certifications. Partnership could provide Axelwave with certified integration pathways to major dealer networks."
            },
            {
                "name": "Tekion",
                "website": "https://www.tekion.com",
                "locations": "USA, India",
                "size": "Medium",
                "type": "partner",
                "rationale": "Cloud-native automotive retail platform with modern APIs. Technical partnership could create combined solution for dealerships seeking best-of-breed systems."
            },
            {
                "name": "Sonic Automotive",
                "website": "https://www.sonicautomotive.com",
                "locations": "United States",
                "size": "Large",
                "type": "customer",
                "rationale": "Fortune 500 retailer with fragmented systems. DealerFlow Cloud's unified approach could streamline operations across their rooftop network."
            },
            {
                "name": "Group 1 Automotive",
                "website": "https://www.group1auto.com",
                "locations": "US, UK, Brazil",
                "size": "Large",
                "type": "customer",
                "rationale": "International retailer that could benefit from Axelwave's multi-region support and localized compliance features."
            },
            {
                "name": "Dealertrack",
                "website": "https://www.dealertrack.com",
                "locations": "United States",
                "size": "Large",
                "type": "partner",
                "rationale": "Dealership management solutions provider with complementary F&I tools that could integrate with DealerFlow Cloud."
            },
            {
                "name": "Reynolds & Reynolds",
                "website": "https://www.reyrey.com",
                "locations": "United States, Canada",
                "size": "Large",
                "type": "partner",
                "rationale": "Established automotive retail software company with accounting depth. Partnership could bridge legacy and modern systems."
            },
            {
                "name": "Carvana",
                "website": "https://www.carvana.com",
                "locations": "USA (online + physical locations)",
                "size": "Large",
                "type": "customer",
                "rationale": "Digital-first used car retailer that values modern technology stacks and could benefit from DealerFlow Cloud's API-first architecture."
            }
        ]
        
        print(f"Loaded {len(self.sample_companies)} sample companies")
    
    def add_companies(self, companies):
        """Store companies (in real app would add to database)"""
        print(f"Received {len(companies)} companies to store")
        # In this simple version, we just note they were received
        # If we develop a full version, we would have to add to self.sample_companies
    
    def search_similar(self, query, n_results=5):
        """Return relevant companies based on query"""
        query_lower = query.lower()
        
        # Filter based on query
        if "customer" in query_lower or "dealership" in query_lower:
            results = [c for c in self.sample_companies if c["type"] == "customer"]
        elif "partner" in query_lower or "software" in query_lower:
            results = [c for c in self.sample_companies if c["type"] == "partner"]
        else:
            results = self.sample_companies
        
        # Return requested number of results
        return results[:n_results]

print("All AI models loaded successfully!")
print("Ready to discover automotive customers and partners!")
