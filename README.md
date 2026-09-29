\# ReviewLens AI



> AI-powered customer review intelligence platform built with Microsoft Azure, local Qwen3 8B, RAG, and a modern analytics dashboard.



!\[ReviewLens AI](https://img.shields.io/badge/Project-ReviewLens%20AI-blue)

!\[Python](https://img.shields.io/badge/Python-3.11-blue)

!\[FastAPI](https://img.shields.io/badge/FastAPI-Backend-009688)

!\[Next.js](https://img.shields.io/badge/Next.js-Frontend-black)

!\[Azure](https://img.shields.io/badge/Microsoft%20Azure-Cloud-0078D4)

!\[Qwen3](https://img.shields.io/badge/LLM-Qwen3%208B-purple)



\---



\## 📌 Overview



\*\*ReviewLens AI\*\* is an AI-powered customer review intelligence system designed to transform large volumes of unstructured customer feedback into actionable insights.



The platform processes customer reviews through an end-to-end pipeline involving:



\- Data ingestion

\- Cleaning and deduplication

\- PII redaction

\- Sentiment analysis

\- Vector embeddings

\- Semantic retrieval

\- Theme extraction

\- Complaint identification

\- Evidence linking

\- Sentiment validation

\- Drift monitoring

\- AI-powered question answering



The system combines \*\*Microsoft Azure services\*\* for cloud infrastructure and enterprise capabilities with a \*\*locally hosted Qwen3 8B model\*\* for evidence-grounded analysis.



\---



\# 🎯 Problem Statement



Organizations receive large volumes of customer reviews, but manually analyzing them is:



\- Time-consuming

\- Difficult to scale

\- Prone to inconsistent interpretation

\- Difficult to trace back to original customer feedback

\- Challenging to monitor over time



ReviewLens AI addresses this problem by automatically converting raw customer reviews into structured intelligence while maintaining traceability back to supporting review evidence.



\---



\# 💡 Solution



ReviewLens AI provides a complete review intelligence pipeline:



```text

Customer Reviews

&#x20;      │

&#x20;      ▼

Azure Blob Storage

&#x20;      │

&#x20;      ▼

Cleaning \& Deduplication

&#x20;      │

&#x20;      ▼

PII Redaction

&#x20;      │

&#x20;      ▼

Azure AI Language

&#x20;      │

&#x20;      ├───────────────┐

&#x20;      ▼               ▼

&#x20; Sentiment       Embeddings

&#x20;                      │

&#x20;                      ▼

&#x20;               Azure AI Search

&#x20;                      │

&#x20;                      ▼

&#x20;               Relevant Reviews

&#x20;                      │

&#x20;                      ▼

&#x20;                Qwen3 8B

&#x20;                 Local LLM

&#x20;                      │

&#x20;         ┌────────────┼────────────┐

&#x20;         ▼            ▼            ▼

&#x20;      Themes      Complaints     Summary

&#x20;         │            │            │

&#x20;         └────────────┼────────────┘

&#x20;                      ▼

&#x20;                Evidence Linking

&#x20;                      │

&#x20;                      ▼

&#x20;                 PostgreSQL

&#x20;                      │

&#x20;                      ▼

&#x20;                   FastAPI

&#x20;                      │

&#x20;                      ▼

&#x20;               Next.js Dashboard

✨ Key Features

1\. Review Ingestion



Customer review files can be uploaded through the application.



Uploaded data is stored in:



Azure Blob Storage



The storage structure supports:



reviews/

├── raw/

├── cleaned/

└── processed/

2\. Cleaning \& Deduplication



Reviews are normalized before analysis.



The pipeline:



Removes unnecessary HTML/content

Normalizes review text

Generates SHA-256 review hashes

Detects duplicate reviews

Prevents duplicate indexing



This ensures that repeated reviews do not artificially influence analytics.



3\. PII Redaction



ReviewLens AI uses Azure AI Language to detect and redact personally identifiable information.



Example:



Original:

The product works well, but support at john@example.com

did not respond.



Redacted:

The product works well, but support at \*\*\*\*\*\*\*\*

did not respond.



PII entities are detected before downstream sentiment and intelligence generation.



4\. Sentiment Analysis



Azure AI Language performs sentiment analysis on processed reviews.



Each review receives:



Sentiment

Positive Score

Neutral Score

Negative Score



Example:



{

&#x20; "sentiment": "negative",

&#x20; "positive\_score": 0.01,

&#x20; "neutral\_score": 0.08,

&#x20; "negative\_score": 0.91

}

🔎 5. Vector Search \& RAG



ReviewLens AI uses:



Sentence Transformers — all-MiniLM-L6-v2



Embedding dimension:



384



Embeddings are stored in:



Azure AI Search



Index:



reviewlens-reviews



The system performs vector similarity search to retrieve relevant customer reviews.



These retrieved reviews become the evidence context for the local LLM.



🤖 6. Qwen3 8B AI Analysis



The system currently uses:



Qwen3 8B



through:



Ollama



The model runs locally and is used for:



Theme extraction

Complaint identification

Review summarization

Evidence-grounded question answering



The AI assistant is designed to answer questions using retrieved review evidence rather than relying only on general model knowledge.



Example:



Question:

What are the main complaints from customers?



Answer:

The main complaints involve delayed delivery and

unresponsive customer support.

📊 7. Themes \& Complaints



The system automatically extracts recurring customer themes and complaints.



Example themes:



Product Quality

Delivery

Customer Support



Example complaints:



Delivery Delays

Poor Customer Support



These insights are linked back to supporting reviews.



🔗 8. Evidence Linking



ReviewLens AI maintains traceability between generated insights and source reviews.



Each insight can be connected to supporting evidence.



This enables users to answer:



"Why did the system generate this insight?"



Instead of showing only an AI-generated conclusion, the platform can show the underlying customer reviews.



🗄️ 9. PostgreSQL



PostgreSQL stores structured application data.



Current database entities include:



reviews

insights

evidence\_links

validation\_results

drift\_results



The database stores:



Processed reviews

Generated insights

Evidence relationships

Validation metrics

Drift monitoring results

📈 10. Sentiment Validation



ReviewLens AI includes a labelled validation dataset containing:



12 reviews

4 Positive

4 Neutral

4 Negative



Current validation results:



Metric	Result

Accuracy	83.33%

Precision	88.89%

Recall	83.33%

F1 Score	82.22%



These metrics provide a measurable evaluation of the sentiment classification pipeline.



📉 11. Drift Monitoring



ReviewLens AI monitors changes in sentiment distribution between a baseline and current period.



Current test result:



Metric	Value

Baseline Negative Rate	50%

Current Negative Rate	50%

Rate Change	0%

Drift Detected	No

Detection Threshold	20%



This provides a mechanism for identifying meaningful changes in customer sentiment over time.



💬 12. AI Assistant



The dashboard includes an AI assistant that can answer questions about customer feedback.



Example questions:



What are the main complaints from customers?



What do customers like about the product?



What problems are customers experiencing with delivery?



What are the most common support issues?



The assistant retrieves relevant reviews from Azure AI Search and provides evidence-grounded responses.



☁️ Microsoft Azure Architecture



ReviewLens AI uses multiple Microsoft Azure services.



Azure Service	Purpose

Azure Blob Storage	Review file storage

Azure AI Language	PII detection and sentiment analysis

Azure AI Search	Vector search and retrieval

Azure Database for PostgreSQL	Persistent application database

Azure Key Vault	Secure secret management

Azure App Service	Backend hosting

Azure Container Registry	Docker image storage

Azure Application Insights	Application monitoring

Log Analytics	Monitoring and telemetry

🔐 Security



Security is incorporated throughout the architecture.



Azure Key Vault



Sensitive database credentials are stored in:



Azure Key Vault



The backend retrieves the database connection securely using Azure identity.



Secrets are not hard-coded into application source code.



Managed Identity



Azure App Services use managed identities to access Azure resources.



The backend identity has scoped permissions for:



Azure Key Vault

Azure Blob Storage

Azure AI Language

Azure AI Search

Azure Container Registry

PII Protection



Customer personally identifiable information is detected and redacted before downstream analysis.



🏗️ Technology Stack

Backend

Python 3.11

FastAPI

Uvicorn

SQLAlchemy

PostgreSQL

Pydantic

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

Docker Engine

Azure Container Registry

Azure App Service

📁 Project Structure

reviewlens-ai/

│

├── backend/

│   ├── agent/

│   │   └── rag\_agent.py

│   │

│   ├── analysis/

│   │   ├── drift.py

│   │   ├── evidence.py

│   │   ├── insights.py

│   │   ├── language.py

│   │   ├── review\_pipeline.py

│   │   ├── validation.py

│   │   └── validation\_sync.py

│   │

│   ├── ingestion/

│   │   └── cleaning.py

│   │

│   ├── rag/

│   │   ├── index\_review.py

│   │   └── retrieve.py

│   │

│   ├── database.py

│   ├── database\_sync.py

│   ├── insight\_sync.py

│   ├── main.py

│   ├── models.py

│   └── test\_keyvault.py

│

├── data/

│   └── validation/

│       └── sentiment\_validation.csv

│

├── frontend/

│   └── frontend/

│       ├── app/

│       ├── public/

│       ├── package.json

│       ├── package-lock.json

│       ├── next.config.ts

│       ├── tsconfig.json

│       └── Dockerfile

│

├── .dockerignore

├── .gitignore

├── Dockerfile

├── requirements.txt

└── README.md

🚀 Local Setup

1\. Clone the repository

git clone https://github.com/<YOUR-USERNAME>/reviewlens-ai.git

cd reviewlens-ai

🐍 Backend Setup



Create a virtual environment:



python -m venv .venv



Activate it:



.venv\\Scripts\\Activate.ps1



Install dependencies:



pip install -r requirements.txt

🔑 Environment Variables



Create a local .env file.



Example:



AZURE\_KEY\_VAULT\_URL=

AZURE\_LANGUAGE\_ENDPOINT=

AZURE\_SEARCH\_ENDPOINT=

AZURE\_STORAGE\_ACCOUNT\_NAME=

AZURE\_STORAGE\_CONTAINER\_NAME=

APPLICATIONINSIGHTS\_CONNECTION\_STRING=



Do not commit .env to GitHub.



Azure authentication uses Azure Identity / DefaultAzureCredential.



▶️ Run the Backend



From the project root:



uvicorn backend.main:app --reload



Backend:



http://127.0.0.1:8000



Swagger documentation:



http://127.0.0.1:8000/docs



Health endpoint:



http://127.0.0.1:8000/health

🌐 Frontend Setup



Move into the frontend application:



cd frontend\\frontend



Install dependencies:



npm install



Run development server:



npm run dev



Dashboard:



http://localhost:3000

🐳 Docker



The backend can be packaged using Docker.



Build:



docker build -t reviewlens-api:v1 .



Run:



docker run -p 8000:8000 reviewlens-api:v1



The frontend also includes a Docker configuration for containerized deployment.



☁️ Azure Deployment



The backend is deployed to Azure App Service using a Docker container stored in Azure Container Registry.



Current backend architecture:



Docker Image

&#x20;    │

&#x20;    ▼

Azure Container Registry

&#x20;    │

&#x20;    ▼

Azure App Service

&#x20;    │

&#x20;    ▼

FastAPI



Backend service:



reviewlens-api-260925



The frontend is designed for deployment through the same container-based Azure architecture.



🔌 API Endpoints

Endpoint	Purpose

/health	Application health

/reviews	Retrieve reviews

/reviews/upload	Upload reviews

/insights	Retrieve generated insights

/evidence	Retrieve evidence links

/validation	Sentiment validation metrics

/drift	Drift monitoring results

/assistant	AI assistant



Interactive API documentation:



/docs

🧪 Testing \& Evaluation



ReviewLens AI includes testing for:



Sentiment

Accuracy

Precision

Recall

F1 Score

Data Quality

Duplicate detection

PII detection

Review processing

AI Insights

Theme extraction

Complaint identification

Evidence linking

Monitoring

Sentiment drift

Application telemetry

API health

📊 Current Results

Sentiment Validation

Sample Size : 12



Accuracy    : 83.33%

Precision   : 88.89%

Recall      : 83.33%

F1 Score    : 82.22%

Drift Monitoring

Baseline Negative Rate : 50%

Current Negative Rate  : 50%

Change                  : 0%

Drift                   : Not detected

Current Review Dataset



The development environment currently contains unique reviews covering:



Positive product feedback

Negative delivery feedback

Customer support feedback

🔍 Example AI Insights

Themes

Product Quality

Delivery

Customer Support

Complaints

Delivery Delays

Poor Customer Support

Evidence



Generated insights are linked to supporting customer reviews stored in the system.



🧠 RAG Pipeline



The AI assistant follows a retrieval-grounded workflow:



User Question

&#x20;     │

&#x20;     ▼

Query Embedding

&#x20;     │

&#x20;     ▼

Azure AI Search

&#x20;     │

&#x20;     ▼

Relevant Reviews

&#x20;     │

&#x20;     ▼

Evidence Context

&#x20;     │

&#x20;     ▼

Qwen3 8B

&#x20;     │

&#x20;     ▼

Grounded Answer



This architecture helps keep answers connected to the actual customer feedback stored in the system.



🎯 Design Principles



ReviewLens AI follows several important design principles:



Evidence First



AI-generated insights should be supported by actual customer reviews.



Privacy First



PII should be detected and redacted before downstream processing.



Measurable AI



Sentiment analysis is evaluated using a labelled validation dataset.



Monitorable AI



The system includes drift monitoring and application telemetry.



Cloud Ready



The application uses Azure-managed services and containerized deployment.



Modular Architecture



The ingestion, analysis, retrieval, AI, database, API, and frontend layers are separated.



🔮 Future Improvements



Planned improvements include:



Hosting Qwen3 8B directly in Azure

Fully public frontend deployment

Larger-scale batch ingestion

Improved theme clustering

Advanced temporal trend analysis

More comprehensive evaluation datasets

Automated ingestion pipelines

Azure Functions for event-driven processing

Enhanced role-based access control

Production-scale monitoring

Automated CI/CD deployment

🛡️ Sensitive Information



The following must never be committed to this repository:



.env

Azure client secrets

Service principal passwords

Database passwords

API keys

Private certificates

Production credentials



Use:



Azure Key Vault

Managed Identity

Environment Variables



for secure configuration.



📜 License



This project is developed as part of the Microsoft Innovate project.



Add an appropriate license before public redistribution if required by your project or institution.



👥 Project



ReviewLens AI



AI-powered customer review intelligence using:



Microsoft Azure

\+

Qwen3 8B

\+

RAG

\+

FastAPI

\+

Next.js

\+

PostgreSQL

⭐ ReviewLens AI



Turn customer reviews into structured, traceable and actionable intelligence.

