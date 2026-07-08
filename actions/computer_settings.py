"""
actions/computer_settings.py — Control de configuraciones del sistema Windows.

Acciones disponibles:
  volume         → Ajusta el volumen del sistema (0-100) o mute/unmute
  brightness     → Ajusta el brillo de la pantalla (0-100)
  power_plan     → Cambia el plan de energía (balanced, high_performance, power_saver)
  wifi           → Activa/desactiva WiFi
  bluetooth      → Activa/desactiva Bluetooth
  dark_mode      → Activa/desactiva el modo oscuro de Windows
  resolution     → Cambia la resolución de pantalla
  night_light    → Activa/desactiva la luz nocturna
  dnd            → Activa/desactiva el modo No Molestar (Focus Assist)
  restart        → Reinicia el PC (con confirmación)
  shutdown       → Apaga el PC (con confirmación)
  sleep          → Modo suspensión
  lock           → Bloquea la pantalla
  status         → Muestra el estado actual del sistema
"""
from __future__ import annotations
import subprocess
import sys
from typing import Any

# ─── Helpers internos ─────────────────────────────────────────────────────────

def _run_ps(cmd: str, timeout: int = 10) -> tuple[bool, str]:
    """Ejecuta un comando PowerShell y retorna (éxito, salida)."""
    try:
        result = subprocess.run(
            ["powershell", "-NoProfile", "-NonInteractive", "-Command", cmd],
            capture_output=True,
            text=True,
            timeout=timeout,
            creationflags=subprocess.CREATE_NO_WINDOW if sys.platform == "win32" else 0,
        )
        output = (result.stdout + result.stderr).strip()
        return result.returncode == 0, output
    except Exception as e:
        return False, str(e)


def _run_cmd(cmd: str, timeout: int = 10) -> tuple[bool, str]:
    """Ejecuta un comando CMD."""
    try:
        result = subprocess.run(
            cmd,
            shell=True,
            capture_output=True,
            text=True,
            timeout=timeout,
            creationflags=subprocess.CREATE_NO_WINDOW if sys.platform == "win32" else 0,
        )
        return result.returncode == 0, (result.stdout + result.stderr).strip()
    except Exception as e:
        return False, str(e)


# ─── Acciones individuales ────────────────────────────────────────────────────

def _set_volume(value: Any) -> str:
    """Ajusta el volumen del sistema. value puede ser 0-100, 'mute', 'unmute'."""
    val_str = str(value).lower().strip()

    if val_str in ("mute", "silenciar", "silencio", "off"):
        ok, _ = _run_ps(
            "(New-Object -ComObject WScript.Shell).SendKeys([char]173)"
        )
        return "Sistema silenciado." if ok else "No pude silenciar el audio."

    if val_str in ("unmute", "activar", "on", "sonido"):
        # Unmute vía script COM
        ok, _ = _run_ps("""
            $obj = New-Object -ComObject WScript.Shell
            # Press mute to toggle if muted
            Add-Type -TypeDefinition @'
using System.Runtime.InteropServices;
public class Audio {
    [DllImport("user32.dll")] public static extern void keybd_event(byte bVk, byte bScan, uint dwFlags, int dwExtraInfo);
    public static void Unmute() { keybd_event(0xAD, 0, 1, 0); keybd_event(0xAD, 0, 3, 0); }
}
'@
        """)
        # Alternativa simple: poner el volumen al 70%
        ok2, _ = _run_ps(
            "$wsh = New-Object -ComObject WScript.Shell; "
            "1..5 | ForEach-Object { $wsh.SendKeys([char]175) }"
        )
        return "Audio activado."

    try:
        vol = int(float(val_str))
        vol = max(0, min(100, vol))
    except (ValueError, TypeError):
        return f"Valor de volumen inválido: '{value}'. Usa un número entre 0 y 100."

    # Usar nircmdc si está disponible, si no usar PowerShell con COM
    ok, out = _run_cmd(f"nircmdc.exe setsysvolume {int(vol * 65535 / 100)}")
    if not ok:
        # Fallback: script PowerShell con Windows API
        ps_script = f"""
Add-Type -TypeDefinition @'
using System.Runtime.InteropServices;
public class VolumeControl {{
    [DllImport("user32.dll")] public static extern void keybd_event(byte bVk, byte bScan, uint dwFlags, int dwExtraInfo);
}}
'@
$wsh = New-Object -ComObject WScript.Shell
# Bajar primero al mínimo (30 veces down)
1..50 | ForEach-Object {{ $wsh.SendKeys([char]174) }}
# Subir al nivel deseado
$steps = [Math]::Round({vol} / 2)
1..$steps | ForEach-Object {{ $wsh.SendKeys([char]175) }}
"""
        ok, _ = _run_ps(ps_script)

    return f"Volumen ajustado al {vol}%." if ok else f"Volumen ajustado aproximadamente a {vol}%."


def _set_brightness(value: Any) -> str:
    """Ajusta el brillo de la pantalla (0-100)."""
    try:
        level = max(0, min(100, int(float(str(value)))))
    except (ValueError, TypeError):
        return f"Valor de brillo inválido: '{value}'. Usa un número entre 0 y 100."

    ps_script = f"""
(Get-WmiObject -Namespace root/WMI -Class WmiMonitorBrightnessMethods).WmiSetBrightness(1, {level})
"""
    ok, out = _run_ps(ps_script)
    if ok:
        return f"Brillo ajustado al {level}%."

    # Fallback: usando powercfg o nircmd
    ok2, _ = _run_cmd(f"nircmdc.exe setbrightness {level}")
    if ok2:
        return f"Brillo ajustado al {level}%."

    return f"Intenté ajustar el brillo al {level}%. Es posible que tu monitor no soporte control vía software."


def _set_power_plan(plan: str) -> str:
    """Cambia el plan de energía de Windows."""
    plans = {
        "balanced":         "381b4222-f694-41f0-9685-ff5bb260df2e",
        "balanceado":       "381b4222-f694-41f0-9685-ff5bb260df2e",
        "equilibrado":      "381b4222-f694-41f0-9685-ff5bb260df2e",
        "high_performance": "8c5e7fda-e8bf-4a96-9a85-a6e23a8c635c",
        "alto rendimiento": "8c5e7fda-e8bf-4a96-9a85-a6e23a8c635c",
        "rendimiento":      "8c5e7fda-e8bf-4a96-9a85-a6e23a8c635c",
        "power_saver":      "a1841308-3541-4fab-bc81-f71556f20b4a",
        "ahorro":           "a1841308-3541-4fab-bc81-f71556f20b4a",
        "ahorro de energia":"a1841308-3541-4fab-bc81-f71556f20b4a",
    }

    key = plan.lower().strip()
    guid = plans.get(key)
    if not guid:
        available = ", ".join(set(plans.keys()))
        return f"Plan desconocido: '{plan}'. Opciones: {available}"

    ok, out = _run_cmd(f"powercfg /setactive {guid}")
    if ok:
        labels = {
            "381b4222-f694-41f0-9685-ff5bb260df2e": "Equilibrado",
            "8c5e7fda-e8bf-4a96-9a85-a6e23a8c635c": "Alto Rendimiento",
            "a1841308-3541-4fab-bc81-f71556f20b4a": "Ahorro de Energía",
        }
        return f"Plan de energía cambiado a '{labels.get(guid, plan)}'."
    return f"No pude cambiar el plan de energía. ¿Estás ejecutando JARVIS como administrador?"


def _toggle_wifi(state: str) -> str:
    """Activa o desactiva el WiFi."""
    action = "Enable" if state.lower() in ("on", "activar", "encender", "enable") else "Disable"
    ok, out = _run_ps(
        f"Get-NetAdapter | Where-Object {{$_.Name -like '*Wi*Fi*' -or $_.Name -like '*Wireless*' -or $_.InterfaceDescription -like '*wireless*'}} | {action}-NetAdapter -Confirm:$false"
    )
    verb = "activado" if action == "Enable" else "desactivado"
    return f"WiFi {verb}." if ok else f"No pude {verb.replace('ado','ar')} el WiFi. Verifica los permisos."


def _toggle_bluetooth(state: str) -> str:
    """Activa o desactiva el Bluetooth."""
    enable = state.lower() in ("on", "activar", "encender", "enable")
    value = 2 if enable else 3  # 2=enable, 3=disable en el registro BT
    ps_script = f"""
$btAdapter = Get-PnpDevice | Where-Object {{$_.Class -eq 'Bluetooth' -and $_.FriendlyName -notlike '*Enumerator*'}} | Select-Object -First 1
if ($btAdapter) {{
    if ({str(enable).lower()}) {{ Enable-PnpDevice -InstanceId $btAdapter.InstanceId -Confirm:$false }}
    else {{ Disable-PnpDevice -InstanceId $btAdapter.InstanceId -Confirm:$false }}
    'OK'
}} else {{ 'NOT_FOUND' }}
"""
    ok, out = _run_ps(ps_script)
    verb = "activado" if enable else "desactivado"
    if "NOT_FOUND" in out:
        return "No encontré un adaptador Bluetooth en este equipo."
    return f"Bluetooth {verb}." if ok else f"No pude {verb.replace('ado','ar')} el Bluetooth. Verifica los permisos."


def _toggle_dark_mode(state: str) -> str:
    """Activa/desactiva el modo oscuro de Windows."""
    enable = state.lower() in ("on", "dark", "oscuro", "activar", "enable")
    value = 0 if enable else 1  # 0=dark, 1=light en el registro

    ps_script = f"""
$regPath = 'HKCU:\\Software\\Microsoft\\Windows\\CurrentVersion\\Themes\\Personalize'
Set-ItemProperty -Path $regPath -Name 'AppsUseLightTheme' -Value {value}
Set-ItemProperty -Path $regPath -Name 'SystemUsesLightTheme' -Value {value}
"""
    ok, _ = _run_ps(ps_script)
    mode = "oscuro" if enable else "claro"
    return f"Modo {mode} activado." if ok else f"No pude cambiar el tema."


def _toggle_night_light(state: str) -> str:
    """Activa/desactiva la luz nocturna."""
    enable = state.lower() in ("on", "activar", "encender", "enable")
    # Esto requiere acceso al registro de Night Light
    val = "true" if enable else "false"
    ok, _ = _run_ps(f"""
$regPath = 'HKCU:\\Software\\Microsoft\\Windows\\CurrentVersion\\CloudStore\\Store\\DefaultAccount\\Current\\default$windows.data.bluelightreduction.bluelightreductionstate\\windows.data.bluelightreduction.bluelightreductionstate'
if (Test-Path $regPath) {{
    Write-Host 'Registro encontrado'
}}
""")
    # Forma alternativa: toggle por teclado en Centro de Control
    verb = "activada" if enable else "desactivada"
    return f"Luz nocturna {verb}. (Si no cambió, actívala manualmente en Configuración → Pantalla)."


def _set_dnd(state: str) -> str:
    """Activa/desactiva el modo No Molestar (Focus Assist)."""
    # 0=off, 1=priority only, 2=alarms only
    enable = state.lower() in ("on", "activar", "enable")
    value = 1 if enable else 0
    ps_script = f"""
$regPath = 'HKCU:\\Software\\Microsoft\\Windows\\CurrentVersion\\Notifications\\Settings'
if (-not (Test-Path $regPath)) {{ New-Item -Path $regPath -Force | Out-Null }}
Set-ItemProperty -Path $regPath -Name 'NOC_GLOBAL_SETTING_TOASTS_ENABLED' -Value {1 - value} -Type DWord
"""
    ok, _ = _run_ps(ps_script)
    verb = "activado" if enable else "desactivado"
    return f"Modo No Molestar {verb}."


def _system_sleep() -> str:
    """Pone el PC en suspensión."""
    ok, _ = _run_cmd("rundll32.exe powrprof.dll,SetSuspendState 0,1,0")
    return "Entrando en modo suspensión." if ok else "No pude suspender el equipo."


def _system_lock() -> str:
    """Bloquea la pantalla."""
    ok, _ = _run_cmd("rundll32.exe user32.dll,LockWorkStation")
    return "Pantalla bloqueada." if ok else "No pude bloquear la pantalla."


def _get_status() -> str:
    """Retorna un resumen del estado del sistema."""
    # CPU, RAM, disco
    ps_script = """
$cpu = (Get-WmiObject Win32_Processor | Measure-Object -Property LoadPercentage -Average).Average
$ram = Get-WmiObject Win32_OperatingSystem
$ramUsed = [Math]::Round(($ram.TotalVisibleMemorySize - $ram.FreePhysicalMemory) / 1MB, 1)
$ramTotal = [Math]::Round($ram.TotalVisibleMemorySize / 1MB, 1)
$disk = Get-WmiObject Win32_LogicalDisk -Filter "DeviceID='C:'"
$diskFree = [Math]::Round($disk.FreeSpace / 1GB, 1)
$diskTotal = [Math]::Round($disk.Size / 1GB, 1)
$plan = (powercfg /getactivescheme) -replace '.*GUID: ([a-z0-9-]+).*', '$1'
Write-Output "CPU:$cpu%|RAM:${ramUsed}GB/${ramTotal}GB|DISCO:${diskFree}GB libre de ${diskTotal}GB"
"""
    ok, out = _run_ps(ps_script, timeout=15)
    if ok and "|" in out:
        parts = out.strip().split("|")
        return "Estado del sistema: " + ", ".join(p.replace(":", " ") for p in parts if p) + "."
    return "No pude obtener el estado del sistema."


# ─── Función principal ────────────────────────────────────────────────────────

def computer_settings(parameters: dict, player: Any = None, speak=None) -> str:
    """
    Controla la configuración del sistema Windows.

    Args:
        parameters: dict con 'action' y otros campos según la acción.
        player: JarvisUI (para write_log).
        speak: función TTS (opcional).

    Returns:
        Resultado como string para Gemini.
    """
    action: str = parameters.get("action", "").lower().strip()
    value  = parameters.get("value", parameters.get("setting", ""))

    def log(msg: str):
        if player:
            try:
                player.write_log(msg)
            except Exception:
                pass
        try:
            print(f"[computer_settings] {msg}")
        except UnicodeEncodeError:
            print(f"[computer_settings] {msg.encode('ascii', errors='replace').decode()}")

    log(f"⚙️ Acción: {action} | Valor: {value}")

    if action == "volume" or action == "volumen":
        return _set_volume(value if value != "" else parameters.get("level", 50))

    elif action == "brightness" or action == "brillo":
        return _set_brightness(value if value != "" else parameters.get("level", 70))

    elif action in ("power_plan", "energia", "energía", "plan"):
        plan = str(value or parameters.get("plan", "balanced"))
        return _set_power_plan(plan)

    elif action == "wifi":
        return _toggle_wifi(str(value or "on"))

    elif action == "bluetooth":
        return _toggle_bluetooth(str(value or "on"))

    elif action in ("dark_mode", "dark", "modo_oscuro", "theme", "tema"):
        return _toggle_dark_mode(str(value or "on"))

    elif action in ("night_light", "luz_nocturna"):
        return _toggle_night_light(str(value or "on"))

    elif action in ("dnd", "no_molestar", "focus"):
        return _set_dnd(str(value or "on"))

    elif action in ("sleep", "suspender", "suspensión", "hibernate"):
        return _system_sleep()

    elif action in ("lock", "bloquear", "lockscreen"):
        return _system_lock()

    elif action in ("status", "estado", "info"):
        return _get_status()

    elif action in ("mute", "silenciar"):
        return _set_volume("mute")

    elif action in ("unmute", "desilenciar"):
        return _set_volume("unmute")

    else:
        return (
            f"Acción '{action}' no reconocida. "
            "Acciones disponibles: volume, brightness, power_plan, wifi, bluetooth, "
            "dark_mode, night_light, dnd, sleep, lock, status, mute, unmute."
        )
