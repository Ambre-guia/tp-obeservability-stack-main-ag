const express = require('express');
const axios = require('axios');
const winston = require('winston');
const promClient = require('prom-client');
const { initTracer } = require('jaeger-client');
const opentracing = require('opentracing');
const { v4: uuidv4 } = require('uuid');

// ============================================================================
// CONFIGURATION
// ============================================================================
const PORT = process.env.PORT || 3000;
const BACKEND_URL = process.env.BACKEND_URL || 'http://backend:5000';
const JAEGER_AGENT_HOST = process.env.JAEGER_AGENT_HOST || 'jaeger';
const JAEGER_AGENT_PORT = process.env.JAEGER_AGENT_PORT || 6831;

// ============================================================================
// LOGGER (Winston) - Logs structurés JSON
// ============================================================================
const logger = winston.createLogger({
  level: 'info',
  format: winston.format.combine(
    winston.format.timestamp({ format: 'YYYY-MM-DD HH:mm:ss' }),
    winston.format.errors({ stack: true }),
    winston.format.json()
  ),
  defaultMeta: { service: 'frontend' },
  transports: [
    new winston.transports.Console()
  ]
});

// ============================================================================
// MÉTRIQUES PROMETHEUS
// ============================================================================
const register = new promClient.Registry();

// Métriques par défaut (mémoire, CPU, etc.)
promClient.collectDefaultMetrics({ register });

// Counter: nombre total de requêtes HTTP
const httpRequestsTotal = new promClient.Counter({
  name: 'http_requests_total',
  help: 'Nombre total de requêtes HTTP',
  labelNames: ['method', 'path', 'status'],
  registers: [register]
});

// Histogram: durée des requêtes HTTP
const httpRequestDuration = new promClient.Histogram({
  name: 'http_request_duration_seconds',
  help: 'Durée des requêtes HTTP en secondes',
  labelNames: ['method', 'path', 'status'],
  buckets: [0.1, 0.5, 1, 2, 5, 10],
  registers: [register]
});

// Counter: nombre total d'erreurs frontend
const frontendErrorsTotal = new promClient.Counter({
  name: 'frontend_errors_total',
  help: 'Nombre total d\'erreurs du frontend',
  labelNames: ['type'],
  registers: [register]
});

// ============================================================================
// TRACING JAEGER
// ============================================================================
const jaegerConfig = {
  serviceName: 'frontend-service',
  sampler: {
    type: 'const',
    param: 1, // Échantillonner toutes les traces
  },
  reporter: {
    logSpans: true,
    agentHost: JAEGER_AGENT_HOST,
    agentPort: JAEGER_AGENT_PORT,
  },
};

const jaegerOptions = {
  logger: {
    info: (msg) => logger.info(msg),
    error: (msg) => logger.error(msg),
  },
};

const tracer = initTracer(jaegerConfig, jaegerOptions);

// ============================================================================
// EXPRESS APP
// ============================================================================
const app = express();

// Servir les fichiers statiques
app.use(express.static('public'));
app.use(express.json());

// ============================================================================
// MIDDLEWARE: Tracing et métriques automatiques
// ============================================================================
app.use((req, res, next) => {
  const startTime = Date.now();
  const requestId = uuidv4();
  
  // Extraire le contexte de trace parent si présent
  const parentSpanContext = tracer.extract(opentracing.FORMAT_HTTP_HEADERS, req.headers);
  
  // Créer un nouveau span pour cette requête
  const span = tracer.startSpan(`${req.method} ${req.path}`, {
    childOf: parentSpanContext || undefined,
    tags: {
      [opentracing.Tags.SPAN_KIND]: opentracing.Tags.SPAN_KIND_RPC_SERVER,
      [opentracing.Tags.HTTP_METHOD]: req.method,
      [opentracing.Tags.HTTP_URL]: req.url,
      'request.id': requestId,
    },
  });

  // Attacher le span et requestId à la requête
  req.span = span;
  req.requestId = requestId;
  req.traceId = span.context().toTraceId();

  logger.info({
    message: 'Requête reçue',
    method: req.method,
    path: req.path,
    request_id: requestId,
    trace_id: req.traceId,
  });

  // Intercepter la réponse
  const originalSend = res.send;
  res.send = function (data) {
    res.send = originalSend;
    
    const duration = (Date.now() - startTime) / 1000;
    
    // Enregistrer les métriques
    httpRequestsTotal.labels(req.method, req.path, res.statusCode.toString()).inc();
    httpRequestDuration.labels(req.method, req.path, res.statusCode.toString()).observe(duration);
    
    // Compléter le span
    span.setTag(opentracing.Tags.HTTP_STATUS_CODE, res.statusCode);
    if (res.statusCode >= 400) {
      span.setTag(opentracing.Tags.ERROR, true);
    }
    span.finish();
    
    logger.info({
      message: 'Requête complétée',
      method: req.method,
      path: req.path,
      status: res.statusCode,
      duration_seconds: duration.toFixed(3),
      request_id: requestId,
      trace_id: req.traceId,
    });
    
    return res.send(data);
  };

  next();
});

// ============================================================================
// ROUTES
// ============================================================================

/**
 * GET / - Page HTML principale
 */
app.get('/', (req, res) => {
  res.sendFile(__dirname + '/public/index.html');
});

/**
 * GET /health - Healthcheck
 */
app.get('/health', (req, res) => {
  logger.info({
    message: 'Healthcheck appelé',
    request_id: req.requestId,
    trace_id: req.traceId,
  });
  
  res.status(200).json({
    status: 'UP',
    service: 'frontend',
    timestamp: new Date().toISOString(),
  });
});

/**
 * GET /metrics - Métriques Prometheus
 */
app.get('/metrics', async (req, res) => {
  res.set('Content-Type', register.contentType);
  res.end(await register.metrics());
});

/**
 * GET /api/products - Appelle le backend pour récupérer les produits
 */
app.get('/api/products', async (req, res) => {
  const span = req.span;
  const childSpan = tracer.startSpan('call_backend_products', { childOf: span });
  
  try {
    logger.info({
      message: 'Appel backend /products',
      backend_url: BACKEND_URL,
      request_id: req.requestId,
      trace_id: req.traceId,
    });

    // Préparer les headers avec propagation du contexte de trace
    const headers = {};
    tracer.inject(childSpan, opentracing.FORMAT_HTTP_HEADERS, headers);

    childSpan.setTag(opentracing.Tags.HTTP_METHOD, 'GET');
    childSpan.setTag(opentracing.Tags.HTTP_URL, `${BACKEND_URL}/products`);
    
    // Appel au backend
    const response = await axios.get(`${BACKEND_URL}/products`, {
      headers,
      timeout: 5000,
    });

    childSpan.setTag(opentracing.Tags.HTTP_STATUS_CODE, response.status);
    childSpan.finish();

    logger.info({
      message: 'Réponse backend reçue',
      status: response.status,
      products_count: response.data?.length || 0,
      request_id: req.requestId,
      trace_id: req.traceId,
    });

    res.json(response.data);
  } catch (error) {
    childSpan.setTag(opentracing.Tags.ERROR, true);
    childSpan.log({
      event: 'error',
      message: error.message,
    });
    childSpan.finish();

    frontendErrorsTotal.labels('backend_call_error').inc();

    logger.error({
      message: 'Erreur lors de l\'appel au backend',
      error: error.message,
      backend_url: BACKEND_URL,
      request_id: req.requestId,
      trace_id: req.traceId,
      stack: error.stack,
    });

    res.status(503).json({
      error: 'Service backend indisponible',
      message: error.message,
    });
  }
});

/**
 * GET /api/slow - Appelle le backend avec endpoint lent
 */
app.get('/api/slow', async (req, res) => {
  const span = req.span;
  const childSpan = tracer.startSpan('call_backend_slow', { childOf: span });
  
  try {
    logger.info({
      message: 'Appel backend /slow',
      backend_url: BACKEND_URL,
      request_id: req.requestId,
      trace_id: req.traceId,
    });

    const headers = {};
    tracer.inject(childSpan, opentracing.FORMAT_HTTP_HEADERS, headers);

    childSpan.setTag(opentracing.Tags.HTTP_METHOD, 'GET');
    childSpan.setTag(opentracing.Tags.HTTP_URL, `${BACKEND_URL}/slow`);
    
    const response = await axios.get(`${BACKEND_URL}/slow`, {
      headers,
      timeout: 15000, // Timeout plus long pour l'endpoint lent
    });

    childSpan.setTag(opentracing.Tags.HTTP_STATUS_CODE, response.status);
    childSpan.finish();

    logger.info({
      message: 'Réponse backend lente reçue',
      status: response.status,
      request_id: req.requestId,
      trace_id: req.traceId,
    });

    res.json(response.data);
  } catch (error) {
    childSpan.setTag(opentracing.Tags.ERROR, true);
    childSpan.log({
      event: 'error',
      message: error.message,
    });
    childSpan.finish();

    frontendErrorsTotal.labels('backend_slow_error').inc();

    logger.error({
      message: 'Erreur lors de l\'appel au backend (endpoint lent)',
      error: error.message,
      request_id: req.requestId,
      trace_id: req.traceId,
    });

    res.status(503).json({
      error: 'Timeout ou erreur sur endpoint lent',
      message: error.message,
    });
  }
});

/**
 * GET /api/error - Génère intentionnellement une erreur 500
 */
app.get('/api/error', (req, res) => {
  logger.warn({
    message: 'Erreur intentionnelle déclenchée',
    request_id: req.requestId,
    trace_id: req.traceId,
  });

  frontendErrorsTotal.labels('intentional_error').inc();

  req.span.setTag(opentracing.Tags.ERROR, true);
  req.span.log({
    event: 'error',
    message: 'Erreur intentionnelle pour test',
  });

  res.status(500).json({
    error: 'Erreur interne du serveur',
    message: 'Cette erreur a été générée intentionnellement pour tester l\'observabilité',
    timestamp: new Date().toISOString(),
  });
});

// ============================================================================
// GESTION DES ERREURS GLOBALE
// ============================================================================
app.use((err, req, res, next) => {
  frontendErrorsTotal.labels('unhandled_error').inc();

  logger.error({
    message: 'Erreur non gérée',
    error: err.message,
    stack: err.stack,
    request_id: req.requestId,
    trace_id: req.traceId,
  });

  if (req.span) {
    req.span.setTag(opentracing.Tags.ERROR, true);
    req.span.log({
      event: 'error',
      message: err.message,
      stack: err.stack,
    });
  }

  res.status(500).json({
    error: 'Erreur interne',
    message: err.message,
  });
});

// ============================================================================
// DÉMARRAGE DU SERVEUR
// ============================================================================
app.listen(PORT, () => {
  logger.info({
    message: `Frontend service démarré sur le port ${PORT}`,
    port: PORT,
    backend_url: BACKEND_URL,
    jaeger_agent: `${JAEGER_AGENT_HOST}:${JAEGER_AGENT_PORT}`,
  });
  
  console.log(`🚀 Frontend service en écoute sur http://localhost:${PORT}`);
  console.log(`📊 Métriques Prometheus: http://localhost:${PORT}/metrics`);
  console.log(`💚 Healthcheck: http://localhost:${PORT}/health`);
});

// Gestion de l'arrêt gracieux
process.on('SIGTERM', () => {
  logger.info('Signal SIGTERM reçu, arrêt du serveur...');
  tracer.close(() => {
    process.exit(0);
  });
});
