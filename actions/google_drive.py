"""
actions/google_drive.py — Integracion segura de Google Drive con control de accesos locales.
"""
from __future__ import annotations
import os
import json
import mimetypes
from pathlib import Path
from typing import Any

try:
    from googleapiclient.discovery import build
    from googleapiclient.http import MediaFileUpload, MediaIoBaseDownload
    from google_auth_oauthlib.flow import InstalledAppFlow
    from google.auth.transport.requests import Request
    from google.oauth2.credentials import Credentials
except ImportError:
    build = None
    MediaFileUpload = None
    MediaIoBaseDownload = None
    InstalledAppFlow = None
    Request = None
    Credentials = None

def log(msg: str, player=None):
    if player:
        try:
            player.write_log(msg)
        except Exception:
            pass
    try:
        print(f"[google_drive] {msg}")
    except Exception:
        pass

SCOPES = ["https://www.googleapis.com/auth/drive"]

def is_safe_path(path: Path) -> bool:
    try:
        resolved = path.resolve()
        system_roots = [
            Path("C:/Windows").resolve(),
            Path("C:/Program Files").resolve(),
            Path("C:/Program Files (x86)").resolve(),
            Path("C:/ProgramData").resolve(),
        ]
        for root in system_roots:
            if resolved == root or root in resolved.parents:
                return False
        return True
    except Exception:
        return False

def get_drive_service() -> Any | None:
    if not build or not Credentials:
        return None
        
    creds = None
    token_path = Path("config/token_drive.json")
    client_secrets_path = Path("config/client_secret.json")

    if token_path.exists():
        try:
            creds = Credentials.from_authorized_user_file(str(token_path), SCOPES)
        except Exception:
            pass

    if not creds or not creds.valid:
        if creds and creds.expired and creds.refresh_token:
            try:
                creds.refresh(Request())
            except Exception:
                creds = None
        else:
            if not client_secrets_path.exists():
                log("client_secret.json no encontrado en config/")
                return None
            try:
                flow = InstalledAppFlow.from_client_secrets_file(str(client_secrets_path), SCOPES)
                creds = flow.run_local_server(port=0)
            except Exception as e:
                log(f"Error en flujo OAuth Drive: {e}")
                return None

        if creds:
            try:
                token_path.parent.mkdir(parents=True, exist_ok=True)
                with open(token_path, "w", encoding="utf-8") as token_file:
                    token_file.write(creds.to_json())
            except Exception:
                pass

    if creds:
        try:
            return build("drive", "v3", credentials=creds)
        except Exception as e:
            log(f"Error al construir servicio Drive: {e}")
            return None
    return None

def google_drive(parameters: dict, player=None, speak=None) -> str:
    """
    Gestiona Google Drive: listar archivos, buscar, subir, descargar, crear carpetas, eliminar, compartir.
    """
    action = parameters.get("action", "").lower().strip()
    folder_id = parameters.get("folder_id", "root").strip()
    file_id = parameters.get("file_id", "").strip()
    path_str = parameters.get("path", "").strip()
    name = parameters.get("name", "").strip()
    query = parameters.get("query", "").strip()
    destination_str = parameters.get("destination", "").strip()
    email = parameters.get("email", "").strip()
    role = parameters.get("role", "reader").lower().strip()
    confirm = parameters.get("confirm", False)

    if not action:
        return "Error: Falta el parametro obligatorio 'action'."

    # Validaciones previas de seguridad de rutas locales para evitar autenticar en vano
    if action == "upload":
        if not path_str:
            return "Error: Se requiere el parametro 'path' con la ruta del archivo local a subir."
        local_path = Path(path_str).resolve()
        if not local_path.exists() or not local_path.is_file():
            return f"Error: El archivo local '{local_path}' no existe o no es valido."
        if not is_safe_path(local_path):
            return f"Error de seguridad: Acceso denegado a la ruta local '{local_path}'."
        if local_path.name.lower() in ["api_keys.json", "api_keys.example.json", "token.json", "token_drive.json", "client_secret.json"]:
            return "Error de seguridad: No se permite la subida de archivos de credenciales confidenciales."

    elif action == "download":
        if not file_id:
            return "Error: Se requiere 'file_id' para descargar."
        if not destination_str:
            return "Error: Se requiere la ruta de destino local 'destination'."
        dest_path = Path(destination_str).resolve()
        if not is_safe_path(dest_path):
            return f"Error de seguridad: Acceso denegado a la ruta local destino '{dest_path}'."

    service = get_drive_service()
    if not service:
        return (
            "Info: No se pudo conectar a Google Drive. Para configurar:\n"
            "  1. Activa Google Drive API en Google Cloud Console.\n"
            "  2. Descarga tus credenciales OAuth y guardalas como 'config/client_secret.json'.\n"
            "  3. Ejecuta de nuevo para completar la autorizacion en tu navegador."
        )

    try:
        if action == "list":
            q = f"'{folder_id}' in parents and trashed = false"
            results = service.files().list(
                q=q, pageSize=15, fields="files(id, name, mimeType)"
            ).execute()
            items = results.get("files", [])
            
            if not items:
                return f"No se encontraron archivos en la carpeta '{folder_id}'."
            
            res = f"Archivos en la carpeta '{folder_id}':\n"
            for item in items:
                is_dir = " (Carpeta)" if item["mimeType"] == "application/vnd.google-apps.folder" else ""
                res += f"  - [{item['id']}] {item['name']}{is_dir}\n"
            return res.strip()

        elif action == "search":
            if not query:
                return "Error: Se requiere un parametro 'query' para buscar."
            q = f"name contains '{query}' and trashed = false"
            results = service.files().list(
                q=q, pageSize=15, fields="files(id, name, mimeType)"
            ).execute()
            items = results.get("files", [])
            
            if not items:
                return f"No se encontraron coincidencias para '{query}'."
            
            res = f"Coincidencias encontradas en Google Drive:\n"
            for item in items:
                is_dir = " (Carpeta)" if item["mimeType"] == "application/vnd.google-apps.folder" else ""
                res += f"  - [{item['id']}] {item['name']}{is_dir}\n"
            return res.strip()

        elif action == "upload":
            local_path = Path(path_str).resolve()
            file_metadata = {"name": local_path.name}
            if folder_id != "root":
                file_metadata["parents"] = [folder_id]

            mime_type, _ = mimetypes.guess_type(local_path)
            media = MediaFileUpload(str(local_path), mimetype=mime_type, resumable=True)
            
            file = service.files().create(body=file_metadata, media_body=media, fields="id").execute()
            return f"Archivo '{local_path.name}' subido con exito. (ID en Drive: {file.get('id')})."

        elif action == "download":
            dest_path = Path(destination_str).resolve()

            # Obtener metadata del archivo para saber el nombre original
            meta = service.files().get(fileId=file_id).execute()
            file_name = meta.get("name", "downloaded_file")
            
            # Si destination es una carpeta, agregar el nombre del archivo
            if dest_path.is_dir():
                dest_file_path = dest_path / file_name
            else:
                dest_file_path = dest_path

            import io
            request = service.files().get_media(fileId=file_id)
            fh = io.FileIO(str(dest_file_path), "wb")
            downloader = MediaIoBaseDownload(fh, request)
            
            done = False
            while not done:
                status, done = downloader.next_chunk()
            
            return f"Archivo '{file_name}' descargado con exito en '{dest_file_path}'."

        elif action == "create_folder":
            if not name:
                return "Error: Se requiere 'name' para la nueva carpeta."
            file_metadata = {
                "name": name,
                "mimeType": "application/vnd.google-apps.folder"
            }
            if folder_id != "root":
                file_metadata["parents"] = [folder_id]
                
            folder = service.files().create(body=file_metadata, fields="id").execute()
            return f"Carpeta '{name}' creada con exito (ID: {folder.get('id')})."

        elif action == "delete":
            if not file_id:
                return "Error: Se requiere 'file_id' para eliminar."
            if not confirm:
                return "Advertencia: ¿Esta seguro de eliminar este elemento? Confirme explicitamente pasando 'confirm': True."
            
            service.files().delete(fileId=file_id).execute()
            return f"Elemento con ID '{file_id}' eliminado permanentemente de Google Drive."

        elif action == "share":
            if not file_id or not email:
                return "Error: Compartir requiere 'file_id' y 'email' del destinatario."
            
            # Validar rol seguro
            if role not in ["reader", "commenter", "writer"]:
                role = "reader"

            user_permission = {
                "type": "user",
                "role": role,
                "emailAddress": email
            }
            service.permissions().create(
                fileId=file_id,
                body=user_permission,
                fields="id"
            ).execute()
            return f"Archivo con ID '{file_id}' compartido exitosamente con '{email}' como '{role}'."

        elif action == "info":
            if not file_id:
                return "Error: Se requiere 'file_id' para obtener informacion."
            meta = service.files().get(fileId=file_id, fields="id, name, mimeType, size, createdTime").execute()
            
            size = meta.get("size", "Desconocido")
            if size != "Desconocido":
                size = f"{int(size) / 1024:.2f} KB"
                
            info = (
                f"Informacion del archivo en Drive:\n"
                f"  Nombre: {meta.get('name')}\n"
                f"  ID: {meta.get('id')}\n"
                f"  MIME Type: {meta.get('mimeType')}\n"
                f"  Tamano: {size}\n"
                f"  Creado: {meta.get('createdTime')}\n"
            )
            return info

        else:
            return f"Error: Accion '{action}' no reconocida para google_drive."

    except Exception as e:
        return f"Error al interactuar con Google Drive API: {e}"
