# ============================================================================
# Stage 1: Builder - Installation des dépendances
# ============================================================================
FROM python:3.11-slim as builder

# Variables d'environnement pour optimiser Python
ENV PYTHONUNBUFFERED=1 \
    PYTHONDONTWRITEBYTECODE=1 \
    PIP_NO_CACHE_DIR=1 \
    PIP_DISABLE_PIP_VERSION_CHECK=1

# Installer les dépendances système nécessaires pour psycopg2
RUN apt-get update && apt-get install -y --no-install-recommends \
    gcc \
    postgresql-client \
    libpq-dev \
    && rm -rf /var/lib/apt/lists/*

# Définir le répertoire de travail
WORKDIR /app

# Copier uniquement requirements.txt pour tirer parti du cache Docker
COPY requirements.txt .

# Installer les dépendances Python
RUN pip install --user --no-warn-script-location -r requirements.txt

# ============================================================================
# Stage 2: Image de production optimisée
# ============================================================================
FROM python:3.11-slim

# Métadonnées de l'image
LABEL maintainer="observability-team"
LABEL description="Backend service Python Flask avec instrumentation complète"

# Variables d'environnement
ENV PYTHONUNBUFFERED=1 \
    PYTHONDONTWRITEBYTECODE=1 \
    PATH=/root/.local/bin:$PATH

# Installer uniquement les bibliothèques runtime PostgreSQL et curl
RUN apt-get update && apt-get install -y --no-install-recommends \
    libpq5 \
    curl \
    && rm -rf /var/lib/apt/lists/*

# Créer un utilisateur non-root pour la sécurité
RUN useradd -m -u 1000 -s /bin/bash appuser

# Définir le répertoire de travail
WORKDIR /app

# Copier les dépendances Python depuis le builder
COPY --from=builder --chown=appuser:appuser /root/.local /home/appuser/.local

# Copier le code source de l'application
COPY --chown=appuser:appuser *.py ./

# Variables d'environnement par défaut
ENV PORT=5000 \
    HOST=0.0.0.0 \
    DATABASE_URL=postgresql://postgres:postgres@db:5432/products_db \
    JAEGER_AGENT_HOST=jaeger \
    JAEGER_AGENT_PORT=6831 \
    FLASK_APP=app.py

# Exposer le port de l'application
EXPOSE 5000

# Changer vers l'utilisateur non-root
USER appuser

# Mettre à jour le PATH pour l'utilisateur
ENV PATH=/home/appuser/.local/bin:$PATH

# Healthcheck pour vérifier que le service est opérationnel
HEALTHCHECK --interval=30s --timeout=5s --start-period=30s --retries=3 \
    CMD python -c "import requests; requests.get('http://localhost:5000/health').raise_for_status()" || exit 1

# Démarrer l'application avec Gunicorn (serveur de production)
# 4 workers, timeout de 120s pour l'endpoint /slow
CMD ["gunicorn", \
     "--bind", "0.0.0.0:5000", \
     "--workers", "4", \
     "--timeout", "120", \
     "--access-logfile", "-", \
     "--error-logfile", "-", \
     "--log-level", "info", \
     "app:app"]
