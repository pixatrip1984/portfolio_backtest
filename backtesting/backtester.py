# Contenido completo del archivo

# Contenido completo
import pandas as pd
from tqdm import tqdm
# Importaciones absolutas
from portfolio.portfolio_manager import PortfolioManager
from backtesting.performance_analyzer import PerformanceAnalyzer

# ... (el resto del código de la clase no cambia) ...
class Backtester:
    """
    Motor de backtesting a nivel de portfolio que simula el trading
    de múltiples activos de forma simultánea.
    """
    def __init__(self, portfolio_manager, analyzer):
        self.portfolio_manager = portfolio_manager
        self.analyzer = analyzer

    def run(self, historical_data: dict, initial_capital: float, min_data_points: int = 200):
        """
        Ejecuta el backtest sobre un diccionario de DataFrames históricos.
        """
        print(f"Iniciando backtest de portfolio para {list(historical_data.keys())}...")

        # --- CORRECCIÓN CLAVE ---
        # 1. Crear el "Reloj Maestro": un índice con todas las fechas/horas únicas.
        # Inicializamos un índice vacío.
        master_index = pd.Index([])
        # Iteramos y unimos los índices de cada DataFrame.
        for df in historical_data.values():
            master_index = master_index.union(df.index)
        # El resultado ya es único y está ordenado, no necesita más procesamiento.
        
        print(f"Simulando {len(master_index)} pasos de tiempo...")

        # 2. Iterar a través del tiempo, no de los activos.
        for i in tqdm(range(min_data_points, len(master_index)), desc="Simulando Portfolio"):
            current_timestamp = master_index[i]

            # 3. En cada paso de tiempo, iterar sobre los activos.
            for symbol, df in historical_data.items():
                # Si hay datos para este activo en este momento...
                if current_timestamp in df.index:
                    # Creamos una vista de los datos hasta el momento actual
                    data_slice = df.loc[:current_timestamp]
                    
                    # Pedimos al PortfolioManager que se actualice para este símbolo
                    self.portfolio_manager.update_for_symbol(data_slice.copy(), symbol)

        print("Simulación de portfolio completada.")
        
        self.analyzer.analyze(
            trade_history=self.portfolio_manager.trade_history,
            initial_capital=initial_capital,
            symbol="Portfolio" # El reporte ahora es para todo el portfolio
        )