# Contenido completo de run_portfolio_backtest.py
import pandas as pd
# Importaciones absolutas
from config import settings
from data_collectors.historical_data import get_extended_historical_klines
from indicators.indicator_manager import IndicatorManager
from signal_generators.confluence_strategy import ConfluenceStrategy
from risk_management.risk_assessor import RiskAssessor
from portfolio.portfolio_manager import PortfolioManager
from backtesting.backtester import Backtester
from backtesting.performance_analyzer import PerformanceAnalyzer

# ... (el resto del código de la función no cambia) ...
def run_portfolio_backtest():
    """
    Configura y ejecuta un backtest de portfolio para múltiples activos.
    """
    # --- 1. Configuración del Backtest ---
    SYMBOLS = ["BTCUSDT", "ETHUSDT", "DOGEUSDT"]
    INTERVAL = "1h"
    START_DATE = "01 Aug, 2024" # 10 meses desde "ahora" (Junio 2025)
    INITIAL_CAPITAL = 10000.0

    # --- 2. Recolección de Datos para cada símbolo ---
    all_historical_data = {}
    for symbol in SYMBOLS:
        df = get_extended_historical_klines(symbol, INTERVAL, START_DATE)
        if not df.empty:
            df['SYMBOL'] = symbol
            df.set_index('Close_time', inplace=True)
            all_historical_data[symbol] = df
    
    if not all_historical_data:
        print("No se pudieron obtener datos para ningún símbolo. Abortando.")
        return

    # --- 3. Inicialización de Módulos (se comparten para todos los activos) ---
    indicator_manager = IndicatorManager()
    risk_assessor = RiskAssessor(atr_multiplier_sl=2.0)
    strategy_to_test = ConfluenceStrategy()
    
    portfolio_manager = PortfolioManager(
        initial_capital=INITIAL_CAPITAL, risk_per_trade_pct=0.01,
        indicator_manager=indicator_manager, strategy=strategy_to_test,
        risk_assessor=risk_assessor, max_open_positions=3, verbose=False
    )
    
    analyzer = PerformanceAnalyzer()
    backtester = Backtester(portfolio_manager, analyzer)
    
    # --- 4. Ejecución del Backtest ---
    backtester.run(all_historical_data, initial_capital=INITIAL_CAPITAL)

if __name__ == "__main__":
    run_portfolio_backtest()