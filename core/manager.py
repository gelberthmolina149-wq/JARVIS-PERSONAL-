"""
core/manager.py — Manager Central de JARVIS.

Recibe cada tool call de Gemini, decide qué agente la maneja
y retorna el resultado. Es el único punto de coordinación del sistema.
"""
from __future__ import annotations
import asyncio
from typing import Any, Callable

from agents.system_agent import SystemAgent
from agents.cloud_agent import CloudAgent
from agents.dev_agent_module import DevAgent
from agents.base_agent import BaseAgent


# ── Tabla de enrutamiento: tool_name → dominio ────────────────────────────
_ROUTING: dict[str, str] = {
    # System Agent
    "open_app":              "system",
    "computer_settings":     "system",
    "computer_control":      "system",
    "windows_settings":      "system",
    "file_controller":       "system",
    "desktop_control":       "system",
    "browser_control":       "system",
    "visual_click":          "system",
    "screen_vision":         "system",
    "screen_process":        "system",
    "vision_guardian":       "system",
    "screen_reader":         "system",
    "system_monitor":        "system",
    "terminal_agent":        "system",
    "native_ui":             "system",
    "rgb_control":           "system",
    "smart_home":            "system",
    "accessibility":         "system",
    "accessibility_overlay": "system",
    "camera_bus":            "system",
    "jarvis_ui_control":     "system",

    # Cloud Agent
    "web_search":       "cloud",
    "weather_report":   "cloud",
    "flight_finder":    "cloud",
    "youtube_video":    "cloud",
    "gmail_control":    "cloud",
    "google_calendar":  "cloud",
    "google_drive":     "cloud",
    "google_maps":      "cloud",
    "whatsapp":         "cloud",
    "send_message":     "cloud",
    "spotify_control":  "cloud",
    "social_media":     "cloud",
    "tiktok_analyzer":  "cloud",
    "reminder":         "cloud",
    "scheduler":        "cloud",
    "rules_engine":     "cloud",
    "game_updater":     "cloud",
    "arca_invoice":     "cloud",

    # Dev Agent
    "code_helper":      "dev",
    "dev_agent":        "dev",
    "codebase":         "dev",
    "git_control":      "dev",
    "file_processor":   "dev",
    "document_creator": "dev",
    "document_manager": "dev",
    "image_generation": "dev",
    "knowledge_base":   "dev",
    "goals":            "dev",
    "user_profile":     "dev",
    "morning_brief":    "dev",
    "openrouter_agent": "dev",
    "agent_task":       "dev",
    "workspace_search": "dev",
}


class AgentManager:
    """
    Manager Central — Orquesta los 3 agentes especializados de JARVIS.
    
    Uso:
        manager = AgentManager()
        result = await manager.dispatch("web_search", {"query": "clima Lima"}, ui, speak)
    """

    def __init__(self):
        self._agents: dict[str, BaseAgent] = {
            "system": SystemAgent(),
            "cloud":  CloudAgent(),
            "dev":    DevAgent(),
        }
        print(f"[Manager] AgentManager inicializado con {len(self._agents)} agentes.")
        for name, agent in self._agents.items():
            tools = list(agent._tools.keys())
            print(f"[Manager]   {name}: {len(tools)} tools registradas")

    async def dispatch(
        self,
        tool_name: str,
        args: dict,
        ui: Any,
        speak: Callable | None = None,
    ) -> str:
        """
        Enruta una tool call al agente correcto y retorna el resultado.
        
        Args:
            tool_name: Nombre de la herramienta a ejecutar.
            args: Parámetros del LLM.
            ui: Objeto JarvisUI.
            speak: Función TTS de JARVIS.
        
        Returns:
            Resultado como string.
        """
        domain = _ROUTING.get(tool_name, "system")  # default: system
        agent = self._agents[domain]

        if not agent.handles(tool_name):
            # Fallback: buscar en los otros agentes
            for other_domain, other_agent in self._agents.items():
                if other_domain != domain and other_agent.handles(tool_name):
                    agent = other_agent
                    domain = other_domain
                    break
            else:
                # Intento de carga dinámica desde actions/
                return await self._dynamic_load(tool_name, args, ui, speak)

        print(f"[Manager] >> {tool_name} -> {domain.upper()}")
        return await agent.execute(tool_name, args, ui, speak)

    async def _dynamic_load(
        self,
        tool_name: str,
        args: dict,
        ui: Any,
        speak: Callable | None = None,
    ) -> str:
        """
        Intenta cargar dinámicamente una tool desde actions/{tool_name}.py.
        Útil para tools creadas en tiempo de ejecución.
        """
        import importlib
        import inspect
        loop = asyncio.get_event_loop()
        from agents.base_agent import _AGENT_EXECUTOR

        try:
            module = importlib.import_module(f"actions.{tool_name}")
            fn = getattr(module, tool_name)
            sig = inspect.signature(fn)
            kwargs: dict = {"parameters": args, "player": ui}
            if "speak" in sig.parameters and speak:
                kwargs["speak"] = speak
            result = await loop.run_in_executor(
                _AGENT_EXECUTOR, lambda: fn(**kwargs)
            )
            return result or f"Tool '{tool_name}' ejecutada."
        except Exception as e:
            return f"Tool desconocida: '{tool_name}'. (Error: {e})"

    def get_agent(self, domain: str) -> BaseAgent | None:
        """Retorna el agente por dominio ('system', 'cloud', 'dev')."""
        return self._agents.get(domain)


# ── Instancia global del manager ──────────────────────────────────────────
_manager_instance: AgentManager | None = None


def get_manager() -> AgentManager:
    """Retorna la instancia singleton del AgentManager."""
    global _manager_instance
    if _manager_instance is None:
        _manager_instance = AgentManager()
    return _manager_instance
