# Contenido completo del archivo
import pandas as pd

class ConfluenceStrategy:
    """
    Estrategia de alta confluencia que busca una reversión a la media
    en un punto de soporte estructural.
    """
    def __init__(self, dc_period=20, bb_period=20, bb_std=2.0, rsi_period=14, rsi_oversold=30, rsi_overbought=70):
        self.dc_period = dc_period
        self.bb_period = bb_period
        self.bb_std = bb_std
        self.rsi_period = rsi_period
        self.rsi_oversold = rsi_oversold
        self.rsi_overbought = rsi_overbought

        std_str = str(int(bb_std)) if float(bb_std).is_integer() else str(bb_std)
        self.upper_band_col = f"BBU_{bb_period}_{std_str}"
        self.lower_band_col = f"BBL_{bb_period}_{std_str}"
        self.middle_band_col = f"BBM_{bb_period}_{std_str}"
        self.rsi_col = f"RSI_{rsi_period}"
        self.dc_upper_col = f"DCU_{dc_period}_{dc_period}"
        self.dc_lower_col = f"DCL_{dc_period}_{dc_period}"
        
        print("Estrategia de Confluencia inicializada.")

    def check_signal(self, df: pd.DataFrame) -> str:
        if len(df) < max(self.dc_period, self.bb_period, self.rsi_period):
            return 'HOLD'
        
        latest = df.iloc[-1]

        # --- SEÑAL DE COMPRA (LONG) ---
        # 1. Estructura: Precio cerca del soporte Donchian.
        is_at_support = abs(latest['Close'] - latest[self.dc_lower_col]) / latest[self.dc_lower_col] < 0.001 # Cerca en un 0.1%
        # 2. Estadística: Precio toca o cruza la banda de Bollinger inferior.
        is_bb_oversold = latest['Close'] <= latest[self.lower_band_col]
        # 3. Momentum: RSI en sobreventa.
        is_rsi_oversold = latest[self.rsi_col] < self.rsi_oversold

        if is_at_support and is_bb_oversold and is_rsi_oversold:
            return 'BUY'

        # --- SEÑAL DE VENTA (SHORT) ---
        is_at_resistance = abs(latest['Close'] - latest[self.dc_upper_col]) / latest[self.dc_upper_col] < 0.001
        is_bb_overbought = latest['Close'] >= latest[self.upper_band_col]
        is_rsi_overbought = latest[self.rsi_col] > self.rsi_overbought

        if is_at_resistance and is_bb_overbought and is_rsi_overbought:
            return 'SELL'

        return 'HOLD'