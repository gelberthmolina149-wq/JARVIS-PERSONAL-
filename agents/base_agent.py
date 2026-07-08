"""
agents/base_agent.py — Clase base para todos los agentes especializados de JARVIS.
Proporciona ejecución de tools con manejo de errores consistente y logging.
"""
from __future__ import annotations
import asyncio
import traceback
from concurrent.futures import ThreadPoolExecutor
from typing import Any, Callable

# Thread pool compartido por todos los agentes
_AGENT_EXECUTOR = ThreadPoolExecutor(max_workers=8, thread_name_prefix="jarvis-agent")


class BaseAgent:
    """
    Clase base para agentes especializados de JARVIS.
    
    Cada agente gestiona un dominio de herramientas (system, cloud, dev)
    y expone un método `execute(tool_name, args, ui, speak)` uniforme.
    """

    def __init__(self, name: str):
        self.name = name
        # Mapa: tool_name → función callable
        self._tools: dict[str, Callable] = {}

    def register(self, tool_name: str, fn: Callable) -> None:
        """Registra una función de tool en este agente."""
        self._tools[tool_name] = fn

    def handles(self, tool_name: str) -> bool:
        """Devuelve True si este agente puede manejar la tool indicada."""
        return tool_name in self._tools

    async def execute(
        self,
        tool_name: str,
        args: dict,
        ui: Any,
        speak: Callable | None = None,
    ) -> str:
        """
        Ejecuta una tool de forma asíncrona en el thread pool.
        
        Args:
            tool_name: Nombre de la tool a ejecutar.
            args: Parámetros recibidos del LLM.
            ui: Referencia al objeto JarvisUI para escribir logs y mostrar estado.
            speak: Función para que JARVIS hable (opcional).
        
        Returns:
            Resultado de la tool como string.
        """
        fn = self._tools.get(tool_name)
        if fn is None:
            return f"[{self.name}] Tool '{tool_name}' no está registrada en este agente."

        loop = asyncio.get_event_loop()
        try:
            # Construir kwargs según la firma de la función
            import inspect
            sig = inspect.signature(fn)
            kwargs: dict = {"parameters": args, "player": ui}
            if "speak" in sig.parameters and speak:
                kwargs["speak"] = speak

            result = await loop.run_in_executor(
                _AGENT_EXECUTOR,
                lambda: fn(**kwargs)
            )
            return result or "Done."

        except Exception as e:
            traceback.print_exc()
            error_msg = f"Tool '{tool_name}' falló: {str(e)[:120]}"
            if ui:
                try:
                    ui.write_log(f"ERR [{self.name}]: {tool_name} — {str(e)[:80]}")
                except Exception:
                    pass
            return error_msg

    def __repr__(self) -> str:
        tools = list(self._tools.keys())
        return f"<{self.__class__.__name__} name='{self.name}' tools={tools}>"
