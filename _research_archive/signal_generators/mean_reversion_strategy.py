# Contenido completo del archivo

import pandas as pd

class MeanReversionStrategy:
    """
    Estrategia de Reversión a la Media usando una confluencia de
    Bandas de Bollinger y RSI para generar señales de entrada.
    """
    def __init__(self, bb_period: int = 20, bb_std: float = 2.0, rsi_period: int = 14, rsi_overbought: int = 70, rsi_oversold: int = 30):
        self.bb_period = bb_period
        self.bb_std = bb_std
        self.rsi_period = rsi_period
        self.rsi_overbought = rsi_overbought
        self.rsi_oversold = rsi_oversold

        # --- CORRECCIÓN FINAL ---
        # Nos aseguramos de que el número de desviación estándar se formatee como un entero
        # si es un número entero (ej. 2.0 -> 2), para coincidir con pandas-ta.
        std_str = str(int(bb_std)) if float(bb_std).is_integer() else str(bb_std)

        # Nombres de las columnas que esperamos de pandas-ta, ahora centralizados.
        self.upper_band_col = f"BBU_{bb_period}_{std_str}"
        self.middle_band_col = f"BBM_{bb_period}_{std_str}" # <-- AÑADIDO
        self.lower_band_col = f"BBL_{bb_period}_{std_str}"
        self.rsi_col = f"RSI_{rsi_period}"

        print(f"Estrategia de Reversión a la Media inicializada.")
        print(f"Buscando columnas de Bollinger: {self.lower_band_col}, {self.middle_band_col}, {self.upper_band_col}")

    def check_signal(self, df: pd.DataFrame) -> str:
        # (El resto de esta función no cambia)
        if len(df) < self.bb_period or len(df) < self.rsi_period:
            return 'HOLD'
        
        latest_candle = df.iloc[-1]

        price_at_lower_band = latest_candle['Close'] <= latest_candle[self.lower_band_col]
        rsi_is_oversold = latest_candle[self.rsi_col] < self.rsi_oversold
        
        if price_at_lower_band and rsi_is_oversold:
            return 'BUY'

        price_at_upper_band = latest_candle['Close'] >= latest_candle[self.upper_band_col]
        rsi_is_overbought = latest_candle[self.rsi_col] > self.rsi_overbought

        if price_at_upper_band and rsi_is_overbought:
            return 'SELL'

        return 'HOLD'