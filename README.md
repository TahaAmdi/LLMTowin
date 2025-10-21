# 🧠 LLMTowin  
> Retrieval-Augmented LLM System for Intelligent Content Crawling & Semantic Search

LLMTowin is a modular LLM engineering framework designed to crawl, embed, and semantically retrieve user-generated content from multiple sources (LinkedIn, GitHub, Medium, etc.) using a Retrieval-Augmented Generation (RAG) pipeline.  

It follows the architectural patterns described in *The LLM Engineers Handbook*, combining:
- MongoDB for NoSQL persistence  
- Qdrant for vector similarity search  
- SentenceTransformers for embeddings  
- FastAPI and Poetry for deployment and environment management  

---

## 🚀 Features

### 🕷️ Crawlers  
Located in llm_engineering/application/crawlers/  

Crawlers extract public data from multiple platforms:
- linkedin.py → posts, comments, and profiles  
- medium.py → articles and topics  
- github.py → repositories and project metadata  

A central dispatcher.py orchestrates these crawlers and passes the data to the ETL pipeline.

---

### 🧩 Networks  
Located in llm_engineering/application/networks/

- embeddings.py → loads a SentenceTransformer model (default: `all-MiniLM-L6-v2`) and generates embeddings.  
- base.py → defines a SingletonMeta class to prevent redundant model loading across the system.  

Supported models:
- SentenceTransformers  
- CrossEncoders  
- HuggingFace AutoTokenizer  

---

### 🧠 Domain Models  
Located in llm_engineering/domain/

Defines core data abstractions and shared types:
- documents.py → Base document structure for MongoDB  
- types.py → Enum (`DataCategory`) for dataset tags like posts, articles, repositories  
- exceptions.py → Custom exception handling and structured logging  

---

### 🧱 Infrastructure  
Located in llm_engineering/infrastructure/db/

- mongo.py → manages database connections and persistence operations  
- qdrant.py → handles vector DB interactions and similarity searches  

---

### ⚙️ Pipelines  
Located in pipelines/ and steps/etl/

Implements the ETL (Extract–Transform–Load) logic:  
- digital_data_etl.py → orchestrates the end-to-end data ingestion & embedding pipeline  
- crawl_links.py → manages crawl queue and scheduling  
- get_or_create_user.py → ensures user data is created or fetched across MongoDB & Qdrant  

---

## 🧬 RAG Pipeline Overview

The RAG system connects three main components:

1. Ingestion Pipeline → crawls and embeds external data into Qdrant  
2. Retrieval Pipeline → queries Qdrant for semantically relevant vectors  
3. Generation Pipeline → injects retrieved data into the LLM prompt to generate contextual responses  

---

### 🔄 Example Flow
Example:  
> “Summarize my most engaging GitHub projects based on semantic similarity.”

The system retrieves your repositories, embeds descriptions, and returns summarized insights using the RAG pipeline.

---

## 🧩 Tech Stack

| Component | Library |
|------------|----------|
| Framework | FastAPI, Poetry |
| Data Storage | MongoDB |
| Vector DB | Qdrant |
| Embeddings | SentenceTransformers, CrossEncoder |
| Tokenization | HuggingFace Transformers |
| Pipeline Orchestration | ZenML |
| Logging | Loguru |
| ETL | BeautifulSoup, TQDM, Requests |

---

## ⚡ Setup & Run

```bash
# 1️⃣ Install dependencies
poetry install

# 2️⃣ Run the digital ETL pipeline
poetry run python pipelines/digital_data_etl.py

# 3️⃣ Generate sentence embeddings
poetry run python llm_engineering/application/networks/embeddings.py


---
LLMTowin/
│
├── llm_engineering/
│   ├── application/
│   │   ├── crawlers/
│   │   └── networks/
│   ├── domain/
│   └── infrastructure/
│       ├── db/
│       └── aws/
│
├── pipelines/
│   ├── digital_data_etl.py
│   └── steps/etl/
│
├── pyproject.toml
└── README.md

MSc Artificial Intelligence – University of Hull 🇬🇧
Exploring the intersection of Transformers, RAG systems, and applied AI engineering.

⚖️ License

MIT License © 2025 David AhmadiShahraki
