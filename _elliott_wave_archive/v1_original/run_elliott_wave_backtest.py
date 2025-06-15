# run_elliott_wave_backtest.py
"""
Script de Backtesting para ElliottWaveStrategy

Prueba la nueva estrategia basada en ondas de Elliott específicamente 
en DOGEUSDT con configuración optimizada para scalping.
"""

import pandas as pd
from datetime import datetime

# Importaciones del sistema
from config import settings
from data_collectors.historical_data import get_extended_historical_klines
from indicators.indicator_manager import IndicatorManager
from signal_generators.elliott_wave_strategy import ElliottWaveStrategy
from risk_management.risk_assessor import RiskAssessor
from portfolio.portfolio_manager import PortfolioManager
from backtesting.backtester import Backtester
from backtesting.performance_analyzer import PerformanceAnalyzer


def run_elliott_wave_backtest():
    """
    Ejecuta un backtest de la ElliottWaveStrategy en DOGEUSDT.
    """
    print("="*60)
    print("🌊 BACKTESTING - ELLIOTT WAVE STRATEGY")
    print("="*60)
    
    # --- 1. Configuración del Backtest ---
    SYMBOL = "DOGEUSDT"
    INTERVAL = "1h"  # Scalping en 1h para balance entre señales y eficiencia
    START_DATE = "01 Oct, 2024"  # ~2.5 meses de datos para análisis robusto
    INITIAL_CAPITAL = 10000.0
    
    print(f"📊 Configuración del backtest:")
    print(f"   Símbolo: {SYMBOL}")
    print(f"   Intervalo: {INTERVAL}")
    print(f"   Periodo: {START_DATE} - presente")
    print(f"   Capital inicial: ${INITIAL_CAPITAL:,.2f}")
    print("-"*60)
    
    # --- 2. Carga de Datos Históricos ---
    print("📥 Cargando datos históricos...")
    try:
        historical_df = get_extended_historical_klines(SYMBOL, INTERVAL, START_DATE)
        
        if historical_df.empty:
            print("❌ ERROR: No se pudieron cargar datos históricos")
            return
        
        # Agregar columna de símbolo y configurar índice
        historical_df['SYMBOL'] = SYMBOL
        historical_df.set_index('Close_time', inplace=True)
        
        print(f"✅ Datos cargados exitosamente:")
        print(f"   Total de velas: {len(historical_df)}")
        print(f"   Periodo: {historical_df.index.min()} a {historical_df.index.max()}")
        print(f"   Precio inicial: ${historical_df['Close'].iloc[0]:.6f}")
        print(f"   Precio final: ${historical_df['Close'].iloc[-1]:.6f}")
        
        # Calcular estadísticas básicas del período
        price_change = ((historical_df['Close'].iloc[-1] / historical_df['Close'].iloc[0]) - 1) * 100
        max_price = historical_df['High'].max()
        min_price = historical_df['Low'].min()
        
        print(f"   Cambio de precio: {price_change:+.2f}%")
        print(f"   Rango: ${min_price:.6f} - ${max_price:.6f}")
        
    except Exception as e:
        print(f"❌ ERROR cargando datos: {e}")
        return
    
    print("-"*60)
    
    # --- 3. Configuración de Componentes ---
    print("🔧 Configurando componentes del sistema...")
    
    try:
        # IndicatorManager simplificado (placeholder)
        indicator_manager = IndicatorManager()
        
        # ElliottWaveStrategy optimizada para scalping
        elliott_strategy = ElliottWaveStrategy(
            min_wave_confidence=0.8,  # Alta confianza para mayor precisión
            scalping_mode=True,       # Optimizado para scalping
            wave_analysis_lookback=100,  # Lookback moderado para balance
            enable_both_directions=True   # Permitir LONG y SHORT
        )
        
        # RiskAssessor con configuración conservadora para scalping
        risk_assessor = RiskAssessor(atr_multiplier_sl=1.5)  # Stop loss más ajustado
        
        # PortfolioManager para backtesting
        portfolio_manager = PortfolioManager(
            initial_capital=INITIAL_CAPITAL,
            risk_per_trade_pct=0.02,  # 2% de riesgo por trade (scalping más agresivo)
            indicator_manager=indicator_manager,
            strategy=elliott_strategy,
            risk_assessor=risk_assessor,
            max_open_positions=1,  # Solo una posición para DOGEUSDT
            verbose=False  # Modo silencioso para backtest
        )
        
        print("✅ Componentes configurados:")
        print(f"   - ElliottWaveStrategy (scalping mode)")
        print(f"   - Confianza mínima: 0.8")
        print(f"   - Riesgo por trade: 2%")
        print(f"   - Stop loss: 1.5x ATR")
        
    except Exception as e:
        print(f"❌ ERROR configurando componentes: {e}")
        return
    
    print("-"*60)
    
    # --- 4. Ejecución del Backtest ---
    print("🚀 Ejecutando backtest...")
    
    try:
        # Crear analizador de rendimiento
        performance_analyzer = PerformanceAnalyzer()
        
        # Crear y ejecutar backtester
        backtester = Backtester(portfolio_manager, performance_analyzer)
        
        # Preparar datos para backtesting (el backtester espera un diccionario)
        backtest_data = {SYMBOL: historical_df}
        
        # Ejecutar el backtest
        start_time = datetime.now()
        backtester.run(
            historical_data=backtest_data,
            initial_capital=INITIAL_CAPITAL,
            min_data_points=150  # Datos mínimos antes de comenzar trading
        )
        end_time = datetime.now()
        
        execution_time = (end_time - start_time).total_seconds()
        print(f"⏱️  Backtest completado en {execution_time:.2f} segundos")
        
    except Exception as e:
        print(f"❌ ERROR durante el backtest: {e}")
        import traceback
        traceback.print_exc()
        return
    
    # --- 5. Análisis de Resultados ---
    print("\n" + "="*60)
    print("📊 ANÁLISIS DE RESULTADOS")
    print("="*60)
    
    try:
        # Obtener historial de trades
        trade_history = portfolio_manager.trade_history
        
        if not trade_history:
            print("⚠️  No se ejecutaron trades durante el backtest.")
            print("💡 Posibles causas:")
            print("   - Criterios de Elliott Wave muy estrictos")
            print("   - Período sin patrones claros")
            print("   - Configuración de confianza muy alta")
            
            # Información de debug
            strategy_info = elliott_strategy.get_strategy_info()
            print(f"\n🔍 Info de estrategia:")
            for key, value in strategy_info.items():
                print(f"   {key}: {value}")
                
            return
        
        # Mostrar estadísticas básicas de trades
        trades_df = pd.DataFrame(trade_history)
        total_trades = len(trades_df)
        winning_trades = len(trades_df[trades_df['pnl'] > 0])
        losing_trades = len(trades_df[trades_df['pnl'] < 0])
        win_rate = (winning_trades / total_trades) * 100 if total_trades > 0 else 0
        
        total_pnl = trades_df['pnl'].sum()
        final_capital = INITIAL_CAPITAL + total_pnl
        
        print(f"📈 Resumen de Trading:")
        print(f"   Total de trades: {total_trades}")
        print(f"   Trades ganadores: {winning_trades}")
        print(f"   Trades perdedores: {losing_trades}")
        print(f"   Win rate: {win_rate:.1f}%")
        print(f"   P&L total: ${total_pnl:,.2f}")
        print(f"   Capital final: ${final_capital:,.2f}")
        print(f"   Retorno total: {((final_capital/INITIAL_CAPITAL)-1)*100:+.2f}%")
        
        # Análisis por dirección
        if 'direction' in trades_df.columns:
            long_trades = trades_df[trades_df['direction'] == 'LONG']
            short_trades = trades_df[trades_df['direction'] == 'SHORT']
            
            print(f"\n📊 Análisis por dirección:")
            if not long_trades.empty:
                long_pnl = long_trades['pnl'].sum()
                long_win_rate = (len(long_trades[long_trades['pnl'] > 0]) / len(long_trades)) * 100
                print(f"   LONG trades: {len(long_trades)} | Win rate: {long_win_rate:.1f}% | P&L: ${long_pnl:,.2f}")
            
            if not short_trades.empty:
                short_pnl = short_trades['pnl'].sum()
                short_win_rate = (len(short_trades[short_trades['pnl'] > 0]) / len(short_trades)) * 100
                print(f"   SHORT trades: {len(short_trades)} | Win rate: {short_win_rate:.1f}% | P&L: ${short_pnl:,.2f}")
        
        # Mejores y peores trades
        best_trade = trades_df.loc[trades_df['pnl'].idxmax()]
        worst_trade = trades_df.loc[trades_df['pnl'].idxmin()]
        
        print(f"\n🏆 Mejor trade: ${best_trade['pnl']:.2f} ({best_trade.get('direction', 'N/A')})")
        print(f"💸 Peor trade: ${worst_trade['pnl']:.2f} ({worst_trade.get('direction', 'N/A')})")
        
        print(f"\n🎯 ¡Backtest de ElliottWaveStrategy completado!")
        
    except Exception as e:
        print(f"❌ ERROR analizando resultados: {e}")
        import traceback
        traceback.print_exc()


def print_optimization_suggestions():
    """
    Imprime sugerencias para optimizar la estrategia.
    """
    print("\n" + "="*60)
    print("💡 SUGERENCIAS DE OPTIMIZACIÓN")
    print("="*60)
    print("1. 🎛️  Ajustar parámetros:")
    print("   - Reducir min_wave_confidence si hay pocas señales")
    print("   - Aumentar wave_analysis_lookback para más contexto")
    print("   - Modificar risk_per_trade_pct según resultados")
    print()
    print("2. 📊 Probar diferentes configuraciones:")
    print("   - Intervalos: 30m, 2h, 4h")
    print("   - Períodos: últimos 6 meses, 1 año")
    print("   - Activos: BTC, ETH para comparar")
    print()
    print("3. 🔧 Mejoras técnicas:")
    print("   - Filtros adicionales de volatilidad")
    print("   - Confirmación con indicadores técnicos")
    print("   - Stop loss dinámico basado en ondas")
    print("="*60)


def main():
    """
    Función principal del script de backtesting.
    """
    start_time = datetime.now()
    
    try:
        # Ejecutar backtest
        run_elliott_wave_backtest()
        
        # Mostrar sugerencias
        print_optimization_suggestions()
        
        # Tiempo total
        end_time = datetime.now()
        total_time = (end_time - start_time).total_seconds()
        print(f"\n⏱️  Tiempo total de ejecución: {total_time:.2f} segundos")
        
    except KeyboardInterrupt:
        print("\n⚠️  Backtest interrumpido por el usuario")
    except Exception as e:
        print(f"\n💥 ERROR INESPERADO: {e}")
        import traceback
        traceback.print_exc()


if __name__ == "__main__":
    main()