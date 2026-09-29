# 🔎 ReviewLens AI

### AI-Powered Customer Review Intelligence Platform

> Transform unstructured customer feedback into **sentiment, themes, complaints, summaries, and traceable evidence** using Microsoft Azure, RAG, and Qwen3 8B.

<p align="center">

![Python](https://img.shields.io/badge/Python-3.11-3776AB?style=for-the-badge&logo=python&logoColor=white)
![FastAPI](https://img.shields.io/badge/FastAPI-Backend-009688?style=for-the-badge&logo=fastapi&logoColor=white)
![Next.js](https://img.shields.io/badge/Next.js-Frontend-000000?style=for-the-badge&logo=next.js&logoColor=white)
![Azure](https://img.shields.io/badge/Microsoft_Azure-Cloud-0078D4?style=for-the-badge&logo=microsoftazure&logoColor=white)
![Qwen](https://img.shields.io/badge/Qwen3-8B-7C3AED?style=for-the-badge)
![PostgreSQL](https://img.shields.io/badge/PostgreSQL-Database-4169E1?style=for-the-badge&logo=postgresql&logoColor=white)

</p>

---

## 🚀 What is ReviewLens AI?

ReviewLens AI is an end-to-end **customer review intelligence platform** that processes customer feedback and converts it into structured, actionable insights.

Instead of manually reading hundreds or thousands of reviews, the system automatically performs:

```text
Reviews
   ↓
Cleaning & Deduplication
   ↓
PII Redaction
   ↓
Sentiment Analysis
   ↓
Vector Embeddings
   ↓
Semantic Retrieval
   ↓
AI Analysis
   ↓
Themes • Complaints • Summary
   ↓
Evidence Linking
   ↓
Dashboard + AI Assistant
🎯 Problem

Organizations receive large amounts of customer feedback, but extracting useful intelligence from it manually is:

⏱️ Time-consuming
📈 Difficult to scale
🔍 Difficult to trace back to source reviews
🧠 Difficult to analyze consistently
📊 Difficult to monitor sentiment changes over time
ReviewLens AI solves this by providing a single pipeline for:

Ingestion → Analysis → Retrieval → Intelligence → Evidence → Monitoring

✨ Key Features
Feature	Description
📥 Review Ingestion	Upload and process customer review datasets
🧹 Cleaning	Normalize and clean review text
♻️ Deduplication	SHA-256 based duplicate review detection
🔐 PII Redaction	Detect and redact personally identifiable information
😊 Sentiment Analysis	Positive, neutral and negative sentiment
🧠 Embeddings	Generate 384-dimensional review embeddings
🔎 Vector Search	Semantic retrieval using Azure AI Search
🏷️ Theme Extraction	Identify recurring customer themes
⚠️ Complaint Detection	Identify common customer complaints
🔗 Evidence Linking	Connect insights back to supporting reviews
🤖 AI Assistant	Ask questions about customer feedback
📊 Validation	Accuracy, precision, recall and F1 evaluation
📉 Drift Monitoring	Monitor changes in negative sentiment
📈 Dashboard	Interactive customer-review analytics
🏗️ Architecture
                         REVIEWLENS AI
                              │
                       Customer Reviews
                              │
                              ▼
                    ┌───────────────────┐
                    │ Azure Blob Storage│
                    └─────────┬─────────┘
                              │
                              ▼
                  Cleaning + Deduplication
                              │
                              ▼
                       PII Redaction
                              │
                              ▼
                    ┌───────────────────┐
                    │ Azure AI Language │
                    └─────────┬─────────┘
                              │
                   ┌──────────┴──────────┐
                   ▼                     ▼
              Sentiment              Embeddings
                                         │
                                         ▼
                               ┌─────────────────┐
                               │ Azure AI Search │
                               └────────┬────────┘
                                        │
                                  Relevant Reviews
                                        │
                                        ▼
                              ┌──────────────────┐
                              │    Qwen3 8B      │
                              │   Local + RAG    │
                              └────────┬─────────┘
                                       │
                     ┌─────────────────┼─────────────────┐
                     ▼                 ▼                 ▼
                  Themes          Complaints          Summary
                     │                 │                 │
                     └─────────────────┼─────────────────┘
                                       ▼
                               Evidence Linking
                                       │
                                       ▼
                               ┌──────────────┐
                               │  PostgreSQL  │
                               └──────┬───────┘
                                      │
                                      ▼
                                FastAPI Backend
                                      │
                                      ▼
                              Next.js Dashboard
                                      │
                                      ▼
                                AI Assistant
                         REVIEWLENS AI
                              │
                       Customer Reviews
                              │
                              ▼
                    ┌───────────────────┐
                    │ Azure Blob Storage│
                    └─────────┬─────────┘
                              │
                              ▼
                  Cleaning + Deduplication
                              │
                              ▼
                       PII Redaction
                              │
                              ▼
                    ┌───────────────────┐
                    │ Azure AI Language │
                    └─────────┬─────────┘
                              │
                   ┌──────────┴──────────┐
                   ▼                     ▼
              Sentiment              Embeddings
                                         │
                                         ▼
                               ┌─────────────────┐
                               │ Azure AI Search │
                               └────────┬────────┘
                                        │
                                  Relevant Reviews
                                        │
                                        ▼
                              ┌──────────────────┐
                              │    Qwen3 8B      │
                              │   Local + RAG    │
                              └────────┬─────────┘
                                       │
                     ┌─────────────────┼─────────────────┐
                     ▼                 ▼                 ▼
                  Themes          Complaints          Summary
                     │                 │                 │
                     └─────────────────┼─────────────────┘
                                       ▼
                               Evidence Linking
                                       │
                                       ▼
                               ┌──────────────┐
                               │  PostgreSQL  │
                               └──────┬───────┘
                                      │
                                      ▼
                                FastAPI Backend
                                      │
                                      ▼
                              Next.js Dashboard
                                      │
                                      ▼
                                AI Assistant
☁️ Microsoft Azure Services
Azure Service	Role
🗄️ Azure Blob Storage	Review file storage
🧠 Azure AI Language	Sentiment + PII detection
🔎 Azure AI Search	Vector search and retrieval
🐘 Azure Database for PostgreSQL	Persistent application database
🔐 Azure Key Vault	Secure secret management
🌐 Azure App Service	Backend hosting
📦 Azure Container Registry	Docker image registry
📊 Application Insights	Application monitoring
📋 Log Analytics	Centralized telemetry
🤖 AI & RAG Pipeline

ReviewLens AI combines semantic retrieval with Qwen3 8B.

Embedding Model
all-MiniLM-L6-v2
Embedding Dimension: 384
Retrieval
User Question
      ↓
Query Embedding
      ↓
Azure AI Search
      ↓
Top Relevant Reviews
      ↓
Evidence Context
      ↓
Qwen3 8B
      ↓
Grounded Answer

The AI assistant uses retrieved customer reviews as evidence for answering questions.

Example

Question

What are the main complaints from customers?

Retrieved evidence

Late delivery
Unresponsive customer support

AI response

The main complaints involve delivery delays
and poor customer support responsiveness.
📊 Evaluation Results

ReviewLens AI includes a labelled sentiment validation dataset.

Sentiment Validation
Metric	Result
🎯 Accuracy	83.33%
🎯 Precision	88.89%
🎯 Recall	83.33%
🎯 F1 Score	82.22%
Validation Dataset
12 labelled reviews

Positive : 4
Neutral  : 4
Negative : 4
📉 Drift Monitoring

The system compares baseline and current sentiment distributions.

Metric	Current Result
Baseline Negative Rate	50%
Current Negative Rate	50%
Rate Change	0%
Drift Detected	No
Detection Threshold	20%

This provides a foundation for monitoring changes in customer sentiment as new review data arrives.

🔗 Evidence-First Intelligence

A major design principle of ReviewLens AI is traceability.

Instead of producing only:

"Customers are unhappy with delivery."

the system can connect the insight to the underlying reviews that support it.

Insight
   │
   ├── Evidence Review 1
   ├── Evidence Review 2
   ├── Evidence Review 3
   └── Evidence Review 4

This makes generated intelligence easier to inspect and validate.

🖥️ Dashboard

The Next.js dashboard provides an interactive view of:

Total reviews
Positive / neutral / negative sentiment
Sentiment distribution
Customer themes
Common complaints
Evidence
Sentiment validation
Drift monitoring
AI Assistant
Dashboard Preview

Add screenshots here after the final dashboard deployment.

docs/
└── screenshots/
    ├── dashboard.png
    ├── insights.png
    ├── validation.png
    └── assistant.png
🛠️ Technology Stack
Backend
Python 3.11
FastAPI
Uvicorn
SQLAlchemy
PostgreSQL
AI / ML
Qwen3 8B
Ollama
Sentence Transformers
all-MiniLM-L6-v2
Azure AI Language
Azure AI Search
Frontend
Next.js
React
TypeScript
Recharts
Lucide React
Cloud
Microsoft Azure
Azure Blob Storage
Azure AI Search
Azure AI Language
Azure PostgreSQL
Azure Key Vault
Azure App Service
Azure Container Registry
Application Insights
Log Analytics
Deployment
Docker
Azure Container Registry
Azure App Service
📁 Project Structure
reviewlens-ai/
│
├── backend/
│   ├── agent/
│   │   └── rag_agent.py
│   │
│   ├── analysis/
│   │   ├── drift.py
│   │   ├── evidence.py
│   │   ├── insights.py
│   │   ├── language.py
│   │   ├── review_pipeline.py
│   │   ├── validation.py
│   │   └── validation_sync.py
│   │
│   ├── ingestion/
│   │   └── cleaning.py
│   │
│   ├── rag/
│   │   ├── index_review.py
│   │   └── retrieve.py
│   │
│   ├── database.py
│   ├── database_sync.py
│   ├── insight_sync.py
│   ├── main.py
│   ├── models.py
│   └── test_keyvault.py
│
├── data/
│   ├── reviews.csv
│   └── validation/
│       └── sentiment_validation.csv
│
├── frontend/
│   └── frontend/
│       ├── app/
│       ├── public/
│       ├── package.json
│       └── Dockerfile
│
├── .dockerignore
├── .gitignore
├── Dockerfile
├── requirements.txt
└── README.md
⚡ Quick Start
Backend
python -m venv .venv
.venv\Scripts\Activate.ps1
pip install -r requirements.txt

Run:

uvicorn backend.main:app --reload

API:

http://127.0.0.1:8000

Swagger:

http://127.0.0.1:8000/docs
Frontend
cd frontend\frontend
npm install
npm run dev

Dashboard:

http://localhost:3000
🔌 API
Endpoint	Purpose
/health	Health check
/reviews	Retrieve reviews
/reviews/upload	Upload reviews
/insights	Retrieve insights
/evidence	Retrieve evidence
/validation	Sentiment validation
/drift	Drift monitoring
/assistant	AI assistant
🔐 Security

ReviewLens AI uses Azure-native security mechanisms.

Azure Key Vault

Database credentials are stored in Azure Key Vault rather than source code.

Managed Identity

Azure services use managed identities where applicable.

PII Protection

Customer PII is detected and redacted before downstream analysis.

Repository Security

Sensitive files are excluded using .gitignore.

.env
*.dump
*.zip
.venv/
node_modules/
.next/
🐳 Container Deployment

The backend and frontend are container-ready.

Application
     ↓
Docker
     ↓
Azure Container Registry
     ↓
Azure App Service

This allows the application to be deployed independently of the local development environment.

🔮 Future Scope
Planned Improvements
☁️ Host Qwen3 8B directly in Azure
📥 Large-scale batch ingestion
📊 Advanced review trend analysis
🧠 Improved theme clustering
⚡ Event-driven ingestion with Azure Functions
🔐 Role-based access control
🔄 Automated CI/CD
📈 Advanced production monitoring
🎓 Microsoft Innovate

ReviewLens AI is developed as part of the Microsoft Innovate project.

The project demonstrates how Microsoft Azure services can be combined with modern AI, RAG, vector search, and cloud-native application architecture to build an end-to-end customer feedback intelligence platform.

⭐ Project Highlights
┌─────────────────────────────────────────────┐
│              REVIEWLENS AI                  │
├─────────────────────────────────────────────┤
│                                             │
│  🔐 PII Protection                          │
│  😊 Sentiment Analysis                      │
│  🔎 Vector Search                           │
│  🤖 Qwen3 8B + RAG                          │
│  🏷️ Theme & Complaint Detection             │
│  🔗 Evidence Linking                        │
│  📊 Sentiment Validation                    │
│  📉 Drift Monitoring                        │
│  ☁️ Microsoft Azure                          │
│  🖥️ Next.js Dashboard                       │
│                                             │
└─────────────────────────────────────────────┘
<p align="center">
🔎 ReviewLens AI

From customer reviews → to evidence-backed intelligence.

</p> ```