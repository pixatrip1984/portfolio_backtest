# Contenido completo del archivo
# Contenido completo
import pandas as pd
# Importaciones absolutas
from risk_management.risk_assessor import RiskAssessor
from risk_management.position import Position
from signal_generators.confluence_strategy import ConfluenceStrategy
from indicators.indicator_manager import IndicatorManager

# ... (el resto del código de la clase no cambia) ...
class PortfolioManager:
    """
    Gestiona un portfolio de múltiples activos, aplicando una estrategia única a cada uno.
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

# Contenido completo de la función _check_new_entry a reemplazar

    def _check_new_entry(self, df: pd.DataFrame, symbol: str):
        """Busca una señal de entrada para un símbolo específico."""
        from risk_management.position import Position
        signal = self.strategy.check_signal(df)
        
        if signal not in ['BUY', 'SELL']:
            return

        direction = 'LONG' if signal == 'BUY' else 'SHORT'
        candle = df.iloc[-1]
        entry_price = candle['Close']
        
        # --- CORRECCIÓN CLAVE ---
        # No construimos el nombre de la columna aquí.
        # Lo tomamos directamente del objeto de la estrategia, que es la fuente de verdad.
        take_profit = candle[self.strategy.middle_band_col]
        
        stop_loss = self.risk_assessor.determine_initial_sl(candle, direction)
        
        position_size = self.risk_assessor.calculate_position_size(self.capital, self.risk_per_trade_pct, entry_price, stop_loss)
        if position_size <= 0: return

        self.open_positions[symbol] = Position(
            entry_time=candle.name, entry_price=entry_price, size=position_size,
            stop_loss=stop_loss, take_profit=take_profit, direction=direction
        )
        if self.verbose:
            print(f"[{candle.name}] NUEVA POSICIÓN {direction} en {symbol}: Entrada ${entry_price:,.2f}")

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