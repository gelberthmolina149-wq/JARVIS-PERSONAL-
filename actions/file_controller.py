"""
actions/file_controller.py — Gestion segura de archivos y carpetas en Windows.
"""
from __future__ import annotations
import os
import shutil
import mimetypes
import time
from pathlib import Path
from typing import Any

try:
    import send2trash
except ImportError:
    send2trash = None

def log(msg: str, player=None):
    if player:
        try:
            player.write_log(msg)
        except Exception:
            pass
    try:
        print(f"[file_controller] {msg}")
    except Exception:
        pass

def resolve_path(raw_path: str) -> Path:
    """Resuelve alias comunes y rutas relativas a rutas absolutas."""
    raw_path_lower = raw_path.lower().strip()
    home = Path.home()

    if raw_path_lower == "desktop":
        target = home / "Desktop"
    elif raw_path_lower == "downloads":
        target = home / "Downloads"
    elif raw_path_lower == "documents":
        target = home / "Documents"
    elif raw_path_lower == "home":
        target = home
    else:
        # Reemplazar ~ con la carpeta home
        if raw_path.startswith("~"):
            target = Path(raw_path.replace("~", str(home), 1))
        else:
            target = Path(raw_path)
            if not target.is_absolute():
                target = Path(os.getcwd()) / target

    return target.resolve()

def is_safe_path(path: Path) -> bool:
    """
    Verifica que la ruta no acceda a directorios criticos del sistema.
    Permite el acceso a la carpeta de usuario o directorios locales del proyecto.
    """
    try:
        resolved = path.resolve()
        
        # Bloquear directorios del sistema de Windows comunes
        system_roots = [
            Path("C:/Windows").resolve(),
            Path("C:/Program Files").resolve(),
            Path("C:/Program Files (x86)").resolve(),
            Path("C:/ProgramData").resolve(),
        ]
        
        for root in system_roots:
            if resolved == root or root in resolved.parents:
                return False
                
        # Validar archivos criticos especificos del sistema
        if resolved.name.lower() in ["hosts", "desktop.ini", "ntuser.dat"]:
            return False
            
        return True
    except Exception:
        return False

def file_controller(parameters: dict, player=None, speak=None) -> str:
    """
    Manages files and folders safely: list, create, delete, move, copy, rename, read, write, find, info.
    """
    action = parameters.get("action", "").lower()
    path_str = parameters.get("path", "").strip()
    destination_str = parameters.get("destination", "").strip()
    new_name = parameters.get("new_name", "").strip()
    content = parameters.get("content", "")
    name_query = parameters.get("name", "").strip()
    extension = parameters.get("extension", "").strip()
    confirm = parameters.get("confirm", False)

    # Parametros para 'edit'
    old_text = parameters.get("old_text", "")
    new_text = parameters.get("new_text", "")
    mode = parameters.get("mode", "replace").lower()

    if not action:
        return "Error: Falta el parametro obligatorio 'action'."
    if not path_str:
        return "Error: Falta el parametro 'path'."

    # Resolucion y validacion de la ruta principal
    target_path = resolve_path(path_str)
    if not is_safe_path(target_path):
        return f"Error de seguridad: Acceso denegado a la ruta '{target_path}'."

    log(f"Ejecutando accion '{action}' en '{target_path}'")

    if action == "list":
        if not target_path.exists():
            return f"Error: El directorio '{target_path}' no existe."
        if not target_path.is_dir():
            return f"Error: '{target_path}' no es un directorio."
        
        try:
            items = os.listdir(target_path)
            files = []
            dirs = []
            for item in items:
                item_path = target_path / item
                if item_path.is_dir():
                    dirs.append(item + "/")
                else:
                    files.append(item)
            
            result = f"Contenido de {target_path}:\n"
            if dirs:
                result += "  Directorios:\n" + "\n".join(f"    {d}" for d in sorted(dirs)) + "\n"
            if files:
                result += "  Archivos:\n" + "\n".join(f"    {f}" for f in sorted(files)) + "\n"
            if not dirs and not files:
                result += "  (Vacio)"
            return result
        except Exception as e:
            return f"Error al listar directorio: {e}"

    elif action == "create_file":
        try:
            target_path.parent.mkdir(parents=True, exist_ok=True)
            with open(target_path, "w", encoding="utf-8") as f:
                f.write(content)
            return f"Archivo creado exitosamente en '{target_path}'."
        except Exception as e:
            return f"Error al crear archivo: {e}"

    elif action == "create_folder":
        try:
            target_path.mkdir(parents=True, exist_ok=True)
            return f"Carpeta creada exitosamente en '{target_path}'."
        except Exception as e:
            return f"Error al crear carpeta: {e}"

    elif action == "read":
        if not target_path.exists():
            return f"Error: El archivo '{target_path}' no existe."
        if not target_path.is_file():
            return f"Error: '{target_path}' no es un archivo valido."
        
        # Validar tamaño del archivo (Max 5MB)
        try:
            size_bytes = target_path.stat().st_size
            if size_bytes > 5 * 1024 * 1024:
                return f"Error: El archivo es demasiado grande ({size_bytes / (1024*1024):.2f} MB). Limite de lectura seguro es 5 MB."
        except Exception as e:
            return f"Error al verificar tamano de archivo: {e}"

        # Lectura con fallbacks de codificacion
        for enc in ["utf-8", "cp1252", "latin-1"]:
            try:
                with open(target_path, "r", encoding=enc) as f:
                    return f.read()
            except UnicodeDecodeError:
                continue
            except Exception as e:
                return f"Error al leer archivo: {e}"
        return "Error: No se pudo decodificar el archivo con ninguna de las codificaciones admitidas."

    elif action == "write":
        try:
            with open(target_path, "w", encoding="utf-8") as f:
                f.write(content)
            return f"Contenido escrito exitosamente en '{target_path}'."
        except Exception as e:
            return f"Error al escribir archivo: {e}"

    elif action == "edit":
        if not target_path.exists():
            return f"Error: El archivo '{target_path}' no existe."
        
        # Primero leer archivo existente
        current_content = ""
        for enc in ["utf-8", "cp1252", "latin-1"]:
            try:
                with open(target_path, "r", encoding=enc) as f:
                    current_content = f.read()
                    break
            except UnicodeDecodeError:
                continue
        else:
            return "Error: No se pudo leer el archivo para edicion."

        # Modificaciones
        if mode == "replace":
            if not old_text:
                return "Error: Se requiere 'old_text' para reemplazar."
            if old_text not in current_content:
                return f"Error: No se encontro el texto a reemplazar '{old_text}' en el archivo."
            new_content = current_content.replace(old_text, new_text)
        elif mode == "append":
            new_content = current_content + new_text
        elif mode == "prepend":
            new_content = new_text + current_content
        elif mode == "overwrite":
            new_content = new_text
        else:
            return f"Error: Modo de edicion '{mode}' no soportado."

        try:
            with open(target_path, "w", encoding="utf-8") as f:
                f.write(new_content)
            return f"Archivo editado exitosamente en '{target_path}'."
        except Exception as e:
            return f"Error al escribir cambios editados: {e}"

    elif action == "move":
        if not destination_str:
            return "Error: Se requiere el parametro 'destination' para mover."
        dest_path = resolve_path(destination_str)
        if not is_safe_path(dest_path):
            return f"Error de seguridad: Acceso denegado a la ruta destino '{dest_path}'."
        
        try:
            dest_path.parent.mkdir(parents=True, exist_ok=True)
            shutil.move(str(target_path), str(dest_path))
            return f"Elemento movido de '{target_path}' a '{dest_path}'."
        except Exception as e:
            return f"Error al mover elemento: {e}"

    elif action == "copy":
        if not destination_str:
            return "Error: Se requiere el parametro 'destination' para copiar."
        dest_path = resolve_path(destination_str)
        if not is_safe_path(dest_path):
            return f"Error de seguridad: Acceso denegado a la ruta destino '{dest_path}'."
        
        try:
            dest_path.parent.mkdir(parents=True, exist_ok=True)
            if target_path.is_dir():
                shutil.copytree(str(target_path), str(dest_path))
            else:
                shutil.copy2(str(target_path), str(dest_path))
            return f"Elemento copiado de '{target_path}' a '{dest_path}'."
        except Exception as e:
            return f"Error al copiar elemento: {e}"

    elif action == "rename":
        if not new_name:
            return "Error: Se requiere el parametro 'new_name' para renombrar."
        
        # Validar nuevo nombre para evitar saltar a otras carpetas
        if "/" in new_name or "\\" in new_name:
            return "Error: El nuevo nombre no debe contener separadores de ruta."
            
        new_path = target_path.parent / new_name
        try:
            target_path.rename(new_path)
            return f"Renombrado '{target_path}' a '{new_path}'."
        except Exception as e:
            return f"Error al renombrar: {e}"

    elif action == "delete":
        if not confirm:
            return f"Advertencia: ¿Esta seguro de que desea eliminar '{target_path}'? Especifique 'confirm': True para proceder."
        
        if not target_path.exists():
            return f"Error: '{target_path}' no existe."
            
        try:
            if send2trash:
                send2trash.send2trash(str(target_path))
                return f"'{target_path}' movido a la Papelera de Reciclaje de forma segura."
            else:
                # Fallback si send2trash no esta listo
                if target_path.is_dir():
                    shutil.rmtree(target_path)
                else:
                    target_path.unlink()
                return f"'{target_path}' eliminado de forma definitiva (send2trash no disponible)."
        except Exception as e:
            return f"Error al eliminar: {e}"

    elif action == "find":
        if not target_path.exists() or not target_path.is_dir():
            return f"Error: La ruta inicial '{target_path}' no existe o no es un directorio."
        
        try:
            matches = []
            name_lower = name_query.lower() if name_query else ""
            ext_lower = extension.lower() if extension else ""
            
            for root, _, files in os.walk(target_path):
                # Limite maximo de resultados para evitar respuestas gigantescas
                if len(matches) >= 50:
                    break
                for file in files:
                    file_path = Path(root) / file
                    if name_lower and name_lower not in file.lower():
                        continue
                    if ext_lower and not file.lower().endswith(ext_lower):
                        continue
                    matches.append(str(file_path))
                    
            if not matches:
                return f"No se encontraron archivos en '{target_path}' que coincidan con la busqueda."
                
            return "Archivos encontrados:\n" + "\n".join(f"  - {m}" for m in matches[:50])
        except Exception as e:
            return f"Error al buscar archivos: {e}"

    elif action == "info":
        if not target_path.exists():
            return f"Error: '{target_path}' no existe."
            
        try:
            stats = target_path.stat()
            size = stats.st_size
            is_directory = target_path.is_dir()
            mtime = time.ctime(stats.st_mtime)
            ctime = time.ctime(stats.st_ctime)
            
            mime_type, _ = mimetypes.guess_type(target_path)
            
            info_str = (
                f"Informacion de '{target_path}':\n"
                f"  Tipo: {'Directorio' if is_directory else 'Archivo'}\n"
                f"  Tamano: {size} bytes ({size / 1024:.2f} KB)\n"
                f"  Creado: {ctime}\n"
                f"  Ultima Modificacion: {mtime}\n"
            )
            if mime_type:
                info_str += f"  MIME Type: {mime_type}\n"
                
            return info_str
        except Exception as e:
            return f"Error al obtener informacion: {e}"

    else:
        return f"Error: Accion '{action}' no reconocida para file_controller."
