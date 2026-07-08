import sys
import json
from pathlib import Path
import threading
from ui import JarvisUI
from PyQt6.QtCore import Qt

# Replicate main setup imports and calls
from main import _load_tz, API_CONFIG_PATH

def main():
    import ctypes
    _single_instance_mutex = ctypes.windll.kernel32.CreateMutexW(None, False, "JARVIS_AI_SINGLE_INSTANCE_MUTEX_DEBUG")
    
    _load_tz()
    
    # Ensure api config path exists or mock it
    cfg = {}
    if API_CONFIG_PATH.exists():
        try:
            cfg = json.loads(API_CONFIG_PATH.read_text(encoding="utf-8"))
        except:
            pass
    cfg["user_name"] = cfg.get("user_name", "Señor")
    
    ui = JarvisUI("face.png")
    
    # --- DEBUG VISIBLE WINDOW MODIFICATIONS ---
    print("[DEBUG VISUAL] Intercepting window properties for maximum high-contrast visibility...")
    if hasattr(ui, "_win"):
        # 1. Standard window borders, min/max buttons, close button (No frameless mode)
        ui._win.setWindowFlags(Qt.WindowType.Window | Qt.WindowType.WindowMinMaxButtonsHint | Qt.WindowType.WindowCloseButtonHint)
        
        # 2. Disable translucent background
        ui._win.setAttribute(Qt.WidgetAttribute.WA_TranslucentBackground, False)
        
        # 3. Solid background styling (High-contrast dark-blue with bright red border)
        ui._win.setStyleSheet("background-color: #0f172a !important; color: #f8fafc; border: 4px solid #ef4444;")
        
        # 4. Set opacity to 1.0 (Solid window)
        ui._win.setWindowOpacity(1.0)
        
        # 5. Clear title
        ui._win.setWindowTitle("DEBUG-JARVIS-HUD-VISIBLE")
        
        # 6. Apply flags and show
        ui._win.show()
        ui._win.raise_()
        ui._win.activateWindow()
        print("[DEBUG VISUAL] Window configured to standard, solid, topmost status.")
        
    print("[JARVIS VISUAL] Starting UI mainloop in DEBUG VISIBLE mode...")
    ui.root.mainloop()

if __name__ == "__main__":
    main()
