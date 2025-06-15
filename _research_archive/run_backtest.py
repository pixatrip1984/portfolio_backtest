# Contenido completo del archivo
import pandas as pd
from config import settings
from data_collectors.historical_data import get_extended_historical_klines
from indicators.indicator_manager import IndicatorManager
from signal_generators.confluence_strategy import ConfluenceStrategy # <-- NUEVA ESTRATEGIA
from risk_management.risk_assessor import RiskAssessor
from portfolio.portfolio_manager import PortfolioManager
from backtesting.backtester import Backtester
from backtesting.performance_analyzer import PerformanceAnalyzer

def run_strategy_backtest():
    SYMBOL = "BTCUSDT"
    INTERVAL = "1h"
    START_DATE = "01 Jan, 2023"
    INITIAL_CAPITAL = 10000.0

    historical_df = get_extended_historical_klines(SYMBOL, INTERVAL, START_DATE)
    if historical_df.empty: return
    historical_df['SYMBOL'] = SYMBOL

    indicator_manager = IndicatorManager()
    risk_assessor = RiskAssessor(atr_multiplier_sl=2.0) # Un SL un poco más amplio
    
    strategy_to_test = ConfluenceStrategy()
    
    # Usamos el mismo PortfolioManager de reversión a la media, ya que la lógica de salida es la misma.
    portfolio_manager = PortfolioManager(
        initial_capital=INITIAL_CAPITAL, risk_per_trade_pct=0.01,
        indicator_manager=indicator_manager, strategy=strategy_to_test,
        risk_assessor=risk_assessor, verbose=False
    )
    
    analyzer = PerformanceAnalyzer()
    backtester = Backtester(portfolio_manager, analyzer)
    backtester.run(historical_df, initial_capital=INITIAL_CAPITAL)

if __name__ == "__main__":
    run_strategy_backtest()