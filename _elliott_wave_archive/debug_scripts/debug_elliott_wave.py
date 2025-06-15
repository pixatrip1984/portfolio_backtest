# debug_elliott_wave.py
"""
Script de Debug Específico para ElliottWaveStrategy

Analiza paso a paso dónde se bloquean las señales y por qué no se generan trades.
"""

import pandas as pd
import numpy as np
from datetime import datetime

# Importaciones del sistema
from config import settings
from data_collectors.historical_data import get_extended_historical_klines
from indicators.indicator_manager import IndicatorManager
from signal_generators.elliott_wave_strategy_v2 import ElliottWaveStrategyV2


def debug_elliott_wave_signals():
    """
    Debug detallado de por qué no se generan señales.
    """
    print("="*60)
    print("🔍 DEBUG ELLIOTT WAVE - ANÁLISIS PASO A PASO")
    print("="*60)
    
    # --- Cargar datos ---
    SYMBOL = "DOGEUSDT"
    INTERVAL = "1h"
    START_DATE = "01 Oct, 2024"
    
    print(f"📊 Cargando datos para debug...")
    historical_df = get_extended_historical_klines(SYMBOL, INTERVAL, START_DATE)
    historical_df.set_index('Close_time', inplace=True)
    
    print(f"✅ {len(historical_df)} velas cargadas")
    print(f"   Precio inicial: ${historical_df['Close'].iloc[0]:.6f}")
    print(f"   Precio final: ${historical_df['Close'].iloc[-1]:.6f}")
    print(f"   Cambio total: {((historical_df['Close'].iloc[-1]/historical_df['Close'].iloc[0])-1)*100:+.2f}%")
    
    # --- Configurar componentes ---
    print(f"\n🔧 Configurando componentes...")
    
    indicator_manager = IndicatorManager()
    df_with_indicators = indicator_manager.calculate_indicators(historical_df)
    
    # Estrategia con parámetros mínimos para debug
    strategy = ElliottWaveStrategyV2(
        min_wave_confidence=0.5,  # Muy bajo para debug
        scalping_mode=True,
        wave_analysis_lookback=50,  # Reducido para rapidez
        trend_filter_enabled=True,
        trend_lookback=20,  # Más corto para detectar tendencias
        adaptive_direction=True
    )
    
    print(f"✅ Estrategia configurada con parámetros debug")
    
    # --- Test 1: Análisis de Tendencia ---
    print(f"\n" + "="*50)
    print(f"🧪 TEST 1: ANÁLISIS DE TENDENCIA")
    print(f"="*50)
    
    # Probar diferentes períodos
    periods_to_test = [10, 20, 30, 50, 100]
    
    for period in periods_to_test:
        strategy.trend_lookback = period
        sample_data = df_with_indicators.tail(period + 50)  # Datos suficientes
        
        trend = strategy._determine_market_trend(sample_data)
        print(f"   Lookback {period:2d}: Tendencia = {trend}")
    
    # --- Test 2: Análisis de Ondas ---
    print(f"\n" + "="*50)
    print(f"🧪 TEST 2: ANÁLISIS DE ONDAS ELLIOTT")
    print(f"="*50)
    
    # Tomar muestra reciente para análisis
    recent_data = df_with_indicators.tail(200)
    
    try:
        detected_waves = strategy.taew_analyzer.analyze_elliott_waves(recent_data, 'Close')
        print(f"   Ondas detectadas: {len(detected_waves)}")
        
        if detected_waves:
            print(f"   Últimas 3 ondas:")
            for i, wave in enumerate(detected_waves[-3:]):
                direction = wave.get('direction', 'N/A')
                confidence = wave.get('confidence', 0)
                points = len(wave.get('x', []))
                print(f"      Onda {i+1}: {direction}, {points} puntos, confianza {confidence:.2f}")
        else:
            print(f"   ⚠️ No se detectaron ondas")
            
    except Exception as e:
        print(f"   ❌ Error en análisis de ondas: {e}")
    
    # --- Test 3: Generación de Señales Paso a Paso ---
    print(f"\n" + "="*50)
    print(f"🧪 TEST 3: GENERACIÓN DE SEÑALES (PASO A PASO)")
    print(f"="*50)
    
    # Test con diferentes confianzas
    confidence_levels = [0.3, 0.5, 0.6, 0.7, 0.8, 0.9]
    
    for conf in confidence_levels:
        strategy.min_wave_confidence = conf
        signal = strategy.check_signal(recent_data)
        print(f"   Confianza {conf:.1f}: Señal = {signal}")
    
    # --- Test 4: Debug de Validaciones de Scalping ---
    print(f"\n" + "="*50)
    print(f"🧪 TEST 4: VALIDACIONES DE SCALPING")
    print(f"="*50)
    
    # Test manual de validaciones
    latest_candle = recent_data.iloc[-1]
    
    print(f"   Datos de la vela más reciente:")
    print(f"      Close: ${latest_candle['Close']:.6f}")
    print(f"      High: ${latest_candle['High']:.6f}")
    print(f"      Low: ${latest_candle['Low']:.6f}")
    print(f"      ATR_14: {latest_candle.get('ATR_14', 'N/A')}")
    print(f"      RSI_14: {latest_candle.get('RSI_14', 'N/A')}")
    
    # Probar validaciones manualmente
    for action in ['CONSIDER_LONG', 'CONSIDER_SHORT']:
        is_valid = strategy._validate_scalping_conditions_v2(recent_data, action)
        print(f"   Validación {action}: {'✅ PASA' if is_valid else '❌ FALLA'}")
    
    # --- Test 5: Forzar Señales (Sin Filtros) ---
    print(f"\n" + "="*50)
    print(f"🧪 TEST 5: FORZAR SEÑALES (SIN FILTROS)")
    print(f"="*50)
    
    # Temporalmente deshabilitar filtros
    strategy.min_wave_confidence = 0.1  # Muy bajo
    strategy.trend_filter_enabled = False  # Sin filtro de tendencia
    strategy.scalping_mode = False  # Sin validaciones de scalping
    
    forced_signal = strategy.check_signal(recent_data)
    print(f"   Señal SIN FILTROS: {forced_signal}")
    
    # Reactivar filtros y probar uno por uno
    strategy.trend_filter_enabled = True
    signal_with_trend = strategy.check_signal(recent_data)
    print(f"   Señal CON filtro tendencia: {signal_with_trend}")
    
    strategy.scalping_mode = True
    signal_with_scalping = strategy.check_signal(recent_data)
    print(f"   Señal CON scalping: {signal_with_scalping}")
    
    strategy.min_wave_confidence = 0.6
    signal_with_confidence = strategy.check_signal(recent_data)
    print(f"   Señal CON confianza 0.6: {signal_with_confidence}")
    
    # --- Test 6: Análisis de Volatilidad y Condiciones de Mercado ---
    print(f"\n" + "="*50)
    print(f"🧪 TEST 6: CONDICIONES DE MERCADO")
    print(f"="*50)
    
    recent_10 = recent_data.tail(10)
    
    # Calcular volatilidad
    price_range = recent_10['High'].max() - recent_10['Low'].min()
    avg_price = recent_10['Close'].mean()
    volatility = price_range / avg_price
    
    print(f"   Volatilidad reciente: {volatility:.4f} ({volatility*100:.2f}%)")
    print(f"   Mínimo requerido: 0.003 (0.3%)")
    print(f"   ¿Cumple volatilidad?: {'✅ SÍ' if volatility >= 0.003 else '❌ NO'}")
    
    # Posición de precio
    current_price = recent_10['Close'].iloc[-1]
    recent_high = recent_10['High'].max()
    recent_low = recent_10['Low'].min()
    
    position_vs_high = current_price / recent_high
    position_vs_low = current_price / recent_low
    
    print(f"   Precio actual vs máximo reciente: {position_vs_high:.3f}")
    print(f"   Precio actual vs mínimo reciente: {position_vs_low:.3f}")
    
    # --- Conclusiones y Recomendaciones ---
    print(f"\n" + "="*60)
    print(f"🎯 CONCLUSIONES DEL DEBUG")
    print(f"="*60)
    
    print(f"📋 Resumen de tests:")
    print(f"   1. Tendencia: Verificar si detecta correctamente")
    print(f"   2. Ondas: {len(detected_waves) if 'detected_waves' in locals() else 0} detectadas")
    print(f"   3. Señales: Probar diferentes confianzas")
    print(f"   4. Scalping: Verificar validaciones")
    print(f"   5. Sin filtros: {forced_signal if 'forced_signal' in locals() else 'N/A'}")
    print(f"   6. Volatilidad: {volatility*100:.2f}% ({'OK' if volatility >= 0.003 else 'BAJA'})")
    
    print(f"\n💡 ACCIONES RECOMENDADAS:")
    if volatility < 0.003:
        print(f"   - Reducir umbral de volatilidad de 0.3% a 0.1%")
    
    if len(detected_waves) == 0:
        print(f"   - Problema en detección de ondas Elliott")
    elif forced_signal == 'HOLD':
        print(f"   - Problema en lógica básica de señales")
    else:
        print(f"   - Los filtros están bloqueando señales válidas")
        print(f"   - Relajar filtros de confianza y tendencia")


def main():
    """Función principal de debug."""
    try:
        debug_elliott_wave_signals()
        
        print(f"\n🚀 DEBUG COMPLETADO")
        print(f"   Con esta información podemos identificar exactamente")
        print(f"   dónde está el problema y solucionarlo específicamente.")
        
    except Exception as e:
        print(f"\n💥 ERROR EN DEBUG: {e}")
        import traceback
        traceback.print_exc()


if __name__ == "__main__":
    main()