"""
actions/whatsapp.py — Integracion de WhatsApp Web y gestion de contactos de JARVIS.
"""
from __future__ import annotations
import os
import json
import urllib.parse
import webbrowser
from pathlib import Path
from typing import Any

def log(msg: str, player=None):
    if player:
        try:
            player.write_log(msg)
        except Exception:
            pass
    try:
        print(f"[whatsapp] {msg}")
    except Exception:
        pass

CONTACTS_FILE = Path("config/whatsapp_contacts.json")

def load_contacts() -> dict[str, str]:
    """Carga la libreta de contactos de WhatsApp."""
    if not CONTACTS_FILE.exists():
        CONTACTS_FILE.parent.mkdir(parents=True, exist_ok=True)
        with open(CONTACTS_FILE, "w", encoding="utf-8") as f:
            json.dump({}, f)
        return {}
    try:
        with open(CONTACTS_FILE, "r", encoding="utf-8") as f:
            return json.load(f)
    except Exception:
        return {}

def save_contacts(contacts: dict[str, str]):
    """Guarda la libreta de contactos de WhatsApp."""
    try:
        with open(CONTACTS_FILE, "w", encoding="utf-8") as f:
            json.dump(contacts, f, indent=4, ensure_ascii=False)
    except Exception as e:
        log(f"Error al guardar contactos: {e}")

def sanitize_phone(phone: str) -> str:
    """Elimina caracteres no numericos excepto el + inicial."""
    cleaned = "".join(c for c in phone if c.isdigit() or c == "+")
    # Limitar spam/longitud
    if len(cleaned) > 20:
        cleaned = cleaned[:20]
    return cleaned

def whatsapp(parameters: dict, player=None, speak=None) -> str:
    """
    Integracion de WhatsApp y agenda local de contactos.
    """
    action = parameters.get("action", "").lower().strip()
    receiver = parameters.get("receiver", "").strip()
    message = parameters.get("message", "").strip()
    image_path = parameters.get("image_path", "").strip()
    name = parameters.get("name", "").strip()
    phone = parameters.get("phone", "").strip()
    count = parameters.get("count", 10)

    if not action:
        return "Error: Falta el parametro obligatorio 'action'."

    contacts = load_contacts()

    if action == "add_contact":
        if not name or not phone:
            return "Error: Para agregar un contacto se requiere 'name' y 'phone'."
        clean_p = sanitize_phone(phone)
        contacts[name.lower()] = clean_p
        save_contacts(contacts)
        return f"Contacto '{name}' guardado con el telefono '{clean_p}'."

    elif action == "delete_contact":
        if not name:
            return "Error: Se requiere 'name' para eliminar el contacto."
        name_l = name.lower()
        if name_l in contacts:
            del contacts[name_l]
            save_contacts(contacts)
            return f"Contacto '{name}' eliminado de la agenda."
        return f"El contacto '{name}' no existe en la agenda."

    elif action == "list_contacts":
        if not contacts:
            return "La agenda de WhatsApp esta vacia."
        res = "Contactos guardados en WhatsApp:\n"
        for k, v in sorted(contacts.items()):
            res += f"  - {k.title()}: {v}\n"
        return res.strip()

    elif action == "send":
        if not receiver:
            return "Error: Se requiere el parametro 'receiver' (nombre o numero de telefono)."
        if not message:
            return "Error: Se requiere el parametro 'message' con el texto a enviar."

        # Buscar en contactos primero
        phone_target = ""
        receiver_l = receiver.lower()
        if receiver_l in contacts:
            phone_target = contacts[receiver_l]
            log(f"Contacto '{receiver}' resuelto a '{phone_target}'")
        else:
            # Validar si es un telefono directo
            phone_target = sanitize_phone(receiver)
            if not phone_target:
                return f"Error: No se encontro el contacto '{receiver}' ni parece un telefono valido."

        # Construir link seguro de WhatsApp Web
        encoded_msg = urllib.parse.quote(message)
        wa_url = f"https://web.whatsapp.com/send?phone={phone_target}&text={encoded_msg}"
        
        try:
            log(f"Abriendo WhatsApp Web para enviar mensaje a '{phone_target}'...")
            webbrowser.open(wa_url)
            return f"WhatsApp Web abierto para enviar mensaje a '{receiver}' ({phone_target})."
        except Exception as e:
            return f"Error al abrir WhatsApp Web: {e}"

    elif action in ["send_image", "read", "unread"]:
        # Acciones complejas o guiadas que requieren integracion local
        # En esta version desktop, abrimos la interfaz de WhatsApp Web como fallback
        log(f"Accion '{action}' iniciada. Redirigiendo a interfaz de usuario.")
        try:
            webbrowser.open("https://web.whatsapp.com/")
            return f"Accion '{action}' requiere interaccion directa en WhatsApp Web. Abriendo sitio oficial."
        except Exception as e:
            return f"Error al abrir WhatsApp Web: {e}"

    else:
        return f"Error: Accion '{action}' no soportada por el modulo de WhatsApp."
