import os
from typing import Dict, Any

# Configuration settings
class Config:
    # LLM Settings
    LLM_MODEL = "tinyllama:1.1b"  # Small model that runs well on CPU
    EMBEDDING_MODEL = "all-MiniLM-L6-v2"  # Small but effective embedding model
    
    # API Keys (free services)
    GOOGLE_API_KEY = os.getenv("GOOGLE_API_KEY", "")
    GOOGLE_CSE_ID = os.getenv("GOOGLE_CSE_ID", "")
    
    # Search Settings
    MAX_RESULTS = 10
    SEARCH_TIMEOUT = 30
    
    # Company size definitions
    COMPANY_SIZE_THRESHOLDS = {
        'Small': (1, 100),
        'Medium': (101, 1000),
        'Large': (1001, float('inf'))
    }
    
    # Industry keywords for automotive retail
    INDUSTRY_KEYWORDS = {
        'customers': [
            'automotive dealership', 'car dealership', 'auto dealer',
            'franchise dealer', 'automotive retail', 'car retail',
            'automotive group', 'dealership network'
        ],
        'partners': [
            'dms software', 'automotive software', 'dealership software',
            'crm automotive', 'auto retail technology', 'automotive saas',
            'vehicle software', 'dealership management system'
        ]
    }
    
    # Geographic focus
    TARGET_REGIONS = ['North America', 'United States', 'Canada', 'Mexico']
    
    @staticmethod
    def get_axelwave_profile() -> Dict[str, Any]:
        """Return structured Axelwave profile"""
        return {
            "company": "Axelwave Technologies",
            "product": "DealerFlow Cloud",
            "industry": "Automotive Retail SaaS",
            "target_customers": [
                "Franchise dealer groups (5-200 rooftops)",
                "Single-point franchises seeking cloud-native operations",
                "OEM programs requiring digital retail & data exchange"
            ],
            "key_features": [
                "Unified sales, F&I, service, parts, CRM, accounting",
                "AI copilots for desking and service triage",
                "Open APIs (REST/GraphQL), events, SDKs",
                "Modern UX and mobile-first workflows"
            ],
            "geographic_focus": "North America first, then EU/UK",
            "pain_points_solved": [
                "Fragmented legacy DMS/CRM/accounting systems",
                "Limited interoperability between systems",
                "Slow month-end close processes",
                "Poor customer experience due to disconnected systems"
            ]
        }