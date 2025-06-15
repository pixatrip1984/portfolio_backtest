# portfolio/portfolio_manager.py
# Versión actualizada compatible con ElliottWaveStrategy

import pandas as pd
# Importaciones absolutas
from risk_management.risk_assessor import RiskAssessor
from risk_management.position import Position


class PortfolioManager:
    """
    Gestiona un portfolio de múltiples activos, aplicando una estrategia única a cada uno.
    Actualizado para ser compatible con ElliottWaveStrategy y estrategias anteriores.
    """
    def __init__(self, initial_capital: float, risk_per_trade_pct: float, indicator_manager, strategy, risk_assessor, max_open_positions: int = 3, verbose: bool = True):
        self.capital = initial_capital
        self.risk_per_trade_pct = risk_per_trade_pct
        self.indicator_manager = indicator_manager
        self.strategy = strategy
        self.risk_assessor = risk_assessor
        self.max_open_positions = max_open_positions
        self.verbose = verbose
        
        self.open_positions = {} # Diccionario para las posiciones abiertas: {'BTCUSDT': Position(...)}
        self.trade_history = []
        if self.verbose:
            print(f"PortfolioManager (Multi-Asset) inicializado. Máx. Posiciones: {max_open_positions}")

    def update_for_symbol(self, df_slice: pd.DataFrame, symbol: str):
        """
        El método principal, ahora llamado para cada símbolo en cada paso de tiempo.
        """
        df_with_indicators = self.indicator_manager.calculate_indicators(df_slice)
        
        # Gestionar la posición existente para este símbolo (si la hay)
        if symbol in self.open_positions:
            self._manage_open_position(df_with_indicators.iloc[-1], symbol)
        
        # Buscar nuevas entradas si no tenemos una posición en este símbolo
        # y no hemos alcanzado el límite de posiciones abiertas.
        elif len(self.open_positions) < self.max_open_positions:
            self._check_new_entry(df_with_indicators, symbol)

    def _check_new_entry(self, df: pd.DataFrame, symbol: str):
        """Busca una señal de entrada para un símbolo específico."""
        from risk_management.position import Position
        signal = self.strategy.check_signal(df)
        
        if signal not in ['BUY', 'SELL']:
            return

        direction = 'LONG' if signal == 'BUY' else 'SHORT'
        candle = df.iloc[-1]
        entry_price = candle['Close']
        
        # --- NUEVA LÓGICA COMPATIBLE ---
        # Determinar take profit basado en el tipo de estrategia
        take_profit = self._calculate_take_profit(candle, direction)
        
        stop_loss = self.risk_assessor.determine_initial_sl(candle, direction)
        
        position_size = self.risk_assessor.calculate_position_size(self.capital, self.risk_per_trade_pct, entry_price, stop_loss)
        if position_size <= 0: return

        self.open_positions[symbol] = Position(
            entry_time=candle.name, entry_price=entry_price, size=position_size,
            stop_loss=stop_loss, take_profit=take_profit, direction=direction
        )
        if self.verbose:
            print(f"[{candle.name}] NUEVA POSICIÓN {direction} en {symbol}: Entrada ${entry_price:,.2f}")

    def _calculate_take_profit(self, candle: pd.Series, direction: str) -> float:
        """
        Calcula el take profit basado en el tipo de estrategia.
        Compatible con estrategias anteriores y ElliottWaveStrategy.
        """
        try:
            # Verificar si es ElliottWaveStrategy
            if hasattr(self.strategy, 'get_take_profit_price'):
                # Usar el método específico de Elliott Wave
                return self.strategy.get_take_profit_price(candle, direction)
            
            # Fallback para estrategias anteriores (Confluence, etc.)
            elif hasattr(self.strategy, 'middle_band_col') and self.strategy.middle_band_col:
                # Usar Bollinger Band media como take profit (estrategias anteriores)
                return candle[self.strategy.middle_band_col]
            
            # Fallback general: usar ATR para calcular take profit
            else:
                atr_value = candle.get('ATR_14', 0)
                if atr_value == 0:
                    # Si no hay ATR, usar un porcentaje fijo
                    multiplier = 0.02  # 2% take profit
                else:
                    # Usar ATR para take profit dinámico
                    multiplier_atr = 2.0  # 2x ATR como take profit
                    
                if direction == 'LONG':
                    if atr_value > 0:
                        return candle['Close'] + (atr_value * multiplier_atr)
                    else:
                        return candle['Close'] * (1 + multiplier)
                elif direction == 'SHORT':
                    if atr_value > 0:
                        return candle['Close'] - (atr_value * multiplier_atr)
                    else:
                        return candle['Close'] * (1 - multiplier)
                        
        except Exception as e:
            print(f"Error calculando take profit: {e}")
            # Fallback final: take profit conservador del 1%
            if direction == 'LONG':
                return candle['Close'] * 1.01
            else:
                return candle['Close'] * 0.99

    def _manage_open_position(self, latest_candle: pd.Series, symbol: str):
        """Gestiona una posición abierta, buscando SL o TP."""
        position = self.open_positions[symbol]
        high_price, low_price = latest_candle['High'], latest_candle['Low']
        exit_price, reason = None, None

        if position.direction == 'LONG':
            if low_price <= position.stop_loss: exit_price, reason = position.stop_loss, 'STOP_LOSS'
            elif high_price >= position.take_profit: exit_price, reason = position.take_profit, 'TAKE_PROFIT'
        
        elif position.direction == 'SHORT':
            if high_price >= position.stop_loss: exit_price, reason = position.stop_loss, 'STOP_LOSS'
            elif low_price <= position.take_profit: exit_price, reason = position.take_profit, 'TAKE_PROFIT'

        if exit_price and reason:
            self._close_position(symbol, exit_price, reason, latest_candle.name)

    def _close_position(self, symbol: str, exit_price: float, reason: str, exit_time):
        """Cierra una posición específica y registra el trade."""
        position = self.open_positions.pop(symbol) # Elimina la posición del diccionario
        
        pnl_multiplier = 1 if position.direction == 'LONG' else -1
        pnl = (exit_price - position.entry_price) * position.size * pnl_multiplier
        self.capital += pnl
        
        trade_info = position.__dict__
        trade_info.update({'pnl': pnl, 'exit_reason': reason, 'exit_time': exit_time, 'symbol': symbol})
        self.trade_history.append(trade_info)
        
        if self.verbose:
            print(f"[{exit_time}] POSICIÓN CERRADA en {symbol} por {reason}: P&L: ${pnl:,.2f}")