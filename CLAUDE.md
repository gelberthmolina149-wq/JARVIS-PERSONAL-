# JARVIS Personal — GEL

## Objetivo
Agente local tipo JARVIS para dropshipping (Angle Finder, Content Creator, NeoLogis).

## Rutas importantes
- Proyecto activo: `C:\Users\User\Documents\jarvis-personal`
- Proyecto referencia: `C:\Users\User\Documents\dexter-666-JARVIS-IA-v1.0.0-10-g8264008 (1)\dexter-666-JARVIS-IA-8264008`
- Punto de entrada: `main.py`
- Launcher: `Iniciar_JARVIS.bat`
- UI: `ui.py` (raíz) — NO usar `iu/ui.py`
- Config: `config/api_keys.json`
- Prompt: `core/prompt.txt`

## Stack
- Python 3.11
- PyQt6 + PyQt6-WebEngine
- Gemini API (google-genai)
- VOSK offline (config/vosk_model/)
- FAL.ai / Leonardo.ai (futuro)

## Arquitectura
- `main.py` — Manager central, loop de voz, herramientas Gemini
- `ui.py` — Interfaz PyQt6 con orb WebGL (sphere.html)
- `actions/` — 50+ módulos de herramientas
- `agent/task_queue.py` — Cola de tareas asíncronas
- `memory/` — Memoria a largo plazo + config_manager

## Estado actual (2026-06-16)
- Sincronizado con referencia: main.py, ui.py, assets, agent, 24 actions nuevas
- api_keys.json configurado con claves de GEL
- VOSK model instalado

## Reglas
- Proponer antes de ejecutar cambios grandes
- No usar admin
- No correr procesos en background innecesarios
- No tocar archivos marcados: .vbs raíz, .bat con admin, auto_programmer.py

## Archivos NO tocar
- `iu/ui.py` (versión parcial antigua, no se usa)
- `actions/auto_programmer.py` (no existe, no crear)

## Próximos pasos
1. Agregar agentes dropshipping: Angle Finder AI, NeoLogis, Content Creator
2. Personalizar core/prompt.txt para contexto de dropshipping
3. Adaptar widgets de UI para el flujo de trabajo de GEL
