"""
actions/google_calendar.py — Integracion de Google Calendar con control seguro de flujos OAuth.
"""
from __future__ import annotations
import json
import datetime
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
        print(f"[google_calendar] {msg}")
    except Exception:
        pass

# Scopes requeridos para Calendar
SCOPES = ["https://www.googleapis.com/auth/calendar"]

def get_calendar_service() -> Any | None:
    """Realiza la autenticacion local con Google Calendar y retorna el servicio."""
    if not build or not Credentials:
        return None

    creds = None
    token_path = Path("config/token.json")
    client_secrets_path = Path("config/client_secret.json")

    # Intentar cargar token guardado
    if token_path.exists():
        try:
            creds = Credentials.from_authorized_user_file(str(token_path), SCOPES)
        except Exception:
            pass

    # Si no hay credenciales validas, hacer login
    if not creds or not creds.valid:
        if creds and creds.expired and creds.refresh_token:
            try:
                creds.refresh(Request())
            except Exception:
                creds = None
        else:
            if not client_secrets_path.exists():
                log("client_secret.json de Google API no encontrado en config/")
                return None
            try:
                flow = InstalledAppFlow.from_client_secrets_file(str(client_secrets_path), SCOPES)
                creds = flow.run_local_server(port=0)
            except Exception as e:
                log(f"Error en flujo OAuth: {e}")
                return None

        # Guardar credenciales para la proxima sesion
        if creds:
            try:
                token_path.parent.mkdir(parents=True, exist_ok=True)
                with open(token_path, "w", encoding="utf-8") as token_file:
                    token_file.write(creds.to_json())
            except Exception:
                pass

    if creds:
        try:
            return build("calendar", "v3", credentials=creds)
        except Exception as e:
            log(f"Error al construir servicio Calendar: {e}")
            return None
    return None

def parse_iso_datetime(dt_str: str) -> str:
    """Parsea una cadena de fecha/hora a formato ISO 8601."""
    # Soporta YYYY-MM-DD HH:MM
    dt_str = dt_str.strip()
    try:
        # Intentar parsear YYYY-MM-DD HH:MM
        dt = datetime.datetime.strptime(dt_str, "%Y-%m-%d %H:%M")
        return dt.isoformat() + "Z"
    except ValueError:
        pass
    
    try:
        # Intentar parsear YYYY-MM-DD
        dt = datetime.datetime.strptime(dt_str, "%Y-%m-%d")
        return dt.isoformat() + "T00:00:00Z"
    except ValueError:
        pass
        
    return dt_str # Retornar crudo si ya esta en formato ISO o es invalido

def google_calendar(parameters: dict, player=None, speak=None) -> str:
    """
    Manages the user's Google Calendar: create, list, edit, or delete events.
    """
    action = parameters.get("action", "list").lower().strip()
    summary = parameters.get("summary", "").strip()
    start_str = parameters.get("start", "").strip()
    end_str = parameters.get("end", "").strip()
    description = parameters.get("description", "").strip()
    location = parameters.get("location", "").strip()
    event_id = parameters.get("event_id", "").strip()
    days_ahead = parameters.get("days_ahead", 7)

    log(f"Ejecutando accion '{action}'")

    service = get_calendar_service()
    if not service:
        # Fallback guiado: Si no esta configurado, informamos al usuario de forma clara
        return (
            "Info: No se pudo conectar a Google Calendar. Para usar esta funcion:\n"
            "  1. Activa Google Calendar API en Google Cloud Console.\n"
            "  2. Descarga tus credenciales OAuth y guardalas como 'config/client_secret.json'.\n"
            "  3. Ejecuta de nuevo para completar la autorizacion en tu navegador."
        )

    try:
        if action == "list":
            now = datetime.datetime.utcnow().isoformat() + "Z"
            events_result = service.events().list(
                calendarId="primary", 
                timeMin=now,
                maxResults=10, 
                singleEvents=True,
                orderBy="startTime"
            ).execute()
            events = events_result.get("items", [])
            
            if not events:
                return "No se encontraron eventos proximos en tu calendario."
            
            res = "Proximos eventos en tu calendario:\n"
            for event in events:
                start = event["start"].get("dateTime", event["start"].get("date"))
                res += f"  - [{event['id'][:8]}] {event.get('summary')}: {start}\n"
            return res.strip()

        elif action == "create":
            if not summary or not start_str:
                return "Error: Para crear un evento se requiere 'summary' y fecha de inicio 'start'."
            
            iso_start = parse_iso_datetime(start_str)
            if not end_str:
                # Duracion por defecto de 1 hora
                try:
                    start_dt = datetime.datetime.fromisoformat(iso_start.replace("Z", ""))
                    iso_end = (start_dt + datetime.timedelta(hours=1)).isoformat() + "Z"
                except Exception:
                    iso_end = iso_start
            else:
                iso_end = parse_iso_datetime(end_str)

            event_body = {
                "summary": summary,
                "location": location,
                "description": description,
                "start": {"dateTime": iso_start, "timeZone": "UTC"},
                "end": {"dateTime": iso_end, "timeZone": "UTC"},
            }

            event = service.events().insert(calendarId="primary", body=event_body).execute()
            return f"Evento creado exitosamente: '{event.get('summary')}' (ID: {event.get('id')[:8]})."

        elif action == "delete":
            if not event_id:
                return "Error: Se requiere 'event_id' para eliminar el evento."
            
            # Buscar ID completo a partir de coincidencia de prefijo
            full_id = event_id
            if len(event_id) == 8:
                # Buscar en la lista para resolver prefijo
                events_result = service.events().list(calendarId="primary", maxResults=50).execute()
                for item in events_result.get("items", []):
                    if item["id"].startswith(event_id):
                        full_id = item["id"]
                        break
            
            service.events().delete(calendarId="primary", eventId=full_id).execute()
            return f"Evento con ID '{event_id}' eliminado correctamente."

        elif action == "edit":
            if not event_id:
                return "Error: Se requiere 'event_id' para editar."
            
            # Resolver prefijo
            full_id = event_id
            if len(event_id) == 8:
                events_result = service.events().list(calendarId="primary", maxResults=50).execute()
                for item in events_result.get("items", []):
                    if item["id"].startswith(event_id):
                        full_id = item["id"]
                        break

            # Obtener evento existente
            event = service.events().get(calendarId="primary", eventId=full_id).execute()
            
            if summary:
                event["summary"] = summary
            if description:
                event["description"] = description
            if location:
                event["location"] = location
            if start_str:
                event["start"]["dateTime"] = parse_iso_datetime(start_str)
            if end_str:
                event["end"]["dateTime"] = parse_iso_datetime(end_str)

            updated_event = service.events().update(calendarId="primary", eventId=full_id, body=event).execute()
            return f"Evento '{updated_event.get('summary')}' editado exitosamente."

        else:
            return f"Error: Accion '{action}' no soportada en google_calendar."

    except Exception as e:
        return f"Error al interactuar con Google Calendar API: {e}"
