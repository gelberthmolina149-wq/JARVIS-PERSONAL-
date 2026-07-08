"""
agents/system_agent.py — Agente 1: Control del Sistema Operativo.
Gestiona todo lo relacionado con Windows: archivos, apps, pantalla, periféricos.
"""
from __future__ import annotations
from .base_agent import BaseAgent


def _build_system_agent() -> BaseAgent:
    """
    Construye y retorna el SystemAgent con todas sus tools registradas.
    Usa imports opcionales para que el agente arranque aunque falten módulos.
    """
    agent = BaseAgent(name="SystemAgent")

    # ── Apertura de aplicaciones ──────────────────────────────────────────
    try:
        from actions.open_app import open_app
        agent.register("open_app", open_app)
    except ImportError:
        pass

    # ── Control de computadora ────────────────────────────────────────────
    try:
        from actions.computer_settings import computer_settings
        agent.register("computer_settings", computer_settings)
    except ImportError:
        pass

    try:
        from actions.computer_control import computer_control
        agent.register("computer_control", computer_control)
    except ImportError:
        pass

    try:
        from actions.windows_settings import windows_settings
        agent.register("windows_settings", windows_settings)
    except ImportError:
        pass

    # ── Archivos y escritorio ─────────────────────────────────────────────
    try:
        from actions.file_controller import file_controller
        agent.register("file_controller", file_controller)
    except ImportError:
        pass

    try:
        from actions.desktop import desktop_control
        agent.register("desktop_control", desktop_control)
    except ImportError:
        pass

    # ── Navegador y web ───────────────────────────────────────────────────
    try:
        from actions.browser_control import browser_control
        agent.register("browser_control", browser_control)
    except ImportError:
        pass

    try:
        from actions.visual_click import visual_click
        agent.register("visual_click", visual_click)
    except ImportError:
        pass

    # ── Visión y pantalla ─────────────────────────────────────────────────
    try:
        from actions.screen_vision import screen_vision
        agent.register("screen_vision", screen_vision)
        agent.register("screen_process", screen_vision)  # alias
    except ImportError:
        pass

    try:
        from actions.vision_guardian import vision_guardian
        agent.register("vision_guardian", vision_guardian)
    except ImportError:
        pass

    try:
        from actions.screen_reader import screen_reader
        agent.register("screen_reader", screen_reader)
    except ImportError:
        pass

    # ── Monitor del sistema ───────────────────────────────────────────────
    try:
        from actions.system_monitor import system_monitor
        agent.register("system_monitor", system_monitor)
    except ImportError:
        pass

    # ── Terminal (con capa de seguridad) ──────────────────────────────────
    try:
        from actions.terminal_agent import terminal_agent
        from agents.security import safe_terminal_agent
        agent.register("terminal_agent", lambda **kw: safe_terminal_agent(terminal_agent, **kw))
    except ImportError:
        try:
            from actions.terminal_agent import terminal_agent
            agent.register("terminal_agent", terminal_agent)
        except ImportError:
            pass

    # ── UI nativa y gestual ───────────────────────────────────────────────
    try:
        from actions.native_ui import native_ui
        agent.register("native_ui", native_ui)
    except ImportError:
        pass

    try:
        from actions.camera_bus import camera_bus
        agent.register("camera_bus", camera_bus)
    except ImportError:
        pass

    try:
        from actions.jarvis_ui_control import jarvis_ui_control
        agent.register("jarvis_ui_control", jarvis_ui_control)
    except ImportError:
        pass

    # ── Periféricos RGB ───────────────────────────────────────────────────
    try:
        from actions.rgb_control import rgb_control
        agent.register("rgb_control", rgb_control)
    except ImportError:
        pass

    # ── Smart Home ────────────────────────────────────────────────────────
    try:
        from actions.smart_home import smart_home
        agent.register("smart_home", smart_home)
    except ImportError:
        pass

    # ── Accesibilidad ─────────────────────────────────────────────────────
    try:
        from actions.accessibility import accessibility
        agent.register("accessibility", accessibility)
    except ImportError:
        pass

    try:
        from actions.accessibility_overlay import accessibility_overlay
        agent.register("accessibility_overlay", accessibility_overlay)
    except ImportError:
        pass

    return agent


# Singleton del agente — se instancia una sola vez al importar
SystemAgent = _build_system_agent
