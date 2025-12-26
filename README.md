# DaaS - Deployment as a Service

**DaaS** is a powerful, automated deployment system for Docker and Docker Compose projects. It simplifies the entire deployment workflow by automatically handling repository cloning, container orchestration, reverse proxy configuration, and SSL certificate management.

## 🚀 Features

- **Automatic Project Detection**: Supports both single `Dockerfile` and `docker-compose.yml` projects
- **Smart Domain Mapping**: Automatically configures Nginx reverse proxy for your services
- **SSL Automation**: Integrated Let's Encrypt/Certbot for automatic HTTPS
- **Multi-Service Support**: Deploy complex applications with multiple interconnected services
- **Underscore Domain Rule**: Converts underscores to dots (e.g., `api_example_com` → `api.example.com`)
- **Isolated Networking**: All projects run on a shared Docker network for seamless communication
- **Easy Management**: Simple CLI for deploying, monitoring, and removing projects

## 📋 Prerequisites

- Docker and Docker Compose installed
- Python 3.8+ with venv support
- Root/sudo access for SSL certificate generation
- Domain names pointing to your server (for SSL)

## 🛠️ Installation

1. **Clone the repository**:
   ```bash
   git clone <your-daas-repo-url>
   cd daas
   ```

2. **Set up the infrastructure**:
   ```bash
   cd infra
   docker-compose up -d
   cd ..
   ```

3. **Install Python dependencies**:
   ```bash
   cd engine
   python3 -m venv venv
   ./venv/bin/pip install -r requirements.txt
   cd ..
   ```

4. **Make the CLI executable**:
   ```bash
   chmod +x daas
   ```

5. **Optional: Add to PATH**:
   ```bash
   # Add this line to your ~/.bashrc or ~/.zshrc
   export PATH="$PATH:/home/acer/daas"
   ```

## 📖 Usage

### Deploy a Project

Deploy any GitHub repository containing a `Dockerfile` or `docker-compose.yml`:

```bash
./daas deploy <GITHUB_URL>
```

**Important**: The port you specify is the **INTERNAL container port**, NOT a host port. Only the DaaS Nginx proxy uses host ports 80/443.

**Example - Single Dockerfile Project**:
```bash
./daas deploy https://github.com/yourusername/simple-web.git
# You'll be prompted for:
# - Domain name (e.g., myapp.example.com or myapp_example_com)
# - Internal port: 8080 (the port your app listens on INSIDE the container)
```

**Example - Docker Compose Project**:
```bash
./daas deploy https://github.com/yourusername/multi-service.git
# You'll be prompted for each service:
# - frontend: domain and internal port 8080
# - api: domain and internal port 5000
# - redis: skip (no domain needed for internal services)
```

**Port Architecture**:
```
Internet → Port 80/443 (DaaS Nginx Proxy) 
  → daas-network 
    → your-container:8080 (internal, not exposed to host)
```

- ✅ **Host Ports 80/443**: Only used by DaaS Nginx proxy
- ✅ **Container Ports**: Your services run on ANY port internally (8080, 3000, 5000, etc.)
- ✅ **No Port Conflicts**: Services are isolated in the Docker network
- ❌ **Don't use port 80**: Reserved for the main proxy

### Check Deployment Status

View all deployed projects and their configurations:

```bash
./daas status
```

Output:
```
Project              Service         Domain
-----------------------------------------------------------------
simple-web           app             myapp.example.com
multi-service        frontend        app.example.com
multi-service        api             api.example.com
```

### Remove a Project

Stop and remove a deployed project:

```bash
./daas remove <PROJECT_NAME>
```

Example:
```bash
./daas remove simple-web
```

## 🧪 Testing with Demo Projects

Two demo projects are included in `demo-projects/` for testing:

### 1. Simple Web (Single Dockerfile)

Deploy the simple-web demo:

```bash
./daas deploy demo-projects/simple-web
# Enter domain: test.local (or any domain)
# Enter port: 8080
```

### 2. Multi-Service (Docker Compose)

Deploy the multi-service demo:

```bash
./daas deploy demo-projects/multi-service
# For frontend: Enter domain (e.g., app.local) and port 8080
# For api: Enter domain (e.g., api.local) and port 5000
# For redis: Leave blank (internal service)
```

**Note**: The demo projects are regular directories in the main repo. For local testing without real domains, add entries to `/etc/hosts`:

```bash
sudo nano /etc/hosts
# Add:
127.0.0.1  test.local
127.0.0.1  app.local
127.0.0.1  api.local
```

## 🏗️ Architecture

```
daas/
├── daas                    # Main CLI entrypoint
├── engine/
│   ├── config.py          # Dynamic configuration
│   ├── manager.py         # Core deployment logic
│   ├── cli.py             # Command-line interface
│   ├── requirements.txt   # Python dependencies
│   └── templates/
│       └── nginx.conf.j2  # Nginx configuration template
├── infra/
│   ├── docker-compose.yml # Nginx proxy + Certbot
│   ├── nginx/
│   │   └── conf.d/        # Generated Nginx configs
│   └── certbot/           # SSL certificates
├── projects/              # Deployed projects (auto-created)
└── demo-projects/         # Example projects
    ├── simple-web/        # Single Dockerfile example
    └── multi-service/     # Docker Compose example
```

## 🔧 Configuration

### Environment Variables

- `DAAS_NETWORK`: Custom Docker network name (default: `daas-network`)

### Nginx Template

Customize the Nginx reverse proxy configuration by editing:
```
engine/templates/nginx.conf.j2
```

## 🔐 SSL/HTTPS

DaaS automatically requests SSL certificates from Let's Encrypt for all configured domains. 

**Requirements**:
- Domain must point to your server's IP
- Port 80 must be accessible for HTTP-01 challenge

**Note**: If SSL generation fails (e.g., domain not pointing to server), DaaS will continue with HTTP-only configuration and display a warning.

## 🌐 Domain Naming Convention

DaaS supports the underscore-to-dot conversion rule:
- Input: `api_myapp_com`
- Output: `api.myapp.com`

This is useful when you can't use dots in certain contexts.

## 📝 How It Works

1. **Clone**: DaaS clones your GitHub repository
2. **Analyze**: Detects `Dockerfile` or `docker-compose.yml`
3. **Configure**: Generates deployment-specific `docker-compose.daas.yml`
4. **Network**: Connects all services to the shared `daas-network`
5. **Nginx**: Creates reverse proxy configuration for each domain
6. **SSL**: Requests Let's Encrypt certificates via Certbot
7. **Deploy**: Builds and starts containers
8. **Reload**: Updates Nginx to route traffic

## 🐛 Troubleshooting

### Containers not accessible
- Check if containers are running: `docker ps`
- Verify network: `docker network inspect daas-network`
- Check Nginx logs: `docker logs daas-proxy`

### SSL certificate generation failed
- Ensure domain points to your server
- Check Certbot logs: `docker logs daas-certbot`
- Verify port 80 is accessible

### Port conflicts
- Check if ports are already in use: `netstat -tulpn | grep <PORT>`
- Modify the internal port when deploying

## 🤝 Contributing

Contributions are welcome! Please feel free to submit issues or pull requests.

## 📄 License

MIT License - feel free to use this project for any purpose.

## 🎯 Roadmap

- [ ] Support for custom Nginx configurations per project
- [ ] Automatic SSL renewal monitoring
- [ ] Web-based dashboard for deployment management
- [ ] Support for private GitHub repositories
- [ ] Database service templates (PostgreSQL, MySQL, MongoDB)
- [ ] Automatic backups and rollback functionality
- [ ] Multi-server deployment support

---

**Made with ❤️ for simplified Docker deployments**
