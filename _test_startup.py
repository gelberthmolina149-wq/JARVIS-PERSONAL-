import sys
import os

print("=== VERIFICACION DE ARRANQUE DE JARVIS ===")

# Imprimir el interprete de Python actual
print(f"Interprete activo: {sys.executable}")

critical_modules = [
    "PyQt6",
    "PyQt6.QtCore",
    "PyQt6.QtWidgets",
    "PyQt6.QtWebEngineWidgets",
    "google.genai",
    "sounddevice",
    "pyautogui",
    "psutil",
    "vosk"
]

failed = []
for mod in critical_modules:
    try:
        __import__(mod)
        print(f"  [OK] Modulo '{mod}' importado con exito.")
    except Exception as e:
        print(f"  [FAIL] Error al importar '{mod}': {e}")
        failed.append(mod)

if failed:
    print(f"\n[FAIL] Faltan modulos criticos: {failed}")
    sys.exit(1)

# Probar la inicializacion de la aplicacion Qt en modo headless para evitar crashes de DLLs
try:
    from PyQt6.QtWidgets import QApplication
    # Inicializacion basica sin levantar ventana
    app = QApplication.instance()
    if not app:
        app = QApplication(["--platform", "offscreen"])
    print("  [OK] Inicializacion de QApplication exitosa.")
except Exception as e:
    print(f"  [FAIL] Error al inicializar QApplication: {e}")
    sys.exit(1)

print("\n=== [PASS] Todos los modulos y la inicializacion de Qt estan listos para arrancar! ===")
