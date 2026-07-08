"""
agents/cloud_agent.py — Agente 2: Servicios en la Nube.
Gestiona APIs externas, comunicaciones, Google Suite, entretenimiento.
"""
from __future__ import annotations
from .base_agent import BaseAgent


def _build_cloud_agent() -> BaseAgent:
    agent = BaseAgent(name="CloudAgent")

    # ── Búsqueda e información ────────────────────────────────────────────
    try:
        from actions.web_search import web_search
        agent.register("web_search", web_search)
    except ImportError:
        pass

    try:
        from actions.weather_report import weather_action
        agent.register("weather_report", weather_action)
    except ImportError:
        pass

    try:
        from actions.flight_finder import flight_finder
        agent.register("flight_finder", flight_finder)
    except ImportError:
        pass

    # ── YouTube ───────────────────────────────────────────────────────────
    try:
        from actions.youtube_video import youtube_video
        agent.register("youtube_video", youtube_video)
    except ImportError:
        pass

    # ── Google Suite ──────────────────────────────────────────────────────
    try:
        from actions.gmail_control import gmail_control
        agent.register("gmail_control", gmail_control)
    except ImportError:
        pass

    try:
        from actions.google_calendar import google_calendar
        agent.register("google_calendar", google_calendar)
    except ImportError:
        pass

    try:
        from actions.google_drive import google_drive
        agent.register("google_drive", google_drive)
    except ImportError:
        pass

    try:
        from actions.google_maps import google_maps
        agent.register("google_maps", google_maps)
    except ImportError:
        pass

    # ── Comunicaciones ────────────────────────────────────────────────────
    try:
        from actions.whatsapp import whatsapp
        agent.register("whatsapp", whatsapp)
    except ImportError:
        pass

    try:
        from actions.send_message import send_message
        agent.register("send_message", send_message)
    except ImportError:
        pass

    # ── Música ────────────────────────────────────────────────────────────
    try:
        from actions.spotify_control import spotify_control
        agent.register("spotify_control", spotify_control)
    except ImportError:
        pass

    # ── Redes sociales ────────────────────────────────────────────────────
    try:
        from actions.social_media import social_media
        agent.register("social_media", social_media)
    except ImportError:
        pass

    try:
        from actions.tiktok_analyzer import tiktok_analyzer
        agent.register("tiktok_analyzer", tiktok_analyzer)
    except ImportError:
        pass

    # ── Automatizaciones y recordatorios ─────────────────────────────────
    try:
        from actions.reminder import reminder
        agent.register("reminder", reminder)
    except ImportError:
        pass

    try:
        from actions.scheduler import scheduler
        agent.register("scheduler", scheduler)
    except ImportError:
        pass

    try:
        from actions.rules_engine import rules_engine
        agent.register("rules_engine", rules_engine)
    except ImportError:
        pass

    # ── Games ─────────────────────────────────────────────────────────────
    try:
        from actions.game_updater import game_updater
        agent.register("game_updater", game_updater)
    except ImportError:
        pass

    # ── Facturación ───────────────────────────────────────────────────────
    try:
        from actions.arca_invoice import arca_invoice
        agent.register("arca_invoice", arca_invoice)
    except ImportError:
        pass

    return agent


CloudAgent = _build_cloud_agent
