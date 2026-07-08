"""
actions/send_message.py — Envío de mensajes de texto en plataformas (Telegram, Discord, Signal, Messenger).
"""
from __future__ import annotations
import os
import json
import requests
from pathlib import Path

def log(msg: str, player=None):
    if player:
        try:
            player.write_log(msg)
        except Exception:
            pass
    try:
        print(f"[send_message] {msg}")
    except Exception:
        pass

def get_platform_credentials(platform: str) -> dict:
    """Busca credenciales de mensajeria dentro de api_keys.json sin exponer logs."""
    config_path = Path("config/api_keys.json")
    if not config_path.exists():
        return {}
    try:
        with open(config_path, "r", encoding="utf-8") as f:
            cfg = json.load(f)
            return cfg.get("messaging_credentials", {}).get(platform.lower(), {})
    except Exception:
        return {}

def send_message(parameters: dict, player=None, speak=None) -> str:
    """
    Sends a text message via Telegram, Discord, Signal or Messenger.
    """
    receiver = parameters.get("receiver", "").strip()
    message_text = parameters.get("message_text", "").strip()
    platform = parameters.get("platform", "").lower().strip()

    if not receiver or not message_text or not platform:
        return "Error: Faltan parametros obligatorios ('receiver', 'message_text', 'platform')."

    # Sanitizar entrada
    clean_message = message_text.replace("\r", "").strip()

    log(f"Enviando mensaje a '{receiver}' via '{platform.upper()}'")

    # Obtener credenciales seguras
    creds = get_platform_credentials(platform)

    if platform == "telegram":
        # Requiere telegram_bot_token y telegram_chat_id (o receiver) en credenciales
        token = creds.get("bot_token")
        chat_id = creds.get("chat_id", receiver) # Usa el chat_id guardado o el receiver proporcionado

        if not token:
            return "Error: Falta 'bot_token' de Telegram en las credenciales de api_keys.json."
        
        try:
            url = f"https://api.telegram.org/bot{token}/sendMessage"
            payload = {"chat_id": chat_id, "text": clean_message}
            resp = requests.post(url, json=payload, timeout=10)
            if resp.status_code == 200:
                return f"Mensaje enviado exitosamente a '{receiver}' via Telegram."
            else:
                return f"Error al enviar por Telegram (HTTP {resp.status_code}): {resp.text}"
        except Exception as e:
            return f"Excepcion al enviar por Telegram: {e}"

    elif platform == "discord":
        # Requiere webhook_url en credenciales
        webhook_url = creds.get("webhook_url", receiver) # Usa webhook_url guardado o receiver directo si es URL
        
        if not webhook_url or not webhook_url.startswith("https://discord.com/api/webhooks/"):
            return "Error: Falta un 'webhook_url' valido de Discord."

        try:
            payload = {"content": f"**Para: {receiver}**\n{clean_message}"}
            resp = requests.post(webhook_url, json=payload, timeout=10)
            if resp.status_code in [200, 204]:
                return f"Mensaje enviado exitosamente a Discord via Webhook."
            else:
                return f"Error al enviar a Discord (HTTP {resp.status_code}): {resp.text}"
        except Exception as e:
            return f"Excepcion al enviar a Discord: {e}"

    elif platform in ["signal", "messenger"]:
        # Fallback informativo/guiado si no estan configuradas las dependencias
        return f"La plataforma '{platform.upper()}' requiere integracion de API de pago o autenticacion de usuario. Credenciales no encontradas."

    else:
        return f"Error: Plataforma '{platform}' no soportada por el modulo send_message."
