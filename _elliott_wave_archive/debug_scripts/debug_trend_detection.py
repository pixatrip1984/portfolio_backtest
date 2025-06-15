# debug_trend_detection.py
"""
Debug específico para entender por qué DOGE +53% no se detecta como BULLISH
"""

import pandas as pd
import numpy as np
from datetime import datetime

from config import settings
from data_collectors.historical_data import get_extended_historical_klines
from indicators.indicator_manager import IndicatorManager


def debug_trend_detection():
    """
    Debug paso a paso de la detección de tendencia para DOGE.
    """
    print("="*60)
    print("🔍 DEBUG DETECCIÓN DE TENDENCIA - DOGE")
    print("="*60)
    
    # Cargar datos
    SYMBOL = "DOGEUSDT"
    INTERVAL = "1h"
    START_DATE = "01 Oct, 2024"
    
    historical_df = get_extended_historical_klines(SYMBOL, INTERVAL, START_DATE)
    historical_df.set_index('Close_time', inplace=True)
    
    # Agregar indicadores
    indicator_manager = IndicatorManager()
    df = indicator_manager.calculate_indicators(historical_df)
    
    # Análisis del período completo
    price_change = ((df['Close'].iloc[-1] / df['Close'].iloc[0]) - 1) * 100
    print(f"📊 DOGE Rally: {price_change:+.2f}% (debería ser BULLISH)")
    print(f"   Precio inicial: ${df['Close'].iloc[0]:.6f}")
    print(f"   Precio final: ${df['Close'].iloc[-1]:.6f}")
    print()
    
    # Test con diferentes períodos
    periods_to_test = [10, 20, 30, 50, 100]
    
    for period in periods_to_test:
        print(f"🧪 ANÁLISIS PERÍODO {period} velas:")
        
        if len(df) < period:
            print(f"   ❌ Datos insuficientes")
            continue
        
        # Tomar muestra reciente
        recent_data = df.tail(period)
        
        # === CÁLCULOS PASO A PASO ===
        
        # 1. Cambios de precio
        recent_prices = recent_data['Close']
        
        price_change_5 = (recent_prices.iloc[-1] / recent_prices.iloc[-5] - 1) if len(recent_prices) >= 5 else 0
        price_change_10 = (recent_prices.iloc[-1] / recent_prices.iloc[-10] - 1) if len(recent_prices) >= 10 else 0
        price_change_20 = (recent_prices.iloc[-1] / recent_prices.iloc[0] - 1) if len(recent_prices) >= 20 else 0
        
        print(f"   💹 Cambios de precio:")
        print(f"      5 velas: {price_change_5*100:+.2f}% (umbral: 0.1%)")
        print(f"      10 velas: {price_change_10*100:+.2f}% (umbral: 0.5%)")
        print(f"      {period} velas: {price_change_20*100:+.2f}% (umbral: 1.0%)")
        
        # 2. Señales de momentum
        momentum_signals = 0
        
        if price_change_5 > 0.001:
            momentum_signals += 1
            print(f"      ✅ Señal 5v: +1")
        elif price_change_5 < -0.001:
            momentum_signals -= 1
            print(f"      ❌ Señal 5v: -1")
        else:
            print(f"      ⚪ Señal 5v: 0")
        
        if price_change_10 > 0.005:
            momentum_signals += 2
            print(f"      ✅ Señal 10v: +2")
        elif price_change_10 < -0.005:
            momentum_signals -= 2
            print(f"      ❌ Señal 10v: -2")
        else:
            print(f"      ⚪ Señal 10v: 0")
        
        if price_change_20 > 0.01:
            momentum_signals += 3
            print(f"      ✅ Señal {period}v: +3")
        elif price_change_20 < -0.01:
            momentum_signals -= 3
            print(f"      ❌ Señal {period}v: -3")
        else:
            print(f"      ⚪ Señal {period}v: 0")
        
        # 3. Análisis de rango
        recent_10 = recent_data.tail(10)
        current_price = recent_10['Close'].iloc[-1]
        recent_high = recent_10['High'].max()
        recent_low = recent_10['Low'].min()
        
        range_position = (current_price - recent_low) / (recent_high - recent_low) if recent_high != recent_low else 0.5
        
        highs_lows_signals = 0
        if range_position > 0.6:
            highs_lows_signals += 2
            print(f"      ✅ Posición rango: {range_position:.2f} (+2)")
        elif range_position < 0.4:
            highs_lows_signals -= 2
            print(f"      ❌ Posición rango: {range_position:.2f} (-2)")
        else:
            print(f"      ⚪ Posición rango: {range_position:.2f} (0)")
        
        # 4. Análisis EMA
        ema_signals = 0
        if 'EMA_21' in recent_data.columns:
            current_ema = recent_data['EMA_21'].iloc[-1]
            price_vs_ema = (current_price / current_ema - 1) if current_ema != 0 else 0
            
            if price_vs_ema > 0.001:
                ema_signals += 1
                print(f"      ✅ Precio vs EMA: {price_vs_ema*100:+.2f}% (+1)")
            elif price_vs_ema < -0.001:
                ema_signals -= 1
                print(f"      ❌ Precio vs EMA: {price_vs_ema*100:+.2f}% (-1)")
            else:
                print(f"      ⚪ Precio vs EMA: {price_vs_ema*100:+.2f}% (0)")
            
            # Pendiente EMA
            recent_ema = recent_data['EMA_21'].tail(5)
            if len(recent_ema) >= 5:
                ema_slope = (recent_ema.iloc[-1] / recent_ema.iloc[-5] - 1) if recent_ema.iloc[-5] != 0 else 0
                
                if ema_slope > 0.001:
                    ema_signals += 1
                    print(f"      ✅ Pendiente EMA: {ema_slope*100:+.2f}% (+1)")
                elif ema_slope < -0.001:
                    ema_signals -= 1
                    print(f"      ❌ Pendiente EMA: {ema_slope*100:+.2f}% (-1)")
                else:
                    print(f"      ⚪ Pendiente EMA: {ema_slope*100:+.2f}% (0)")
        
        # 5. Score total
        total_score = momentum_signals + highs_lows_signals + ema_signals
        
        print(f"   📊 RESUMEN:")
        print(f"      Momentum: {momentum_signals}")
        print(f"      Rango: {highs_lows_signals}")
        print(f"      EMA: {ema_signals}")
        print(f"      TOTAL: {total_score}")
        
        if total_score >= 2:
            trend = "BULLISH"
            print(f"      🟢 TENDENCIA: {trend}")
        elif total_score <= -2:
            trend = "BEARISH"
            print(f"      🔴 TENDENCIA: {trend}")
        else:
            trend = "NEUTRAL"
            print(f"      ⚪ TENDENCIA: {trend}")
        
        print("-" * 50)
    
    # === ANÁLISIS ESPECÍFICO DEL PROBLEMA ===
    print(f"\n🎯 ANÁLISIS DEL PROBLEMA:")
    
    # Ver el comportamiento en diferentes segmentos del rally
    segments = [
        ("Inicio rally", df.iloc[100:200]),
        ("Medio rally", df.iloc[len(df)//2-50:len(df)//2+50]),
        ("Final rally", df.tail(100))
    ]
    
    for segment_name, segment_data in segments:
        if len(segment_data) < 20:
            continue
            
        segment_change = ((segment_data['Close'].iloc[-1] / segment_data['Close'].iloc[0]) - 1) * 100
        print(f"\n📈 {segment_name}: {segment_change:+.2f}%")
        
        # Test con la lógica perfeccionada
        test_recent = segment_data.tail(20)
        
        price_ch_5 = (test_recent['Close'].iloc[-1] / test_recent['Close'].iloc[-5] - 1) if len(test_recent) >= 5 else 0
        price_ch_10 = (test_recent['Close'].iloc[-1] / test_recent['Close'].iloc[-10] - 1) if len(test_recent) >= 10 else 0
        
        print(f"   Cambio 5v: {price_ch_5*100:+.2f}%")
        print(f"   Cambio 10v: {price_ch_10*100:+.2f}%")
        
        if price_ch_5 > 0.001 or price_ch_10 > 0.005:
            print(f"   ✅ Debería detectar BULLISH")
        else:
            print(f"   ❌ Por qué no detecta BULLISH?")
    
    # === RECOMENDACIONES ===
    print(f"\n💡 RECOMENDACIONES:")
    print(f"   Si los cambios de precio son positivos pero no se detecta BULLISH:")
    print(f"   1. Reducir umbrales aún más (0.01% en lugar de 0.1%)")
    print(f"   2. Simplificar lógica (solo cambio de precio)")
    print(f"   3. Forzar BULLISH si cambio > 10% en cualquier período")
    
    # === SOLUCIÓN FORZADA ===
    print(f"\n🔧 PRUEBA DE SOLUCIÓN FORZADA:")
    total_rally = ((df['Close'].iloc[-1] / df['Close'].iloc[0]) - 1) * 100
    
    if total_rally > 10:  # Si el rally total es > 10%
        print(f"   ✅ Rally {total_rally:+.2f}% > 10% → FORZAR BULLISH")
        print(f"   Esta lógica simple debería funcionar para DOGE")
    else:
        print(f"   ❌ Rally {total_rally:+.2f}% < 10%")


def main():
    """Función principal del debug."""
    try:
        debug_trend_detection()
        
        print(f"\n🎯 DEBUG COMPLETADO")
        print(f"   Con esta información podemos ver exactamente")
        print(f"   por qué un rally del +53% no se detecta como BULLISH")
        
    except Exception as e:
        print(f"\n💥 ERROR: {e}")
        import traceback
        traceback.print_exc()


if __name__ == "__main__":
    main()