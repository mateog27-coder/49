# core/domain/card.py
from dataclasses import dataclass, field

@dataclass
class Card:
    """
    Modelo de datos UNIFICADO y PROFESIONAL para una tarjeta de crédito.
    Este es el único modelo de 'Card' que usará todo el Proyecto 49.
    Contiene toda la información necesaria para generación y verificación.
    """
    # --- Datos de la Tarjeta ---
    number: str
    exp_month: str
    exp_year: str
    cvv: str
    
    # --- Metadatos del BIN (Crucial para un checker profesional) ---
    brand: str = field(default="Unknown")      # Ej: VISA, MASTERCARD, AMERICAN EXPRESS
    bank: str = field(default="Unknown Bank")  # Ej: Bank of America, Santander
    country: str = field(default="Unknown")    # Ej: US, MX, ES
    card_type: str = field(default="Unknown")  # Ej: CREDIT, DEBIT
    
    # --- Metadatos del Checker ---
    status: str = field(default="Unchecked")   # Ej: LIVE, DEAD, DECLINED, ERROR
    gateway: str = field(default="N/A")        # Gateway donde fue verificada (Ej: "Amazon", "Stripe")
    response_message: str = field(default="Not yet checked") # Mensaje del gateway (Ej: "Insufficient Funds")

    def __str__(self) -> str:
        """
        Representación en string de la tarjeta, ideal para mostrar en listas o logs.
        Oculta el número de tarjeta por seguridad.
        """
        masked_number = f"****-****-****-{self.number[-4:]}"
        return (f"Card: {masked_number} | Exp: {self.exp_month}/{self.exp_year} | "
                f"Brand: {self.brand} | Bank: {self.bank} | "
                f"Status: {self.status} | Gateway: {self.gateway}")

    def to_dict(self) -> dict:
        """
        Convierte el objeto Card a un diccionario.
        Útil para guardarlo en un archivo JSON, CSV o para serializarlo.
        """
        return {
            "number": self.number,
            "exp_month": self.exp_month,
            "exp_year": self.exp_year,
            "cvv": self.cvv,
            "brand": self.brand,
            "bank": self.bank,
            "country": self.country,
            "card_type": self.card_type,
            "status": self.status,
            "gateway": self.gateway,
            "response_message": self.response_message
        }

    @property
    def full_exp(self) -> str:
        """Devuelve la fecha de expiración en formato MM/YYYY."""
        return f"{self.exp_month}/20{self.exp_year}"

    @property
    def is_expired(self) -> bool:
        """
        Verifica si la tarjeta está expirada basándose en la fecha actual.
        Es una utilidad para filtrar tarjetas antes de verificarlas.
        """
        from datetime import datetime
        try:
            exp_date = datetime.strptime(self.full_exp, "%m/%Y")
            return datetime.now() > exp_date
        except (ValueError, TypeError):
            return True # Si la fecha es inválida, la consideramos expirada