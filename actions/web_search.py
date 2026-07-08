"""
actions/web_search.py — Búsqueda web inteligente para JARVIS.

Estrategia en cascada:
  1. DuckDuckGo Instant Answer API (sin key, resultado directo)
  2. DuckDuckGo HTML scraping (resultados reales)
  3. Fallback: apertura del navegador con la búsqueda

Modos:
  search  → búsqueda estándar, retorna resumen + fuentes
  compare → tabla comparativa de ítems por aspecto (precio, specs, reviews)
"""
from __future__ import annotations
import json
import re
import urllib.parse
import webbrowser
from typing import Any

try:
    import requests
    _HAS_REQUESTS = True
except ImportError:
    _HAS_REQUESTS = False

_HEADERS = {
    "User-Agent": (
        "Mozilla/5.0 (Windows NT 10.0; Win64; x64) "
        "AppleWebKit/537.36 (KHTML, like Gecko) "
        "Chrome/124.0.0.0 Safari/537.36"
    ),
    "Accept-Language": "es-ES,es;q=0.9,en;q=0.8",
}

_MAX_RESULT_LEN = 1200  # Máximo de caracteres en la respuesta final


# ─── DuckDuckGo Instant Answer ────────────────────────────────────────────────

def _ddg_instant(query: str) -> str | None:
    """
    Consulta DuckDuckGo Instant Answer API.
    Retorna un resumen de texto si hay respuesta directa, None en otro caso.
    """
    try:
        url = "https://api.duckduckgo.com/"
        params = {
            "q": query,
            "format": "json",
            "no_html": "1",
            "skip_disambig": "1",
            "no_redirect": "1",
        }
        resp = requests.get(url, params=params, headers=_HEADERS, timeout=6)
        data = resp.json()

        abstract = data.get("AbstractText", "").strip()
        answer   = data.get("Answer", "").strip()
        definition = data.get("Definition", "").strip()

        if answer:
            return answer[:_MAX_RESULT_LEN]
        if abstract:
            return abstract[:_MAX_RESULT_LEN]
        if definition:
            return definition[:_MAX_RESULT_LEN]

        # Resultados relacionados
        related = data.get("RelatedTopics", [])
        snippets = []
        for item in related[:4]:
            if isinstance(item, dict) and item.get("Text"):
                snippets.append(item["Text"])
        if snippets:
            return " | ".join(snippets)[:_MAX_RESULT_LEN]

    except Exception:
        pass
    return None


# ─── DuckDuckGo HTML scraping ─────────────────────────────────────────────────

def _ddg_html(query: str, max_results: int = 5) -> list[dict]:
    """
    Scraping básico de resultados HTML de DuckDuckGo.
    Retorna lista de {title, snippet, url}.
    """
    results = []
    try:
        url = "https://html.duckduckgo.com/html/"
        params = {"q": query, "kl": "es-es"}
        resp = requests.post(url, data=params, headers=_HEADERS, timeout=8)
        html = resp.text

        # Extraer bloques de resultados con regex básico
        # Título
        titles   = re.findall(r'class="result__title"[^>]*>.*?<a[^>]*>(.*?)</a>', html, re.DOTALL)
        snippets = re.findall(r'class="result__snippet"[^>]*>(.*?)</span>', html, re.DOTALL)
        urls     = re.findall(r'class="result__url"[^>]*>(.*?)</a>', html, re.DOTALL)

        # Limpiar HTML tags
        def strip_tags(s: str) -> str:
            return re.sub(r'<[^>]+>', '', s).strip()

        for i in range(min(max_results, len(titles), len(snippets))):
            title   = strip_tags(titles[i])[:120]
            snippet = strip_tags(snippets[i])[:300]
            url_    = strip_tags(urls[i]).strip() if i < len(urls) else ""
            if title and snippet:
                results.append({"title": title, "snippet": snippet, "url": url_})

    except Exception:
        pass
    return results


# ─── Búsqueda estándar ────────────────────────────────────────────────────────

def _do_search(query: str, player: Any = None) -> str:
    """Ejecuta búsqueda y retorna un texto listo para verbalizar."""

    def log(msg: str):
        if player:
            try:
                player.write_log(msg)
            except Exception:
                pass

    log(f"🔍 Buscando: {query}")

    # 1. Instant Answer (respuesta directa)
    instant = _ddg_instant(query)
    if instant and len(instant) > 40:
        log(f"⚡ Respuesta directa: {instant[:80]}...")
        return instant

    # 2. Resultados HTML
    results = _ddg_html(query, max_results=4)
    if results:
        log(f"📄 {len(results)} resultados encontrados")
        parts = []
        for i, r in enumerate(results, 1):
            parts.append(f"{i}. {r['title']}: {r['snippet']}")
        summary = "\n".join(parts)
        if len(summary) > _MAX_RESULT_LEN:
            summary = summary[:_MAX_RESULT_LEN] + "..."
        return f"Resultados para '{query}':\n{summary}"

    # 3. Fallback: abrir el navegador
    log("🌐 Abriendo navegador como fallback")
    search_url = f"https://www.google.com/search?q={urllib.parse.quote(query)}"
    try:
        webbrowser.open(search_url)
    except Exception:
        pass
    return f"No pude obtener resultados directos para '{query}'. Abrí Google en el navegador con esa búsqueda."


# ─── Modo comparación ─────────────────────────────────────────────────────────

def _do_compare(items: list[str], aspect: str, player: Any = None) -> str:
    """Compara una lista de ítems en un aspecto específico."""
    if not items:
        return "No especificaste qué comparar."

    aspect = aspect or "características"
    results = []

    for item in items[:4]:  # Máximo 4 ítems para no saturar
        query = f"{item} {aspect}"
        snippet = _ddg_instant(query)
        if not snippet:
            html_results = _ddg_html(query, max_results=1)
            snippet = html_results[0]["snippet"] if html_results else "Sin información"
        results.append(f"• {item}: {snippet[:200]}")

    if not results:
        return f"No pude comparar los ítems solicitados por '{aspect}'."

    header = f"Comparación por {aspect}:\n"
    return header + "\n".join(results)


# ─── Función principal ────────────────────────────────────────────────────────

def web_search(parameters: dict, player: Any = None, speak=None) -> str:
    """
    Realiza búsquedas web usando DuckDuckGo.

    Args:
        parameters: dict con:
            - query  (str): término de búsqueda
            - mode   (str): 'search' (default) | 'compare'
            - items  (list): para mode='compare', lista de ítems a comparar
            - aspect (str): para mode='compare', aspecto de comparación
        player: JarvisUI (para write_log).
        speak: función TTS (opcional).

    Returns:
        Resultado en texto listo para que Gemini lo verbalice.
    """
    if not _HAS_REQUESTS:
        query = parameters.get("query", "")
        url = f"https://www.google.com/search?q={urllib.parse.quote(query)}"
        try:
            webbrowser.open(url)
        except Exception:
            pass
        return f"El módulo 'requests' no está disponible. Abrí Google con '{query}'."

    mode:   str       = parameters.get("mode", "search").lower().strip()
    query:  str       = parameters.get("query", "").strip()
    items:  list[str] = parameters.get("items", [])
    aspect: str       = parameters.get("aspect", "comparación").strip()

    if not query and not items:
        return "No especificaste qué buscar, señor."

    if mode == "compare" and items:
        return _do_compare(items, aspect, player)

    if not query and items:
        query = " vs ".join(items)

    return _do_search(query, player)
