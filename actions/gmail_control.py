"""
actions/gmail_control.py — Integracion segura de Gmail: lectura, busqueda y envio de correos.
"""
from __future__ import annotations
import json
import base64
import html
from email.mime.text import MIMEText
from pathlib import Path
from typing import Any

try:
    from googleapiclient.discovery import build
    from google_auth_oauthlib.flow import InstalledAppFlow
    from google.auth.transport.requests import Request
    from google.oauth2.credentials import Credentials
except ImportError:
    build = None
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
        print(f"[gmail_control] {msg}")
    except Exception:
        pass

SCOPES = [
    "https://www.googleapis.com/auth/gmail.readonly",
    "https://www.googleapis.com/auth/gmail.send",
    "https://www.googleapis.com/auth/gmail.modify"
]

def get_gmail_service() -> Any | None:
    if not build or not Credentials:
        return None
        
    creds = None
    token_path = Path("config/token_gmail.json")
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
                log(f"Error en flujo OAuth Gmail: {e}")
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
            return build("gmail", "v1", credentials=creds)
        except Exception as e:
            log(f"Error al construir servicio Gmail: {e}")
            return None
    return None

def build_message(to: str, subject: str, body_text: str) -> dict[str, str]:
    """Crea un correo MIME en base64 de forma segura."""
    # Sanitizacion basica contra inyeccion HTML en clientes de correo
    safe_body = html.escape(body_text).replace("\n", "<br>")
    
    message = MIMEText(safe_body, "html", "utf-8")
    message["to"] = to
    message["subject"] = subject
    
    raw = base64.urlsafe_b64encode(message.as_bytes()).decode("utf-8")
    return {"raw": raw}

def gmail_control(parameters: dict, player=None, speak=None) -> str:
    """
    Gestiona Gmail: leer bandeja, buscar correos, leer correo, enviar, responder, archivar, eliminar.
    """
    action = parameters.get("action", "").lower().strip()
    count = parameters.get("count", 5)
    message_id = parameters.get("message_id", "").strip()
    to = parameters.get("to", "").strip()
    subject = parameters.get("subject", "").strip()
    body = parameters.get("body", "").strip()
    query = parameters.get("query", "").strip()
    confirm = parameters.get("confirm", False)

    if not action:
        return "Error: Falta el parametro obligatorio 'action'."

    service = get_gmail_service()
    if not service:
        return (
            "Info: No se pudo conectar a Gmail. Para configurar:\n"
            "  1. Activa Gmail API en Google Cloud Console.\n"
            "  2. Descarga tus credenciales OAuth y guardalas como 'config/client_secret.json'.\n"
            "  3. Ejecuta de nuevo para completar la autorizacion en tu navegador."
        )

    try:
        if action in ["inbox", "search"]:
            q = query if action == "search" else "label:INBOX"
            results = service.users().messages().list(userId="me", q=q, maxResults=count).execute()
            messages = results.get("messages", [])
            
            if not messages:
                return "No se encontraron correos."
            
            res = f"Bandeja de Gmail ({len(messages)} correos):\n"
            for msg in messages:
                # Obtener detalles del header (Subject, From)
                detail = service.users().messages().get(userId="me", id=msg["id"], format="metadata", metadataHeaders=["Subject", "From"]).execute()
                headers = detail.get("payload", {}).get("headers", [])
                
                subj = "Sin Asunto"
                sender = "Desconocido"
                for h in headers:
                    if h["name"] == "Subject":
                        subj = h["value"]
                    elif h["name"] == "From":
                        sender = h["value"]
                res += f"  - [{msg['id'][:8]}] De: {sender} | Asunto: {subj}\n"
            return res.strip()

        elif action == "read":
            if not message_id:
                return "Error: Se requiere 'message_id' para leer el correo."
            
            # Resolver prefijo corto si aplica
            full_id = message_id
            if len(message_id) == 8:
                results = service.users().messages().list(userId="me", maxResults=50).execute()
                for msg in results.get("messages", []):
                    if msg["id"].startswith(message_id):
                        full_id = msg["id"]
                        break

            detail = service.users().messages().get(userId="me", id=full_id, format="full").execute()
            payload = detail.get("payload", {})
            headers = payload.get("headers", [])
            
            subj = "Sin Asunto"
            sender = "Desconocido"
            date = "Desconocida"
            for h in headers:
                if h["name"] == "Subject":
                    subj = h["value"]
                elif h["name"] == "From":
                    sender = h["value"]
                elif h["name"] == "Date":
                    date = h["value"]

            # Intentar extraer cuerpo de texto
            body_text = ""
            parts = payload.get("parts", [])
            if not parts:
                body_text = payload.get("body", {}).get("data", "")
            else:
                for part in parts:
                    if part.get("mimeType") == "text/plain":
                        body_text = part.get("body", {}).get("data", "")
                        break
                if not body_text and parts:
                    # Fallback a la primera parte si no hay texto plano directo
                    body_text = parts[0].get("body", {}).get("data", "")

            if body_text:
                body_decoded = base64.urlsafe_b64decode(body_text.encode("utf-8")).decode("utf-8", errors="ignore")
            else:
                body_decoded = "(Cuerpo vacio o formato no soportado)"

            info = (
                f"Correo [{full_id[:8]}]:\n"
                f"  De: {sender}\n"
                f"  Fecha: {date}\n"
                f"  Asunto: {subj}\n"
                f"  Mensaje:\n{body_decoded[:1500]}\n"
            )
            if len(body_decoded) > 1500:
                info += "  ...(mensaje truncado a 1500 caracteres)..."
            return info

        elif action == "send":
            if not to or not subject or not body:
                return "Error: Enviar requiere 'to' (destinatario), 'subject' y 'body'."
            
            raw_msg = build_message(to, subject, body)
            service.users().messages().send(userId="me", body=raw_msg).execute()
            return f"Correo enviado exitosamente a '{to}'."

        elif action == "reply":
            if not message_id or not body:
                return "Error: Responder requiere 'message_id' y 'body'."
            
            # Obtener datos del mensaje original para asunto e ID de referencia
            orig = service.users().messages().get(userId="me", id=message_id, format="metadata", metadataHeaders=["Subject", "From", "Message-ID"]).execute()
            headers = orig.get("payload", {}).get("headers", [])
            
            to_addr = ""
            subj = ""
            msg_id = ""
            for h in headers:
                if h["name"] == "From":
                    to_addr = h["value"]
                elif h["name"] == "Subject":
                    subj = h["value"]
                    if not subj.lower().startswith("re:"):
                        subj = "Re: " + subj
                elif h["name"] == "Message-ID":
                    msg_id = h["value"]

            if not to_addr:
                return "Error: No se pudo determinar el destinatario del mensaje original."

            safe_body = html.escape(body).replace("\n", "<br>")
            message = MIMEText(safe_body, "html", "utf-8")
            message["to"] = to_addr
            message["subject"] = subj
            if msg_id:
                message["In-Reply-To"] = msg_id
                message["References"] = msg_id

            raw = base64.urlsafe_b64encode(message.as_bytes()).decode("utf-8")
            service.users().messages().send(userId="me", body={"raw": raw, "threadId": orig.get("threadId")}).execute()
            return f"Respuesta enviada exitosamente a '{to_addr}'."

        elif action == "delete":
            if not message_id:
                return "Error: Se requiere 'message_id' para eliminar."
            if not confirm:
                return "Advertencia: ¿Esta seguro de enviar este correo a la papelera? Confirme pasando 'confirm': True."
            
            service.users().messages().trash(userId="me", id=message_id).execute()
            return f"Correo con ID '{message_id}' movido a la papelera de Gmail."

        elif action == "archive":
            if not message_id:
                return "Error: Se requiere 'message_id' para archivar."
            # Quitar la etiqueta INBOX equivale a archivar
            body_modify = {
                "removeLabelIds": ["INBOX"]
            }
            service.users().messages().modify(userId="me", id=message_id, body=body_modify).execute()
            return f"Correo '{message_id}' archivado correctamente."

        else:
            return f"Error: Accion '{action}' no reconocida para gmail_control."

    except Exception as e:
        return f"Error al interactuar con Gmail API: {e}"
