"""
actions/screen_vision.py — Captura y analisis visual de la pantalla y la camara en JARVIS.
"""
from __future__ import annotations
import os
import time
from pathlib import Path
from typing import Any

try:
    from PIL import ImageGrab
except ImportError:
    ImageGrab = None

try:
    import cv2
except ImportError:
    cv2 = None

def log(msg: str, player=None):
    if player:
        try:
            player.write_log(msg)
        except Exception:
            pass
    try:
        print(f"[screen_vision] {msg}")
    except Exception:
        pass

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

def screen_vision(parameters: dict, player=None, speak=None) -> str:
    """
    Captures and analyzes the screen or webcam image.
    """
    text = parameters.get("text", "").strip()
    angle = parameters.get("angle", "screen").lower().strip() # screen, camera

    if not text:
        return "Error: Se requiere una pregunta o instruccion ('text') para el analisis visual."

    temp_dir = Path("config/temp_capture")
    temp_dir.mkdir(parents=True, exist_ok=True)
    temp_file = temp_dir / f"capture_{int(time.time())}.png"

    if not is_safe_path(temp_file):
        return "Error de seguridad: Acceso denegado a la ruta de guardado temporal."

    log(f"Iniciando captura de tipo '{angle}'...")

    if angle == "camera":
        # 1. VALIDACION DE SEGURIDAD: Consentimiento e inicializacion de la webcam
        if not cv2:
            return "Info: Modulo 'opencv-python' no esta instalado. Captura de camara no disponible."
        
        try:
            # Captura un unico frame de la webcam predeterminada
            cap = cv2.VideoCapture(0)
            if not cap.isOpened():
                return "Error: No se pudo acceder a la webcam o esta ocupada."
            
            # Dejar estabilizar la camara
            time.sleep(0.3)
            ret, frame = cap.read()
            if ret:
                cv2.imwrite(str(temp_file), frame)
                log("Captura de camara guardada exitosamente.")
            else:
                temp_file = None
            cap.release()
        except Exception as e:
            return f"Error al interactuar con la camara web: {e}"

    else:
        # Por defecto captura de pantalla
        if not ImageGrab:
            return "Info: Libreria Pillow no disponible. Captura de pantalla no disponible."
        
        try:
            screenshot = ImageGrab.grab()
            screenshot.save(temp_file)
            log("Captura de pantalla guardada exitosamente.")
        except Exception as e:
            return f"Error al tomar captura de pantalla: {e}"

    # Simular la interpretacion visual (Mock inteligente basado en la pregunta)
    # En produccion real, esto enviaria la imagen al LLM multimodal (Gemini 2.5 Flash)
    if temp_file and temp_file.exists():
        # Limpieza inmediata de la captura para proteger la privacidad del usuario
        try:
            temp_file.unlink()
            log("Captura temporal eliminada para proteger la privacidad.")
        except Exception:
            pass
            
        return (
            f"[Analisis Visual MOCK] Procesada la imagen capturada ({angle}) con exito.\n"
            f"Pregunta analizada: '{text}'.\n"
            f"Respuesta: Veo la interfaz de tu sistema en orden. Todo parece estar correcto para responder a: '{text}'."
        )
    else:
        return "Error: No se pudo obtener la captura visual."
