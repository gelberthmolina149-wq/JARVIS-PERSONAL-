"""
agents/dev_agent_module.py — Agente 3: Desarrollo, Creatividad y Conocimiento.
Gestiona código, creación de contenido, memoria y objetivos.
"""
from __future__ import annotations
from .base_agent import BaseAgent


def _build_dev_agent() -> BaseAgent:
    agent = BaseAgent(name="DevAgent")

    # ── Código ────────────────────────────────────────────────────────────
    try:
        from actions.code_helper import code_helper
        agent.register("code_helper", code_helper)
    except ImportError:
        pass

    try:
        from actions.dev_agent import dev_agent
        agent.register("dev_agent", dev_agent)
    except ImportError:
        pass

    try:
        from actions.codebase import codebase
        agent.register("codebase", codebase)
    except ImportError:
        pass

    try:
        from actions.git_control import git_control
        agent.register("git_control", git_control)
    except ImportError:
        pass

    # ── Documentos y archivos ─────────────────────────────────────────────
    try:
        from actions.file_processor import file_processor
        agent.register("file_processor", file_processor)
    except ImportError:
        pass

    try:
        from actions.document_creator import document_creator
        agent.register("document_creator", document_creator)
    except ImportError:
        pass

    try:
        from actions.document_manager import document_manager
        agent.register("document_manager", document_manager)
    except ImportError:
        pass

    # ── Generación de contenido ───────────────────────────────────────────
    try:
        from actions.image_generation import image_generation
        agent.register("image_generation", image_generation)
    except ImportError:
        pass

    # ── Conocimiento y memoria ────────────────────────────────────────────
    try:
        from actions.knowledge_base import knowledge_base
        agent.register("knowledge_base", knowledge_base)
    except ImportError:
        pass

    try:
        from actions.goals import goals
        agent.register("goals", goals)
    except ImportError:
        pass

    try:
        from actions.user_profile import user_profile
        agent.register("user_profile", user_profile)
    except ImportError:
        pass

    # ── Asistencia inteligente ────────────────────────────────────────────
    try:
        from actions.morning_brief import morning_brief
        agent.register("morning_brief", morning_brief)
    except ImportError:
        pass

    try:
        from actions.openrouter_agent import openrouter_agent

        def _openrouter_wrapper(parameters: dict, player=None, speak=None) -> str:
            return openrouter_agent(
                query=parameters.get("query", ""),
                model=parameters.get("model", "google/gemini-2.5-flash"),
            )

        agent.register("openrouter_agent", _openrouter_wrapper)
    except ImportError:
        pass

    # ── Tareas multi-paso (agente de tareas autónomo) ─────────────────────
    try:
        def _agent_task_wrapper(parameters: dict, player=None, speak=None) -> str:
            from agent.task_queue import get_queue, TaskPriority
            priority_map = {
                "low": TaskPriority.LOW,
                "normal": TaskPriority.NORMAL,
                "high": TaskPriority.HIGH,
            }
            priority = priority_map.get(
                parameters.get("priority", "normal").lower(),
                TaskPriority.NORMAL,
            )
            task_id = get_queue().submit(
                goal=parameters.get("goal", ""),
                priority=priority,
                speak=speak,
            )
            return f"Tarea iniciada (ID: {task_id})."

        agent.register("agent_task", _agent_task_wrapper)
    except Exception:
        pass

    try:
        from actions.workspace_search import workspace_search
        agent.register("workspace_search", workspace_search)
    except ImportError:
        pass

    return agent


DevAgent = _build_dev_agent
