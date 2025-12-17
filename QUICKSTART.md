# 🚀 Guide de démarrage rapide

## ✅ Stack démarrée avec succès !

Tous les services sont opérationnels. Voici les URLs d'accès :

## 🌐 URLs d'accès (ports mis à jour)

| Service | URL | Credentials | Description |
|---------|-----|-------------|-------------|
| **Frontend** | http://localhost:3000 | - | Interface web de test |
| **Backend API** | http://localhost:5002 | - | API REST (port modifié) |
| **Grafana** | http://localhost:3001 | admin / admin | Dashboards métriques |
| **Prometheus** | http://localhost:9091 | - | Interface Prometheus (port modifié) |
| **Kibana** | http://localhost:5601 | - | Exploration logs |
| **Jaeger** | http://localhost:16686 | - | Visualisation traces |
| **Elasticsearch** | http://localhost:9200 | - | API Elasticsearch |
| **Logstash** | http://localhost:5001 | - | Pipeline logs (port modifié) |
| **PostgreSQL** | localhost:5433 | user / pass | Base de données (port modifié) |

## 📊 Tests rapides

### 1. Tester l'application
```bash
# Frontend - Interface web
open http://localhost:3000

# Backend - API
curl http://localhost:5002/health | jq
curl http://localhost:5002/products | jq
```

### 2. Voir les logs
```bash
# Tous les services
docker compose logs -f

# Un service spécifique
docker compose logs -f backend
docker compose logs -f frontend
```

### 3. Accéder aux dashboards

**Grafana** (métriques) :
1. Ouvrir http://localhost:3001
2. Login : admin / admin
3. Aller dans Explore → sélectionner Prometheus
4. Tester : `rate(http_requests_total[5m])`

**Kibana** (logs) :
1. Ouvrir http://localhost:5601
2. Management → Index Patterns → Créer `logs-*`
3. Discover pour explorer les logs

**Jaeger** (traces) :
1. Ouvrir http://localhost:16686
2. Sélectionner service : `frontend-service` ou `backend-service`
3. Find Traces

## 🔧 Commandes utiles

```bash
# Voir le statut
docker compose ps

# Arrêter
docker compose down

# Redémarrer
docker compose restart

# Rebuild un service
docker compose build backend
docker compose up -d backend

# Voir les métriques Prometheus
curl http://localhost:3000/metrics  # Frontend
curl http://localhost:5002/metrics  # Backend
```

## 🎯 Scénario de test

1. Ouvrir http://localhost:3000
2. Cliquer sur "Requête Normale"
3. Observer dans Jaeger la trace complète
4. Observer dans Kibana les logs avec le même `trace_id`
5. Observer dans Grafana l'augmentation de `http_requests_total`

## 🐛 Si problème

```bash
# Voir les logs d'erreur
docker compose logs backend frontend

# Vérifier la base de données
docker compose exec database psql -U user -d products -c "SELECT * FROM products;"

# Tester Elasticsearch
curl http://localhost:9200/_cluster/health?pretty
```

Bon monitoring ! 📊🔍📈
