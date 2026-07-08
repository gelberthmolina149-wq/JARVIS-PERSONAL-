"""
agents/security.py — Capa de seguridad mejorada para terminal_agent de JARVIS.

Intercepta de forma proactiva comandos destructivos, accesos a credenciales/secretos
y descargas remotas de scripts.
"""
from __future__ import annotations
import re
from typing import Callable, Any

# Patrones de comandos de alto riesgo
_DANGEROUS_PATTERNS: list[re.Pattern] = [
    # 1. Comandos Destructivos
    re.compile(r'\brm\s+(-rf?|--recursive)\b', re.IGNORECASE),
    re.compile(r'\bdel\s+/[FfSs]\b', re.IGNORECASE),
    re.compile(r'\brmdir\s+/[Ss]\b', re.IGNORECASE),
    re.compile(r'\bformat\s+[A-Za-z]:', re.IGNORECASE),
    re.compile(r'\bdiskpart\b', re.IGNORECASE),
    re.compile(r'\breg\s+delete\b', re.IGNORECASE),
    re.compile(r'\bnetsh\s+(firewall|advfirewall)\b', re.IGNORECASE),
    re.compile(r'\bSet-MpPreference\b', re.IGNORECASE),  # Desactivar Windows Defender
    re.compile(r'\bshutdown\s+/[RrSs]\b', re.IGNORECASE),
    re.compile(r'\brestart-computer\b', re.IGNORECASE),
    re.compile(r'\btaskkill\s+/[Ff]\b', re.IGNORECASE),
    re.compile(r':\(\)\s*\{.*\}.*&', re.IGNORECASE),   # fork bomb
    re.compile(r'>\s*/dev/sd[a-z]', re.IGNORECASE),    # wipe disk
    
    # 2. Descargas Remotas y Ejecución Inyectada
    re.compile(r'\bcurl\b.*\|\s*(bash|sh)\b', re.IGNORECASE),
    re.compile(r'\bwget\b.*-O\s*-\s*\|\s*(bash|sh)\b', re.IGNORECASE),
    re.compile(r'\bInvoke-Expression\b', re.IGNORECASE),
    re.compile(r'\biex\b', re.IGNORECASE),
    re.compile(r'\bInvoke-WebRequest\b', re.IGNORECASE),
    re.compile(r'\biwr\b', re.IGNORECASE),
    re.compile(r'\bStart-BitsTransfer\b', re.IGNORECASE),
    re.compile(r'\.DownloadString\b', re.IGNORECASE),
    re.compile(r'\.DownloadFile\b', re.IGNORECASE),
    re.compile(r'\.DownloadData\b', re.IGNORECASE),
    re.compile(r'Net\.WebClient', re.IGNORECASE),
    re.compile(r'HttpClient', re.IGNORECASE),
]

# Palabras clave de secretos y carpetas sensibles
_SENSITIVE_KEYWORDS: list[str] = [
    "api_keys.json", "api_keys.example.json", "tokens.json",
    "gemini_api_key", "openrouter_api_key",
    "password", "contraseña", "token", "secret_key", "private_key", "id_rsa",
    "Get-ChildItem env:", "env:"
]

def _is_dangerous(command: str) -> bool:
    """Verifica si el comando coincide con algun patron de riesgo o palabra clave sensible."""
    for pattern in _DANGEROUS_PATTERNS:
        if pattern.search(command):
            return True
            
    cmd_lower = command.lower()
    for kw in _SENSITIVE_KEYWORDS:
        if kw.lower() in cmd_lower:
            return True
            
    return False

def safe_terminal_agent(
    terminal_fn: Callable,
    parameters: dict,
    player: Any = None,
    speak: Callable | None = None,
) -> str:
    """
    Wrapper de seguridad para terminal_agent.
    Aborta la ejecucion antes de tocar la terminal si el comando es catalogado de riesgo.
    """
    command = parameters.get("command", "") or parameters.get("cmd", "")

    if command and _is_dangerous(command) and not parameters.get("confirmed", False):
        warning = (
            f"[ALERTA] SEGURIDAD: El comando '{command[:60]}...' fue bloqueado por la Directiva de Seguridad de JARVIS.\n"
            "Se detecto un comando potencialmente destructivo, acceso a secretos o descarga externa.\n"
            "Si es seguro ejecutarlo, repite indicando confirmacion explicativa (confirmed=True)."
        )
        if player:
            try:
                player.write_log(f"SECURITY: Blocked dangerous command: {command[:80]}")
            except Exception:
                pass
        try:
            print(f"[Security] [BLOQUEADO] Bloqueado: {command[:80]}")
        except Exception:
            pass
        return warning

    return terminal_fn(parameters=parameters, player=player)
