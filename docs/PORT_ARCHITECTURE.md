# DaaS Port Architecture

## Overview

DaaS uses a **reverse proxy architecture** where only the main Nginx proxy is exposed to the host, and all application containers communicate through an isolated Docker network.

## Port Flow

```
Internet/User
    ↓
Host Port 80 (HTTP) / 443 (HTTPS)
    ↓
DaaS Nginx Proxy Container
    ↓
daas-network (Docker internal network)
    ↓
Your Application Containers (ports 8080, 3000, 5000, etc.)
```

## Key Concepts

### 1. Host Ports (80/443)
- **Only used by**: DaaS Nginx Proxy
- **Purpose**: Accept all incoming HTTP/HTTPS traffic
- **SSL/TLS**: Terminated at this level by Certbot certificates
- **Never used by**: Your application containers

### 2. Internal Container Ports
- **Examples**: 8080, 3000, 5000, 8001, etc.
- **Visibility**: Only accessible within the `daas-network`
- **No conflicts**: Multiple apps can use the same internal port (e.g., both can use 8080)
- **Not exposed**: Never mapped to host ports

### 3. The Question: "What port?"
When DaaS asks for a port, it means:
- **"What port does your application listen on INSIDE its container?"**
- NOT "What host port should I expose?"

## Examples

### Example 1: Simple Nginx App
```dockerfile
# Your Dockerfile
FROM nginx:alpine
RUN echo 'server { listen 8080; ... }' > /etc/nginx/conf.d/default.conf
EXPOSE 8080
```

**Deployment**:
- Domain: `myapp.example.com`
- Internal Port: `8080`

**Result**:
- User visits: `https://myapp.example.com`
- DaaS Nginx forwards to: `myapp-container:8080`
- Your Nginx inside container serves on: `8080`

### Example 2: Flask API
```python
# Your app.py
if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000)
```

**Deployment**:
- Domain: `api.example.com`
- Internal Port: `5000`

**Result**:
- User visits: `https://api.example.com`
- DaaS Nginx forwards to: `api-container:5000`
- Your Flask app serves on: `5000`

### Example 3: Multi-Service App
```yaml
# docker-compose.yml
services:
  frontend:
    # Nginx on port 8080
  api:
    # Flask on port 5000
  redis:
    # Redis on port 6379 (internal only, no domain)
```

**Deployment**:
- Frontend domain: `app.example.com`, port `8080`
- API domain: `api.example.com`, port `5000`
- Redis: No domain (internal service)

**Result**:
- User visits `https://app.example.com` → frontend:8080
- User visits `https://api.example.com` → api:5000
- Frontend/API can access redis:6379 internally

## Why This Architecture?

### ✅ Advantages

1. **No Port Conflicts**: Multiple apps can use the same internal port
2. **Centralized SSL**: One place to manage certificates
3. **Security**: Apps not directly exposed to internet
4. **Flexibility**: Easy to add/remove services
5. **Standard Ports**: Users always access via 80/443

### ❌ What NOT to Do

1. **Don't use port 80 in your containers**: Reserved for proxy
2. **Don't expose ports in docker-compose**: DaaS handles routing
3. **Don't map ports to host**: Everything goes through the network

## Docker Network Details

All containers are connected to `daas-network`:
- **Type**: Bridge network
- **DNS**: Automatic service discovery by container name
- **Isolation**: Containers can only talk to each other, not directly to host
- **Proxy Access**: Only the Nginx proxy bridges external traffic

## Common Ports by Technology

| Technology | Common Internal Port |
|------------|---------------------|
| Nginx      | 8080                |
| Apache     | 8080                |
| Node.js    | 3000                |
| Flask/Django | 5000 or 8000      |
| Spring Boot | 8080               |
| Go apps    | 8080                |
| React dev  | 3000                |
| Vue dev    | 8080                |

**Remember**: These are just conventions. You can use any non-reserved port (1024-65535).
