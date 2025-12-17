# 🔧 Backend Service - API Flask avec Observabilité Complète

Microservice backend Python Flask avec instrumentation complète pour l'observabilité : logs structurés JSON, métriques Prometheus et tracing distribué Jaeger. Utilise PostgreSQL comme base de données.

## 📋 Fonctionnalités

### Routes API disponibles

#### Gestion des produits
- **GET /products** - Récupère tous les produits depuis PostgreSQL
- **GET /products/:id** - Récupère un produit spécifique par ID
- **POST /products** - Crée un nouveau produit

#### Endpoints de test
- **GET /slow** - Simule une latence de 5 secondes (configurable)
- **GET /error** - Génère une erreur aléatoire pour tester la gestion d'erreurs

#### Monitoring
- **GET /health** - Healthcheck avec vérification de la connexion DB
- **GET /metrics** - Métriques Prometheus

### Base de données PostgreSQL

**Table `products`** :
```sql
CREATE TABLE products (
    id SERIAL PRIMARY KEY,
    name VARCHAR(200) NOT NULL,
    price FLOAT NOT NULL,
    category VARCHAR(100) NOT NULL,
    created_at TIMESTAMP NOT NULL DEFAULT NOW()
);
```

Le script `init_db.py` initialise automatiquement 10 produits exemples.

### Instrumentation d'observabilité

#### 1. **Logs structurés JSON (python-json-logger)**
- Format JSON avec champs standardisés
- Niveaux : `INFO`, `WARNING`, `ERROR`
- Champs obligatoires :
  - `service`: "backend"
  - `timestamp`: Date/heure UTC
  - `level`: Niveau de log
  - `message`: Message descriptif
  - `trace_id`: ID de trace Jaeger (si disponible)
  - `span_id`: ID du span Jaeger (si disponible)
- Sortie sur `stdout` pour collecte par Loki

#### 2. **Métriques Prometheus (prometheus-flask-exporter)**
Métriques automatiques :
- `http_requests_total` - Counter avec labels `method`, `path`, `status`
- `http_request_duration_seconds` - Histogram de latence

Métriques personnalisées :
- `database_queries_total` - Counter avec labels `operation`, `table`
- `database_connection_pool` - Gauge avec label `status` (size, checked_out)

#### 3. **Tracing distribué Jaeger (jaeger-client)**
- Span créé automatiquement pour chaque requête HTTP
- Spans enfants pour chaque opération SQL
- Tags standards OpenTracing :
  - `http.method`, `http.url`, `http.status_code`
  - `db.type`, `db.statement`
  - `error` (si erreur)
- Extraction automatique du contexte depuis le frontend

## 🚀 Démarrage rapide

### Prérequis
- Python 3.11+
- PostgreSQL
- Docker (pour build d'image)

### Installation locale

```bash
# Créer un environnement virtuel
python -m venv venv
source venv/bin/activate  # Linux/Mac
# ou
venv\Scripts\activate     # Windows

# Installer les dépendances
pip install -r requirements.txt

# Configurer la base de données (voir variables d'env)
export DATABASE_URL="postgresql://user:password@localhost:5432/products_db"

# Initialiser la base de données
python init_db.py

# Démarrer le serveur
python app.py

# Ou avec Gunicorn (production)
gunicorn --bind 0.0.0.0:5000 --workers 4 app:app
```

### Variables d'environnement

```bash
# Serveur
PORT=5000                                                  # Port du serveur
HOST=0.0.0.0                                              # Host d'écoute
FLASK_DEBUG=False                                          # Mode debug

# Base de données PostgreSQL
DATABASE_URL=postgresql://postgres:postgres@db:5432/products_db
DB_POOL_SIZE=10                                            # Taille du pool
DB_MAX_OVERFLOW=20                                         # Connexions supplémentaires max
DB_POOL_RECYCLE=3600                                       # Recyclage des connexions (secondes)

# Jaeger Tracing
JAEGER_AGENT_HOST=jaeger                                   # Host de l'agent Jaeger
JAEGER_AGENT_PORT=6831                                     # Port de l'agent Jaeger
JAEGER_SERVICE_NAME=backend-service                        # Nom du service
JAEGER_SAMPLER_TYPE=const                                  # Type d'échantillonnage
JAEGER_SAMPLER_PARAM=1                                     # Échantillonner 100%

# CORS
CORS_ORIGINS=*                                             # Origines autorisées

# Configuration
SLOW_ENDPOINT_DELAY=5                                      # Délai endpoint /slow (secondes)
```

### Build Docker

```bash
# Build de l'image
docker build -t backend-service:latest .

# Run du container
docker run -p 5000:5000 \
  -e DATABASE_URL=postgresql://postgres:postgres@db:5432/products_db \
  -e JAEGER_AGENT_HOST=jaeger \
  backend-service:latest
```

## 📊 Utilisation de l'API

### Récupérer tous les produits

```bash
curl http://localhost:5000/products
```

**Réponse** :
```json
[
  {
    "id": 1,
    "name": "MacBook Pro 16\"",
    "price": 2899.99,
    "category": "Ordinateurs",
    "created_at": "2024-12-14T20:00:00"
  },
  ...
]
```

### Récupérer un produit spécifique

```bash
curl http://localhost:5000/products/1
```

### Créer un nouveau produit

```bash
curl -X POST http://localhost:5000/products \
  -H "Content-Type: application/json" \
  -d '{
    "name": "iPad Pro",
    "price": 1199.00,
    "category": "Tablettes"
  }'
```

**Réponse** :
```json
{
  "id": 11,
  "name": "iPad Pro",
  "price": 1199.0,
  "category": "Tablettes",
  "created_at": "2024-12-14T21:30:00"
}
```

### Tester l'endpoint lent

```bash
# Attend 5 secondes avant de répondre
curl http://localhost:5000/slow
```

### Générer une erreur

```bash
curl http://localhost:5000/error
```

### Healthcheck

```bash
curl http://localhost:5000/health
```

**Réponse** :
```json
{
  "status": "UP",
  "service": "backend",
  "database": "connected",
  "timestamp": "2024-12-14T21:30:00"
}
```

### Métriques Prometheus

```bash
curl http://localhost:5000/metrics
```

## 🔍 Visualisation de l'observabilité

### Logs (Loki/Grafana)

Les logs sont émis en JSON structuré sur `stdout` :

```json
{
  "timestamp": "2024-12-14 21:30:00",
  "level": "INFO",
  "service": "backend",
  "message": "Récupération de tous les produits",
  "trace_id": "1234567890abcdef",
  "span_id": "abcdef1234567890",
  "count": 10
}
```

Requête LogQL exemple :
```logql
{service="backend"} | json | trace_id="1234567890abcdef"
```

### Métriques (Prometheus/Grafana)

Exemples de requêtes PromQL :

```promql
# Taux de requêtes par seconde
rate(http_requests_total{job="backend"}[5m])

# Latence P95
histogram_quantile(0.95, rate(http_request_duration_seconds_bucket[5m]))

# Requêtes SQL par opération
rate(database_queries_total[5m])

# État du pool de connexions
database_connection_pool
```

### Traces (Jaeger)

Interface Jaeger disponible sur http://localhost:16686

- Service : `backend-service`
- Opérations : `GET /products`, `POST /products`, `db_query_products`, etc.
- Voir la propagation de traces depuis le frontend

## 🏗️ Architecture

```
backend/
├── Dockerfile              # Build multi-stage optimisé
├── .dockerignore          # Exclusions Docker
├── requirements.txt       # Dépendances Python
├── config.py              # Configuration centralisée
├── models.py              # Modèles SQLAlchemy
├── app.py                 # Application Flask principale
├── init_db.py             # Script d'initialisation DB
└── README.md              # Cette documentation
```

## 📦 Dépendances principales

- **Flask** - Framework web
- **Flask-SQLAlchemy** - ORM pour PostgreSQL
- **psycopg2-binary** - Driver PostgreSQL
- **python-json-logger** - Logs JSON structurés
- **prometheus-flask-exporter** - Métriques Prometheus
- **jaeger-client** - Client de tracing Jaeger
- **Flask-OpenTracing** - Intégration OpenTracing
- **gunicorn** - Serveur WSGI de production

## 🔒 Sécurité

- Image Debian Slim légère
- Utilisateur non-root (appuser:1000)
- Connection pooling PostgreSQL avec `pool_pre_ping`
- Validation des données avant insertion
- Gestion d'erreurs avec try/except
- CORS configurable

## 🎓 Logs exemple de requête complète

```json
// Requête reçue
{
  "timestamp": "2024-12-14 21:30:00",
  "level": "INFO",
  "service": "backend",
  "message": "Requête reçue: GET /products",
  "method": "GET",
  "path": "/products",
  "trace_id": "abc123"
}

// Requête SQL
{
  "timestamp": "2024-12-14 21:30:00",
  "level": "INFO",
  "service": "backend",
  "message": "10 produits récupérés",
  "count": 10,
  "trace_id": "abc123",
  "span_id": "def456"
}

// Requête complétée
{
  "timestamp": "2024-12-14 21:30:01",
  "level": "INFO",
  "service": "backend",
  "message": "Requête complétée: GET /products",
  "method": "GET",
  "path": "/products",
  "status": 200,
  "trace_id": "abc123"
}
```

## 🔧 Commandes utiles

```bash
# Initialiser la base de données
python init_db.py

# Démarrer en mode développement
python app.py

# Démarrer avec Gunicorn (production)
gunicorn --bind 0.0.0.0:5000 --workers 4 --timeout 120 app:app

# Linter le code
flake8 *.py

# Tests unitaires (à implémenter)
pytest
```

## 📄 Licence

ISC
