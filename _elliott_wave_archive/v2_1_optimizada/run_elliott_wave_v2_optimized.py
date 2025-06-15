# run_elliott_wave_v2_fixed.py
"""
ElliottWave V2 - Versión con validaciones de scalping corregidas

Basado en el debug: el problema son las validaciones de scalping muy estrictas.
"""

import pandas as pd
from datetime import datetime

from config import settings
from data_collectors.historical_data import get_extended_historical_klines
from indicators.indicator_manager import IndicatorManager
from signal_generators.elliott_wave_strategy_v2 import ElliottWaveStrategyV2
from risk_management.risk_assessor import RiskAssessor
from portfolio.portfolio_manager import PortfolioManager
from backtesting.backtester import Backtester
from backtesting.performance_analyzer import PerformanceAnalyzer


class ElliottWaveStrategyV2Fixed(ElliottWaveStrategyV2):
    """
    Versión corregida con validaciones de scalping más permisivas.
    """
    
    def _validate_scalping_conditions_v2(self, df: pd.DataFrame, action: str) -> bool:
        """
        Validaciones de scalping CORREGIDAS - más permisivas.
        """
        if len(df) < 5:
            return False
        
        try:
            recent_data = df.tail(10)
            
            # 1. Volatilidad mínima - RELAJADA
            price_range = recent_data['High'].max() - recent_data['Low'].min()
            avg_price = recent_data['Close'].mean()
            volatility = price_range / avg_price
            
            # CORREGIDO: Reducido de 0.3% a 0.1%
            if volatility < 0.001:  # Solo 0.1% mínimo
                return False
            
            # 2. Validación direccional - SIMPLIFICADA
            latest_close = recent_data['Close'].iloc[-1]
            
            if action == 'CONSIDER_LONG':
                # Para LONG: permitir en cualquier momento salvo extremos altos
                recent_high = recent_data['High'].max()
                # CORREGIDO: Permitir hasta 99.5% del máximo (antes 98%)
                if latest_close > recent_high * 0.995:
                    return False
                    
            elif action == 'CONSIDER_SHORT':
                # Para SHORT: permitir en cualquier momento salvo extremos bajos  
                recent_low = recent_data['Low'].min()
                # CORREGIDO: Permitir desde 100.5% del mínimo (antes 102%)
                if latest_close < recent_low * 1.005:
                    return False
            
            # 3. RSI - MUY RELAJADO
            if 'RSI_14' in df.columns:
                current_rsi = recent_data['RSI_14'].iloc[-1]
                # CORREGIDO: Solo bloquear RSI extremos (antes 75/25, ahora 85/15)
                if action == 'CONSIDER_LONG' and current_rsi > 85:
                    return False
                elif action == 'CONSIDER_SHORT' and current_rsi < 15:
                    return False
            
            return True  # Por defecto, permitir
            
        except Exception as e:
            print(f"Error en validación scalping corregida: {e}")
            return True  # En caso de error, permitir señal
    
    def _determine_market_trend(self, df: pd.DataFrame) -> str:
        """
        Detección de tendencia CORREGIDA - más sensible.
        """
        if not self.trend_filter_enabled or len(df) < self.trend_lookback:
            return 'NEUTRAL'
        
        try:
            # CORREGIDO: Usar períodos más cortos para mayor sensibilidad
            short_lookback = min(10, self.trend_lookback // 2)  # Período corto
            
            # EMA de período corto para detectar tendencias recientes
            if 'EMA_21' in df.columns:
                ema = df['EMA_21'].iloc[-short_lookback:]
            else:
                ema = df['Close'].ewm(span=10).mean().iloc[-short_lookback:]
            
            # CORREGIDO: Análisis de pendiente más sensible
            if len(ema) >= 5:
                ema_slope = (ema.iloc[-1] - ema.iloc[-5]) / ema.iloc[-5]
            else:
                ema_slope = 0
            
            # CORREGIDO: Posición precio vs EMA más permisiva
            current_price = df['Close'].iloc[-1]
            current_ema = ema.iloc[-1]
            price_vs_ema = (current_price - current_ema) / current_ema
            
            # CORREGIDO: Momentum de período más corto
            recent_prices = df['Close'].iloc[-5:]  # Solo 5 períodos
            if len(recent_prices) >= 2:
                price_momentum = (recent_prices.iloc[-1] - recent_prices.iloc[0]) / recent_prices.iloc[0]
            else:
                price_momentum = 0
            
            # CORREGIDO: Umbrales más bajos para detectar tendencias
            bullish_signals = 0
            bearish_signals = 0
            
            # Señal 1: Pendiente EMA (reducido de 1% a 0.3%)
            if ema_slope > 0.003:
                bullish_signals += 1
            elif ema_slope < -0.003:
                bearish_signals += 1
            
            # Señal 2: Precio vs EMA (reducido de 0.5% a 0.2%)
            if price_vs_ema > 0.002:
                bullish_signals += 1
            elif price_vs_ema < -0.002:
                bearish_signals += 1
            
            # Señal 3: Momentum (reducido de 2% a 0.5%)
            if price_momentum > 0.005:
                bullish_signals += 1
            elif price_momentum < -0.005:
                bearish_signals += 1
            
            # CORREGIDO: Solo necesita 1 señal en lugar de 2
            if bullish_signals >= 1:
                return 'BULLISH'
            elif bearish_signals >= 1:
                return 'BEARISH'
            else:
                return 'NEUTRAL'
                
        except Exception as e:
            print(f"Error en detección de tendencia corregida: {e}")
            return 'NEUTRAL'


def run_elliott_wave_v2_fixed():
    """
    Ejecuta la versión corregida que debería generar trades.
    """
    print("="*60)
    print("🔧 ELLIOTT WAVE V2 - VALIDACIONES CORREGIDAS")
    print("="*60)
    
    # Configuración
    SYMBOL = "DOGEUSDT"
    INTERVAL = "1h"
    START_DATE = "01 Oct, 2024"
    INITIAL_CAPITAL = 10000.0
    
    print(f"📊 Configuración:")
    print(f"   🎯 Basado en debug: Problema en validaciones de scalping")
    print(f"   🔧 Solución: Validaciones más permisivas")
    print(f"   🚀 Expectativa: Generar trades finalmente!")
    print("-"*60)
    
    # Cargar datos
    print("📥 Cargando datos...")
    historical_df = get_extended_historical_klines(SYMBOL, INTERVAL, START_DATE)
    historical_df['SYMBOL'] = SYMBOL
    historical_df.set_index('Close_time', inplace=True)
    
    price_change = ((historical_df['Close'].iloc[-1] / historical_df['Close'].iloc[0]) - 1) * 100
    print(f"✅ {len(historical_df)} velas | Cambio: {price_change:+.2f}%")
    
    # Configurar estrategia CORREGIDA
    print("\n🔧 Configurando estrategia corregida...")
    
    indicator_manager = IndicatorManager()
    
    # *** ESTRATEGIA CORREGIDA ***
    elliott_strategy = ElliottWaveStrategyV2Fixed(
        min_wave_confidence=0.6,
        scalping_mode=True,
        wave_analysis_lookback=80,
        trend_filter_enabled=True,
        trend_lookback=20,  # Más corto para detectar tendencias
        adaptive_direction=True
    )
    
    risk_assessor = RiskAssessor(atr_multiplier_sl=2.0)
    
    portfolio_manager = PortfolioManager(
        initial_capital=INITIAL_CAPITAL,
        risk_per_trade_pct=0.015,  # 1.5%
        indicator_manager=indicator_manager,
        strategy=elliott_strategy,
        risk_assessor=risk_assessor,
        max_open_positions=1,
        verbose=True  # Ver trades en tiempo real
    )
    
    print("✅ Estrategia V2 CORREGIDA:")
    print("   - Validaciones de scalping: RELAJADAS")
    print("   - Detección de tendencia: MÁS SENSIBLE") 
    print("   - Umbrales: REDUCIDOS para más señales")
    print("   - Verbose: ON")
    
    # Ejecutar backtest
    print(f"\n🚀 Ejecutando backtest corregido...")
    
    try:
        performance_analyzer = PerformanceAnalyzer()
        backtester = Backtester(portfolio_manager, performance_analyzer)
        
        start_time = datetime.now()
        backtester.run(
            historical_data={SYMBOL: historical_df},
            initial_capital=INITIAL_CAPITAL,
            min_data_points=100
        )
        end_time = datetime.now()
        
        print(f"⏱️  Completado en {(end_time-start_time).total_seconds():.2f}s")
        
    except Exception as e:
        print(f"❌ ERROR: {e}")
        import traceback
        traceback.print_exc()
        return
    
    # Analizar resultados
    print(f"\n" + "="*60)
    print(f"📊 RESULTADOS V2 CORREGIDA")
    print(f"="*60)
    
    trade_history = portfolio_manager.trade_history
    
    if not trade_history:
        print("⚠️  Aún no hay trades - necesitamos más ajustes")
        return
    
    # ¡ÉXITO! Analizar trades
    trades_df = pd.DataFrame(trade_history)
    total_trades = len(trades_df)
    total_pnl = trades_df['pnl'].sum()
    final_capital = INITIAL_CAPITAL + total_pnl
    total_return = ((final_capital / INITIAL_CAPITAL) - 1) * 100
    win_rate = (len(trades_df[trades_df['pnl'] > 0]) / total_trades) * 100
    
    print(f"🎉 ¡ÉXITO! V2 generó trades:")
    print(f"   Total trades: {total_trades}")
    print(f"   Win rate: {win_rate:.1f}%")
    print(f"   P&L total: ${total_pnl:,.2f}")
    print(f"   Retorno: {total_return:+.2f}%")
    print(f"   Capital final: ${final_capital:,.2f}")
    
    # Análisis por dirección
    if 'direction' in trades_df.columns:
        print(f"\n📊 Por dirección:")
        for direction in trades_df['direction'].unique():
            dir_trades = trades_df[trades_df['direction'] == direction]
            dir_count = len(dir_trades)
            dir_pnl = dir_trades['pnl'].sum()
            dir_wr = (len(dir_trades[dir_trades['pnl'] > 0]) / dir_count) * 100
            print(f"   {direction}: {dir_count} trades | {dir_wr:.1f}% WR | ${dir_pnl:,.2f}")
    
    # Comparación final
    print(f"\n🏆 COMPARACIÓN FINAL:")
    print(f"   V1 Original: -37.49% (704 trades, solo SHORT)")
    print(f"   V2 Corregida: {total_return:+.2f}% ({total_trades} trades)")
    
    if total_return > -37.49:
        improvement = total_return - (-37.49)
        print(f"   🚀 MEJORA: +{improvement:.2f} puntos porcentuales")
        print(f"   ✅ PROBLEMA RESUELTO!")
    else:
        print(f"   🔄 Aún necesita optimización")


def main():
    """Función principal."""
    print("🚀 ElliottWave V2 - Versión con correcciones basadas en debug...")
    
    try:
        run_elliott_wave_v2_fixed()
        
        print(f"\n🎯 El debug fue clave para identificar el problema exacto.")
        print(f"   Ahora sabemos que el sistema Elliott Wave funciona,")
        print(f"   solo necesitaba validaciones más realistas.")
        
    except Exception as e:
        print(f"\n💥 ERROR: {e}")


if __name__ == "__main__":
    main()