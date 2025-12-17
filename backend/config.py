"""
Configuration du microservice backend
Centralise toutes les variables d'environnement et paramètres
"""
import os
from datetime import timedelta

class Config:
    """Configuration principale de l'application"""
    
    # Configuration Flask
    SECRET_KEY = os.environ.get('SECRET_KEY', 'dev-secret-key-change-in-production')
    DEBUG = os.environ.get('FLASK_DEBUG', 'False').lower() == 'true'
    
    # Configuration serveur
    PORT = int(os.environ.get('PORT', 5000))
    HOST = os.environ.get('HOST', '0.0.0.0')
    
    # Configuration base de données PostgreSQL
    DATABASE_URL = os.environ.get(
        'DATABASE_URL',
        'postgresql://postgres:postgres@db:5432/products_db'
    )
    SQLALCHEMY_DATABASE_URI = DATABASE_URL
    SQLALCHEMY_TRACK_MODIFICATIONS = False
    SQLALCHEMY_ECHO = os.environ.get('SQL_ECHO', 'False').lower() == 'true'
    
    # Configuration du pool de connexions PostgreSQL
    SQLALCHEMY_ENGINE_OPTIONS = {
        'pool_size': int(os.environ.get('DB_POOL_SIZE', 10)),
        'pool_recycle': int(os.environ.get('DB_POOL_RECYCLE', 3600)),
        'pool_pre_ping': True,  # Vérifie la connexion avant utilisation
        'max_overflow': int(os.environ.get('DB_MAX_OVERFLOW', 20)),
    }
    
    # Configuration Jaeger
    JAEGER_AGENT_HOST = os.environ.get('JAEGER_AGENT_HOST', 'jaeger')
    JAEGER_AGENT_PORT = int(os.environ.get('JAEGER_AGENT_PORT', 6831))
    JAEGER_SERVICE_NAME = os.environ.get('JAEGER_SERVICE_NAME', 'backend-service')
    JAEGER_SAMPLER_TYPE = os.environ.get('JAEGER_SAMPLER_TYPE', 'const')
    JAEGER_SAMPLER_PARAM = int(os.environ.get('JAEGER_SAMPLER_PARAM', 1))
    
    # Configuration CORS
    CORS_ORIGINS = os.environ.get('CORS_ORIGINS', '*')
    
    # Simulation de latence pour endpoint /slow
    SLOW_ENDPOINT_DELAY = int(os.environ.get('SLOW_ENDPOINT_DELAY', 5))
