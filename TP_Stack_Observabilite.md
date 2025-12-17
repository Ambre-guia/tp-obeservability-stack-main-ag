# 📘 TP6 : Stack Open-Source d'Observabilité (ELK + Jaeger + Prometheus)

**Niveau** : Intermédiaire  
**Prérequis** : Connaissances Docker, Docker Compose, notions de microservices  

---

## 🎯 Objectifs pédagogiques

À la fin de ce TP, vous serez capable de :
- Déployer une stack d'observabilité complète avec Docker Compose
- Comprendre et différencier les 3 piliers : Métriques (Prometheus), Logs (ELK), Traces (Jaeger)
- Configurer Grafana pour créer des dashboards de monitoring
- Analyser les performances d'une application microservices
- Diagnostiquer des problèmes en production (latence, erreurs)
- Corréler logs, métriques et traces pour du troubleshooting avancé

---

## 📋 Contexte du projet

Vous allez déployer **MesProduits Observability Stack**, une application microservices complète comprenant :

| Composant | Description | Port |
|-----------|-------------|------|
| **Frontend (Node.js)** | Interface web avec métriques exposées | 3000 |
| **Backend (Flask)** | API REST avec logs structurés et tracing | 5002 |
| **PostgreSQL** | Base de données avec exporter de métriques | 5433 |
| **Prometheus** | Collecte et stockage des métriques | 9091 |
| **Grafana** | Visualisation et dashboards | 3001 |
| **Elasticsearch** | Stockage et indexation des logs | 9200 |
| **Logstash** | Agrégation et transformation des logs | 5001 |
| **Kibana** | Exploration et analyse des logs | 5601 |
| **Jaeger** | Distributed tracing | 16686 |
| **Postgres Exporter** | Métriques PostgreSQL | 9187 |

L'objectif est de monitorer l'application complète et diagnostiquer des incidents simulés.

---

## ❓ QUESTIONS PRÉLIMINAIRES (À répondre avant de commencer)

### Section A : Compréhension théorique

**Q1.** Citez les 3 piliers de l'observabilité et donnez un exemple d'outil pour chacun.

Votre réponse :
- Pilier 1 : _________________________ → Outil : _________________________
- Pilier 2 : _________________________ → Outil : _________________________
- Pilier 3 : _________________________ → Outil : _________________________

---

**Q2.** Quelle est la différence fondamentale entre monitoring et observabilité ?

Votre réponse :
```
________________________________________________________________________
________________________________________________________________________
________________________________________________________________________
```

---

**Q3.** Associez chaque cas d'usage à l'outil approprié :

| Cas d'usage | Outil (Prometheus/ELK/Jaeger) |
|-------------|-------------------------------|
| Analyser pourquoi une requête met 5 secondes | _________ |
| Voir le taux de requêtes HTTP par seconde | _________ |
| Chercher les erreurs 500 dans les logs | _________ |
| Identifier quel microservice cause la latence | _________ |

---

**Q4.** Qu'est-ce qu'un Golden Signal en SRE ? Citez les 4 types.

Votre réponse :
```
1. _________________________
2. _________________________
3. _________________________
4. _________________________
```

---

**Q5.** Expliquez la différence entre push et pull pour la collecte de métriques.

Votre réponse :
```
________________________________________________________________________
________________________________________________________________________
________________________________________________________________________
```

---

## 🛠 Partie 1 : Déploiement de la stack

### Étape 1.1 : Récupération du projet

La structure du projet est la suivante :

```
tp6-observability-stack/
│
├── docker-compose.yml
├── .env.example
├── .env
├── README.md
├── QUICKSTART.md
├── init.sql
│
├── frontend/
│   ├── Dockerfile
│   ├── package.json
│   ├── server.js
│   └── public/
│       └── index.html
│
├── backend/
│   ├── Dockerfile
│   ├── requirements.txt
│   ├── app.py
│   ├── models.py
│   ├── config.py
│   └── init_db.py
│
├── prometheus/
│   └── prometheus.yml
│
├── logstash/
│   └── pipeline.conf
│
└── grafana/
    └── provisioning/
        ├── datasources/
        │   └── datasources.yml
        └── dashboards/
            └── dashboards.yml
```

---

### Étape 1.2 : Configuration de l'environnement

Le fichier `.env` contient déjà toutes les valeurs par défaut :

```bash
# PostgreSQL
POSTGRES_USER=user
POSTGRES_PASSWORD=pass
POSTGRES_DB=products

# Grafana
GRAFANA_ADMIN_USER=admin
GRAFANA_ADMIN_PASSWORD=admin
```

**Q6.** Ces valeurs sont-elles adaptées pour un environnement de production ?

Votre réponse : ☐ Oui ☐ Non

Si non, pourquoi ? ___________________________________________________________

---

### Étape 1.3 : Démarrage de la stack

Lancez tous les services :

```bash
docker compose up -d
```

**Q7.** Quelle commande permet de vérifier que tous les conteneurs sont bien démarrés et en état "healthy" ?

Commande : `docker compose __________`

---

**Q8.** Combien de conteneurs doivent être actifs au total ?

Réponse : **_______** conteneurs

---

### Étape 1.4 : Vérification des services

Complétez le tableau en accédant à chaque interface :

| Service | URL | Credentials | Status ✅/❌ |
|---------|-----|-------------|-------------|
| Frontend | http://localhost:3000 | - | |
| Backend API | http://localhost:5002/health | - | |
| Prometheus | http://localhost:_____ | - | |
| Grafana | http://localhost:_____ | admin/admin | |
| Kibana | http://localhost:_____ | - | |
| Jaeger UI | http://localhost:_____ | - | |

---

**Q9.** Prenez un screenshot de la page d'accueil du Frontend montrant les boutons de test.

📸 **Screenshot à inclure** : `screenshot_frontend.png`

---

**Q10.** Exécutez la commande suivante et analysez les logs :

```bash
docker compose logs backend --tail=20 | grep "initialisé"
```

Copiez la ligne indiquant que l'application Flask est initialisée :

```
________________________________________________________________________
```

---

## ✅ Checkpoint 1

- ☐ Tous les conteneurs démarrés
- ☐ Accès aux 6 interfaces web validé
- ☐ Questions Q1 à Q10 répondues

---

## 📊 Partie 2 : Métriques avec Prometheus & Grafana

### Étape 2.1 : Exploration de Prometheus

Ouvrez Prometheus : **http://localhost:9091**

**Q11.** Allez dans **Status > Targets**. Combien de targets sont scrapées par Prometheus ? Listez-les.

Réponse :
```
Target 1 : _____________________
Target 2 : _____________________
Target 3 : _____________________
Target 4 : _____________________
Target 5 : _____________________
```

---

**Q12.** Toutes les targets sont-elles en état **UP** (verte) ? Si une target est DOWN, quelle pourrait être la cause ?

Votre réponse :
```
________________________________________________________________________
________________________________________________________________________
```

---

### Étape 2.2 : Requêtes PromQL

**Q13.** Dans l'onglet **Graph**, exécutez cette requête et notez le résultat :

```promql
up
```

Que signifie un résultat `up{job="frontend"} = 1` ?

Votre réponse : _____________________________________________________________

---

**Q14.** Exécutez cette requête pour voir le taux de requêtes HTTP par seconde sur les 5 dernières minutes :

```promql
rate(http_requests_total[5m])
```

Combien de séries temporelles sont retournées ? **__________**

---

**Q15.** Filtrez pour ne voir que les requêtes vers le backend avec le code 200 :

```promql
http_requests_total{job="________", status="________"}
```

---

### Étape 2.3 : Génération de trafic

Ouvrez un terminal et exécutez :

```bash
# Générer 20 requêtes normales
for i in {1..20}; do curl http://localhost:3000/api/products; sleep 1; done
```

**Q16.** Pendant que le script tourne, exécutez dans Prometheus :

```promql
sum(rate(http_requests_total[1m]))
```

Quelle valeur approximative obtenez-vous (req/s) ? **__________**

---

### Étape 2.4 : Analyse de latence

**Q17.** Le backend expose une métrique `http_request_duration_seconds` (histogram). Quelle requête PromQL permet de calculer la latence médiane (P50) sur 5 minutes ?

```promql
histogram_quantile(_______, 
  rate(http_request_duration_seconds_bucket[5m])
)
```

---

**Q18.** Dans l'interface web du frontend (http://localhost:3000), cliquez 5 fois sur le bouton **"Requête Lente"**.

Quelle est la nouvelle latence P50 dans Prometheus ? **__________** secondes

---

**Q19.** Comparez avec la latence P99 :

```promql
histogram_quantile(0.99, 
  rate(http_request_duration_seconds_bucket[5m])
)
```

P99 = **__________** secondes

---

**Q20.** Que signifie une différence importante entre P50 et P99 ?

Votre réponse :
```
________________________________________________________________________
________________________________________________________________________
```

---

### Étape 2.5 : Dashboard Grafana

Ouvrez Grafana : **http://localhost:3001** (admin/admin)

**Q21.** Allez dans **Configuration > Data Sources**. Quel est le status de la datasource Prometheus ?

- ☐ Connected ✅
- ☐ Error ❌

---

**Q22.** Créez un nouveau dashboard :

1. Cliquez sur **+ > Dashboard > Add visualization**
2. Sélectionnez la datasource **Prometheus**
3. Utilisez cette requête :

```promql
sum(rate(http_requests_total[5m])) by (status)
```

4. Choisissez le type de visualisation **Time series**
5. Titre : "Taux de requêtes par status"

Prenez un screenshot.

📸 **Screenshot à inclure** : `screenshot_grafana_dashboard.png`

---

**Q23.** Ajoutez un second panneau montrant le taux d'erreur (% de 5xx) :

```promql
sum(rate(http_requests_total{status=~"5.."}[5m])) 
/ 
sum(rate(http_requests_total[5m])) * 100
```

Quelle est la valeur actuelle ? **__________** %

---

**Q24.** Sauvegardez votre dashboard et exportez-le au format JSON.

Chemin : **Dashboard settings > __________ > __________**

---

## ✅ Checkpoint 2

- ☐ Prometheus targets validées
- ☐ 5 requêtes PromQL exécutées
- ☐ Dashboard Grafana créé avec 2 panneaux
- ☐ Questions Q11 à Q24 répondues

---

## 📋 Partie 3 : Logs avec ELK Stack

### Étape 3.1 : Configuration de Kibana

Ouvrez Kibana : **http://localhost:5601**

**Q25.** À la première connexion, créez un Index Pattern :

1. Allez dans **Stack Management > Index Patterns** (☰ menu > Management)
2. Cliquez sur **Create index pattern**
3. Index pattern : `logs-*`
4. Time field : `@timestamp`

Combien d'index Elasticsearch correspondent à ce pattern ? **__________**

**Indice** : Allez dans **Dev Tools** et exécutez :

```
GET _cat/indices/logs-*?v
```

---

**Q26.** Si aucun index n'existe encore, attendez 2-3 minutes que Logstash ingère les premiers logs, puis générez du trafic :

```bash
for i in {1..10}; do curl http://localhost:3000/api/products; sleep 1; done
```

---

### Étape 3.2 : Exploration des logs

Allez dans **Discover**.

**Q27.** Filtrez pour n'afficher que les logs du backend en utilisant KQL (Kibana Query Language) :

```
service_name : "__________"
```

Combien de logs sont affichés sur les 15 dernières minutes ? **__________**

---

**Q28.** Ajoutez un filtre pour ne voir que les logs de niveau ERROR :

```
service_name : "backend" AND log_level : "__________"
```

---

**Q29.** Cliquez sur un log et développez le JSON. Quels champs sont présents ? (citez-en 5)

```
1. _________________________
2. _________________________
3. _________________________
4. _________________________
5. _________________________
```

---

**Q30.** Repérez le champ `trace_id` dans un log. Copiez sa valeur ici :

```
trace_id : _____________________________________________________
```

---

### Étape 3.3 : Génération d'erreurs

Dans l'interface web (http://localhost:3000), cliquez 10 fois sur le bouton **"Générer Erreur"**.

**Q31.** Rafraîchissez Kibana. Combien de nouveaux logs ERROR apparaissent ? **__________**

---

**Q32.** Créez une visualisation montrant le nombre de logs par niveau :

1. Allez dans **Visualize Library > Create visualization**
2. Choisissez **Vertical Bar**
3. Select index pattern : `logs-*`
4. **Buckets** :
   - X-axis : Aggregation = **Terms**, Field = `log_level.keyword`
5. **Metrics** :
   - Y-axis : Aggregation = **Count**

Prenez un screenshot.

📸 **Screenshot à inclure** : `screenshot_kibana_logs_chart.png`

---

### Étape 3.4 : Analyse des logs structurés

**Q33.** Le backend envoie des logs au format JSON. Quel est l'avantage par rapport à des logs en texte libre ?

Votre réponse :
```
________________________________________________________________________
________________________________________________________________________
```

---

**Q34.** Ouvrez le fichier `logstash/pipeline.conf`. Quel filtre est utilisé pour parser les logs JSON ?

Ligne : `__________ { source => "message" }`

---

**Q35.** Dans Kibana, créez un filtre pour afficher uniquement les requêtes vers `/api/slow` :

```
log_message : "*slow*"
```

Combien de résultats ? **__________**

---

## ✅ Checkpoint 3

- ☐ Index pattern Kibana créé
- ☐ Logs filtrés par service et niveau
- ☐ Visualisation créée
- ☐ Questions Q25 à Q35 répondues

---

## 🔍 Partie 4 : Distributed Tracing avec Jaeger

### Étape 4.1 : Exploration de Jaeger

Ouvrez Jaeger : **http://localhost:16686**

**Q36.** Dans le menu **Search**, sélectionnez le service **frontend-service** et cliquez sur **Find Traces**.

Combien de traces sont affichées sur les 15 dernières minutes ? **__________** traces

---

**Q37.** Cliquez sur une trace avec une durée < 100ms. Combien de spans compose cette trace ?

Réponse : **__________** spans

---

**Q38.** Listez les spans dans l'ordre d'exécution :

```
1. _________________________
2. _________________________
3. _________________________
```

---

### Étape 4.2 : Analyse d'une requête lente

Dans l'interface web, cliquez sur le bouton **"Requête Lente"**.

**Q39.** Dans Jaeger, filtrez les traces par **Min Duration = 5s**. Sélectionnez la trace la plus récente.

Durée totale : **__________** ms

---

**Q40.** Quel span est responsable de la latence ? (identifiez l'opération et sa durée)

```
Opération : _____________________
Durée : __________ ms
```

---

**Q41.** Cliquez sur le span lent et allez dans l'onglet **Tags**. Quelle est la valeur du tag `delay.seconds` ?

```
delay.seconds : __________
```

---

**Q42.** Copiez le **Trace ID** de cette trace :

```
Trace ID : _____________________________________________________
```

---

### Étape 4.3 : Corrélation Logs ↔ Traces

**Q43.** Retournez dans Kibana et cherchez ce `trace_id` dans les logs :

```
trace_id : "VOTRE_TRACE_ID_ICI"
```

Combien de logs correspondent ? **__________**

---

**Q44.** Prenez un screenshot montrant Jaeger et Kibana côte à côte avec le même `trace_id`.

📸 **Screenshot à inclure** : `screenshot_correlation_logs_traces.png`

---

### Étape 4.4 : Comparaison des traces

**Q45.** Comparez ces deux requêtes dans l'interface web :

- Requête A : Cliquez sur **"Requête Normale"**
- Requête B : Cliquez sur **"Requête Lente"**

Complétez le tableau en consultant Jaeger :

| Métrique | Requête A | Requête B |
|----------|-----------|-----------|
| Durée totale | ______ ms | ______ ms |
| Nombre de spans | ______ | ______ |
| Span le plus lent | ______ | ______ |

---

**Q46.** Dans Jaeger, sélectionnez les deux traces et utilisez le bouton **Compare**. Quelle différence majeure observez-vous ?

Votre réponse :
```
________________________________________________________________________
```

---

**Q47.** Le backend utilise la bibliothèque `jaeger-client` pour le tracing. Quels headers HTTP propagent le contexte de trace entre frontend et backend ?

- ☐ X-Trace-Id
- ☐ uber-trace-id
- ☐ X-Request-Id
- ☐ traceparent

---

## ✅ Checkpoint 4

- ☐ Traces explorées dans Jaeger
- ☐ Requête lente analysée
- ☐ Corrélation logs ↔ traces effectuée
- ☐ Questions Q36 à Q47 répondues

---

## 🚨 Partie 5 : Diagnostic d'incident

### Scénario : Le backend renvoie des erreurs 500

Vous recevez une alerte : **"Augmentation soudaine des erreurs 500 sur le backend depuis 5 minutes"**.

Votre mission : diagnostiquer la cause en utilisant les 3 piliers de l'observabilité.

---

### Étape 5.1 : Métriques - Quantifier le problème

Générez des erreurs :

```bash
# Dans l'interface web, cliquez 20 fois sur "Générer Erreur"
```

**Q48.** Dans Prometheus, calculez le taux d'erreur 5xx sur les 5 dernières minutes :

```promql
sum(rate(http_requests_total{status=~"5.."}[5m])) 
/ 
sum(rate(http_requests_total[5m])) * 100
```

Taux d'erreur actuel : **__________** %

---

**Q49.** Identifiez quel endpoint est le plus impacté :

```promql
sum(rate(http_requests_total{status=~"5.."}[5m])) by (path)
```

Endpoint problématique : **__________**

---

### Étape 5.2 : Logs - Identifier la cause

**Q50.** Dans Kibana, cherchez les logs ERROR du backend sur les 5 dernières minutes :

```
service_name : "backend" AND log_level : "ERROR" AND @timestamp >= now-5m
```

Quelle est l'erreur la plus fréquente ? (copiez le message)

```
Error message : _____________________________________________________
```

---

**Q51.** Analysez un log d'erreur. Quels champs vous donnent des indices sur la cause ?

Champs utiles :
```
1. _________________________
2. _________________________
3. _________________________
```

---

### Étape 5.3 : Traces - Localiser le bottleneck

**Q52.** Dans Jaeger, filtrez les traces avec **Tags = error:true**.

Combien de traces en erreur ? **__________**

---

**Q53.** Sélectionnez une trace en erreur. Quel span a un tag `error` ?

```
Span en erreur : _____________________
Tag error.kind : _____________________
```

---

**Q54.** Examinez les logs du span. Quelle est la cause probable de l'erreur ?

- ☐ Timeout de connexion à la base de données
- ☐ Erreur intentionnelle générée pour le test
- ☐ Contrainte de clé étrangère violée
- ☐ Table inexistante

---

### Étape 5.4 : Synthèse du diagnostic

**Q55.** En vous basant sur vos observations (métriques + logs + traces), proposez une hypothèse sur la cause racine de l'incident :

Votre hypothèse :
```
________________________________________________________________________
________________________________________________________________________
________________________________________________________________________
```

---

**Q56.** Proposez 2 actions correctives :

```
1. _____________________________________________________________________

2. _____________________________________________________________________
```

---

**Q57.** Créez un dashboard d'incident dans Grafana avec :

1. **Panneau 1** : Taux d'erreur 5xx
```promql
sum(rate(http_requests_total{status=~"5.."}[5m])) by (path)
```

2. **Panneau 2** : Latence P99
```promql
histogram_quantile(0.99, rate(http_request_duration_seconds_bucket[5m]))
```

3. **Panneau 3** : Nombre d'erreurs frontend
```promql
sum(frontend_errors_total) by (type)
```

Prenez un screenshot.

📸 **Screenshot à inclure** : `screenshot_incident_dashboard.png`

---

## ✅ Checkpoint 5 (BONUS)

- ☐ Taux d'erreur quantifié
- ☐ Logs d'erreur analysés
- ☐ Traces en erreur identifiées
- ☐ Diagnostic complet rédigé
- ☐ Dashboard d'incident créé

---

## 📦 Livrables

Vous devez rendre un document PDF contenant :

✅ Page de garde avec nom, prénom, date  
✅ Réponses aux **57 questions** (Q1 à Q57)  
✅ **7 screenshots** :
- `screenshot_frontend.png`
- `screenshot_grafana_dashboard.png`
- `screenshot_kibana_logs_chart.png`
- `screenshot_correlation_logs_traces.png`
- `screenshot_incident_dashboard.png` (bonus)

✅ Export JSON du dashboard Grafana (en annexe)  
✅ Commandes Docker utilisées (`docker compose ps`, logs, etc.)

**Format** : `TP_NOM_Prenom.pdf`

---


## 📚 Annexes

### Annexe A : Aide-mémoire PromQL

```promql
# Métrique brute
http_requests_total

# Filtrage par label
http_requests_total{job="backend", status="200"}

# Taux par seconde (5 min)
rate(http_requests_total[5m])

# Somme agrégée
sum(rate(http_requests_total[5m])) by (status)

# Latence P50
histogram_quantile(0.50, rate(http_request_duration_seconds_bucket[5m]))

# Latence P99
histogram_quantile(0.99, rate(http_request_duration_seconds_bucket[5m]))

# Taux d'erreur (%)
sum(rate(http_requests_total{status=~"5.."}[5m])) 
/ 
sum(rate(http_requests_total[5m])) * 100
```

---

### Annexe B : Aide-mémoire Kibana Query Language (KQL)

```
# Recherche simple
service_name : "backend"

# ET logique
service_name : "backend" AND log_level : "ERROR"

# OU logique
log_level : "ERROR" OR log_level : "WARN"

# Intervalle de temps
@timestamp >= now-15m

# Wildcard
log_message : "/api/*"

# Existence d'un champ
trace_id : *

# Valeur numérique
status >= 500
```

---

### Annexe C : Commandes Docker Compose utiles

```bash
# Démarrer la stack
docker compose up -d

# Voir les logs d'un service
docker compose logs -f backend

# Voir l'état des services
docker compose ps

# Redémarrer un service
docker compose restart prometheus

# Arrêter la stack
docker compose down

# Supprimer les volumes (⚠️ efface les données)
docker compose down -v

# Voir les ressources consommées
docker stats
```

---

### Annexe D : URLs de la stack

| Service | URL | Credentials |
|---------|-----|-------------|
| Frontend | http://localhost:3000 | - |
| Backend | http://localhost:5002 | - |
| Prometheus | http://localhost:9091 | - |
| Grafana | http://localhost:3001 | admin/admin |
| Kibana | http://localhost:5601 | - |
| Jaeger | http://localhost:16686 | - |
| Elasticsearch | http://localhost:9200 | - |
| PostgreSQL | localhost:5433 | user/pass |

---

### Annexe E : Troubleshooting

#### ❌ Elasticsearch ne démarre pas

**Erreur** : `max virtual memory areas vm.max_map_count [65530] is too low`

**Solution Linux** :
```bash
sudo sysctl -w vm.max_map_count=262144
```

**Solution macOS/Windows** (Docker Desktop) :
- Paramètres Docker Desktop
- Resources > Advanced > Memory : min 4 Go

---

#### ❌ Grafana : "Datasource not found"

**Solution** :
1. Vérifiez que Prometheus est UP : `docker compose ps`
2. Vérifiez l'URL dans Grafana : `http://prometheus:9090`
3. Testez : Configuration > Data Sources > Prometheus > Test

---

#### ❌ Jaeger : Aucune trace affichée

**Causes possibles** :
- Le frontend/backend n'envoient pas de traces
- Jaeger agent non accessible

**Debug** :
```bash
docker compose logs backend | grep -i "jaeger\|trace"
```

---

#### ❌ Kibana : "Index pattern creation failed"

**Solution** :
1. Vérifier qu'Elasticsearch a des données :
```bash
curl http://localhost:9200/_cat/indices?v
```

2. Attendre 2-3 minutes que Logstash ingère les logs
3. Générer du trafic sur l'application
4. Rafraîchir le pattern

---

## 🌐 Ressources complémentaires

- 📖 [Prometheus Documentation](https://prometheus.io/docs/)
- 📖 [Grafana Dashboard Guide](https://grafana.com/docs/grafana/latest/dashboards/)
- 📖 [Elastic Stack Documentation](https://www.elastic.co/guide/index.html)
- 📖 [Jaeger Documentation](https://www.jaegertracing.io/docs/)
- 📖 [OpenTelemetry](https://opentelemetry.io/)
- 📖 [Google SRE Book - Monitoring Distributed Systems](https://sre.google/sre-book/monitoring-distributed-systems/)

---

## 💡 Conseils

> **L'observabilité n'est pas du monitoring** - c'est la capacité à comprendre l'état interne d'un système en observant ses outputs. 🔍

**Astuce** : Sauvegardez régulièrement vos screenshots et réponses au fur et à mesure du TP !

---

**Bon travail ! 💪**
