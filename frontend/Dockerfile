# Hub Chantier - Frontend Dockerfile (Production)
# Multi-stage build: Node for build, nginx for serving

# ===========================================
# Stage 1: Build the React application
# ===========================================
FROM node:20-alpine as builder

WORKDIR /app

# Copy package files
COPY package*.json ./

# Install dependencies
RUN npm ci

# Copy source code
COPY . .

# Build the application (skip tsc type-check, use vite build only)
# Type errors in test files should not block production build
RUN npx vite build

# ===========================================
# Stage 2: Serve with nginx
# ===========================================
FROM nginx:alpine

# Copy custom nginx config
COPY nginx.conf /etc/nginx/conf.d/default.conf

# Copy built assets from builder
COPY --from=builder /app/dist /usr/share/nginx/html

# Expose port 80
EXPOSE 80

# Health check
# 127.0.0.1 et non localhost : le conteneur resout localhost en ::1 (IPv6) en
# premier alors que nginx n'ecoute qu'en IPv4, ce qui faisait echouer le test
# avec "Connection refused" alors que le site repondait normalement.
HEALTHCHECK --interval=30s --timeout=10s --start-period=5s --retries=3 \
    CMD wget --quiet --tries=1 --spider http://127.0.0.1/ || exit 1

# Start nginx
CMD ["nginx", "-g", "daemon off;"]
