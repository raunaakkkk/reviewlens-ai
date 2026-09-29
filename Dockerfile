FROM python:3.11-slim

WORKDIR /app

ENV PYTHONDONTWRITEBYTECODE=1
ENV PYTHONUNBUFFERED=1
ENV HF_HOME=/opt/huggingface
ENV TRANSFORMERS_CACHE=/opt/huggingface

RUN apt-get update && \
    apt-get install -y --no-install-recommends libgomp1 && \
    rm -rf /var/lib/apt/lists/*

COPY requirements.txt .

RUN pip install --no-cache-dir --upgrade pip && \
    pip install --no-cache-dir \
        fastapi==0.141.1 \
        uvicorn==0.54.0 \
        gunicorn \
        python-multipart==0.0.32 \
        python-dotenv \
        requests==2.34.2 \
        pandas \
        SQLAlchemy==2.1.1 \
        psycopg2-binary \
        azure-identity \
        azure-keyvault-secrets \
        azure-storage-blob \
        azure-ai-textanalytics \
        azure-search-documents \
        azure-monitor-opentelemetry \
        scikit-learn==1.9.1 \
        torch==2.14.0+cpu \
        sentence-transformers==6.1.0 \
        transformers==5.17.0 \
        --extra-index-url https://download.pytorch.org/whl/cpu

COPY backend ./backend

RUN python -c "import torch; print('Torch:', torch.__version__); print('CUDA:', torch.cuda.is_available())"

RUN python -c "from sentence_transformers import SentenceTransformer; m=SentenceTransformer('all-MiniLM-L6-v2'); print('Embedding dimension:', len(m.encode('test')))"

EXPOSE 8000

CMD ["gunicorn", "--bind=0.0.0.0:8000", "--timeout=600", "-k", "uvicorn.workers.UvicornWorker", "backend.main:app"]
