import os
import shutil
import yaml
from git import Repo
import docker
from jinja2 import Template, Environment, FileSystemLoader
import subprocess
import click
from config import PROJECTS_DIR, NGINX_CONF_DIR, NETWORK_NAME, NGINX_TEMPLATE_PATH, TEMPLATES_DIR

class DaaSManager:
    def __init__(self):
        self.client = docker.from_env()
        self.jinja_env = Environment(loader=FileSystemLoader(TEMPLATES_DIR))

    def deploy_project(self, github_url, domains_mapping):
        """
        domains_mapping: dict of {service_name: {"domain": domain, "port": port}}
        """
        project_name = github_url.split("/")[-1].replace(".git", "")
        project_path = os.path.join(PROJECTS_DIR, project_name)

        # 1. Clone Repo
        if os.path.exists(project_path):
            shutil.rmtree(project_path)
        Repo.clone_from(github_url, project_path)

        # 2. Analyze
        is_compose = os.path.exists(os.path.join(project_path, "docker-compose.yml"))
        has_dockerfile = os.path.exists(os.path.join(project_path, "Dockerfile"))

        if not is_compose and not has_dockerfile:
            raise Exception("No Dockerfile or docker-compose.yml found")

        # 3. Prepare deployment compose file
        deploy_compose = {}
        if is_compose:
            with open(os.path.join(project_path, "docker-compose.yml"), "r") as f:
                deploy_compose = yaml.safe_load(f)
        else:
            deploy_compose = {
                "version": "3.8",
                "services": {
                    "app": {
                        "build": ".",
                        "restart": "always"
                    }
                }
            }

        # Add network and container names
        for service_name, config in deploy_compose.get("services", {}).items():
            if "networks" not in config:
                config["networks"] = []
            if NETWORK_NAME not in config["networks"]:
                config["networks"].append(NETWORK_NAME)
            
            # Ensure container name is unique and predictable
            config["container_name"] = f"{project_name}-{service_name}"

        deploy_compose["networks"] = {
            NETWORK_NAME: {
                "external": True
            }
        }

        deploy_compose_path = os.path.join(project_path, "docker-compose.daas.yml")
        with open(deploy_compose_path, "w") as f:
            yaml.dump(deploy_compose, f)

        # 4. Generate SSL and Nginx Config
        for service_name, config in domains_mapping.items():
            domain = config["domain"]
            port = config["port"]
            self._setup_ssl_and_nginx(service_name, domain, port, project_name)

        # 5. Build and Up
        subprocess.run(["docker-compose", "-f", "docker-compose.daas.yml", "up", "-d", "--build"], cwd=project_path)
        
        # 6. Reload Nginx
        self._reload_nginx()

    def _setup_ssl_and_nginx(self, service_name, domain, port, project_name):
        # Rule: underscores act as dots
        domain = domain.replace("_", ".")
        
        # Initial Nginx config for Certbot validation (HTTP only)
        temp_template = Template("""
server {
    listen 80;
    server_name {{ domain }};
    location /.well-known/acme-challenge/ {
        root /var/www/certbot;
    }
}
""")
        conf_path = os.path.join(NGINX_CONF_DIR, f"{project_name}-{service_name}.conf")
        with open(conf_path, "w") as f:
            f.write(temp_template.render(domain=domain))
        
        self._reload_nginx()

        # Run Certbot
        click.echo(f"Requesting SSL for {domain}...")
        try:
            certbot_cmd = [
                "docker", "exec", "daas-certbot",
                "certbot", "certonly", "--webroot", "-w", "/var/www/certbot",
                "-d", domain, "--email", f"admin@{domain}", "--agree-tos", "--no-eff-email", "--non-interactive"
            ]
            subprocess.run(certbot_cmd, check=True)
        except subprocess.CalledProcessError as e:
            click.echo(f"Warning: SSL certificate generation failed for {domain}. This is expected if the domain is not pointing to this server.")

        # Final Nginx config (HTTPS)
        container_name = f"{project_name}-{service_name}"
        
        with open(conf_path, "w") as f:
            template = self.jinja_env.get_template("nginx.conf.j2")
            f.write(template.render(domain=domain, service_name=container_name, port=port))

    def _reload_nginx(self):
        subprocess.run(["docker", "exec", "daas-proxy", "nginx", "-s", "reload"])

manager = DaaSManager()
