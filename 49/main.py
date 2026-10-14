# main.py
import customtkinter as ctk
import sys
import os

# --- INICIO CONFIGURACIÓN PYTHON PATH ---
# Este bloque es más robusto y asegura que la raíz del proyecto esté siempre en el path,
# sin importar desde dónde se ejecute el script.
project_root = os.path.dirname(os.path.abspath(__file__))
if project_root not in sys.path:
    sys.path.insert(0, project_root)
# --- FIN CONFIGURACIÓN PYTHON PATH ---

# Importamos nuestra aplicación personalizada
from gui.app import ProCheckerApp

# --- Punto de Entrada de la Aplicación ---
if __name__ == "__main__":
    # 1. Establecemos el modo de apariencia a "Dark". Esto es necesario.
    ctk.set_appearance_mode("Dark")
    
    # 2. NO establecemos un tema por defecto (como "dark-blue").
    #    Nuestra clase ProCheckerApp ya se encarga de definir todos los colores
    #    (negro y rojo) manualmente, así que no queremos que un tema por defecto
    #    interfiera con nuestra personalización.
    #    ctk.set_default_color_theme("dark-blue")  <-- ESTA LÍNEA SE ELIMINA

    # 3. Creamos y ejecutamos la aplicación
    app = ProCheckerApp()
    app.mainloop()