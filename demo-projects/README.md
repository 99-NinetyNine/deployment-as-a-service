# Demo Projects

This directory contains example projects to test DaaS functionality.

## Projects

### 1. simple-web
A single-service project using only a Dockerfile. Serves a static HTML page with Nginx.

**Structure**:
- `Dockerfile`: Nginx-based web server
- `index.html`: Simple landing page

**Deployment**:
```bash
./daas deploy /home/acer/daas/demo-projects/simple-web
```

### 2. multi-service
A multi-service project using Docker Compose with three services:
- **frontend**: Nginx serving a static page (port 80)
- **api**: Flask REST API with Redis integration (port 5000)
- **redis**: Redis cache (internal, no domain needed)

**Structure**:
- `docker-compose.yml`: Service orchestration
- `frontend/`: Nginx-based frontend
- `api/`: Flask API with Redis

**Deployment**:
```bash
./daas deploy /home/acer/daas/demo-projects/multi-service
```

When prompted:
- **frontend**: Enter domain (e.g., `app.local`) and port `80`
- **api**: Enter domain (e.g., `api.local`) and port `5000`
- **redis**: Leave blank (internal service)

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
