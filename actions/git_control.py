"""
actions/git_control.py — Control seguro de repositorios Git en JARVIS.
"""
from __future__ import annotations
import subprocess
import urllib.parse
from pathlib import Path
from typing import Any

def log(msg: str, player=None):
    if player:
        try:
            player.write_log(msg)
        except Exception:
            pass
    try:
        print(f"[git_control] {msg}")
    except Exception:
        pass

def git_control(parameters: dict, player=None, speak=None) -> str:
    """
    Git operations: commit, add, status, push, pull, log, clone, checkout, branch.
    """
    action = parameters.get("action", "").lower().strip()
    message = parameters.get("message", "").strip()
    files = parameters.get("files") # Puede ser string o array
    repo_url = parameters.get("repo_url", "").strip()
    branch_name = parameters.get("branch_name", "").strip()

    if not action:
        return "Error: Falta el parametro obligatorio 'action'."

    # Comprobar presencia de git en el sistema
    CREATE_NO_WINDOW = 0x08000000
    try:
        subprocess.run(["git", "--version"], capture_output=True, creationflags=CREATE_NO_WINDOW)
    except FileNotFoundError:
        return "Error: Git no esta instalado o no se encuentra en el PATH de este sistema."

    log(f"Ejecutando accion Git '{action}'")

    if action == "clone":
        if not repo_url:
            return "Error: Se requiere el parametro 'repo_url' para clonar."
        
        # Validar dominio seguro de repositorios Git
        parsed = urllib.parse.urlparse(repo_url)
        allowed_domains = ["github.com", "gitlab.com", "bitbucket.org"]
        domain = parsed.netloc.lower()
        
        # Remover puerto si esta presente
        if ":" in domain:
            domain = domain.split(":")[0]
            
        if not any(domain == d or domain.endswith("." + d) for d in allowed_domains):
            return f"Error de seguridad: El dominio '{domain}' no esta permitido para clonar repositorios."

        # Comando estructurado sin inyeccion shell
        cmd = ["git", "clone", repo_url]
        try:
            res = subprocess.run(cmd, capture_output=True, text=True, creationflags=CREATE_NO_WINDOW, timeout=90)
            if res.returncode == 0:
                return f"Repositorio clonado con exito desde '{repo_url}'."
            else:
                return f"Error al clonar repositorio (Git exit {res.returncode}): {res.stderr.strip()}"
        except Exception as e:
            return f"Excepcion al clonar: {e}"

    # Para otras operaciones, validar que el directorio actual o destino sea repositorio
    try:
        git_check = subprocess.run(
            ["git", "rev-parse", "--is-inside-work-tree"], 
            capture_output=True, text=True, creationflags=CREATE_NO_WINDOW
        )
        if git_check.returncode != 0:
            return "Error: El directorio de trabajo actual no es un repositorio Git valido."
    except Exception as e:
        return f"Error al validar estado del repositorio: {e}"

    if action == "status":
        cmd = ["git", "status", "-s"]
        res = subprocess.run(cmd, capture_output=True, text=True, creationflags=CREATE_NO_WINDOW)
        out = res.stdout.strip()
        return out if out else "El repositorio esta limpio (sin cambios pendientes)."

    elif action == "add":
        # files puede ser un string de archivo o lista de archivos
        cmd = ["git", "add"]
        if isinstance(files, list):
            cmd.extend(files)
        elif isinstance(files, str) and files:
            cmd.append(files)
        else:
            cmd.append(".") # Default add all
            
        res = subprocess.run(cmd, capture_output=True, text=True, creationflags=CREATE_NO_WINDOW)
        if res.returncode == 0:
            return "Archivos agregados al index de Git exitosamente."
        else:
            return f"Error al agregar archivos: {res.stderr.strip()}"

    elif action == "commit":
        if not message:
            return "Error: Se requiere un mensaje de confirmacion ('message') para el commit."
        
        # Sanitizar mensaje para evitar modificadores no deseados, forzar lista de argumentos estructurada
        cmd = ["git", "commit", "-m", message]
        res = subprocess.run(cmd, capture_output=True, text=True, creationflags=CREATE_NO_WINDOW)
        if res.returncode == 0:
            return f"Commit realizado con exito:\n{res.stdout.strip()}"
        else:
            return f"Error al realizar commit: {res.stderr.strip()}"

    elif action == "push":
        # Evitar comandos interactivos, forzar push directo
        cmd = ["git", "push"]
        if branch_name:
            cmd.extend(["origin", branch_name])
        res = subprocess.run(cmd, capture_output=True, text=True, creationflags=CREATE_NO_WINDOW, timeout=45)
        if res.returncode == 0:
            return "Push completado exitosamente en el repositorio remoto."
        else:
            return f"Error al hacer push: {res.stderr.strip()}"

    elif action == "pull":
        cmd = ["git", "pull"]
        res = subprocess.run(cmd, capture_output=True, text=True, creationflags=CREATE_NO_WINDOW, timeout=45)
        if res.returncode == 0:
            return f"Pull completado exitosamente:\n{res.stdout.strip()}"
        else:
            return f"Error al hacer pull: {res.stderr.strip()}"

    elif action == "log":
        # Limitar numero de commits a mostrar para no saturar memoria o contexto
        cmd = ["git", "log", "-n", "5", "--oneline"]
        res = subprocess.run(cmd, capture_output=True, text=True, creationflags=CREATE_NO_WINDOW)
        return res.stdout.strip()

    elif action == "checkout":
        if not branch_name:
            return "Error: Se requiere 'branch_name' para cambiar de rama."
        cmd = ["git", "checkout", branch_name]
        res = subprocess.run(cmd, capture_output=True, text=True, creationflags=CREATE_NO_WINDOW)
        if res.returncode == 0:
            return f"Cambiado a la rama '{branch_name}'."
        else:
            return f"Error al cambiar rama: {res.stderr.strip()}"

    elif action == "branch":
        cmd = ["git", "branch"]
        if branch_name:
            cmd.append(branch_name) # Crear rama
        res = subprocess.run(cmd, capture_output=True, text=True, creationflags=CREATE_NO_WINDOW)
        return res.stdout.strip()

    else:
        return f"Error: Accion Git '{action}' no soportada."
