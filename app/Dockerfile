FROM python:3.11-slim

WORKDIR /app

# Pour éviter certains soucis réseau / SSL
ENV PYTHONUNBUFFERED=1 \
    PIP_NO_CACHE_DIR=1

# Installer les dépendances système minimales (optionnel mais utile)
RUN apt-get update && apt-get install -y --no-install-recommends \
    curl \
    && rm -rf /var/lib/apt/lists/*

# Installer les libs Python
COPY requirements.txt .
RUN pip install -r requirements.txt

# Copier ton code
COPY . .

# Si ton main lance directement FastAPI via uvicorn, adapte la commande :
# CMD ["uvicorn", "main:app", "--host", "0.0.0.0", "--port", "8000"]

# Si ton main.py fait tout, on garde :
CMD ["python", "main.py"]

