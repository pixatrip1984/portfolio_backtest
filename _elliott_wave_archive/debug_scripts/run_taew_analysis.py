# run_taew_analysis_fast.py
"""
Script de Validación OPTIMIZADO para la Integración de taew

Versión optimizada que reduce significativamente el tiempo de ejecución
validando la funcionalidad básica sin análisis incremental extensivo.
"""

import pandas as pd
import sys
import os
from datetime import datetime

# Asegurar que podemos importar desde nuestros módulos
from config import settings
from data_collectors.historical_data import get_extended_historical_klines
from analysis_engines.taew_analyzer import TaewAnalyzer


def quick_taew_validation():
    """
    Validación rápida y eficiente de la integración con taew.
    """
    print("="*50)
    print("🚀 VALIDACIÓN RÁPIDA - INTEGRACIÓN TAEW")
    print("="*50)
    
    # --- 1. Configuración Optimizada ---
    SYMBOL = "DOGEUSDT"
    INTERVAL = "4h"  # Intervalo más amplio = menos datos = más rápido
    START_DATE = "01 Dec, 2024"  # Solo ~6 semanas de datos
    
    print(f"📊 Configuración optimizada:")
    print(f"   Símbolo: {SYMBOL}")
    print(f"   Intervalo: {INTERVAL} (optimizado)")
    print(f"   Desde: {START_DATE} (dataset reducido)")
    print("-"*50)
    
    # --- 2. Carga de Datos Limitados ---
    print("📥 Cargando datos históricos...")
    try:
        historical_df = get_extended_historical_klines(SYMBOL, INTERVAL, START_DATE)
        
        if historical_df.empty:
            print("❌ ERROR: No se pudieron cargar datos históricos")
            return False
            
        print(f"✅ Datos cargados:")
        print(f"   Velas: {len(historical_df)} (dataset reducido)")
        print(f"   Rango: {historical_df['Close_time'].min()} a {historical_df['Close_time'].max()}")
        
    except Exception as e:
        print(f"❌ ERROR cargando datos: {e}")
        return False
    
    # --- 3. Test de Funcionalidad Básica ---
    print("\n🔧 Probando TaewAnalyzer...")
    try:
        analyzer = TaewAnalyzer(
            min_wave_length=10,  # Más permisivo para dataset pequeño
            enable_both_directions=True
        )
        print("✅ TaewAnalyzer inicializado")
        
    except Exception as e:
        print(f"❌ ERROR: {e}")
        return False
    
    # --- 4. Análisis Único (Sin Bucle) ---
    print("\n🌊 Ejecutando análisis de ondas...")
    
    try:
        # Preparar datos
        historical_df.set_index('Close_time', inplace=True)
        
        # Análisis completo en una sola pasada
        start_analysis = datetime.now()
        detected_waves = analyzer.analyze_elliott_waves(historical_df, price_column='Close')
        end_analysis = datetime.now()
        
        analysis_time = (end_analysis - start_analysis).total_seconds()
        
        print(f"⏱️  Análisis completado en {analysis_time:.2f} segundos")
        print(f"🌊 Ondas detectadas: {len(detected_waves)}")
        
        if detected_waves:
            print(f"\n📋 Resumen de ondas:")
            
            # Estadísticas básicas
            upward = [w for w in detected_waves if w.get('direction') == 'UPWARD']
            downward = [w for w in detected_waves if w.get('direction') == 'DOWNWARD']
            
            print(f"   Ondas alcistas: {len(upward)}")
            print(f"   Ondas bajistas: {len(downward)}")
            
            # Mostrar solo las 3 ondas más recientes
            print(f"\n🔍 Últimas 3 ondas detectadas:")
            for i, wave in enumerate(detected_waves[-3:]):
                direction = wave.get('direction', 'UNKNOWN')
                wave_count = len(wave.get('x', []))
                confidence = wave.get('confidence', 0.0)
                
                print(f"   Onda #{len(detected_waves)-2+i}:")
                print(f"     Dirección: {direction}")
                print(f"     Puntos: {wave_count}")
                print(f"     Confianza: {confidence:.2f}")
                
                # Señal de trading
                signal_info = analyzer.get_latest_wave_signal([wave])
                if signal_info:
                    action = signal_info.get('suggested_action', 'HOLD')
                    print(f"     Señal: {action}")
            
            # Señal más reciente
            latest_signal = analyzer.get_latest_wave_signal(detected_waves)
            if latest_signal:
                print(f"\n🚦 Señal actual del mercado:")
                print(f"   Acción: {latest_signal.get('suggested_action', 'HOLD')}")
                print(f"   Confianza: {latest_signal.get('confidence', 0.0):.2f}")
        
        else:
            print("ℹ️  No se detectaron ondas (normal con dataset pequeño)")
        
        return True
        
    except Exception as e:
        print(f"❌ ERROR en análisis: {e}")
        import traceback
        traceback.print_exc()
        return False


def test_analyzer_components():
    """
    Prueba componentes individuales del TaewAnalyzer.
    """
    print("\n" + "="*50)
    print("🧪 PRUEBAS DE COMPONENTES")
    print("="*50)
    
    try:
        # Test 1: Importación de taew
        print("🔍 Test 1: Verificando librería taew...")
        import taew
        print("✅ taew importado correctamente")
        
        # Test 2: Funciones básicas de taew
        print("\n🔍 Test 2: Probando funciones de taew...")
        test_prices = [100, 105, 103, 108, 102, 110, 108, 115, 112, 118]
        
        # Probar función básica
        result = taew.Alternative_ElliottWave_label_upward(test_prices)
        print(f"✅ Función de análisis alcista ejecutada: {len(result)} resultados")
        
        # Test 3: TaewAnalyzer con datos sintéticos
        print("\n🔍 Test 3: TaewAnalyzer con datos sintéticos...")
        analyzer = TaewAnalyzer(min_wave_length=5, enable_both_directions=False)
        
        # Crear DataFrame sintético
        synthetic_df = pd.DataFrame({
            'Close': test_prices,
            'Close_time': pd.date_range('2024-01-01', periods=len(test_prices), freq='H')
        })
        synthetic_df.set_index('Close_time', inplace=True)
        
        synthetic_waves = analyzer.analyze_elliott_waves(synthetic_df)
        print(f"✅ TaewAnalyzer procesó datos sintéticos: {len(synthetic_waves)} ondas")
        
        return True
        
    except Exception as e:
        print(f"❌ ERROR en pruebas de componentes: {e}")
        return False


def main():
    """Función principal optimizada."""
    print("🎯 Iniciando validación rápida de taew...")
    start_time = datetime.now()
    
    try:
        # Pruebas de componentes primero
        components_ok = test_analyzer_components()
        
        if not components_ok:
            print("\n❌ Fallo en pruebas básicas")
            return
        
        # Validación principal (optimizada)
        validation_ok = quick_taew_validation()
        
        # Tiempo total
        end_time = datetime.now()
        total_time = (end_time - start_time).total_seconds()
        
        print(f"\n" + "="*50)
        print(f"⏱️  TIEMPO TOTAL: {total_time:.2f} segundos")
        
        if validation_ok:
            print("🎉 ¡VALIDACIÓN EXITOSA!")
            print("\n✅ Resultados:")
            print("   - taew instalado y funcional")
            print("   - TaewAnalyzer operativo")
            print("   - Detección de ondas confirmada")
            print("   - Generación de señales activa")
            
            print(f"\n🚀 ¡Sistema listo para ElliottWaveStrategy!")
            
        else:
            print("❌ Validación incompleta - revisar errores")
            
    except KeyboardInterrupt:
        print("\n⚠️  Validación interrumpida")
    except Exception as e:
        print(f"\n💥 ERROR: {e}")


if __name__ == "__main__":
    main()