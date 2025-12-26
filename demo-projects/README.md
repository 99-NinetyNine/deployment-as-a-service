# Demo Projects

This directory contains example projects to test DaaS functionality.

## Projects

### 1. simple-web
A single-service project using only a Dockerfile. Serves a static HTML page with Nginx on port 8080.

**Structure**:
- `Dockerfile`: Nginx-based web server (listens on port 8080)
- `index.html`: Simple landing page

**Deployment**:
```bash
./daas deploy demo-projects/simple-web
# Enter domain: test.local
# Enter port: 8080
```

### 2. multi-service
A multi-service project using Docker Compose with three services:
- **frontend**: Nginx serving a static page (internal port 8080)
- **api**: Flask REST API with Redis integration (internal port 5000)
- **redis**: Redis cache (internal, no domain needed)

**Structure**:
- `docker-compose.yml`: Service orchestration
- `frontend/`: Nginx-based frontend
- `api/`: Flask API with Redis

**Deployment**:
```bash
./daas deploy demo-projects/multi-service
```

When prompted:
- **frontend**: Enter domain (e.g., `app.local`) and port `8080`
- **api**: Enter domain (e.g., `api.local`) and port `5000`
- **redis**: Leave blank (internal service)

## Important: Port Architecture

The ports you enter are **INTERNAL container ports**, not host ports:
- Your services run on ports like 8080, 3000, 5000 INSIDE their containers
- The DaaS Nginx proxy (on host ports 80/443) forwards traffic to these internal ports
- No services are exposed directly to the host - everything goes through the proxy
- This prevents port conflicts and provides SSL termination

## Testing Locally

For local testing without real domains, you can use `/etc/hosts`:

```bash
sudo nano /etc/hosts
```

Add entries:
```
127.0.0.1  app.local
127.0.0.1  api.local
```

Then access:
- Frontend: http://app.local
- API: http://api.local
