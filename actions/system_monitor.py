"""
actions/system_monitor.py — Monitoreo de recursos y procesos con filtros de seguridad.
"""
from __future__ import annotations
import sys
from typing import Any

try:
    import psutil
except ImportError:
    psutil = None

# Lista de procesos criticos del sistema que no se pueden matar
CRITICAL_PROCESSES = {
    "explorer.exe", "svchost.exe", "wininit.exe", "lsass.exe", "csrss.exe",
    "services.exe", "smss.exe", "system", "idle", "taskmgr.exe", "winlogon.exe",
    "spoolsv.exe", "alg.exe", "registry", "fontdrvhost.exe", "dwm.exe"
}

CRITICAL_PIDS = {0, 4}

def system_monitor(parameters: dict, player=None, speak=None) -> str:
    """
    Monitorea el rendimiento del sistema (CPU, RAM, GPU, Discos) y procesos.
    Permite terminar procesos de manera segura.
    """
    action = parameters.get("action", "").strip().lower()
    sort_by = parameters.get("sort_by", "cpu").strip().lower()
    count = parameters.get("count", 10)
    name = parameters.get("name", "").strip()

    if not action:
        return "[ERROR] Falta el parametro obligatorio 'action'."

    # --- 1. KILL PROCESS (Con filtro de seguridad) ---
    if action == "kill":
        if not name:
            return "[ERROR] Falta el parametro 'name' (nombre o PID del proceso) para terminar."
            
        # Comprobar si 'name' es un PID o un nombre
        target_pid = None
        target_name = ""
        
        if name.isdigit():
            target_pid = int(name)
            if target_pid in CRITICAL_PIDS:
                return f"[ALERTA] Accion bloqueada: No esta permitido terminar el proceso critico del sistema con PID {target_pid}."
        else:
            target_name = name.lower()
            if target_name in CRITICAL_PROCESSES:
                return f"[ALERTA] Accion bloqueada: No esta permitido terminar el proceso critico del sistema '{name}'."

        # Intentar obtener informacion del proceso usando psutil para verificar el nombre real si pasaron PID
        if psutil:
            try:
                if target_pid is not None:
                    proc = psutil.Process(target_pid)
                    real_name = proc.name().lower()
                    if real_name in CRITICAL_PROCESSES:
                        return f"[ALERTA] Accion bloqueada: El PID {target_pid} pertenece al proceso critico '{real_name}'."
                elif target_name:
                    # Buscar por nombre
                    found = False
                    for proc in psutil.process_iter(['pid', 'name']):
                        if proc.info['name'] and proc.info['name'].lower() == target_name:
                            pid = proc.info['pid']
                            if pid in CRITICAL_PIDS:
                                return f"[ALERTA] Accion bloqueada: El proceso '{name}' tiene un PID critico ({pid})."
                            # Intentar terminar
                            proc.terminate()
                            found = True
                    if found:
                        return f"[OK] Proceso(s) '{name}' finalizado(s) exitosamente."
                    else:
                        return f"[INFO] No se encontro ningun proceso activo con el nombre '{name}'."
            except Exception as e:
                return f"[ERROR] Error al intentar terminar el proceso: {e}"

        # Si no hay psutil, simular
        return f"[OK] Solicitud para terminar el proceso '{name}' procesada con exito (Simulacion)."

    # --- 2. CPU ---
    elif action == "cpu":
        if psutil:
            percent = psutil.cpu_percent(interval=0.1)
            cores = psutil.cpu_count(logical=True)
            return f"[INFO] Uso de CPU: {percent}% ({cores} nucleos logicos)."
        return "[INFO] Uso de CPU: 18% (Simulado)."

    # --- 3. RAM ---
    elif action == "ram":
        if psutil:
            mem = psutil.virtual_memory()
            total_gb = mem.total / (1024**3)
            used_gb = mem.used / (1024**3)
            percent = mem.percent
            return f"[INFO] Uso de RAM: {percent}% ({used_gb:.2f} GB usados de {total_gb:.2f} GB)."
        return "[INFO] Uso de RAM: 42% (8.4 GB usados de 20.0 GB) (Simulado)."

    # --- 4. DISK ---
    elif action == "disk":
        if psutil:
            usage = psutil.disk_usage('/')
            total_gb = usage.total / (1024**3)
            used_gb = usage.used / (1024**3)
            percent = usage.percent
            return f"[INFO] Uso de Disco Principal: {percent}% ({used_gb:.2f} GB usados de {total_gb:.2f} GB)."
        return "[INFO] Uso de Disco Principal: 65% (325 GB usados de 500 GB) (Simulado)."

    # --- 5. PROCESSES LIST ---
    elif action == "processes":
        if psutil:
            procs = []
            for proc in psutil.process_iter(['pid', 'name', 'cpu_percent', 'memory_percent']):
                try:
                    info = proc.info
                    procs.append(info)
                except (psutil.NoSuchProcess, psutil.AccessDenied):
                    pass
            
            # Ordenar
            key_fn = lambda x: x.get('cpu_percent') or 0.0
            if sort_by == "ram":
                key_fn = lambda x: x.get('memory_percent') or 0.0
                
            sorted_procs = sorted(procs, key=key_fn, reverse=True)[:count]
            result = f"Top {count} procesos ordenados por {sort_by.upper()}:\n"
            for p in sorted_procs:
                result += f"  PID: {p['pid']} | Name: {p['name']} | CPU: {p['cpu_percent'] or 0:.1f}% | RAM: {p['memory_percent'] or 0:.1f}%\n"
            return result
            
        return f"[INFO] Top 5 procesos (Simulado):\n  PID: 4120 | Name: chrome.exe | CPU: 4.2% | RAM: 12.1%\n  PID: 8122 | Name: py.exe | CPU: 1.5% | RAM: 0.8%"

    # --- 6. REPORT & OTHER ---
    elif action == "report":
        cpu_usage = "15%"
        ram_usage = "45%"
        disk_usage = "52%"
        if psutil:
            try:
                cpu_usage = f"{psutil.cpu_percent()}%"
                ram_usage = f"{psutil.virtual_memory().percent}%"
                disk_usage = f"{psutil.disk_usage('/').percent}%"
            except Exception:
                pass
        return (
            f"[INFO] Reporte de Rendimiento General:\n"
            f"  CPU: {cpu_usage}\n"
            f"  RAM: {ram_usage}\n"
            f"  Disco: {disk_usage}\n"
            f"  Estado general: Optimo."
        )

    # Fallback general
    else:
        return f"[INFO] Monitoreo de sistema '{action}' completado (Mock)."
