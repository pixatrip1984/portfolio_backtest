# run_elliott_wave_v2_backtest.py
"""
Script de Backtesting para ElliottWaveStrategy V2

Prueba la estrategia optimizada con filtro de tendencia y lógica adaptativa
en el mismo período de DOGEUSDT para comparar mejoras.
"""

import pandas as pd
from datetime import datetime

# Importaciones del sistema
from config import settings
from data_collectors.historical_data import get_extended_historical_klines
from indicators.indicator_manager import IndicatorManager
from signal_generators.elliott_wave_strategy_v2 import ElliottWaveStrategyV2
from risk_management.risk_assessor import RiskAssessor
from portfolio.portfolio_manager import PortfolioManager
from backtesting.backtester import Backtester
from backtesting.performance_analyzer import PerformanceAnalyzer


def run_elliott_wave_v2_backtest():
    """
    Ejecuta backtest de la ElliottWaveStrategy V2 optimizada.
    """
    print("="*60)
    print("🌊 BACKTESTING - ELLIOTT WAVE STRATEGY V2 (OPTIMIZADA)")
    print("="*60)
    
    # --- 1. Configuración Idéntica para Comparación ---
    SYMBOL = "DOGEUSDT"
    INTERVAL = "1h"
    START_DATE = "01 Oct, 2024"  # Mismo período para comparar
    INITIAL_CAPITAL = 10000.0
    
    print(f"📊 Configuración del backtest:")
    print(f"   Símbolo: {SYMBOL}")
    print(f"   Intervalo: {INTERVAL}")
    print(f"   Periodo: {START_DATE} - presente")
    print(f"   Capital inicial: ${INITIAL_CAPITAL:,.2f}")
    print(f"   🆚 Comparando vs V1 anterior")
    print("-"*60)
    
    # --- 2. Carga de Datos ---
    print("📥 Cargando datos históricos...")
    try:
        historical_df = get_extended_historical_klines(SYMBOL, INTERVAL, START_DATE)
        
        if historical_df.empty:
            print("❌ ERROR: No se pudieron cargar datos históricos")
            return
        
        historical_df['SYMBOL'] = SYMBOL
        historical_df.set_index('Close_time', inplace=True)
        
        print(f"✅ Datos cargados exitosamente:")
        print(f"   Total de velas: {len(historical_df)}")
        print(f"   Periodo: {historical_df.index.min()} a {historical_df.index.max()}")
        
        # Estadísticas del período
        price_change = ((historical_df['Close'].iloc[-1] / historical_df['Close'].iloc[0]) - 1) * 100
        print(f"   Precio inicial: ${historical_df['Close'].iloc[0]:.6f}")
        print(f"   Precio final: ${historical_df['Close'].iloc[-1]:.6f}")
        print(f"   Cambio período: {price_change:+.2f}%")
        
    except Exception as e:
        print(f"❌ ERROR cargando datos: {e}")
        return
    
    print("-"*60)
    
    # --- 3. Configuración de Estrategia V2 ---
    print("🔧 Configurando ElliottWaveStrategy V2...")
    
    try:
        # IndicatorManager con indicadores esenciales
        indicator_manager = IndicatorManager()
        
        # *** ESTRATEGIA V2 OPTIMIZADA ***
        elliott_strategy_v2 = ElliottWaveStrategyV2(
            min_wave_confidence=0.75,      # Reducido para más señales
            scalping_mode=True,
            wave_analysis_lookback=100,
            trend_filter_enabled=True,     # NUEVO: Filtro de tendencia
            trend_lookback=50,             # NUEVO: Período de tendencia
            adaptive_direction=True        # NUEVO: Dirección adaptativa
        )
        
        # RiskAssessor optimizado
        risk_assessor = RiskAssessor(atr_multiplier_sl=1.8)  # SL ligeramente más amplio
        
        # PortfolioManager
        portfolio_manager = PortfolioManager(
            initial_capital=INITIAL_CAPITAL,
            risk_per_trade_pct=0.015,  # Reducido a 1.5% por trade (más conservador)
            indicator_manager=indicator_manager,
            strategy=elliott_strategy_v2,
            risk_assessor=risk_assessor,
            max_open_positions=1,
            verbose=False
        )
        
        print("✅ Estrategia V2 configurada:")
        print(f"   - Filtro de tendencia: ✅ ACTIVADO")
        print(f"   - Dirección adaptativa: ✅ ACTIVADO")
        print(f"   - Confianza mínima: 0.75 (reducida)")
        print(f"   - Riesgo por trade: 1.5% (conservador)")
        print(f"   - Stop loss: 1.8x ATR")
        
    except Exception as e:
        print(f"❌ ERROR configurando V2: {e}")
        return
    
    print("-"*60)
    
    # --- 4. Ejecución del Backtest V2 ---
    print("🚀 Ejecutando backtest V2...")
    
    try:
        performance_analyzer = PerformanceAnalyzer()
        backtester = Backtester(portfolio_manager, performance_analyzer)
        
        backtest_data = {SYMBOL: historical_df}
        
        start_time = datetime.now()
        backtester.run(
            historical_data=backtest_data,
            initial_capital=INITIAL_CAPITAL,
            min_data_points=150
        )
        end_time = datetime.now()
        
        execution_time = (end_time - start_time).total_seconds()
        print(f"⏱️  Backtest V2 completado en {execution_time:.2f} segundos")
        
    except Exception as e:
        print(f"❌ ERROR durante backtest V2: {e}")
        import traceback
        traceback.print_exc()
        return
    
    # --- 5. Análisis Detallado de Resultados V2 ---
    print("\n" + "="*60)
    print("📊 ANÁLISIS DE RESULTADOS V2")
    print("="*60)
    
    try:
        trade_history = portfolio_manager.trade_history
        
        if not trade_history:
            print("⚠️  No se ejecutaron trades en V2.")
            print("🔍 Posibles causas:")
            print("   - Filtros muy estrictos")
            print("   - Período sin señales claras")
            print("   - Configuración muy conservadora")
            
            # Debug info
            strategy_info = elliott_strategy_v2.get_strategy_info()
            print(f"\n🔧 Debug de estrategia V2:")
            for key, value in strategy_info.items():
                print(f"   {key}: {value}")
            return
        
        # Análisis completo de trades
        trades_df = pd.DataFrame(trade_history)
        
        # === MÉTRICAS PRINCIPALES ===
        total_trades = len(trades_df)
        winning_trades = len(trades_df[trades_df['pnl'] > 0])
        losing_trades = len(trades_df[trades_df['pnl'] < 0])
        win_rate = (winning_trades / total_trades) * 100
        
        total_pnl = trades_df['pnl'].sum()
        final_capital = INITIAL_CAPITAL + total_pnl
        total_return = ((final_capital / INITIAL_CAPITAL) - 1) * 100
        
        print(f"🎯 RESULTADOS PRINCIPALES:")
        print(f"   Total de trades: {total_trades}")
        print(f"   Trades ganadores: {winning_trades}")
        print(f"   Trades perdedores: {losing_trades}")
        print(f"   Win rate: {win_rate:.1f}%")
        print(f"   P&L total: ${total_pnl:,.2f}")
        print(f"   Capital final: ${final_capital:,.2f}")
        print(f"   Retorno total: {total_return:+.2f}%")
        
        # === COMPARACIÓN CON V1 ===
        print(f"\n📈 COMPARACIÓN V1 vs V2:")
        print(f"   V1: -37.49% | V2: {total_return:+.2f}% | Mejora: {total_return + 37.49:+.2f}pp")
        print(f"   V1: 704 trades | V2: {total_trades} trades")
        print(f"   V1: 48.7% WR | V2: {win_rate:.1f}% WR")
        
        # === ANÁLISIS POR DIRECCIÓN ===
        if 'direction' in trades_df.columns:
            direction_analysis = trades_df.groupby('direction').agg({
                'pnl': ['count', 'sum', lambda x: (x > 0).mean() * 100]
            }).round(2)
            
            print(f"\n📊 ANÁLISIS POR DIRECCIÓN:")
            for direction in trades_df['direction'].unique():
                dir_trades = trades_df[trades_df['direction'] == direction]
                dir_count = len(dir_trades)
                dir_pnl = dir_trades['pnl'].sum()
                dir_wr = (len(dir_trades[dir_trades['pnl'] > 0]) / dir_count) * 100
                
                print(f"   {direction}: {dir_count} trades | {dir_wr:.1f}% WR | ${dir_pnl:,.2f} P&L")
        
        # === MÉTRICAS ADICIONALES ===
        if total_trades > 0:
            avg_win = trades_df[trades_df['pnl'] > 0]['pnl'].mean() if winning_trades > 0 else 0
            avg_loss = trades_df[trades_df['pnl'] < 0]['pnl'].mean() if losing_trades > 0 else 0
            profit_factor = abs(avg_win * winning_trades / (avg_loss * losing_trades)) if avg_loss != 0 else float('inf')
            
            best_trade = trades_df['pnl'].max()
            worst_trade = trades_df['pnl'].min()
            
            print(f"\n💰 MÉTRICAS AVANZADAS:")
            print(f"   Ganancia promedio: ${avg_win:.2f}")
            print(f"   Pérdida promedio: ${avg_loss:.2f}")
            print(f"   Profit Factor: {profit_factor:.2f}")
            print(f"   Mejor trade: ${best_trade:.2f}")
            print(f"   Peor trade: ${worst_trade:.2f}")
        
        # === EVALUACIÓN FINAL ===
        print(f"\n🎯 EVALUACIÓN V2:")
        if total_return > 0:
            print(f"   🟢 POSITIVO: Estrategia rentable (+{total_return:.2f}%)")
        else:
            print(f"   🔴 NEGATIVO: Pérdidas ({total_return:.2f}%)")
            
        if total_return > -37.49:  # Comparación con V1
            improvement = total_return - (-37.49)
            print(f"   🚀 MEJORA vs V1: +{improvement:.2f} puntos porcentuales")
        else:
            print(f"   ⚠️  Aún necesita optimización")
        
    except Exception as e:
        print(f"❌ ERROR analizando resultados V2: {e}")
        import traceback
        traceback.print_exc()


def print_optimization_recommendations():
    """
    Recomendaciones específicas para optimizar V2.
    """
    print("\n" + "="*60)
    print("💡 RECOMENDACIONES DE OPTIMIZACIÓN V2")
    print("="*60)
    print("1. 🎛️  Si V2 tiene pocas señales:")
    print("   - Reducir min_wave_confidence a 0.65")
    print("   - Aumentar wave_analysis_lookback a 150")
    print("   - Reducir signal_cooldown a 2")
    print()
    print("2. 🔄 Si V2 mejora pero aún es negativo:")
    print("   - Probar trend_lookback = 30 (más reactivo)")
    print("   - Ajustar take_profit más conservador (1.0x)")
    print("   - Probar intervalos más largos (2h, 4h)")
    print()
    print("3. 🎯 Si V2 es positivo:")
    print("   - Optimizar risk_per_trade_pct (1% - 2.5%)")
    print("   - Probar en otros activos (BTC, ETH)")
    print("   - Implementar trailing stop dinámico")
    print()
    print("4. 📊 Próximas mejoras:")
    print("   - Filtro de volumen para calidad de señales")
    print("   - Machine learning para optimizar parámetros")
    print("   - Análisis multi-timeframe")
    print("="*60)


def compare_strategies():
    """
    Función para comparar resultados de V1 vs V2.
    """
    print("\n" + "="*60)
    print("🆚 COMPARACIÓN ESTRATÉGICA V1 vs V2")
    print("="*60)
    print("🔴 V1 (Original):")
    print("   - Solo señales SHORT")
    print("   - Sin filtro de tendencia")
    print("   - -37.49% en mercado alcista")
    print("   - 704 trades, 48.7% WR")
    print()
    print("🟢 V2 (Optimizada):")
    print("   - Señales LONG y SHORT adaptativas")
    print("   - Filtro de tendencia principal")
    print("   - Lógica de inversión inteligente")
    print("   - Take profit más conservador")
    print("   - Parámetros optimizados")
    print()
    print("🎯 Objetivo V2:")
    print("   - Rentabilidad positiva en mercados alcistas")
    print("   - Balance entre LONG y SHORT")
    print("   - Mejor win rate y profit factor")
    print("="*60)


def main():
    """
    Función principal del backtest V2.
    """
    print("🚀 Iniciando backtest ElliottWaveStrategy V2...")
    start_time = datetime.now()
    
    try:
        # Mostrar comparación antes del backtest
        compare_strategies()
        
        # Ejecutar backtest V2
        run_elliott_wave_v2_backtest()
        
        # Mostrar recomendaciones
        print_optimization_recommendations()
        
        # Tiempo total
        end_time = datetime.now()
        total_time = (end_time - start_time).total_seconds()
        print(f"\n⏱️  Tiempo total V2: {total_time:.2f} segundos")
        
        # Conclusión
        print(f"\n🎉 BACKTEST V2 COMPLETADO")
        print(f"📋 Archivos generados:")
        print(f"   - backtest_report_Portfolio.html (métricas detalladas)")
        print(f"🔄 Siguiente paso: Comparar resultados y optimizar")
        
    except KeyboardInterrupt:
        print("\n⚠️  Backtest V2 interrumpido")
    except Exception as e:
        print(f"\n💥 ERROR INESPERADO V2: {e}")
        import traceback
        traceback.print_exc()


if __name__ == "__main__":
    main()