"""
actions/code_helper.py — Asistente de desarrollo: escribir, editar, explicar y correr codigo de forma segura.
"""
from __future__ import annotations
import os
import subprocess
from pathlib import Path
from typing import Any

def log(msg: str, player=None):
    if player:
        try:
            player.write_log(msg)
        except Exception:
            pass
    try:
        print(f"[code_helper] {msg}")
    except Exception:
        pass

def is_safe_path(path: Path) -> bool:
    """Verifica que el archivo no comprometa carpetas de sistema."""
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

def code_helper(parameters: dict, player=None, speak=None) -> str:
    """
    Writes, edits, explains, runs, or builds code files.
    """
    action = parameters.get("action", "auto").lower().strip()
    description = parameters.get("description", "").strip()
    language = parameters.get("language", "python").lower().strip()
    output_path_str = parameters.get("output_path", "").strip()
    file_path_str = parameters.get("file_path", "").strip()
    code_raw = parameters.get("code", "")
    args_str = parameters.get("args", "").strip()
    timeout = parameters.get("timeout", 30)

    # 1. Resolucion de Rutas
    output_path = Path(output_path_str).resolve() if output_path_str else None
    file_path = Path(file_path_str).resolve() if file_path_str else None

    # 2. Validaciones de Seguridad
    if output_path and not is_safe_path(output_path):
        return f"Error de seguridad: Acceso denegado a la ruta de salida '{output_path}'."
    if file_path and not is_safe_path(file_path):
        return f"Error de seguridad: Acceso denegado a la ruta del archivo '{file_path}'."

    log(f"Ejecutando accion '{action}'")

    if action == "write":
        if not output_path:
            return "Error: Se requiere 'output_path' para escribir codigo."
        try:
            output_path.parent.mkdir(parents=True, exist_ok=True)
            with open(output_path, "w", encoding="utf-8") as f:
                f.write(code_raw)
            return f"Codigo guardado exitosamente en '{output_path}'."
        except Exception as e:
            return f"Error al escribir archivo de codigo: {e}"

    elif action == "edit":
        if not file_path or not file_path.exists():
            return f"Error: El archivo a editar '{file_path_str}' no existe."
        # Cargar codigo existente
        try:
            with open(file_path, "r", encoding="utf-8") as f:
                content = f.read()
        except Exception as e:
            return f"Error al leer archivo para edicion: {e}"
            
        # Reemplazo simple o sobrescritura
        if code_raw:
            try:
                with open(file_path, "w", encoding="utf-8") as f:
                    f.write(code_raw)
                return f"Archivo '{file_path}' modificado exitosamente."
            except Exception as e:
                return f"Error al guardar cambios editados: {e}"
        else:
            return "Error: Falta 'code' con el contenido nuevo para editar."

    elif action == "explain":
        # Retorna el codigo estructurado para que el LLM lo analice
        if file_path:
            try:
                with open(file_path, "r", encoding="utf-8") as f:
                    code_raw = f.read()
            except Exception as e:
                return f"Error al leer archivo: {e}"
        if not code_raw:
            return "Error: Falta el codigo a explicar."
        
        return f"Codigo fuente ({language}):\n\n{code_raw}\n\nAnaliza este codigo y explicaselo al usuario de forma clara."

    elif action == "run":
        if not file_path or not file_path.exists():
            return "Error: Se requiere un 'file_path' existente para ejecutar codigo."
        
        # Bloquear extensiones de binarios compilados peligrosos
        ext = file_path.suffix.lower()
        if ext in [".exe", ".bat", ".cmd", ".vbs", ".ps1"]:
            return f"Error de seguridad: No se permite la ejecucion directa de archivos de comandos '{ext}'."

        # Construir argumentos de ejecucion de forma estructurada (sin inyeccion shell)
        run_args = []
        if language == "python":
            run_args = ["python", str(file_path)]
        elif language in ["javascript", "js"]:
            run_args = ["node", str(file_path)]
        else:
            return f"Error: Lenguaje '{language}' no soportado para ejecucion directa."

        if args_str:
            run_args.extend(args_str.split())

        log(f"Corriendo subproceso: {' '.join(run_args)}")
        
        CREATE_NO_WINDOW = 0x08000000
        try:
            result = subprocess.run(
                run_args,
                capture_output=True,
                text=True,
                timeout=float(timeout),
                creationflags=CREATE_NO_WINDOW
            )
            out = result.stdout.strip()
            err = result.stderr.strip()
            res_str = ""
            if out:
                res_str += f"Salida (stdout):\n{out}\n"
            if err:
                res_str += f"Errores (stderr):\n{err}\n"
            if not res_str:
                res_str = f"Ejecucion terminada con codigo {result.returncode}."
            return res_str
        except subprocess.TimeoutExpired:
            return f"Error: La ejecucion excedio el limite de tiempo de {timeout} segundos."
        except Exception as e:
            return f"Error al ejecutar codigo: {e}"

    elif action in ["build", "auto"]:
        return f"La accion '{action}' requiere configuracion de dependencias externas. No se pudo completar."

    else:
        return f"Error: Accion '{action}' no reconocida en code_helper."
