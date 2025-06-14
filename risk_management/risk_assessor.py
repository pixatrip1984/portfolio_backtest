# Contenido completo del archivo

import pandas as pd

class RiskAssessor:
    """
    Calcula el Stop Loss inicial y el tamaño de la posición.
    """
    def __init__(self, atr_multiplier_sl: float = 1.5):
        self.atr_multiplier_sl = atr_multiplier_sl
        print(f"RiskAssessor inicializado: SL inicial a {atr_multiplier_sl}x ATR.")

    def determine_initial_sl(self, latest_candle: pd.Series, direction: str) -> float:
        """
        Calcula el precio del Stop Loss inicial basado en ATR y la dirección del trade.
        """
        atr_value = latest_candle['ATR_14']
        entry_price = latest_candle['Close']
        
        if direction == 'LONG':
            stop_loss_price = entry_price - (atr_value * self.atr_multiplier_sl)
        elif direction == 'SHORT':
            stop_loss_price = entry_price + (atr_value * self.atr_multiplier_sl)
        else:
            # Por seguridad, si la dirección no es válida, devolvemos un SL no ejecutable.
            return entry_price 
        
        return stop_loss_price

    def calculate_position_size(self, portfolio_balance: float, risk_per_trade_pct: float, entry_price: float, stop_loss_price: float) -> float:
        """Calcula el tamaño de la posición."""
        risk_per_unit = abs(entry_price - stop_loss_price)
        if risk_per_unit <= 0:
            return 0.0
        
        capital_at_risk = portfolio_balance * risk_per_trade_pct
        position_size = capital_at_risk / risk_per_unit
        return position_size