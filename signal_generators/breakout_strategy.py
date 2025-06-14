# Contenido completo del archivo
import pandas as pd

class BreakoutStrategy:
    """
    Estrategia de breakout que genera señales en ambas direcciones (LONG y SHORT).
    """
    def __init__(self, period: int = 20):
        self.period = period
        self.upper_channel_col = f"DCU_{period}_{period}"
        self.lower_channel_col = f"DCL_{period}_{period}"
        print(f"Estrategia de Breakout (Bi-direccional) inicializada con periodo de {period} velas.")

    def check_signal(self, df: pd.DataFrame, current_direction: str) -> str:
        """
        Analiza el DataFrame y devuelve una señal de trading.
        Ahora considera la dirección actual para evitar señales redundantes.
        """
        if len(df) < self.period + 1:
            return 'HOLD'
        
        latest_candle = df.iloc[-1]
        previous_candle = df.iloc[-2]

        upper_channel = previous_candle[self.upper_channel_col]
        lower_channel = previous_candle[self.lower_channel_col]
        
        # Si no estamos en largo y el precio rompe hacia arriba -> señal de compra.
        if current_direction != 'LONG' and latest_candle['Close'] > upper_channel:
            return 'BUY'
        
        # Si no estamos en corto y el precio rompe hacia abajo -> señal de venta.
        if current_direction != 'SHORT' and latest_candle['Close'] < lower_channel:
            return 'SELL'

        return 'HOLD'