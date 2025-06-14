import pandas as pd

class BasicStrategy:
    """
    Una estrategia de trading básica que genera señales de COMPRA/VENTA/MANTENER.
    Utiliza una combinación de RSI y el cruce del histograma del MACD.
    """
    def __init__(self, rsi_oversold: int = 30, rsi_overbought: int = 70):
        """
        Inicializa la estrategia con los umbrales para el RSI.

        Args:
            rsi_oversold (int): El nivel de RSI considerado como sobreventa.
            rsi_overbought (int): El nivel de RSI considerado como sobrecompra.
        """
        self.rsi_oversold = rsi_oversold
        self.rsi_overbought = rsi_overbought
        print(f"Estrategia Básica inicializada con RSI Oversold < {rsi_oversold} y Overbought > {rsi_overbought}")

    def check_signal(self, df: pd.DataFrame) -> str:
        """
        Analiza el DataFrame con indicadores y devuelve una señal de trading.

        Args:
            df (pd.DataFrame): El DataFrame que debe contener las columnas de velas
                               y los indicadores calculados (RSI_14, MACDh_12_26_9).

        Returns:
            str: La señal generada ('BUY', 'SELL', 'HOLD').
        """
        # Necesitamos al menos dos filas para detectar un cruce.
        if len(df) < 2:
            return 'HOLD'

        # Obtenemos la última vela (la más reciente, que acaba de cerrar) y la penúltima.
        latest_candle = df.iloc[-1]
        previous_candle = df.iloc[-2]

        # --- Lógica de la Señal de COMPRA ---
        # Condición 1: RSI en zona de sobreventa.
        is_rsi_oversold = latest_candle['RSI_14'] < self.rsi_oversold
        # Condición 2: El histograma del MACD acaba de cruzar hacia arriba (de negativo a positivo).
        macd_crossed_up = latest_candle['MACDh_12_26_9'] > 0 and previous_candle['MACDh_12_26_9'] < 0

        if is_rsi_oversold and macd_crossed_up:
            return 'BUY'

        # --- Lógica de la Señal de VENTA ---
        # Condición 1: RSI en zona de sobrecompra.
        is_rsi_overbought = latest_candle['RSI_14'] > self.rsi_overbought
        # Condición 2: El histograma del MACD acaba de cruzar hacia abajo (de positivo a negativo).
        macd_crossed_down = latest_candle['MACDh_12_26_9'] < 0 and previous_candle['MACDh_12_26_9'] > 0
        
        if is_rsi_overbought and macd_crossed_down:
            return 'SELL'

        # Si no se cumple ninguna de las condiciones anteriores, mantenemos la posición.
        return 'HOLD'