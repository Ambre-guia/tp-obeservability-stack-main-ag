# 🎯 Frontend Service - Microservice avec Observabilité Complète

Microservice frontend Node.js/Express avec instrumentation complète pour l'observabilité : logs structurés (Winston), métriques (Prometheus) et tracing distribué (Jaeger).

## 📋 Fonctionnalités

### Routes disponibles

- **GET /** - Page HTML interactive avec boutons de test
- **GET /api/products** - Appelle le backend pour récupérer les produits
- **GET /api/slow** - Appelle le backend avec un endpoint lent (pour tester les timeouts)
- **GET /api/error** - Génère intentionnellement une erreur 500 (pour tester la gestion d'erreurs)
- **GET /health** - Healthcheck du service
- **GET /metrics** - Métriques Prometheus

### Instrumentation d'observabilité

#### 1. **Logs structurés (Winston)**
- Format JSON avec timestamp
- Niveaux : `info`, `warn`, `error`
- Champs systématiques :
  - `service`: "frontend"
  - `request_id`: UUID unique par requête
  - `trace_id`: ID de trace Jaeger
  - `timestamp`, `level`, `message`
- Sortie sur `stdout` pour collecte par Loki

#### 2. **Métriques Prometheus (prom-client)**
- `http_requests_total` - Counter avec labels `method`, `path`, `status`
- `http_request_duration_seconds` - Histogram avec buckets [0.1, 0.5, 1, 2, 5, 10]
- `frontend_errors_total` - Counter avec label `type`
- Métriques système par défaut (CPU, mémoire, etc.)

#### 3. **Tracing distribué (Jaeger)**
- Span créé pour chaque requête HTTP
- Tags standards : `http.method`, `http.url`, `http.status_code`
- Propagation du contexte vers le backend via headers
- Child spans pour les appels backend
- Logging d'erreurs dans les spans

## 🚀 Démarrage rapide

### Prérequis
- Node.js 18+
- Docker (pour build d'image)

### Installation locale

```bash
# Installer les dépendances
npm install

# Démarrer le serveur
npm start

# Ou en mode développement avec auto-reload
npm run dev
```

### Variables d'environnement

```bash
PORT=3000                           # Port du serveur (défaut: 3000)
BACKEND_URL=http://backend:5000     # URL du backend
JAEGER_AGENT_HOST=jaeger            # Host de l'agent Jaeger
JAEGER_AGENT_PORT=6831              # Port de l'agent Jaeger
```

### Build Docker

```bash
# Build de l'image
docker build -t frontend-service:latest .

# Run du container
docker run -p 3000:3000 \
  -e BACKEND_URL=http://backend:5000 \
  -e JAEGER_AGENT_HOST=jaeger \
  frontend-service:latest
```

## 📊 Tests d'observabilité

### Via l'interface web

1. Ouvrir http://localhost:3000
2. Utiliser les boutons pour tester :
   - **Requête Normale** : Appelle `/api/products`
   - **Requête Lente** : Appelle `/api/slow`
   - **Générer Erreur** : Appelle `/api/error`
   - **Charger 100 Requêtes** : Test de charge avec 100 requêtes parallèles

### Via cURL

```bash
# Healthcheck
curl http://localhost:3000/health

# Métriques Prometheus
curl http://localhost:3000/metrics

# Requête normale
curl http://localhost:3000/api/products

# Requête lente
curl http://localhost:3000/api/slow

# Générer une erreur
curl http://localhost:3000/api/error
```

## 🔍 Visualisation de l'observabilité

### Logs (Loki/Grafana)
Les logs sont émis en JSON sur `stdout` et peuvent être collectés par :
- **Loki** via Promtail ou Docker driver
- Visualisés dans **Grafana** via Explore ou dashboards

Exemple de requête LogQL :
```logql
{service="frontend"} | json | trace_id="abc123"
```

### Métriques (Prometheus/Grafana)
Endpoint `/metrics` exposé au format Prometheus.

Exemples de requêtes PromQL :
```promql
# Taux de requêtes par seconde
rate(http_requests_total[5m])

# Latence P95
histogram_quantile(0.95, rate(http_request_duration_seconds_bucket[5m]))

# Taux d'erreurs
rate(frontend_errors_total[5m])
```

### Traces (Jaeger)
Interface Jaeger disponible sur http://localhost:16686

- Rechercher par `frontend-service`
- Filtrer par opération : `GET /api/products`, `GET /api/slow`, etc.
- Voir la propagation vers le backend

## 🏗️ Architecture

```
frontend/
├── Dockerfile              # Build multi-stage optimisé
├── .dockerignore          # Exclusions pour Docker
├── package.json           # Dépendances npm
├── server.js              # Serveur Express avec instrumentation
├── public/
│   └── index.html         # Interface web de test
└── README.md              # Cette documentation
```

## 📦 Dépendances principales

- **express** - Framework web
- **axios** - Client HTTP pour appels backend
- **winston** - Logger structuré
- **prom-client** - Client Prometheus
- **jaeger-client** - Client de tracing Jaeger
- **opentracing** - API standard pour tracing
- **uuid** - Génération de request_id

## 🔒 Sécurité

- Image Alpine légère
- Utilisateur non-root (nodejs:1001)
- Dumb-init pour gestion propre des signaux
- Healthcheck intégré
- Pas de dépendances de développement en production

## 📝 Logs exemple

```json
{
  "level": "info",
  "message": "Requête reçue",
  "method": "GET",
  "path": "/api/products",
  "request_id": "a1b2c3d4-e5f6-7890-abcd-ef1234567890",
  "trace_id": "1234567890abcdef",
  "service": "frontend",
  "timestamp": "2024-12-14 21:30:00"
}
```

## 🎓 Pour aller plus loin

- Ajouter des dashboards Grafana personnalisés
- Configurer des alertes Prometheus
- Mettre en place des SLOs (Service Level Objectives)
- Intégrer des tests de charge automatisés

## 📄 Licence

ISC
