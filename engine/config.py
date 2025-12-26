import os

# Base directory is the root of the 'daas' folder
BASE_DIR = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))

# Project paths
PROJECTS_DIR = os.path.join(BASE_DIR, "projects")
INFRA_DIR = os.path.join(BASE_DIR, "infra")

# Nginx paths
NGINX_DIR = os.path.join(INFRA_DIR, "nginx")
NGINX_CONF_DIR = os.path.join(NGINX_DIR, "conf.d")

# Certbot paths
CERTBOT_DIR = os.path.join(INFRA_DIR, "certbot")

# Networking
NETWORK_NAME = os.getenv("DAAS_NETWORK", "daas-network")

# Templates
TEMPLATES_DIR = os.path.join(os.path.dirname(__file__), "templates")
NGINX_TEMPLATE_PATH = os.path.join(TEMPLATES_DIR, "nginx.conf.j2")

# Ensure directories exist
for d in [PROJECTS_DIR, NGINX_CONF_DIR, os.path.join(CERTBOT_DIR, "conf"), os.path.join(CERTBOT_DIR, "www")]:
    os.makedirs(d, exist_ok=True)
