# EVAI_TakeHome
TThis repository is a take home assignment by EVAI.

# Problem
An AI-powered prototype solution that helps Axelwave Technologies discover potential customers and partners in the automotive retail industry. The system uses local AI models to analyze business opportunities and generate actionable insights.

# Features
- Customer Discovery: Find 10 automotive dealerships most likely to buy Axelwave's DealerFlow Cloud platform.
-Partner Discovery: Identify 10 technology companies that could partner with Axelwave to deliver their solution.
- AI-Powered Analysis: Generate rationales for each company selection using local LLMs.

# Architecture
┌─────────────────────────────────────┐
│      Streamlit Web Interface        │
├─────────────────────────────────────┤
│     Discovery Engine (Orchestrator) │
├─────────────────────────────────────┤
│           AI Agents Layer           │
│  • Search Agent                     │
│  • Analysis Agent                   │
│  • Validation Agent                 │
├─────────────────────────────────────┤
│      Data Sources & Local AI        │
│  • Built-in industry knowledge      │
│  • Local LLM (Transformers)         │
│  • In-memory vector storage         │
└─────────────────────────────────────┘

# Tech Stack
- Frontend: Streamlit
- AI/ML: tinyllama:1.1b
- Data Processing: Pandas, NumPy

# Structure
EVAI_TakeHome/
├── app.py                                                               # Main Streamlit application
├── discovery_engine.py                                                  # Core discovery logic orchestrator
├── agents.py                                                            # AI agents (Search, Analysis, Validation)
├── models.py                                                            # AI models (LLM, Embeddings, Vector Store)
├── config.py                                                            # Configuration and constants
├── data_sources.py                                                      # Data source interfaces
├── requirements.txt                                                     # Python dependencies
├── README.md                                                            # This file
└── chroma_data/                                                         # Optional vector database storage
└── Fictitious_Company_AxelwaveTechnologies_DemoData/                    # Given documents
└── ProblemStatement/
└── .gitignore

# Setup Instructions
I used Python3.10 and ran the experiment locally (CPU).
1. Clone the repository
2. Go to the folder EVAI_TakeHome by:
    cd D:\EVAI_TakeHome
3. Install dependencies:
    pip install -r requirements.txt
4. Run the below command to start:
    streamlit run app.py

# Using the Application
After completing step 4 above, the application will open in the local browser. You can choose "Potential Customers" or "Potential Partners" and click "Discover Companies" to get the output list. You can then export the results as a JSON file.