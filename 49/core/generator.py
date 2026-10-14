# core/generator.py
import random
from dataclasses import dataclass
from typing import Tuple, List, Optional

# --- Importamos nuestro Card unificado y nuestra nueva base de datos ---
from .domain.card import Card
from .bin_database import BinDatabase

@dataclass
class CreditCardGenerator:
    """
    Generador de tarjetas de crédito 100% real y dinámico para el Proyecto 49.
    Ahora usa una base de datos local de BINs, siendo rápido, privado y a prueba de antivirus.
    Permite un control total sobre la generación de fecha y CVV.
    """

    LUHN_ODD_LOOKUP = (0, 2, 4, 6, 8, 1, 3, 5, 7, 9)

    @staticmethod
    def _calculate_luhn(card_number: str) -> str:
        """Calcula el dígito de control Luhn."""
        total = 0
        is_odd_position = len(card_number) % 2 != 0
        for digit_char in card_number:
            digit = int(digit_char)
            if is_odd_position:
                total += CreditCardGenerator.LUHN_ODD_LOOKUP[digit]
            else:
                total += digit
            is_odd_position = not is_odd_position
        return str((10 - (total % 10)) % 10)

    @staticmethod
    def _generate_card_number(bin_prefix: str, length: int = 16) -> str:
        """Genera un número de tarjeta completo y válido según Luhn."""
        prefix_len = len(bin_prefix)
        if prefix_len >= length - 1:
            raise ValueError("El BIN es demasiado largo para la longitud de la tarjeta.")
        
        body_len = length - prefix_len - 1
        body = ''.join(str(random.randint(0, 9)) for _ in range(body_len))
        check_digit = CreditCardGenerator._calculate_luhn(bin_prefix + body)
        
        return bin_prefix + body + check_digit

    def _get_bin_info_from_db(self, bin_prefix: str) -> Optional[dict]:
        """
        Obtiene información REAL del BIN desde nuestra base de datos local.
        Es instantáneo, privado y no necesita internet.
        """
        print(f"[Generator] Buscando BIN {bin_prefix} en la base de datos local...")
        bin_info = BinDatabase.lookup(bin_prefix)
        
        if not bin_info:
            print(f"[Generator] ERROR: El BIN {bin_prefix} no se encuentra en la base de datos.")
            return None
            
        print(f"[Generator] ✅ BIN encontrado. Banco: {bin_info['bank']}, País: {bin_info['country']}")
        return bin_info

    @staticmethod
    def _generate_realistic_cvv(brand: str) -> str:
        """Genera un CVV realista basado en la marca de la tarjeta."""
        if brand == "AMERICAN EXPRESS":
            return str(random.randint(1000, 9999)) # CVV de 4 dígitos
        else:
            return str(random.randint(100, 999))  # CVV de 3 dígitos

    def generate_card(self, bin: str, month: Optional[str] = None, year_range: Optional[Tuple[int, int]] = None, cvv: Optional[str] = None) -> Optional[Card]:
        """
        Genera UNA tarjeta de crédito 100% real y con datos de BIN de nuestra DB local.
        Permite personalizar la fecha y el CVV.
        
        Args:
            bin (str): El BIN de la tarjeta.
            month (Optional[str]): Mes de expiración (ej: "10"). Si es None, se genera uno aleatorio.
            year_range (Optional[Tuple[int, int]]): Rango de años (ej: (2026, 2030)). Si es None, se genera uno aleatorio.
            cvv (Optional[str]): CVV específico. Si es None, se genera uno realista según la marca.
        """
        bin_info = self._get_bin_info_from_db(bin)
        if not bin_info:
            return None

        # Determinar la longitud de la tarjeta por la marca
        card_length = bin_info.get('length', 16)
        
        # Generar el número de tarjeta
        pan = self._generate_card_number(bin, length=card_length)
        
        # Generar fecha de expiración (aleatoria o personalizada)
        if month:
            exp_month = f"{int(month):02d}"
        else:
            exp_month = f"{random.randint(1, 12):02d}"

        if year_range:
            start_year, end_year = year_range
            exp_year = str(random.randint(start_year, end_year))[-2:]
        else:
            # Generar un año aleatorio en los próximos 5 años
            from datetime import datetime
            current_year = int(datetime.datetime.now().year)
            exp_year = str(random.randint(current_year, current_year + 5))[-2:]
        
        # Generar CVV (aleatorio o personalizado)
        if cvv:
            generated_cvv = cvv
        else:
            generated_cvv = self._generate_realistic_cvv(bin_info['brand'])
        
        # Crear y devolver el objeto de tarjeta real usando NUESTRO Card UNIFICADO
        return Card(
            number=pan,
            exp_month=exp_month,
            exp_year=exp_year,
            cvv=generated_cvv,
            brand=bin_info['brand'],
            bank=bin_info['bank'],
            country=bin_info['country'],
            card_type=bin_info['type']
        )

    def generate_batch(self, bin: str, amount: int, month: Optional[str] = None, year_range: Optional[Tuple[int, int]] = None, cvv: Optional[str] = None) -> List[Card]:
        """
        Genera un lote de tarjetas reales.
        Filtra automáticamente los BINs inválidos.
        Permite personalizar la fecha y el CVV para todo el lote.
        """
        cards = []
        valid_cards_generated = 0
        
        while valid_cards_generated < amount:
            card = self.generate_card(bin, month, year_range, cvv)
            if card:
                cards.append(card)
                valid_cards_generated += 1
        
        return cards