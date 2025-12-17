# ============================================================================
# Stage 1: Construction des dépendances
# ============================================================================
FROM node:18-alpine AS builder

# Définir le répertoire de travail
WORKDIR /app

# Copier uniquement les fichiers de dépendances pour tirer parti du cache Docker
COPY package*.json ./

# Installer les dépendances de production uniquement
RUN npm ci --only=production && \
    npm cache clean --force

# ============================================================================
# Stage 2: Image de production optimisée
# ============================================================================
FROM node:18-alpine

# Métadonnées de l'image
LABEL maintainer="observability-team"
LABEL description="Frontend service avec instrumentation complète (Logs, Métriques, Traces)"

# Installer dumb-init pour gérer les signaux proprement
RUN apk add --no-cache dumb-init

# Créer un utilisateur non-root pour la sécurité
RUN addgroup -g 1001 -S nodejs && \
    adduser -S nodejs -u 1001

# Définir le répertoire de travail
WORKDIR /app

# Copier les dépendances depuis le stage builder
COPY --from=builder --chown=nodejs:nodejs /app/node_modules ./node_modules

# Copier le code source de l'application
COPY --chown=nodejs:nodejs server.js ./
COPY --chown=nodejs:nodejs public ./public/

# Variables d'environnement par défaut
ENV NODE_ENV=production \
    PORT=3000 \
    BACKEND_URL=http://backend:5000 \
    JAEGER_AGENT_HOST=jaeger \
    JAEGER_AGENT_PORT=6831

# Exposer le port de l'application
EXPOSE 3000

# Changer vers l'utilisateur non-root
USER nodejs

# Healthcheck pour vérifier que le service est opérationnel
HEALTHCHECK --interval=30s --timeout=3s --start-period=10s --retries=3 \
    CMD node -e "require('http').get('http://localhost:3000/health', (r) => { process.exit(r.statusCode === 200 ? 0 : 1); })"

# Utiliser dumb-init pour gérer les signaux proprement (SIGTERM, etc.)
ENTRYPOINT ["dumb-init", "--"]

# Démarrer l'application
CMD ["node", "server.js"]
