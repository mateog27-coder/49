# core/services/card_validator_service.py
import threading
import queue
import logging
from typing import List, Callable, Optional

# --- Importaciones UNIFICADAS para el Proyecto 49 ---
# Nota: Ahora usamos importaciones absolutas desde la raíz del proyecto
from core.test_results import TestResult, TestStatus
from core.domain.card import Card
from core.checkers.base_checker import BaseChecker

# Obtén el logger que configuramos en main.py
logger = logging.getLogger(__name__)

class CardValidatorService:
    """
    El motor principal de validación del Proyecto 49.
    Orquesta la revisión de tarjetas en hilos separados para máxima velocidad.
    """

    def __init__(self, gui_callback: Callable[[str], None]):
        """
        Args:
            gui_callback (Callable): Una función para enviar resultados a la GUI.
        """
        self.gui_callback = gui_callback
        self.card_queue: queue.Queue[Card] = queue.Queue()
        self.stop_event = threading.Event()
        self.worker_threads: List[threading.Thread] = []
        self.is_running = False

    def start_validation(self, cards: List[Card], checker: BaseChecker):
        """
        Inicia el proceso de validación con un checker específico.
        Args:
            cards (List[Card]): La lista de tarjetas a validar.
            checker (BaseChecker): La instancia del checker a usar (Amazon, Eneba, etc.).
        """
        if self.is_running:
            logger.warning("El validador ya está en ejecución.")
            return

        self.is_running = True
        self.stop_event.clear()

        # Llena la cola con todas las tarjetas
        for card in cards:
            self.card_queue.put(card)

        # Lanza los hilos trabajadores (workers)
        num_workers = 5  # Puedes ajustar este número según tu PC y proxies
        logger.info(f"🚀 Lanzando {num_workers} hilos para validar {len(cards)} tarjetas.")
        
        for i in range(num_workers):
            thread = threading.Thread(target=self._worker_loop, args=(checker,), daemon=True, name=f"Worker-{i+1}")
            self.worker_threads.append(thread)
            thread.start()

        # Lanza un hilo supervisor para saber cuándo todo ha terminado
        threading.Thread(target=self._supervisor_loop, daemon=True).start()

    def stop_validation(self):
        """Detiene la validación de forma segura."""
        if not self.is_running:
            return
        
        logger.info("⏹️ Deteniendo validación... Espere a que los hilos terminen.")
        self.stop_event.set()
        
    def _supervisor_loop(self):
        """Espera a que todas las tarjetas en la cola sean procesadas."""
        self.card_queue.join()  # Esto se bloquea hasta que todas las tareas estén hechas
        self.is_running = False
        self.worker_threads.clear()
        if callable(self.gui_callback):
            self.gui_callback("✅ Validación completada.\n")

    def _worker_loop(self, checker: BaseChecker):
        """El bucle que cada hilo trabajador ejecuta constantemente."""
        while not self.stop_event.is_set():
            try:
                card: Card = self.card_queue.get(timeout=1) # Espera 1s por una tarjeta
                
                # Usa el checker para probar la tarjeta
                result: TestResult = checker.check(card)
                
                # Prepara el mensaje para la GUI basado en nuestro NUEVO sistema de estados
                if result.status == TestStatus.LIVE:
                    status_icon = "✅ LIVE"
                elif result.status == TestStatus.CVV2_LIVE:
                    status_icon = "🔒 3DS"
                elif result.status == TestStatus.DECLINED:
                    status_icon = "❌ DECLINED"
                elif result.status == TestStatus.DEAD:
                    status_icon = "💀 DEAD"
                else: # ERROR o UNKNOWN
                    status_icon = "🔴 ERROR"
                    
                # Usa el método __str__ de nuestro Card unificado para mostrar el número de forma segura
                gui_message = (
                    f"{status_icon} | Gateway: {result.gateway} | {str(card)} | "
                    f"Razón: {result.response_message}\n"
                )
                
                # Envía el mensaje a la GUI
                if callable(self.gui_callback):
                    self.gui_callback(gui_message)
                
                self.card_queue.task_done() # Marca la tarea como completada

            except queue.Empty:
               continue
            except Exception as e:
                logger.error(f"Error inesperado en el worker thread {threading.current_thread().name}: {e}", exc_info=True)
                self.card_queue.task_done()