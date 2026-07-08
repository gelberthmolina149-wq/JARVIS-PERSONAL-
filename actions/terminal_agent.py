"""
actions/terminal_agent.py — Ejecucion segura de comandos en PowerShell/CMD bajo Windows.
"""
from __future__ import annotations
import subprocess
from typing import Any

def log(msg: str, player=None):
    if player:
        try:
            player.write_log(msg)
        except Exception:
            pass
    try:
        print(f"[terminal_agent] {msg}")
    except Exception:
        pass

def terminal_agent(parameters: dict, player=None, speak=None) -> str:
    """
    Executes standard command line instructions in Windows without raising visible windows.
    """
    command = parameters.get("command", "") or parameters.get("cmd", "")
    timeout = parameters.get("timeout", 30)

    if not command:
        return "Error: Falta el comando obligatorio ('command' o 'cmd')."

    # Configuracion de ejecucion para evitar popups persistentes (CREATE_NO_WINDOW)
    # 0x08000000 es la mascara para CREATE_NO_WINDOW en Windows
    CREATE_NO_WINDOW = 0x08000000

    log(f"Ejecutando comando: '{command[:80]}'")

    try:
        # PowerShell por defecto para compatibilidad mejorada con scripts y salidas formateadas
        result = subprocess.run(
            ["powershell", "-NoProfile", "-Command", command],
            capture_output=True,
            text=True,
            timeout=float(timeout),
            creationflags=CREATE_NO_WINDOW
        )
        
        stdout_clean = result.stdout.strip()
        stderr_clean = result.stderr.strip()
        
        output_msg = ""
        if stdout_clean:
            output_msg += stdout_clean
        if stderr_clean:
            if output_msg:
                output_msg += "\n\n--- Errores (stderr) ---\n"
            output_msg += stderr_clean
            
        if not output_msg:
            output_msg = f"Comando ejecutado con exito. Codigo de salida: {result.returncode}"
            
        return output_msg
    except subprocess.TimeoutExpired:
        return f"Error: La ejecucion del comando excedio el limite de tiempo de {timeout} segundos."
    except Exception as e:
        return f"Error de ejecucion en terminal_agent: {e}"
