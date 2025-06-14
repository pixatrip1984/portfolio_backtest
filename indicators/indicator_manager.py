# Contenido completo del archivo

import pandas as pd
import pandas_ta as ta

class IndicatorManager:
    """
    Gestiona el cálculo de indicadores técnicos en un DataFrame de klines.
    """
    def __init__(self):
        """
        Inicializa el gestor de indicadores.
        """
        self.strategy = ta.Strategy(
            name="Scalping SuperTool Strategy",
            description="Una combinación de indicadores para scalping.",
            ta=[
                {"kind": "ema", "length": 9, "col_names": ("EMA_9")},
                {"kind": "ema", "length": 21, "col_names": ("EMA_21")},
                {"kind": "rsi", "length": 14, "col_names": ("RSI_14")},
                {"kind": "macd", "fast": 12, "slow": 26, "signal": 9, "col_names": ("MACD_12_26_9", "MACDh_12_26_9", "MACDs_12_26_9")},
                {"kind": "bbands", "length": 20, "std": 2, "col_names": ("BBL_20_2", "BBM_20_2", "BBU_20_2", "BBB_20_2", "BBP_20_2")},
                {"kind": "atr", "length": 14, "col_names": ("ATR_14")},
                {"kind": "donchian", "lower_length": 20, "upper_length": 20, "col_names": ("DCL_20_20", "DCM_20_20", "DCU_20_20")},
                # --- NUEVO INDICADOR AÑADIDO ---
                # ADX para medir la fuerza de la tendencia. Nos dará la columna ADX_14.
                # No nos interesan las columnas DMP_14 y DMN_14 por ahora.
                {"kind": "adx", "length": 14, "col_names": ("ADX_14", "DMP_14", "DMN_14")},
            ]
        )
        print("IndicatorManager inicializado con la siguiente estrategia:")
        print(self.strategy)

    def calculate_indicators(self, df: pd.DataFrame) -> pd.DataFrame:
        """
        Calcula todos los indicadores definidos en la estrategia sobre el DataFrame.
        """
        df_with_indicators = df.copy()
        
        # Renombramos a minúsculas para compatibilidad con pandas-ta.
        df_with_indicators.rename(columns={
            "Open": "open", "High": "high", "Low": "low", "Close": "close", "Volume": "volume"
        }, inplace=True)
        
        df_with_indicators.ta.strategy(self.strategy, append=True)
        
        # Revertimos los nombres a Mayúscula inicial.
        df_with_indicators.rename(columns={
            "open": "Open", "high": "High", "low": "Low", "close": "Close", "volume": "Volume"
        }, inplace=True)
        
        return df_with_indicators