import os
import sys
import subprocess
import shutil

def run_command(command, description):
    print(f"[*] {description}...")
    try:
        subprocess.check_call(command, shell=True)
        return True
    except subprocess.CalledProcessError as e:
        print(f"[!] Error: {e}")
        return False

def main():
    # 1. Obtener rutas dinámicas
    base_dir = os.path.dirname(os.path.abspath(__file__))
    venv_dir = os.path.join(base_dir, ".venv_gui")
    python_exe = os.path.join(venv_dir, "bin", "python3")
    pip_exe = os.path.join(venv_dir, "bin", "pip")
    requirements = os.path.join(base_dir, "requirements_GUI.txt")
    gui_script = os.path.join(base_dir, "gui_app.py")
    
    # Localizar el icono dentro del repositorio (portable)
    icon_path = os.path.join(base_dir, "IGP.jpg")
    if not os.path.exists(icon_path):
        # Fallback por si acaso
        icon_path = "utilities-terminal"

    print(f"--- 🛠️ Instalador Automático de JRO Uploader GUI ---")
    print(f"Carpeta del proyecto: {base_dir}")

    # 2. Crear entorno virtual si no existe
    if not os.path.exists(venv_dir):
        if not run_command(f"python3 -m venv {venv_dir}", "Creando entorno virtual .venv_gui"):
            return

    # 3. Instalar dependencias
    if os.path.exists(requirements):
        if not run_command(f"{pip_exe} install --upgrade pip", "Actualizando pip"):
            return
        if not run_command(f"{pip_exe} install -r {requirements}", "Instalando dependencias desde requirements_GUI.txt"):
            print("[!] Nota: Asegúrate de estar conectado a la Intranet del IGP para descargar jrodb.")
            return
    else:
        print(f"[!] Error: No se encontró {requirements}")
        return

    # 4. Crear el lanzador .desktop en el Escritorio del usuario actual
    desktop_path = os.path.join(os.path.expanduser("~"), "Desktop", "JRO_Uploader.desktop")
    
    desktop_entry = f"""[Desktop Entry]
Version=1.0
Type=Application
Name=JRO Uploader GUI
Comment=Gestión manual de datos JRO
Exec={python_exe} {gui_script}
Icon={icon_path if os.path.exists(icon_path) else 'utilities-terminal'}
Terminal=false
Categories=Application;Development;
"""

    try:
        with open(desktop_path, "w") as f:
            f.write(desktop_entry)
        os.chmod(desktop_path, 0o755)
        print(f"[*] Lanzador creado en: {desktop_path}")
        print("--- ✅ INSTALACIÓN COMPLETADA ---")
        print("IMPORTANTE: Ve a tu escritorio, haz clic derecho en el icono y selecciona 'Allow Launching'.")
    except Exception as e:
        print(f"[!] Error al crear el lanzador: {e}")

if __name__ == "__main__":
    main()
