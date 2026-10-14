# core/checkers/base_checker.py
from typing import Optional

# --- Importaciones UNIFICADAS del Proyecto 49 ---
# Nota: Ahora usamos importaciones absolutas desde la raíz del proyecto
from core.test_results import TestResult, TestStatus
from core.domain.card import Card

class BaseChecker:
    """
    Clase base abstracta que todos los checkers específicos (AmazonChecker, EnebaChecker, etc.)
    deben heredar e implementar.
    Define la estructura y la lógica común para todos los checkers.
    """

    def __init__(self):
        # Cada checker puede tener sus propias configuraciones iniciales aquí
        pass

    def check(self, card: Card, proxy: Optional[str] = None) -> TestResult:
        """
        Método principal que cada checker debe sobreescribir con su lógica específica.
        Ahora acepta un proxy opcional para cada prueba.
        """
        raise NotImplementedError("El método check() debe ser implementado por el checker específico (ej: AmazonChecker).")

    def _get_status_from_response(self, response_text: str, response_code: Optional[str] = None) -> TestStatus:
        """
        Método de ayuda para analizar la respuesta del gateway y determinar el estado.
        Ahora es más robusto y puede usar códigos de error.
        """
        response_text_lower = response_text.lower()

        # Priorizar códigos de error numéricos si están disponibles
        if response_code:
            # Ejemplos de códigos de Stripe: https://stripe.com/docs/error-codes
            if response_code in ('card_declined', 'generic_decline'):
                return TestStatus.DECLINED
            if response_code in ('incorrect_number', 'invalid_number', 'invalid_expiry_month'):
                return TestStatus.DEAD
            if response_code == 'authentication_required':
                return TestStatus.CVV2_LIVE

        # Palabras clave para tarjetas LIVE
        live_keywords = ['succeeded', 'approved', 'success', 'payment successful']
        if any(keyword in response_text_lower for keyword in live_keywords):
            return TestStatus.LIVE

        # Palabras clave para tarjetas DECLINED
        declined_keywords = ['declined', 'do not honour', 'insufficient funds', 'transaction not allowed']
        if any(keyword in response_text_lower for keyword in declined_keywords):
            return TestStatus.DECLINED

        # Palabras clave para tarjetas DEAD
        dead_keywords = ['invalid', 'do not match', 'incorrect', 'bad number', 'stolen card']
        if any(keyword in response_text_lower for keyword in dead_keywords):
            return TestStatus.DEAD

        # Palabras clave para 3D Secure / CVV2
        secure_keywords = ['3d secure', 'verify', 'authentication required']
        if any(keyword in response_text_lower for keyword in secure_keywords):
            return TestStatus.CVV2_LIVE
        
        # Si nada coincide, es desconocido o un error
        if 'error' in response_text_lower or 'timeout' in response_text_lower:
            return TestStatus.ERROR
            
        return TestStatus.UNKNOWN