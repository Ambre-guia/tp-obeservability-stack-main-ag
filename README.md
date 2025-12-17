# 🚀 Stack d'Observabilité Complète

Stack complète d'observabilité pour microservices avec **monitoring**, **logging** et **tracing distribué**.

## 📋 Architecture de la Stack

### Microservices
- **Frontend** (Node.js/Express) - Interface web + API Gateway
- **Backend** (Python/Flask) - API REST avec PostgreSQL
- **Database** (PostgreSQL 15) - Stockage des données

### Observabilité
- **Prometheus** - Collecte et stockage des métriques
- **Grafana** - Visualisation des métriques et dashboards
- **Elasticsearch** - Stockage et indexation des logs
- **Logstash** - Agrégation et transformation des logs
- **Kibana** - Exploration et analyse des logs
- **Jaeger** - Tracing distribué des requêtes
- **Postgres Exporter** - Métriques PostgreSQL

## 🎯 Les 3 Piliers de l'Observabilité

### 1. 📊 Métriques (Prometheus + Grafana)
- Collecte automatique toutes les 15s
- Métriques applicatives : requêtes HTTP, latence, erreurs
- Métriques système : CPU, mémoire, disque
- Métriques DB : connexions, requêtes, performances

### 2. 📝 Logs (ELK Stack)
- Logs JSON structurés
- Indexation et recherche rapide
- Corrélation avec les traces via `trace_id`
- Retention configurable

### 3. 🔍 Traces (Jaeger)
- Traçage des requêtes frontend → backend
- Spans pour chaque opération (HTTP, SQL)
- Visualisation du flow complet
- Détection des goulots d'étranglement

## 🚀 Démarrage rapide

### Prérequis
- Docker 20.10+
- Docker Compose 2.0+
- 8 GB RAM minimum
- 10 GB espace disque

### Installation

```bash
# Cloner ou se placer dans le répertoire
cd tp6-observability-stack

# Copier le fichier d'environnement
cp .env.example .env

# Éditer les variables si nécessaire
nano .env

# Construire et démarrer tous les services
docker-compose up -d

# Voir les logs de tous les services
docker-compose logs -f

# Voir les logs d'un service spécifique
docker-compose logs -f backend
```

### Vérification du démarrage

```bash
# Vérifier que tous les services sont UP
docker-compose ps

# Vérifier les healthchecks
docker-compose ps | grep -i healthy
```

## 🌐 URLs d'accès

| Service | URL | Credentials | Description |
|---------|-----|------------|-------------|
| **Frontend** | http://localhost:3000 | - | Interface web de test |
| **Backend API** | http://localhost:5000 | - | API REST |
| **Grafana** | http://localhost:3001 | admin / admin | Dashboards métriques |
| **Prometheus** | http://localhost:9090 | - | Interface Prometheus |
| **Kibana** | http://localhost:5601 | - | Exploration logs |
| **Jaeger** | http://localhost:16686 | - | Visualisation traces |
| **Elasticsearch** | http://localhost:9200 | - | API Elasticsearch |
| **PostgreSQL** | localhost:5432 | user / pass | Base de données |

## 📊 Guide d'utilisation

### 1. Tester l'application

Ouvrez http://localhost:3000 et utilisez les boutons :
- **Requête Normale** : Charge la liste des produits
- **Requête Lente** : Simule une latence de 5s
- **Générer Erreur** : Déclenche une erreur 500
- **Charger 100 Requêtes** : Test de charge

### 2. Visualiser les métriques (Grafana)

1. Ouvrir http://localhost:3001 (admin/admin)
2. Aller dans **Explore** ou **Dashboards**
3. Sélectionner la datasource **Prometheus**
4. Exemples de requêtes :

```promql
# Requêtes par seconde
rate(http_requests_total[5m])

# Latence P95
histogram_quantile(0.95, rate(http_request_duration_seconds_bucket[5m]))

# Taux d'erreurs
rate(http_requests_total{status=~"5.."}[5m])

# Métriques PostgreSQL
pg_stat_database_tup_fetched{datname="products"}
```

### 3. Explorer les logs (Kibana)

1. Ouvrir http://localhost:5601
2. Aller dans **Management** → **Index Patterns**
3. Créer un index pattern : `logs-*` avec champ temps `@timestamp`
4. Aller dans **Discover** pour explorer les logs
5. Exemples de recherches :

```
service_name:"backend" AND log_level:"ERROR"
trace_id:"abc123def456"
log_message:*product*
```

### 4. Analyser les traces (Jaeger)

1. Ouvrir http://localhost:16686
2. Sélectionner le service : **frontend-service** ou **backend-service**
3. Filtrer par opération : `GET /api/products`, etc.
4. Cliquer sur une trace pour voir :
   - Durée totale
   - Spans individuels
   - Tags et logs
   - Propagation frontend → backend

### 5. Corrélation Logs ↔ Traces

Les logs contiennent le `trace_id` de Jaeger :

```json
{
  "service": "backend",
  "message": "Récupération de tous les produits",
  "trace_id": "1234567890abcdef",
  "span_id": "abcdef1234567890"
}
```

Dans Kibana, filtrer par `trace_id` pour voir tous les logs d'une requête.
Copier le `trace_id` et le chercher dans Jaeger pour voir la trace complète.

## 📡 API Endpoints

### Frontend (Port 3000)
```bash
GET  /                  # Interface web
GET  /health           # Healthcheck
GET  /metrics          # Métriques Prometheus
GET  /api/products     # Liste produits (via backend)
GET  /api/slow         # Endpoint lent
GET  /api/error        # Génère erreur
```

### Backend (Port 5000)
```bash
GET  /health           # Healthcheck + DB status
GET  /metrics          # Métriques Prometheus
GET  /products         # Liste tous les produits
GET  /products/:id     # Détail d'un produit
POST /products         # Créer un produit
GET  /slow             # Simule latence 5s
GET  /error            # Génère erreur aléatoire
```

### Exemples avec cURL

```bash
# Healthcheck backend
curl http://localhost:5000/health

# Récupérer les produits
curl http://localhost:5000/products | jq

# Créer un produit
curl -X POST http://localhost:5000/products \
  -H "Content-Type: application/json" \
  -d '{
    "name": "iPad Pro",
    "price": 1199.00,
    "category": "Tablettes"
  }'

# Test de charge (10 requêtes)
for i in {1..10}; do
  curl http://localhost:3000/api/products &
done
```

## 🔧 Commandes utiles

### Gestion des services

```bash
# Démarrer la stack
docker-compose up -d

# Arrêter la stack
docker-compose down

# Redémarrer un service
docker-compose restart backend

# Voir les logs
docker-compose logs -f backend frontend

# Voir les stats
docker stats

# Reconstruire les images
docker-compose build --no-cache

# Nettoyer tout (⚠️ perte de données)
docker-compose down -v
```

### Debugging

```bash
# Entrer dans un container
docker-compose exec backend bash
docker-compose exec frontend sh

# Vérifier la DB
docker-compose exec database psql -U user -d products
# SELECT * FROM products;

# Tester Elasticsearch
curl http://localhost:9200/_cluster/health?pretty

# Vérifier Prometheus targets
curl http://localhost:9090/api/v1/targets | jq
```

### Monitoring

```bash
# Voir l'utilisation des ressources
docker-compose ps --format "table {{.Name}}\t{{.Status}}\t{{.Ports}}"

# Logs d'un service avec timestamp
docker-compose logs -f --timestamps backend

# Top des containers par CPU/RAM
docker stats --format "table {{.Name}}\t{{.CPUPerc}}\t{{.MemUsage}}"
```

## 📁 Structure du projet

```
tp6-observability-stack/
├── docker-compose.yml              # Stack complète
├── .env.example                    # Variables d'environnement
├── init.sql                        # Initialisation PostgreSQL
├── README.md                       # Ce fichier
│
├── frontend/                       # Microservice Node.js
│   ├── Dockerfile
│   ├── package.json
│   ├── server.js
│   └── public/index.html
│
├── backend/                        # Microservice Python
│   ├── Dockerfile
│   ├── requirements.txt
│   ├── app.py
│   ├── models.py
│   ├── config.py
│   └── init_db.py
│
├── prometheus/                     # Config Prometheus
│   └── prometheus.yml
│
├── grafana/                        # Config Grafana
│   ├── provisioning/
│   │   ├── datasources/
│   │   │   └── datasources.yml
│   │   └── dashboards/
│   │       └── dashboards.yml
│   └── dashboards/
│
└── logstash/                       # Config Logstash
    └── pipeline.conf
```

## 🔍 Métriques disponibles

### Frontend (Node.js)
- `http_requests_total` - Total requêtes
- `http_request_duration_seconds` - Latence
- `frontend_errors_total` - Erreurs
- `nodejs_*` - Métriques Node.js

### Backend (Python)
- `http_requests_total` - Total requêtes
- `http_request_duration_seconds` - Latence
- `database_queries_total` - Requêtes SQL
- `database_connection_pool` - Pool de connexions
- `flask_*` - Métriques Flask

### PostgreSQL
- `pg_stat_database_*` - Stats DB
- `pg_stat_activity_*` - Connexions actives
- `pg_locks_*` - Locks
- Et 100+ autres métriques

## 🐛 Troubleshooting

### Problème : Services ne démarrent pas
```bash
# Vérifier les logs
docker-compose logs

# Vérifier l'espace disque
df -h

# Nettoyer Docker
docker system prune -a --volumes
```

### Problème : Elasticsearch ne démarre pas (Out of Memory)
```bash
# Augmenter la mémoire Docker (8GB min)
# Ou réduire ES_JAVA_OPTS dans .env
ES_JAVA_OPTS=-Xms256m -Xmx256m
```

### Problème : Backend ne peut pas se connecter à la DB
```bash
# Vérifier que PostgreSQL est UP
docker-compose ps database

# Vérifier les logs
docker-compose logs database

# Attendre que la DB soit healthy
docker-compose up -d database
sleep 10
docker-compose up -d backend
```

### Problème : Pas de métriques dans Grafana
```bash
# Vérifier les targets Prometheus
curl http://localhost:9090/api/v1/targets | jq '.data.activeTargets[] | {job: .labels.job, health: .health}'

# Vérifier que les services exposent /metrics
curl http://localhost:3000/metrics
curl http://localhost:5000/metrics
```

## 🎓 Scénarios de démonstration

### Scénario 1 : Requête normale
1. Cliquer sur "Requête Normale" dans le frontend
2. Observer dans Jaeger : trace complète frontend → backend → DB
3. Observer dans Kibana : logs avec `trace_id` identique
4. Observer dans Grafana : pic de métrique `http_requests_total`

### Scénario 2 : Détection de latence
1. Cliquer sur "Requête Lente"
2. Observer dans Jaeger : span de 5s pour `simulate_slow_operation`
3. Créer une alerte Prometheus si latence P95 > 2s

### Scénario 3 : Gestion d'erreur
1. Cliquer sur "Générer Erreur"
2. Observer dans Kibana : log avec `level:ERROR`
3. Observer dans Jaeger : span marqué avec tag `error:true`
4. Observer dans Grafana : augmentation de `frontend_errors_total`

### Scénario 4 : Test de charge
1. Cliquer sur "Charger 100 Requêtes"
2. Observer dans Grafana : pic de requêtes/sec
3. Observer métriques PostgreSQL : connexions actives
4. Vérifier que les healthchecks restent verts

## 📚 Ressources

- [Prometheus Documentation](https://prometheus.io/docs/)
- [Grafana Documentation](https://grafana.com/docs/)
- [Elasticsearch Guide](https://www.elastic.co/guide/en/elasticsearch/reference/current/index.html)
- [Jaeger Documentation](https://www.jaegertracing.io/docs/)
- [OpenTelemetry](https://opentelemetry.io/)

## 📄 Licence

MIT

---

**Bon monitoring ! 📊🔍📈**
