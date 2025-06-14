import time
import pandas as pd
from config import settings
from data_collectors.binance_websocket import BinanceWebsocketClient
from data_collectors.historical_data import get_historical_klines
from indicators.indicator_manager import IndicatorManager
from signal_generators.basic_strategy import BasicStrategy
from risk_management.risk_assessor import RiskAssessor
from DELTRADER.portfolio.portfolio_manager import PortfolioManager

# --- Instancias de nuestros Módulos ---
# Módulos de bajo nivel (herramientas)
indicator_manager = IndicatorManager()
basic_strategy = BasicStrategy(rsi_oversold=30, rsi_overbought=70)
risk_assessor = RiskAssessor(atr_multiplier_sl=2.0, atr_multiplier_tp=3.0)

# El Módulo Orquestador de alto nivel
portfolio_manager = PortfolioManager(
    initial_capital=10000.0,
    risk_per_trade_pct=0.01, # Arriesgar el 1% del capital por operación
    indicator_manager=indicator_manager,
    strategy=basic_strategy,
    risk_assessor=risk_assessor
)

# --- Definición del Callback ---
def on_new_data_received(df: pd.DataFrame):
    """
    Callback que se activa al recibir nuevos datos de velas.
    Ahora solo delega la tarea al PortfolioManager. Es un simple passthrough.
    """
    try:
        portfolio_manager.update(df)
    except Exception as e:
        print(f"Error en el callback on_new_data_received: {e}")
        import traceback
        traceback.print_exc()

def main():
    print("Iniciando la Super-Herramienta de Predicción (Framework Cuantitativo)...")
    
    historical_df = get_historical_klines(settings.SYMBOL, settings.INTERVAL, limit=500)
    
    ws_client = BinanceWebsocketClient(
        url=settings.WEBSOCKET_URL,
        initial_df=historical_df,
        callback=on_new_data_received
    )
    
    ws_client.start()

    try:
        while True:
            time.sleep(1)
    except KeyboardInterrupt:
        print("Deteniendo la aplicación...")
        ws_client.stop()
        print("Aplicación detenida.")
        print("\n--- Historial de Trades ---")
        print(pd.DataFrame(portfolio_manager.trade_history))

if __name__ == "__main__":
    main()