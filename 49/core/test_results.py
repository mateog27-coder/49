# core/test_results.py
from enum import Enum, auto
from dataclasses import dataclass
from typing import Optional, Dict, Any
from .domain.card import Card # Asegúrate de que la ruta es correcta

class TestStatus(Enum):
    LIVE = auto()
    DECLINED = auto()
    DEAD = auto()
    CVV2_LIVE = auto()
    ERROR = auto()
    UNKNOWN = auto()

@dataclass
class TestResult:
    status: TestStatus
    gateway: str
    response_message: str
    card: Card
    response_code: Optional[str] = None
    proxy_used: Optional[str] = None
    session_data: Optional[Dict[str, Any]] = None

    def to_dict(self) -> dict:
        return {
            "card": self.card.to_dict(),
            "status": self.status.name,
            "gateway": self.gateway,
            "response_message": self.response_message,
            "response_code": self.response_code,
            "proxy_used": self.proxy_used,
            "session_data": self.session_data
        }