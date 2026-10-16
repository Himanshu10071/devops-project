# ---------- build stage: Node compiles the React app into static files ----------
FROM node:24-alpine AS build
WORKDIR /app
COPY package.json package-lock.json ./
RUN npm ci --no-audit --no-fund
COPY . .
RUN npm run build

# ---------- runtime stage: unprivileged Nginx serves dist/ (no Node in the final image) ----------
FROM nginxinc/nginx-unprivileged:1.30-alpine

# Where Nginx proxies /api. Docker Compose uses the "backend" service name;
# the Helm chart overrides it with the in-cluster backend Service.
ENV BACKEND_URL=http://backend:8000

USER root
RUN apk upgrade --no-cache
USER 101

COPY --chown=101:101 nginx.conf.template /etc/nginx/templates/default.conf.template
COPY --chown=101:101 --from=build /app/dist /usr/share/nginx/html

EXPOSE 8080
HEALTHCHECK --interval=30s --timeout=3s CMD wget -qO- http://127.0.0.1:8080/healthz || exit 1
