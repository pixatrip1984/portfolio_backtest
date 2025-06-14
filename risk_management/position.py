# Contenido completo del archivo
from dataclasses import dataclass
from datetime import datetime

@dataclass
class Position:
    """
    Encapsula la información de UNA posición. El símbolo se gestiona externamente.
    """
    entry_time: datetime
    entry_price: float
    size: float
    stop_loss: float
    take_profit: float
    direction: str      # 'LONG' o 'SHORT'