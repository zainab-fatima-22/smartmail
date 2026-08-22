# SmartMail frontend — multi-stage build: compile with Vite, serve the
# static output with nginx.
#
# IMPORTANT LIMITATION: Vite embeds environment variables (VITE_API_URL)
# into the JavaScript bundle AT BUILD TIME, not at container start time.
# That means the backend URL must be known when this image is built. Pass
# it as a build arg:
#   docker build --build-arg VITE_API_URL=https://api.example.com -t smartmail-frontend .
# The default below (http://localhost:8000) works for local
# docker-compose use, where both containers run on the same machine.

FROM node:20-slim AS build

WORKDIR /app

COPY frontend/package.json frontend/package-lock.json* ./
RUN npm install

COPY frontend/ ./

ARG VITE_API_URL=http://localhost:8000
ENV VITE_API_URL=$VITE_API_URL

RUN npm run build

# ---- Serve stage ----
FROM nginx:alpine

COPY --from=build /app/dist /usr/share/nginx/html

# React Router uses client-side routing (BrowserRouter) — without this,
# refreshing the browser on e.g. /history would 404 at the nginx level
# instead of letting React Router handle the route.
RUN echo 'server { \
    listen 80; \
    root /usr/share/nginx/html; \
    index index.html; \
    location / { try_files $uri $uri/ /index.html; } \
}' > /etc/nginx/conf.d/default.conf

EXPOSE 80

HEALTHCHECK --interval=30s --timeout=5s --start-period=10s --retries=3 \
    CMD wget -q --spider http://localhost:80 || exit 1

CMD ["nginx", "-g", "daemon off;"]
