import click
from manager import manager
import os
import yaml
import shutil
import subprocess
from config import PROJECTS_DIR, NGINX_CONF_DIR

@click.group()
def cli():
    pass

@cli.command()
@click.argument('github_url')
@click.option('--domain', help='Domain for single Dockerfile project')
def deploy(github_url, domain):
    """Deploy a project from GitHub or local path."""
    
    # Convert relative paths to absolute paths
    if not github_url.startswith(('http://', 'https://', 'git@')):
        github_url = os.path.abspath(github_url)
    
    project_name = github_url.split("/")[-1].replace(".git", "")
    project_path = os.path.join(PROJECTS_DIR, project_name)
    
    # 1. Clone to inspect
    if not os.path.exists(project_path):
        from git import Repo
        Repo.clone_from(github_url, project_path)
    
    is_compose = os.path.exists(os.path.join(project_path, "docker-compose.yml"))
    
    domain_mapping = {}
    if is_compose:
        with open(os.path.join(project_path, "docker-compose.yml"), "r") as f:
            compose_data = yaml.safe_load(f)
            services = list(compose_data.get("services", {}).keys())
        
        click.echo(f"Found services: {', '.join(services)}")
        for service in services:
            d = click.prompt(f"Enter domain for service '{service}' (blank to skip)", default="", show_default=False)
            d = d.strip()  # Remove whitespace
            if d:
                port = click.prompt(f"Enter internal port for '{service}'", default=8080)
                domain_mapping[service] = {"domain": d, "port": port}
    else:
        if not domain:
            domain = click.prompt("Enter domain for this project (blank to skip)", default="", show_default=False)
        domain = domain.strip() if domain else ""  # Remove whitespace
        if domain:
            port = click.prompt(f"Enter internal port for this project", default=8080)
            domain_mapping["app"] = {"domain": domain, "port": port}

    if not domain_mapping:
        click.echo("No domains configured. Skipping deployment.")
        return

    click.echo(f"Deploying {project_name} with mappings: {domain_mapping}")
    try:
        manager.deploy_project(github_url, domain_mapping)
        click.echo("Deployment successful!")
    except Exception as e:
        click.echo(f"Deployment failed: {e}")

@cli.command()
def status():
    """List deployed projects and their configurations."""
    if not os.path.exists(PROJECTS_DIR):
        click.echo("No projects deployed.")
        return
    
    projects = os.listdir(PROJECTS_DIR)
    # Remove hidden files/folders and .gitkeep
    projects = [p for p in projects if not p.startswith('.') and p != '.gitkeep']
    
    if not projects:
        click.echo("No projects deployed.")
        return

    click.echo(f"{'Project':<20} {'Service':<15} {'Domain':<30}")
    click.echo("-" * 65)
    
    for project in projects:
        if not os.path.isdir(os.path.join(PROJECTS_DIR, project)):
            continue
        conf_files = [f for f in os.listdir(NGINX_CONF_DIR) if f.startswith(project)]
        for conf in conf_files:
            service_name = conf.replace(project + "-", "").replace(".conf", "")
            with open(os.path.join(NGINX_CONF_DIR, conf), "r") as f:
                content = f.read()
                import re
                match = re.search(r"server_name (.*?);", content)
                domain = match.group(1) if match else "N/A"
                click.echo(f"{project:<20} {service_name:<15} {domain:<30}")

@cli.command()
@click.argument('project_name')
def remove(project_name):
    """Remove a deployed project."""
    project_path = os.path.join(PROJECTS_DIR, project_name)
    if not os.path.exists(project_path):
        click.echo(f"Project '{project_name}' not found.")
        return

    click.echo(f"Removing project '{project_name}'...")
    
    # Stop containers
    subprocess.run(["docker-compose", "-f", "docker-compose.daas.yml", "down"], cwd=project_path)
    
    # Remove nginx configs
    conf_files = [f for f in os.listdir(NGINX_CONF_DIR) if f.startswith(project_name)]
    for conf in conf_files:
        os.remove(os.path.join(NGINX_CONF_DIR, conf))
    
    # Remove project directory
    shutil.rmtree(project_path)
    
    # Reload nginx
    manager._reload_nginx()
    
    click.echo("Project removed successfully.")

if __name__ == '__main__':
    cli()
