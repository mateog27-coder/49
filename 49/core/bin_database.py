# core/bin_database.py
# Base de datos local de BINs para el Proyecto 49.
# Esto elimina la dependencia de APIs externas y evita que el antivirus lo bloquee.

# Diccionario principal de BINs
# Estructura: BIN: {brand, bank, country, type, length}
BIN_DATABASE = {
    # --- BINs de COLOMBIA (Colpatria, Davivienda, Bancolombia, etc.) ---
    "486502": {"brand": "VISA", "bank": "Bancolombia", "country": "CO", "type": "CREDIT", "length": 16},
    "530691": {"brand": "MASTERCARD", "bank": "Bancolombia", "country": "CO", "type": "CREDIT", "length": 16},
    "533900": {"brand": "MASTERCARD", "bank": "Bancolombia", "country": "CO", "type": "CREDIT", "length": 16},
    "527628": {"brand": "MASTERCARD", "bank": "Bancolombia", "country": "CO", "type": "CREDIT", "length": 16},
    "469723": {"brand": "VISA", "bank": "Davivienda", "country": "CO", "type": "CREDIT", "length": 16},
    "533427": {"brand": "MASTERCARD", "bank": "Davivienda", "country": "CO", "type": "CREDIT", "length": 16},
    "409116": {"brand": "VISA", "bank": "Colpatria", "country": "CO", "type": "CREDIT", "length": 16},
    "553395": {"brand": "MASTERCARD", "bank": "Colpatria", "country": "CO", "type": "CREDIT", "length": 16},
    "531138": {"brand": "MASTERCARD", "bank": "Banco Popular", "country": "CO", "type": "CREDIT", "length": 16},
    "408253": {"brand": "VISA", "bank": "Banco Popular", "country": "CO", "type": "CREDIT", "length": 16},
    "466228": {"brand": "VISA", "bank": "Banco de Bogota", "country": "CO", "type": "CREDIT", "length": 16},
    "555763": {"brand": "MASTERCARD", "bank": "Banco de Bogota", "country": "CO", "type": "CREDIT", "length": 16},
    "540111": {"brand": "MASTERCARD", "bank": "Banco de Occidente", "country": "CO", "type": "CREDIT", "length": 16},
    "453253": {"brand": "VISA", "bank": "Banco de Occidente", "country": "CO", "type": "CREDIT", "length": 16},
    
    # --- BINs INTERNACIONALES (Ejemplos) ---
    "453264": {"brand": "VISA", "bank": "Bank of America", "country": "US", "type": "CREDIT", "length": 16},
    "542432": {"brand": "MASTERCARD", "bank": "Citibank", "country": "US", "type": "CREDIT", "length": 16},
    "374421": {"brand": "AMERICAN EXPRESS", "bank": "American Express Co.", "country": "US", "type": "CREDIT", "length": 15},
    "601111": {"brand": "DISCOVER", "bank": "Discover Bank", "country": "US", "type": "CREDIT", "length": 16},
    "555555": {"brand": "MASTERCARD", "bank": "Banco Nacional de Mexico", "country": "MX", "type": "CREDIT", "length": 16},
    "415505": {"brand": "VISA", "bank": "Banco Santander", "country": "ES", "type": "CREDIT", "length": 16},
    "510510": {"brand": "MASTERCARD", "bank": "Banco Santander", "country": "ES", "type": "CREDIT", "length": 16},
    "401288": {"brand": "VISA", "bank": "BBVA", "country": "ES", "type": "CREDIT", "length": 16},
    "502870": {"brand": "MASTERCARD", "bank": "BBVA", "country": "ES", "type": "CREDIT", "length": 16},
    
    # --- BINs de ARGENTINA (Ejemplos) ---
    "422511": {"brand": "VISA", "bank": "Banco Galicia", "country": "AR", "type": "CREDIT", "length": 16},
    "533245": {"brand": "MASTERCARD", "bank": "Banco Galicia", "country": "AR", "type": "CREDIT", "length": 16},
    "440000": {"brand": "VISA", "bank": "BBVA Argentina", "country": "AR", "type": "CREDIT", "length": 16},
    "530529": {"brand": "MASTERCARD", "bank": "BBVA Argentina", "country": "AR", "type": "CREDIT", "length": 16},
}

class BinDatabase:
    """
    Clase que gestiona la base de datos local de BINs.
    Esta es la fuente de verdad del Proyecto 49.
    """

    @staticmethod
    def lookup(bin_prefix: str) -> dict:
        """
        Busca la información del BIN en la base de datos local.
        Devuelve un diccionario con los datos o None si no se encuentra.
        """
        return BIN_DATABASE.get(bin_prefix, None)

    @staticmethod
    def add_bin(bin_prefix: str, bank_info: dict):
        """
        Añade un nuevo BIN a la base de datos de forma temporal (en memoria).
        Esto se puede usar para añadir BINs que el usuario encuentre manualmente.
        """
        # Asegurarse de que los datos son válidos
        if not all(key in bank_info for key in ['brand', 'bank', 'country', 'type', 'length']):
            raise ValueError("La información del BIN debe contener: brand, bank, country, type, length")
        
        BIN_DATABASE[bin_prefix] = bank_info

    @staticmethod
    def get_all_bins() -> list:
        """Devuelve una lista de todos los BINs disponibles."""
        return list(BIN_DATABASE.keys())