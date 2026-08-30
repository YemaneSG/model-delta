# Multi-stage build: Node builds the Angular app, nginx serves the static output.

FROM node:22-alpine AS builder

WORKDIR /app

COPY package.json package-lock.json ./
RUN npm ci --prefer-offline

COPY . .
RUN npx ng build --configuration production

# ── Serve stage ──────────────────────────────────────────────────────────────

FROM nginx:1.27-alpine

COPY nginx.conf /etc/nginx/conf.d/default.conf
COPY --from=builder /app/dist/showcase-ui/browser /usr/share/nginx/html

EXPOSE 80
