# Contenido completo del archivo

import pandas as pd
import quantstats as qs

class PerformanceAnalyzer:
    """
    Analiza el historial de trades y genera un reporte de rendimiento,
    tanto a nivel de portfolio agregado como un desglose por cada símbolo.
    """
    def analyze(self, trade_history: list, initial_capital: float, symbol: str):
        """
        Toma el historial de trades y calcula/muestra las métricas de rendimiento.
        'symbol' se usa ahora para el nombre del archivo de reporte.
        """
        if not trade_history:
            print("No se realizaron trades. No hay nada que analizar.")
            return

        df = pd.DataFrame(trade_history)
        
        # --- 1. Análisis a Nivel de Portfolio Agregado ---
        print("\n--- Resumen del Backtest (Portfolio Total) ---")
        self._generate_report(
            df, 
            initial_capital, 
            report_title=f'{symbol} Strategy Performance',
            report_filename=f"backtest_report_{symbol}.html"
        )

        # --- 2. Análisis por Símbolo Individual (Desglose) ---
        # Verificamos si hay más de un símbolo para justificar el desglose.
        if df['symbol'].nunique() > 1:
            print("\n--- Desglose por Símbolo ---")
            # Agrupamos el historial de trades por el símbolo
            for symbol_name, symbol_trades in df.groupby('symbol'):
                print(f"\n[ Análisis para: {symbol_name} ]")
                # Llamamos a una versión simplificada del reporte para cada símbolo.
                # No generamos un HTML para cada uno, solo un resumen en consola.
                self._generate_summary_for_group(symbol_trades)
        
        print("\n-------------------------------------------------")


    def _generate_report(self, trade_df: pd.DataFrame, initial_capital: float, report_title: str, report_filename: str):
        """
        Función auxiliar que genera el reporte completo de QuantStats y el resumen en consola.
        """
        # --- Cálculo de Retornos para QuantStats ---
        # Aseguramos que el índice sea de tipo datetime y esté ordenado
        trade_df['exit_time'] = pd.to_datetime(trade_df['exit_time'])
        trade_df.sort_values(by='exit_time', inplace=True)
        
        equity_curve = trade_df['pnl'].cumsum() + initial_capital
        returns = equity_curve.pct_change().fillna(0)
        returns.index = pd.to_datetime(returns.index)

        # --- Generar Reporte HTML con QuantStats ---
        # Usamos periods_per_year para anualizar correctamente las métricas.
        # 252*24 para datos horarios, 252*24*60 para datos de 1min, etc.
        qs.reports.html(returns, output=report_filename, title=report_title, periods_per_year=252*24)
        print(f"Reporte de rendimiento completo guardado en: {report_filename}")

        # --- Imprimir Métricas Clave en la Consola ---
        self._print_summary_metrics(returns, trade_df, initial_capital)


    def _generate_summary_for_group(self, symbol_trades: pd.DataFrame):
        """
        Función auxiliar que calcula e imprime un resumen de métricas para un subconjunto de trades.
        """
        total_pnl = symbol_trades['pnl'].sum()
        win_rate = (symbol_trades['pnl'] > 0).mean() if not symbol_trades.empty else 0
        total_trades = len(symbol_trades)
        avg_profit = symbol_trades[symbol_trades['pnl'] > 0]['pnl'].mean()
        avg_loss = symbol_trades[symbol_trades['pnl'] < 0]['pnl'].mean()

        print(f"  Total de Trades: {total_trades}")
        print(f"  Ganancia/Pérdida Neta: ${total_pnl:,.2f}")
        print(f"  Tasa de Acierto (Win Rate): {win_rate:.2%}")
        print(f"  Ganancia Promedio (en trades ganadores): ${avg_profit:,.2f}")
        print(f"  Pérdida Promedio (en trades perdedores): ${avg_loss:,.2f}")


    def _print_summary_metrics(self, returns: pd.Series, trade_df: pd.DataFrame, initial_capital: float):
        """
        Función auxiliar para imprimir el bloque de resumen principal.
        """
        total_pnl = trade_df['pnl'].sum()
        final_capital = initial_capital + total_pnl
        win_rate = (trade_df['pnl'] > 0).mean() if not trade_df.empty else 0
        
        # Usamos try-except para manejar casos con muy pocos datos donde las estadísticas pueden fallar.
        try:
            sharpe = qs.stats.sharpe(returns, periods=252*24)
            max_drawdown = qs.stats.max_drawdown(returns)
        except Exception:
            sharpe = 0.0
            max_drawdown = 0.0

        print(f"Periodo Analizado: {trade_df['exit_time'].min()} a {trade_df['exit_time'].max()}")
        print(f"Capital Inicial: ${initial_capital:,.2f}")
        print(f"Capital Final: ${final_capital:,.2f}")
        print(f"Ganancia/Pérdida Neta: ${total_pnl:,.2f}")
        print(f"Retorno Total: {total_pnl / initial_capital:.2%}")
        print(f"Total de Trades: {len(trade_df)}")
        print(f"Tasa de Acierto (Win Rate): {win_rate:.2%}")
        print(f"Max Drawdown: {max_drawdown:.2%}")
        print(f"Sharpe Ratio (annualized): {sharpe:.2f}")