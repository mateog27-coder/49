# gui/app.py
import customtkinter as ctk
import threading
import time
import random
import string
import sys
import os
import json
from typing import List

# ---	INICIO CONFIGURACIÓN	PYTHON-PATH	---
# Este bloque asegura que Python pueda encontrar los módulos del proyecto sin importar cómo se ejecute.
project_root = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
if project_root not in sys.path:
    sys.path.insert(0, project_root)
# ---	FIN CONFIGURACIÓN	PYTHON-PATH	---

# --- Importaciones UNIFICADAS del Proyecto 49 (AHORA ABSOLUTAS) ---
# ¡OJO! Ya no usamos '..' aquí. Usamos importaciones absolutas desde la raíz del proyecto.
from core.generator import CreditCardGenerator
from core.domain.card import Card
from core.test_results import TestStatus
from core.checkers.eneba_checker import EnebaChecker
from core.services.card_validator_service import CardValidatorService
# --- CONFIGURACIÓN DE TEMA HACKER 3.0 (EVOLUCIONADO) ---
ctk.set_appearance_mode("Dark")
# Paleta refinada según la crítica. Menos rojo, más contraste y jerarquía.
COLORS = {
    "bg_main": "#0d0d0d",
    "bg_sidebar": "#121212",
    "bg_card": "#1a1a1a",
    "bg_input": "#252525",
    "border": "#2a2a2a", # Bordes más sutiles
    "border_focus": "#ff4d4d", # Rojo solo para focus/hover
    "text_primary": "#ffffff",
    "text_secondary": "#a0a0a0",
    "text_accent": "#ff4d4d", # Rojo para acentos
    "button_bg": "#2a2a2a",
    "button_hover": "#3a3a3a",
    "success": "#00ff41",
    "warning": "#ffa500",
    "error": "#ff4d4d",
}

class ProCheckerApp(ctk.CTk):
    def __init__(self):
        super().__init__()
        self.cards_to_validate: List[Card] = []
        self.generator = None
        self.validator_service = None
        self.is_running = False
        self.stored_cookies = {}
        self.activity_log = [] # Log de actividad para el dashboard

        # --- Configuración de la Ventana Principal ---
        self.title("PROJECT 49 - PRO CHECKER")
        self.geometry("1500x850")
        self.minsize(1200, 700)
        self.grid_columnconfigure(1, weight=1)
        self.grid_rowconfigure(0, weight=1)
        self.configure(fg_color=COLORS["bg_main"])

        # --- BARRA LATERAL IZQUIERDA (NAVBAR) ---
        self.sidebar_frame = ctk.CTkFrame(self, width=250, corner_radius=0, fg_color=COLORS["bg_sidebar"], border_width=1, border_color=COLORS["border"])
        self.sidebar_frame.grid(row=0, column=0, sticky="nsew")
        self.sidebar_frame.grid_rowconfigure(10, weight=1)

        # Logo y título con identidad mejorada
        self.logo_label = ctk.CTkLabel(self.sidebar_frame, text="◈", font=ctk.CTkFont(size=60, family="Consolas"), text_color=COLORS["text_accent"])
        self.logo_label.grid(row=0, column=0, padx=20, pady=(30, 10))
        self.title_label = ctk.CTkLabel(self.sidebar_frame, text="PROJECT\n49", font=ctk.CTkFont(size=28, weight="bold", family="Consolas"), text_color=COLORS["text_primary"])
        self.title_label.grid(row=1, column=0, padx=20, pady=(0, 20))

        # Barra separadora
        ctk.CTkFrame(self.sidebar_frame, height=1, fg_color=COLORS["border"]).grid(row=2, column=0, padx=20, pady=(0, 20), sticky="ew")

        # Botones de navegación con estados visuales
        self.nav_buttons = {}
        buttons_data = [
            ("dashboard", "▦ DASHBOARD", "Vista general del sistema."),
            ("generator", "⚡ GENERATOR", "Generar lotes de tarjetas."),
            ("validator", "◉ VALIDATOR", "Probar lotes de tarjetas."),
            ("results", "▤ RESULTS", "Ver resultados de la prueba."),
            ("settings", "⚙ SETTINGS", "Configuración y Cookies."),
        ]
        for i, (key, text, tooltip) in enumerate(buttons_data):
            btn = ctk.CTkButton(self.sidebar_frame, text=text, command=lambda k=key: self.switch_view(k), 
                                fg_color="transparent", text_color=COLORS["text_secondary"], 
                                hover_color=COLORS["bg_card"], border_width=1, border_color=COLORS["bg_sidebar"], # Corregido aquí
                                font=ctk.CTkFont(family="Consolas"), corner_radius=0)
            btn.grid(row=i + 4, column=0, padx=20, pady=(5, 0), sticky="ew")
            self.nav_buttons[key] = btn

        # --- PANEL PRINCIPAL DERECHO ---
        self.main_frame = ctk.CTkFrame(self, fg_color=COLORS["bg_main"], border_width=1, border_color=COLORS["border"])
        self.main_frame.grid(row=0, column=1, sticky="nsew", padx=20, pady=20)

        # --- Área de Contenido Dinámico ---
        self.content_frame = ctk.CTkFrame(self.main_frame, fg_color=COLORS["bg_main"])
        self.content_frame.grid(row=0, column=0, sticky="nsew")
        self.content_frame.grid_columnconfigure(0, weight=1)
        self.content_frame.grid_rowconfigure(2, weight=1)

        self.switch_view("dashboard") # Vista inicial ahora es el Dashboard

    def log_activity(self, action: str):
        """Añade una acción al log de actividad del dashboard."""
        timestamp = time.strftime("%H:%M")
        self.activity_log.append(f"{timestamp} {action}")
        if len(self.activity_log) > 20: # Mantiene el log corto
            self.activity_log.pop(0)
        # Verificación de existencia ANTES de intentar actualizar el widget
        if hasattr(self, 'activity_log_display') and self.activity_log_display.winfo_exists():
            self._update_activity_log_display()

    def _update_activity_log_display(self):
        # Verificación doble para evitar el error si el widget se destruye mid-actualización
        if not hasattr(self, 'activity_log_display') or not self.activity_log_display.winfo_exists():
            return
        self.activity_log_display.delete("1.0", "end")
        for log_entry in self.activity_log:
            self.activity_log_display.insert("end", log_entry + "\n")
        self.activity_log_display.configure(state="disabled")

# --- LÓGICA DE VISTAS Y NAVEGACIÓN ---
    def clear_content(self):
        for widget in self.content_frame.winfo_children():
            widget.destroy()

    def switch_view(self, view_name: str):
        # Resetear estilos de botones
        for btn in self.nav_buttons.values():
            btn.configure(fg_color="transparent", text_color=COLORS["text_secondary"], border_color=COLORS["bg_sidebar"])

        # Estilo del botón activo
        if view_name in self.nav_buttons:
            self.nav_buttons[view_name].configure(fg_color=COLORS["bg_card"], text_color=COLORS["text_accent"], border_color=COLORS["text_accent"])

        self.clear_content()

        if view_name == "dashboard":
            self.show_dashboard()
        elif view_name == "generator":
            self.show_generator()
        elif view_name == "validator":
            self.show_validator()
        elif view_name == "results":
            self.show_results()
        elif view_name == "settings":
            self.show_settings()

    def _create_styled_entry(self, parent):
        entry = ctk.CTkEntry(parent, fg_color=COLORS["bg_input"], border_color=COLORS["border"], text_color=COLORS["text_primary"], font=ctk.CTkFont(family="Consolas"))
        return entry

    def _create_styled_button(self, parent, text, command, color=COLORS["button_bg"], hover_color=COLORS["button_hover"]):
        btn = ctk.CTkButton(parent, text=text, command=command, fg_color=color, hover_color=hover_color, text_color=COLORS["text_primary"], border_color=COLORS["border"], font=ctk.CTkFont(family="Consolas", weight="bold"))
        return btn

    def _create_stat_card(self, parent, title: str, value: str, color: str):
        """Crea una tarjeta de estadística para el dashboard."""
        card = ctk.CTkFrame(parent, fg_color=COLORS["bg_card"], border_width=1, border_color=COLORS["border"])
        card.pack(fill="both", expand=True, padx=5)
        
        ctk.CTkLabel(card, text=title, font=ctk.CTkFont(family="Consolas"), text_color=COLORS["text_secondary"]).pack(pady=(10, 0))
        ctk.CTkLabel(card, text=value, font=ctk.CTkFont(size=24, weight="bold", family="Consolas"), text_color=color).pack(pady=(5, 10))
        return card

    def show_dashboard(self):
        self.log_activity("Dashboard accessed")
        # Título
        title = ctk.CTkLabel(self.content_frame, text="▦ DASHBOARD", font=ctk.CTkFont(size=28, weight="bold", family="Consolas"), text_color=COLORS["text_accent"])
        title.grid(row=0, column=0, sticky="w", padx=20, pady=(30, 20))

        # Contenedor principal para el dashboard
        main_container = ctk.CTkFrame(self.content_frame, fg_color="transparent")
        main_container.grid(row=1, column=0, padx=20, pady=10, sticky="nsew")
        main_container.grid_columnconfigure(0, weight=1)
        main_container.grid_columnconfigure(1, weight=1)
        main_container.grid_columnconfigure(2, weight=1)
        main_container.grid_rowconfigure(0, weight=1)
        main_container.grid_rowconfigure(1, weight=1)

        # Tarjetas de estadísticas
        stats_frame = ctk.CTkFrame(main_container, fg_color="transparent")
        stats_frame.grid(row=0, column=0, columnspan=3, sticky="ew", pady=(0, 20))
        
        self._create_stat_card(stats_frame, "TOTAL CARDS", str(len(self.cards_to_validate)), COLORS["text_secondary"]).pack(side="left", expand=True, fill="both")
        self._create_stat_card(stats_frame, "PROCESSED", "0", COLORS["success"]).pack(side="left", expand=True, fill="both")
        self._create_stat_card(stats_frame, "ERRORS", "0", COLORS["error"]).pack(side="left", expand=True, fill="both")
        
        # Panel de actividad
        activity_frame = ctk.CTkFrame(main_container, fg_color=COLORS["bg_card"], border_width=1, border_color=COLORS["border"])
        activity_frame.grid(row=1, column=0, columnspan=2, sticky="nsew", padx=(0, 10), pady=10)
        ctk.CTkLabel(activity_frame, text="ACTIVITY", font=ctk.CTkFont(family="Consolas"), text_color=COLORS["text_secondary"]).pack(pady=(10, 5), anchor="w", padx=10)
        self.activity_log_display = ctk.CTkTextbox(activity_frame, fg_color=COLORS["bg_input"], text_color=COLORS["text_primary"], font=ctk.CTkFont(family="Consolas"))
        self.activity_log_display.pack(fill="both", expand=True, padx=10, pady=(0, 10))
        self._update_activity_log_display()

        # Panel de estado del sistema
        status_frame = ctk.CTkFrame(main_container, fg_color=COLORS["bg_card"], border_width=1, border_color=COLORS["border"])
        status_frame.grid(row=1, column=2, sticky="nsew", padx=(10, 0), pady=10)
        ctk.CTkLabel(status_frame, text="SYSTEM STATUS", font=ctk.CTkFont(family="Consolas"), text_color=COLORS["text_secondary"]).pack(pady=(10, 5), anchor="w", padx=10)
        
        status_items = [
            ("● Engine", "ONLINE", COLORS["success"]),
            ("● Database", "READY", COLORS["success"]),
            ("● Interface", "READY", COLORS["success"]),
        ]
        for item, status, color in status_items:
            item_frame = ctk.CTkFrame(status_frame, fg_color="transparent")
            item_frame.pack(fill="x", padx=10, pady=2)
            ctk.CTkLabel(item_frame, text=item, font=ctk.CTkFont(family="Consolas"), text_color=COLORS["text_secondary"]).pack(side="left")
            ctk.CTkLabel(item_frame, text=status, font=ctk.CTkFont(family="Consolas"), text_color=color).pack(side="right")

    def _update_activity_log_display(self):
        self.activity_log_display.delete("1.0", "end")
        for log_entry in self.activity_log:
            self.activity_log_display.insert("end", log_entry + "\n")
        self.activity_log_display.configure(state="disabled")

    def show_generator(self):
        self.log_activity("Generator accessed")
        # Título con subtítulo
        title_frame = ctk.CTkFrame(self.content_frame, fg_color="transparent")
        title_frame.grid(row=0, column=0, sticky="w", padx=20, pady=(30, 20))
        ctk.CTkLabel(title_frame, text="⚡ CARD GENERATOR", font=ctk.CTkFont(size=28, weight="bold", family="Consolas"), text_color=COLORS["text_accent"]).pack(anchor="w")
        ctk.CTkLabel(title_frame, text="Generate test data for local validation", font=ctk.CTkFont(size=12, family="Consolas"), text_color=COLORS["text_secondary"]).pack(anchor="w")

        # Contenedor principal para evitar espacio vacío
        main_container = ctk.CTkFrame(self.content_frame, fg_color="transparent")
        main_container.grid(row=1, column=0, padx=20, pady=10, sticky="nsew")
        main_container.grid_columnconfigure(0, weight=1)
        main_container.grid_columnconfigure(1, weight=1)
        main_container.grid_rowconfigure(0, weight=1)

        # Panel de configuración (izquierda)
        config_frame = ctk.CTkFrame(main_container, fg_color=COLORS["bg_card"], border_width=1, border_color=COLORS["border"])
        config_frame.grid(row=0, column=0, sticky="nsew", padx=(0, 10), pady=10)
        config_frame.grid_columnconfigure(1, weight=1)
        
        ctk.CTkLabel(config_frame, text="CONFIGURATION", font=ctk.CTkFont(size=16, weight="bold", family="Consolas"), text_color=COLORS["text_accent"]).grid(row=0, column=0, columnspan=2, sticky="w", padx=20, pady=10)
        
        ctk.CTkLabel(config_frame, text="BIN (6 dígitos):", font=ctk.CTkFont(family="Consolas"), text_color=COLORS["text_secondary"]).grid(row=1, column=0, sticky="w", padx=20, pady=10)
        self.bin_entry = self._create_styled_entry(config_frame)
        self.bin_entry.grid(row=1, column=1, padx=(10, 20), pady=10, sticky="ew")
        
        ctk.CTkLabel(config_frame, text="Mes Venc.:", font=ctk.CTkFont(family="Consolas"), text_color=COLORS["text_secondary"]).grid(row=2, column=0, sticky="w", padx=20, pady=(0, 10))
        self.month_combo = ctk.CTkComboBox(config_frame, values=[f"{i:02d}" for i in range(1, 13)], fg_color=COLORS["bg_input"], border_color=COLORS["border"], button_color=COLORS["button_bg"], text_color=COLORS["text_primary"], font=ctk.CTkFont(family="Consolas"))
        self.month_combo.grid(row=2, column=1, padx=(10, 20), pady=(0, 10), sticky="ew")
        self.month_combo.set("10")

        ctk.CTkLabel(config_frame, text="Rango Año Venc.:", font=ctk.CTkFont(family="Consolas"), text_color=COLORS["text_secondary"]).grid(row=3, column=0, sticky="w", padx=20, pady=(0, 10))
        year_range_frame = ctk.CTkFrame(config_frame, fg_color="transparent")
        year_range_frame.grid(row=3, column=1, columnspan=2, padx=(10, 20), pady=(0, 10), sticky="ew")
        
        self.year_start_combo = ctk.CTkComboBox(year_range_frame, values=[str(i) for i in range(2024, 2036)], fg_color=COLORS["bg_input"], border_color=COLORS["border"], button_color=COLORS["button_bg"], text_color=COLORS["text_primary"], font=ctk.CTkFont(family="Consolas"), width=100)
        self.year_start_combo.grid(row=0, column=0, padx=(0, 5))
        self.year_start_combo.set("2026")
        ctk.CTkLabel(year_range_frame, text=" a ", font=ctk.CTkFont(family="Consolas"), text_color=COLORS["text_secondary"]).grid(row=0, column=1, sticky="w", padx=5)
        self.year_end_combo = ctk.CTkComboBox(year_range_frame, values=[str(i) for i in range(2024, 2036)], fg_color=COLORS["bg_input"], border_color=COLORS["border"], button_color=COLORS["button_bg"], text_color=COLORS["text_primary"], font=ctk.CTkFont(family="Consolas"), width=100)
        self.year_end_combo.grid(row=0, column=2, padx=(5, 0))
        self.year_end_combo.set("2030")

        ctk.CTkLabel(config_frame, text="Cantidad:", font=ctk.CTkFont(family="Consolas"), text_color=COLORS["text_secondary"]).grid(row=4, column=0, sticky="w", padx=20, pady=(0, 10))
        self.amount_entry = self._create_styled_entry(config_frame)
        self.amount_entry.grid(row=4, column=1, padx=(10, 20), pady=(0, 10), sticky="ew")
        self.amount_entry.insert(0, "10")

        generate_btn = self._create_styled_button(config_frame, text="GENERAR LOTE", command=self.generate_cards, color=COLORS["text_accent"], hover_color=COLORS["border_focus"])
        generate_btn.grid(row=5, column=0, columnspan=2, pady=20, sticky="ew", padx=20)

        # Panel de preview (derecha)
        preview_frame = ctk.CTkFrame(main_container, fg_color=COLORS["bg_card"], border_width=1, border_color=COLORS["border"])
        preview_frame.grid(row=0, column=1, sticky="nsew", padx=(10, 0), pady=10)
        preview_frame.grid_columnconfigure(0, weight=1)
        preview_frame.grid_rowconfigure(1, weight=1)

        ctk.CTkLabel(preview_frame, text="GENERATION PREVIEW", font=ctk.CTkFont(size=16, weight="bold", family="Consolas"), text_color=COLORS["text_accent"]).grid(row=0, column=0, sticky="w", padx=20, pady=10)
        ctk.CTkLabel(preview_frame, text=f"Generated: {len(self.cards_to_validate)}", font=ctk.CTkFont(family="Consolas"), text_color=COLORS["success"]).grid(row=1, column=0, sticky="w", padx=20)
        ctk.CTkLabel(preview_frame, text="Status: READY", font=ctk.CTkFont(family="Consolas"), text_color=COLORS["success"]).grid(row=2, column=0, sticky="w", padx=20, pady=(0, 10))

        preview_data_frame = ctk.CTkScrollableFrame(preview_frame, fg_color=COLORS["bg_input"], border_width=1, border_color=COLORS["border"], label_text="TEST DATA PREVIEW")
        preview_data_frame.grid(row=3, column=0, sticky="nsew", padx=20, pady=(0, 20))
        
        # Mostrar datos de ejemplo si no hay tarjetas generadas
        if not self.cards_to_validate:
            ctk.CTkLabel(preview_data_frame, text="No cards generated yet.", font=ctk.CTkFont(family="Consolas"), text_color=COLORS["text_secondary"]).pack(pady=10)
        else:
            for card in self.cards_to_validate[:5]: # Muestra solo las 5 primeras
                ctk.CTkLabel(preview_data_frame, text=f"****-****-****-{card.number[-4:]}", font=ctk.CTkFont(family="Consolas"), text_color=COLORS["text_secondary"]).pack(anchor="w", padx=10, pady=2)


    def show_validator(self):
        self.log_activity("Validator accessed")
        title_frame = ctk.CTkFrame(self.content_frame, fg_color="transparent")
        title_frame.grid(row=0, column=0, sticky="w", padx=20, pady=(30, 20))
        ctk.CTkLabel(title_frame, text="◉ CARD VALIDATOR", font=ctk.CTkFont(size=28, weight="bold", family="Consolas"), text_color=COLORS["text_accent"]).pack(anchor="w")
        ctk.CTkLabel(title_frame, text="Validate card batches against multiple gateways", font=ctk.CTkFont(size=12, family="Consolas"), text_color=COLORS["text_secondary"]).pack(anchor="w")

        form_frame = ctk.CTkFrame(self.content_frame, fg_color=COLORS["bg_card"], border_width=1, border_color=COLORS["border"])
        form_frame.grid(row=1, column=0, padx=20, pady=10, sticky="ew")
        form_frame.grid_columnconfigure(1, weight=1)

        ctk.CTkLabel(form_frame, text="Gateway:", font=ctk.CTkFont(family="Consolas"), text_color=COLORS["text_secondary"]).grid(row=0, column=0, sticky="w", padx=20, pady=10)
        self.gateway_combo = ctk.CTkComboBox(form_frame, values=["Eneba (Stripe)", "Amazon"], fg_color=COLORS["bg_input"], border_color=COLORS["border"], button_color=COLORS["button_bg"], text_color=COLORS["text_primary"], font=ctk.CTkFont(family="Consolas"))
        self.gateway_combo.grid(row=0, column=1, padx=(10, 20), pady=10, sticky="ew")
        self.gateway_combo.set("Eneba (Stripe)")

        btn_frame = ctk.CTkFrame(form_frame, fg_color="transparent")
        btn_frame.grid(row=1, column=0, columnspan=2, pady=20, sticky="ew", padx=20)
        btn_frame.grid_columnconfigure((0, 1), weight=1)

        self.start_btn = self._create_styled_button(btn_frame, text="INICIAR", command=self.start_validation, color=COLORS["success"], hover_color="#00cc33")
        self.start_btn.grid(row=0, column=0, padx=5, sticky="ew")
        
        self.stop_btn = self._create_styled_button(btn_frame, text="PARAR", command=self.stop_validation, color=COLORS["error"], hover_color="#cc0000")
        self.stop_btn.grid(row=0, column=1, padx=5, sticky="ew")

        log_frame = ctk.CTkFrame(self.content_frame, fg_color=COLORS["bg_card"], border_width=1, border_color=COLORS["border"])
        log_frame.grid(row=2, column=0, padx=20, pady=(0, 20), sticky="nsew")
        log_frame.grid_columnconfigure(0, weight=1)
        log_frame.grid_rowconfigure(0, weight=1)
        
        ctk.CTkLabel(log_frame, text="LOGS:", font=ctk.CTkFont(size=16, weight="bold", family="Consolas"), text_color=COLORS["text_accent"]).grid(row=0, column=0, sticky="w", padx=10, pady=(10, 5))
        self.log_display = ctk.CTkTextbox(log_frame, wrap="word", fg_color=COLORS["bg_input"], text_color=COLORS["text_primary"], border_color=COLORS["border"], font=ctk.CTkFont(family="Consolas"))
        self.log_display.grid(row=1, column=0, sticky="nsew", padx=10, pady=(0, 10))
        self.update_log("System ready. Awaiting input...")

    def show_results(self):
        self.log_activity("Results accessed")
        title_frame = ctk.CTkFrame(self.content_frame, fg_color="transparent")
        title_frame.grid(row=0, column=0, sticky="w", padx=20, pady=(30, 20))
        ctk.CTkLabel(title_frame, text="▤ VALIDATION RESULTS", font=ctk.CTkFont(size=28, weight="bold", family="Consolas"), text_color=COLORS["text_accent"]).pack(anchor="w")
        ctk.CTkLabel(title_frame, text="Review the outcomes of your card validations", font=ctk.CTkFont(size=12, family="Consolas"), text_color=COLORS["text_secondary"]).pack(anchor="w")

        table_frame = ctk.CTkScrollableFrame(self.content_frame, fg_color=COLORS["bg_card"], border_width=1, border_color=COLORS["border"], label_text="PROCESSED CARDS", label_font=ctk.CTkFont(family="Consolas"))
        table_frame.grid(row=1, column=0, padx=20, pady=10, sticky="nsew")
        self.content_frame.grid_rowconfigure(1, weight=1)

        headers = ["STATUS", "CARD NUMBER", "EXP.", "CVV", "BANK", "MESSAGE"]
        header_frame = ctk.CTkFrame(table_frame, fg_color="transparent")
        header_frame.grid(row=0, column=0, sticky="ew", pady=(0, 5))
        for i, header in enumerate(headers):
            ctk.CTkLabel(header_frame, text=header, font=ctk.CTkFont(size=14, weight="bold", family="Consolas"), text_color=COLORS["text_accent"]).grid(row=0, column=i, padx=5, pady=5, sticky="ew")

        if not self.cards_to_validate:
            ctk.CTkLabel(table_frame, text="No results. Generate and validate a batch first.", font=ctk.CTkFont(family="Consolas"), text_color=COLORS["text_secondary"]).pack(pady=20)
            return

        for card in self.cards_to_validate:
            status_text = "Procesado"
            status_color = COLORS["warning"]
            
            row_frame = ctk.CTkFrame(table_frame, fg_color="transparent")
            row_frame.pack(fill="x", pady=2)

            ctk.CTkLabel(row_frame, text=status_text, font=ctk.CTkFont(weight="bold", family="Consolas"), text_color=status_color, width=100).grid(row=0, column=0, padx=5)
            ctk.CTkLabel(row_frame, text=f"****-****-****-{card.number[-4:]}", font=ctk.CTkFont(family="Consolas"), text_color=COLORS["text_secondary"], width=150).grid(row=0, column=1, padx=5)
            ctk.CTkLabel(row_frame, text=f"{card.exp_month}/{card.exp_year}", font=ctk.CTkFont(family="Consolas"), text_color=COLORS["text_secondary"], width=80).grid(row=0, column=2, padx=5)
            ctk.CTkLabel(row_frame, text=card.cvv, font=ctk.CTkFont(weight="bold", family="Consolas"), text_color=COLORS["warning"], width=60).grid(row=0, column=3, padx=5)
            ctk.CTkLabel(row_frame, text=card.bank, font=ctk.CTkFont(family="Consolas"), text_color=COLORS["text_secondary"], width=150).grid(row=0, column=4, padx=5)
            ctk.CTkLabel(row_frame, text="Ver logs para detalles.", font=ctk.CTkFont(family="Consolas"), text_color=COLORS["text_secondary"], width=250).grid(row=0, column=5, padx=5)


    def show_settings(self):
        self.log_activity("Settings accessed")
        title_frame = ctk.CTkFrame(self.content_frame, fg_color="transparent")
        title_frame.grid(row=0, column=0, sticky="w", padx=20, pady=(30, 20))
        ctk.CTkLabel(title_frame, text="⚙ SETTINGS & COOKIES", font=ctk.CTkFont(size=28, weight="bold", family="Consolas"), text_color=COLORS["text_accent"]).pack(anchor="w")
        ctk.CTkLabel(title_frame, text="Configure gateways and session cookies", font=ctk.CTkFont(size=12, family="Consolas"), text_color=COLORS["text_secondary"]).pack(anchor="w")

        settings_frame = ctk.CTkFrame(self.content_frame, fg_color=COLORS["bg_card"], border_width=1, border_color=COLORS["border"])
        settings_frame.grid(row=1, column=0, padx=20, pady=10, sticky="nsew")
        settings_frame.grid_columnconfigure(0, weight=1)
        settings_frame.grid_rowconfigure(1, weight=1)

        # Selector de Gateway
        ctk.CTkLabel(settings_frame, text="Selecciona Gateway para configurar cookies:", font=ctk.CTkFont(family="Consolas"), text_color=COLORS["text_secondary"]).grid(row=0, column=0, sticky="w", padx=20, pady=10)
        self.cookie_gateway_combo = ctk.CTkComboBox(settings_frame, values=["Eneba (Stripe)", "Amazon"], fg_color=COLORS["bg_input"], border_color=COLORS["border"], button_color=COLORS["button_bg"], text_color=COLORS["text_primary"], font=ctk.CTkFont(family="Consolas"))
        self.cookie_gateway_combo.grid(row=0, column=1, padx=(10, 20), pady=10, sticky="ew")
        self.cookie_gateway_combo.set("Eneba (Stripe)")

        # Caja de texto para las cookies
        ctk.CTkLabel(settings_frame, text="Pega la cookie de sesión aquí:", font=ctk.CTkFont(family="Consolas"), text_color=COLORS["text_secondary"]).grid(row=1, column=0, sticky="nw", padx=20, pady=(10, 5))
        self.cookie_textbox = ctk.CTkTextbox(settings_frame, fg_color=COLORS["bg_input"], text_color=COLORS["text_primary"], border_color=COLORS["border"], font=ctk.CTkFont(family="Consolas"))
        self.cookie_textbox.grid(row=2, column=0, columnspan=2, padx=20, pady=(0, 10), sticky="nsew")

        # Botón para guardar
        save_btn = self._create_styled_button(settings_frame, text="GUARDAR COOKIE", command=self.save_cookie, color=COLORS["text_accent"], hover_color=COLORS["border_focus"])
        save_btn.grid(row=3, column=0, columnspan=2, pady=10, sticky="ew", padx=20)
        
        # Cargar la cookie del gateway seleccionado si existe
        self._load_cookie_for_gateway()

    def _load_cookie_for_gateway(self):
        gateway = self.cookie_gateway_combo.get()
        if gateway in self.stored_cookies:
            self.cookie_textbox.delete("1.0", "end")
            self.cookie_textbox.insert("1.0", self.stored_cookies[gateway])
        else:
            self.cookie_textbox.delete("1.0", "end")

    def save_cookie(self):
        gateway = self.cookie_gateway_combo.get()
        cookie_value = self.cookie_textbox.get("1.0", "end").strip()
        if not cookie_value:
            self.update_log("⚠️ No se puede guardar una cookie vacía.")
            return
        self.stored_cookies[gateway] = cookie_value
        self.log_activity(f"Cookie saved for {gateway}")
        self.update_log(f"✅ Cookie para {gateway} guardada en memoria.")

    def update_log(self, message: str):
        if hasattr(self, 'log_display') and self.log_display.winfo_exists():
            self.log_display.configure(state="normal")
            timestamp = time.strftime("%H:%M:%S")
            self.log_display.insert("end", f"[{timestamp}] {message}\n")
            self.log_display.see("end")
            self.log_display.configure(state="disabled")

# --- LÓGICA DEL APLICATIVO (GENERADOR Y VALIDADOR) ---
    def generate_cards(self):
        try:
            bin_val = self.bin_entry.get().strip()
            month_val = self.month_combo.get()
            year_start_val = int(self.year_start_combo.get())
            year_end_val = int(self.year_end_combo.get())
            amount_val = int(self.amount_entry.get())

            if not bin_val or len(bin_val) != 6:
                self.update_log("❌ Error: El BIN (6 dígitos) es obligatorio.")
                return

            self.update_log(f"🔧 Generating {amount_val} cards for BIN {bin_val}...")
            self.log_activity(f"Generated {amount_val} cards for BIN {bin_val}")
            
            self.generator = CreditCardGenerator()
            self.cards_to_validate = self.generator.generate_batch(
                bin=bin_val,
                amount=amount_val,
                month=month_val,
                year_range=(year_start_val, year_end_val)
            )
            self.update_log(f"✅ {len(self.cards_to_validate)} cards generated. Ready to validate.")
        except ValueError as ve:
            self.update_log(f"❌ Value Error: {ve}.")
        except Exception as e:
            self.update_log(f"❌ Error generating cards: {e}")

    def start_validation(self):
        if not self.cards_to_validate:
            self.update_log("❌ Error: No cards to validate. Generate a batch first.")
            return

        gateway = self.gateway_combo.get()
        checker_instance = None
        if "Eneba" in gateway:
            checker_instance = EnebaChecker()
            if gateway in self.stored_cookies:
                checker_instance.set_session_cookie(self.stored_cookies[gateway])
                self.update_log(f"🍪 Usando cookie de sesión para {gateway}.")
                self.log_activity(f"Started validation on {gateway} with cookies")
            else:
                self.update_log(f"⚠️ No hay cookie guardada para {gateway}. Procediendo sin camuflaje.")
                self.log_activity(f"Started validation on {gateway} without cookies")

        elif "Amazon" in gateway:
            self.update_log("❌ Error: Amazon checker is not ready.")
            return

        if not checker_instance:
            self.update_log(f"❌ Error: Could not initialize checker for {gateway}.")
            return

        self.start_btn.configure(state="disabled")
        self.stop_btn.configure(state="normal")
        self.update_log(f"🚀 Starting validation on {gateway} with {len(self.cards_to_validate)} cards...")
        
        self.validator_service = CardValidatorService(gui_callback=self.update_log)
        self.validator_service.start_validation(cards=self.cards_to_validate, checker=checker_instance)

    def stop_validation(self):
        if self.validator_service:
            self.validator_service.stop_validation()
        self.update_log("🛑 Stopping validation...")
        self.log_activity("Validation stopped")
        self.start_btn.configure(state="normal")
        self.stop_btn.configure(state="disabled")

# --- Punto de Entrada de la Aplicación ---
if __name__ == "__main__":
    app = ProCheckerApp()
    app.mainloop() 