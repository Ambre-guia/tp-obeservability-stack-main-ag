"""
Microservice Backend Flask avec instrumentation complète d'observabilité
- Logs structurés JSON (python-json-logger)
- Métriques Prometheus (prometheus-flask-exporter)
- Tracing distribué Jaeger (jaeger-client)
"""
import logging
import sys
import time
import random
from datetime import datetime
from flask import Flask, jsonify, request
from flask_cors import CORS
from pythonjsonlogger import jsonlogger
from prometheus_flask_exporter import PrometheusMetrics
from prometheus_client import Counter, Gauge
from jaeger_client import Config as JaegerConfig
import opentracing
from opentracing.ext import tags as ot_tags

from config import Config
from models import db, Product

# ============================================================================
# CONFIGURATION DU LOGGER JSON STRUCTURÉ
# ============================================================================
def setup_logging():
    """Configure le logger avec format JSON structuré"""
    logger = logging.getLogger()
    logger.setLevel(logging.INFO)
    
    # Handler pour stdout
    log_handler = logging.StreamHandler(sys.stdout)
    
    # Format JSON personnalisé avec les champs requis
    class CustomJsonFormatter(jsonlogger.JsonFormatter):
        def add_fields(self, log_record, record, message_dict):
            super(CustomJsonFormatter, self).add_fields(log_record, record, message_dict)
            log_record['timestamp'] = datetime.utcnow().strftime('%Y-%m-%d %H:%M:%S')
            log_record['level'] = record.levelname
            log_record['service'] = 'backend'
            
            # Ajouter trace_id et span_id si disponibles
            span = opentracing.tracer.active_span
            if span and hasattr(span, 'context'):
                try:
                    ctx = span.context
                    if hasattr(ctx, 'trace_id'):
                        log_record['trace_id'] = format(ctx.trace_id, 'x')
                    if hasattr(ctx, 'span_id'):
                        log_record['span_id'] = format(ctx.span_id, 'x')
                except:
                    pass
    
    formatter = CustomJsonFormatter(
        '%(timestamp)s %(level)s %(service)s %(message)s'
    )
    log_handler.setFormatter(formatter)
    logger.addHandler(log_handler)
    
    return logger

logger = setup_logging()

# ============================================================================
# INITIALISATION JAEGER TRACING
# ============================================================================
def init_jaeger_tracer(app):
    """
    Initialise le tracer Jaeger pour le tracing distribué
    
    Args:
        app: Instance Flask
        
    Returns:
        tracer: Instance du tracer
    """
    jaeger_config = JaegerConfig(
        config={
            'sampler': {
                'type': app.config['JAEGER_SAMPLER_TYPE'],
                'param': app.config['JAEGER_SAMPLER_PARAM'],
            },
            'local_agent': {
                'reporting_host': app.config['JAEGER_AGENT_HOST'],
                'reporting_port': app.config['JAEGER_AGENT_PORT'],
            },
            'logging': True,
        },
        service_name=app.config['JAEGER_SERVICE_NAME'],
        validate=True,
    )
    
    tracer = jaeger_config.initialize_tracer()
    opentracing.tracer = tracer
    
    logger.info(
        'Jaeger tracer initialisé',
        extra={
            'jaeger_host': app.config['JAEGER_AGENT_HOST'],
            'jaeger_port': app.config['JAEGER_AGENT_PORT']
        }
    )
    
    return tracer

# ============================================================================
# CRÉATION DE L'APPLICATION FLASK
# ============================================================================
app = Flask(__name__)
app.config.from_object(Config)

# Activer CORS pour le frontend
CORS(app, origins=app.config['CORS_ORIGINS'])

# Initialiser la base de données
db.init_app(app)

# Initialiser le tracing Jaeger
tracer = init_jaeger_tracer(app)

# Initialiser les métriques Prometheus avec endpoint /metrics automatique
metrics = PrometheusMetrics(app)

# Métriques personnalisées pour la base de données
db_queries_total = Counter(
    'database_queries_total',
    'Nombre total de requêtes SQL',
    ['operation', 'table']
)

db_connection_pool = Gauge(
    'database_connection_pool',
    'État du pool de connexions PostgreSQL',
    ['status']
)

logger.info(
    'Application Flask initialisée',
    extra={
        'port': app.config['PORT'],
        'database': app.config['DATABASE_URL'].split('@')[-1] if '@' in app.config['DATABASE_URL'] else 'N/A'
    }
)

# ============================================================================
# MIDDLEWARE POUR LOGGING ET TRACING
# ============================================================================
@app.before_request
def before_request_logging():
    """Log avant chaque requête et crée un span"""
    # Extraire le contexte de trace parent si présent
    try:
        parent_span_ctx = tracer.extract(opentracing.Format.HTTP_HEADERS, request.headers)
    except:
        parent_span_ctx = None
    
    # Créer un nouveau span pour cette requête
    span = tracer.start_span(
        f"{request.method} {request.path}",
        child_of=parent_span_ctx
    )
    span.set_tag(ot_tags.SPAN_KIND, ot_tags.SPAN_KIND_RPC_SERVER)
    span.set_tag(ot_tags.HTTP_METHOD, request.method)
    span.set_tag(ot_tags.HTTP_URL, request.url)
    span.set_tag('http.path', request.path)
    
    # Stocker le span dans g pour y accéder plus tard
    from flask import g
    g.span = span
    
    logger.info(
        f'Requête reçue: {request.method} {request.path}',
        extra={
            'method': request.method,
            'path': request.path,
            'remote_addr': request.remote_addr
        }
    )

@app.after_request
def after_request_logging(response):
    """Log après chaque requête et ferme le span"""
    from flask import g
    if hasattr(g, 'span'):
        g.span.set_tag(ot_tags.HTTP_STATUS_CODE, response.status_code)
        if response.status_code >= 400:
            g.span.set_tag(ot_tags.ERROR, True)
        g.span.finish()
    
    logger.info(
        f'Requête complétée: {request.method} {request.path}',
        extra={
            'method': request.method,
            'path': request.path,
            'status': response.status_code
        }
    )
    return response

# ============================================================================
# ROUTES API
# ============================================================================

@app.route('/health', methods=['GET'])
def health_check():
    """
    Healthcheck avec vérification de la connexion base de données
    
    Returns:
        JSON: Statut du service et de la base de données
    """
    logger.info('Healthcheck appelé')
    
    health_status = {
        'status': 'UP',
        'service': 'backend',
        'timestamp': datetime.utcnow().isoformat()
    }
    
    # Vérifier la connexion à la base de données
    try:
        with opentracing.tracer.start_active_span('db_health_check'):
            db.session.execute(db.text('SELECT 1'))
            health_status['database'] = 'connected'
            
            # Métriques du pool de connexions (compatible SQLAlchemy 2.0)
            try:
                pool = db.engine.pool
                db_connection_pool.labels(status='size').set(pool.size())
                # checkedout() pour SQLAlchemy 2.0
                if hasattr(pool, 'checkedout'):
                    db_connection_pool.labels(status='checked_out').set(pool.checkedout())
            except:
                pass
            
            logger.info('Base de données accessible')
    except Exception as e:
        health_status['database'] = 'disconnected'
        health_status['status'] = 'DEGRADED'
        logger.error(f'Erreur connexion base de données: {str(e)}')
        return jsonify(health_status), 503
    
    return jsonify(health_status), 200

@app.route('/products', methods=['GET'])
def get_products():
    """
    Récupère tous les produits depuis PostgreSQL
    
    Returns:
        JSON: Liste des produits
    """
    logger.info('Récupération de tous les produits')
    
    try:
        with opentracing.tracer.start_active_span('db_query_products') as scope:
            scope.span.set_tag('db.type', 'sql')
            scope.span.set_tag('db.statement', 'SELECT * FROM products')
            
            products = Product.query.all()
            db_queries_total.labels(operation='SELECT', table='products').inc()
            
            logger.info(
                f'{len(products)} produits récupérés',
                extra={'count': len(products)}
            )
            
            return jsonify([product.to_dict() for product in products]), 200
            
    except Exception as e:
        logger.error(
            f'Erreur lors de la récupération des produits: {str(e)}',
            exc_info=True
        )
        return jsonify({
            'error': 'Erreur serveur',
            'message': str(e)
        }), 500

@app.route('/products/<int:product_id>', methods=['GET'])
def get_product(product_id):
    """
    Récupère un produit spécifique par son ID
    
    Args:
        product_id (int): ID du produit
        
    Returns:
        JSON: Produit trouvé ou erreur 404
    """
    logger.info(f'Récupération du produit ID={product_id}')
    
    try:
        with opentracing.tracer.start_active_span('db_query_product_by_id') as scope:
            scope.span.set_tag('db.type', 'sql')
            scope.span.set_tag('db.statement', f'SELECT * FROM products WHERE id = {product_id}')
            scope.span.set_tag('product.id', product_id)
            
            product = Product.query.get(product_id)
            db_queries_total.labels(operation='SELECT', table='products').inc()
            
            if product is None:
                logger.warning(f'Produit ID={product_id} non trouvé')
                return jsonify({
                    'error': 'Produit non trouvé',
                    'product_id': product_id
                }), 404
            
            logger.info(f'Produit ID={product_id} trouvé: {product.name}')
            return jsonify(product.to_dict()), 200
            
    except Exception as e:
        logger.error(
            f'Erreur lors de la récupération du produit ID={product_id}: {str(e)}',
            exc_info=True
        )
        return jsonify({
            'error': 'Erreur serveur',
            'message': str(e)
        }), 500

@app.route('/products', methods=['POST'])
def create_product():
    """
    Crée un nouveau produit dans la base de données
    
    Request Body:
        {
            "name": "Nom du produit",
            "price": 29.99,
            "category": "Catégorie"
        }
        
    Returns:
        JSON: Produit créé avec son ID
    """
    logger.info('Création d\'un nouveau produit')
    
    try:
        data = request.get_json()
        
        if not data:
            return jsonify({'error': 'Données JSON manquantes'}), 400
        
        # Créer le produit depuis les données
        product = Product.from_dict(data)
        
        # Valider les données
        is_valid, validation_message = product.validate()
        if not is_valid:
            logger.warning(f'Validation échouée: {validation_message}')
            return jsonify({
                'error': 'Validation échouée',
                'message': validation_message
            }), 400
        
        # Enregistrer en base de données
        with opentracing.tracer.start_active_span('db_insert_product') as scope:
            scope.span.set_tag('db.type', 'sql')
            scope.span.set_tag('db.statement', 'INSERT INTO products')
            
            db.session.add(product)
            db.session.commit()
            db_queries_total.labels(operation='INSERT', table='products').inc()
            
            logger.info(
                f'Produit créé avec succès: ID={product.id}',
                extra={
                    'product_id': product.id,
                    'product_name': product.name
                }
            )
            
            return jsonify(product.to_dict()), 201
            
    except Exception as e:
        db.session.rollback()
        logger.error(
            f'Erreur lors de la création du produit: {str(e)}',
            exc_info=True
        )
        return jsonify({
            'error': 'Erreur serveur',
            'message': str(e)
        }), 500

@app.route('/slow', methods=['GET'])
def slow_endpoint():
    """
    Simule une latence de 5 secondes pour tester les timeouts
    
    Returns:
        JSON: Message après la latence
    """
    delay = app.config['SLOW_ENDPOINT_DELAY']
    logger.info(f'Endpoint lent appelé - simulation de {delay}s de latence')
    
    with opentracing.tracer.start_active_span('simulate_slow_operation') as scope:
        scope.span.set_tag('delay.seconds', delay)
        time.sleep(delay)
    
    logger.info(f'Latence de {delay}s terminée')
    
    return jsonify({
        'message': f'Réponse après {delay} secondes de latence',
        'delay_seconds': delay,
        'timestamp': datetime.utcnow().isoformat()
    }), 200

@app.route('/error', methods=['GET'])
def error_endpoint():
    """
    Génère intentionnellement une erreur aléatoire pour tester la gestion d'erreurs
    
    Returns:
        JSON: Message d'erreur
    """
    logger.warning('Endpoint d\'erreur appelé - génération d\'une exception')
    
    errors = [
        ('Division par zéro', lambda: 1 / 0),
        ('Index hors limites', lambda: [][999]),
        ('Clé inexistante', lambda: {}['key_inexistante']),
        ('Type invalide', lambda: int('not_a_number')),
    ]
    
    error_name, error_func = random.choice(errors)
    
    try:
        span = opentracing.tracer.active_span
        if span:
            span.set_tag(ot_tags.ERROR, True)
            span.log_kv({'event': 'error', 'error.kind': error_name})
        
        error_func()
        
    except Exception as e:
        logger.error(
            f'Exception générée intentionnellement: {error_name}',
            exc_info=True,
            extra={'error_type': error_name}
        )
        
        return jsonify({
            'error': 'Erreur interne du serveur',
            'type': error_name,
            'message': str(e),
            'timestamp': datetime.utcnow().isoformat()
        }), 500

# ============================================================================
# GESTION DES ERREURS GLOBALE
# ============================================================================
@app.errorhandler(404)
def not_found(error):
    """Gestion des erreurs 404"""
    logger.warning(f'Route non trouvée: {request.path}')
    return jsonify({
        'error': 'Route non trouvée',
        'path': request.path
    }), 404

@app.errorhandler(500)
def internal_error(error):
    """Gestion des erreurs 500"""
    db.session.rollback()
    logger.error(f'Erreur interne: {str(error)}', exc_info=True)
    return jsonify({
        'error': 'Erreur interne du serveur',
        'message': str(error)
    }), 500

# ============================================================================
# INITIALISATION DE LA BASE DE DONNÉES
# ============================================================================
@app.cli.command()
def init_db():
    """Commande CLI pour initialiser la base de données"""
    db.create_all()
    logger.info('Base de données initialisée')
    print('✅ Base de données initialisée avec succès')

# ============================================================================
# POINT D'ENTRÉE PRINCIPAL
# ============================================================================
if __name__ == '__main__':
    logger.info(
        f'Démarrage du backend service sur {app.config["HOST"]}:{app.config["PORT"]}'
    )
    
    app.run(
        host=app.config['HOST'],
        port=app.config['PORT'],
        debug=app.config['DEBUG']
    )
