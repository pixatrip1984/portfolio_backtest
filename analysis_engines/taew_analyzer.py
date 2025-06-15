# analysis_engines/taew_analyzer.py
"""
TaewAnalyzer - Wrapper para la librería taew

Este módulo encapsula y estandariza el uso de la librería taew para el análisis 
de Ondas de Elliott, proporcionando una interfaz consistente para nuestro sistema 
de trading algorítmico.
"""

import pandas as pd
import numpy as np
from typing import List, Dict, Optional, Union

try:
    import taew
    TAEW_AVAILABLE = True
except ImportError:
    TAEW_AVAILABLE = False
    print("ADVERTENCIA: taew no está instalado. Ejecute: pip install taew")


class TaewAnalyzer:
    """
    Wrapper para la librería taew que estandariza el análisis de Ondas de Elliott.
    
    Esta clase proporciona una interfaz simplificada para identificar ondas 
    impulsivas y correctivas en datos de precios históricos.
    """
    
    def __init__(self, min_wave_length: int = 10, enable_both_directions: bool = True):
        """
        Inicializa el analizador de ondas de Elliott.
        
        Args:
            min_wave_length: Longitud mínima requerida para considerar una onda válida
            enable_both_directions: Si True, analiza ondas alcistas y bajistas
        """
        if not TAEW_AVAILABLE:
            raise ImportError("La librería taew no está disponible. Instale con: pip install taew")
        
        self.min_wave_length = min_wave_length
        self.enable_both_directions = enable_both_directions
        
        # Cache para almacenar resultados previos y evitar recálculos innecesarios
        self.last_processed_length = 0
        self.cached_waves = []
        
        print(f"TaewAnalyzer inicializado:")
        print(f"  - Longitud mínima de onda: {min_wave_length}")
        print(f"  - Análisis bidireccional: {enable_both_directions}")

    def analyze_elliott_waves(self, df: pd.DataFrame, price_column: str = 'Close') -> List[Dict]:
        """
        Analiza las ondas de Elliott en los datos de precios proporcionados.
        
        Args:
            df: DataFrame con datos OHLCV
            price_column: Nombre de la columna de precios a analizar
            
        Returns:
            Lista de diccionarios con información de ondas detectadas
        """
        if df.empty or len(df) < self.min_wave_length:
            return []
        
        # Optimización: solo procesar nuevos datos si el DataFrame ha crecido
        if len(df) == self.last_processed_length:
            return self.cached_waves
        
        try:
            # Extraer la serie de precios como array numpy
            prices = df[price_column].values.astype(np.float64)
            
            detected_waves = []
            
            # Análizar ondas alcistas (impulsivas hacia arriba)
            if self.enable_both_directions or True:  # Siempre analizar alcistas por defecto
                upward_waves = self._detect_upward_waves(prices)
                detected_waves.extend(upward_waves)
            
            # Analizar ondas bajistas (impulsivas hacia abajo)
            if self.enable_both_directions:
                downward_waves = self._detect_downward_waves(prices)
                detected_waves.extend(downward_waves)
            
            # Agregar información de tiempo basada en el índice del DataFrame
            for wave in detected_waves:
                wave['timestamps'] = self._map_indices_to_timestamps(wave['z'], df)
            
            # Filtrar ondas por longitud mínima
            filtered_waves = [w for w in detected_waves if len(w['x']) >= 5]  # Ondas completas 12345
            
            # Actualizar cache
            self.last_processed_length = len(df)
            self.cached_waves = filtered_waves
            
            return filtered_waves
            
        except Exception as e:
            print(f"Error en análisis de ondas de Elliott: {e}")
            return []

    def _detect_upward_waves(self, prices: np.ndarray) -> List[Dict]:
        """Detecta ondas impulsivas alcistas usando taew."""
        try:
            # Usar el método alternativo que incluye validación de Fibonacci
            upward_waves = taew.Alternative_ElliottWave_label_upward(prices.tolist())
            
            # Estandarizar el formato de salida
            standardized_waves = []
            for wave in upward_waves:
                standardized_wave = {
                    'direction': 'UPWARD',
                    'type': 'IMPULSE',
                    'x': wave.get('x', []),  # Precios de los puntos de la onda
                    'z': wave.get('z', []),  # Índices temporales de los puntos
                    'wave_count': len(wave.get('x', [])),
                    'search_index': wave.get('searchIndex', -1),
                    'confidence': self._calculate_confidence(wave)
                }
                standardized_waves.append(standardized_wave)
            
            return standardized_waves
            
        except Exception as e:
            print(f"Error detectando ondas alcistas: {e}")
            return []

    def _detect_downward_waves(self, prices: np.ndarray) -> List[Dict]:
        """Detecta ondas impulsivas bajistas usando taew."""
        try:
            downward_waves = taew.Alternative_ElliottWave_label_downward(prices.tolist())
            
            standardized_waves = []
            for wave in downward_waves:
                standardized_wave = {
                    'direction': 'DOWNWARD',
                    'type': 'IMPULSE',
                    'x': wave.get('x', []),
                    'z': wave.get('z', []),
                    'wave_count': len(wave.get('x', [])),
                    'search_index': wave.get('searchIndex', -1),
                    'confidence': self._calculate_confidence(wave)
                }
                standardized_waves.append(standardized_wave)
            
            return standardized_waves
            
        except Exception as e:
            print(f"Error detectando ondas bajistas: {e}")
            return []

    def _map_indices_to_timestamps(self, indices: List[int], df: pd.DataFrame) -> List:
        """Mapea los índices de las ondas a timestamps del DataFrame."""
        try:
            timestamps = []
            for idx in indices:
                if 0 <= idx < len(df):
                    # Usar el índice del DataFrame (que debería ser timestamp)
                    timestamps.append(df.index[idx])
                else:
                    timestamps.append(None)
            return timestamps
        except Exception:
            return [None] * len(indices)

    def _calculate_confidence(self, wave: Dict) -> float:
        """
        Calcula un score de confianza básico para la onda detectada.
        
        Por ahora es un placeholder que se puede mejorar con criterios más sofisticados.
        """
        # Score básico basado en la completitud de la onda
        x_points = wave.get('x', [])
        if len(x_points) >= 6:  # Onda completa 12345 + confirmación
            return 0.9
        elif len(x_points) == 5:  # Onda completa 12345
            return 0.8
        elif len(x_points) >= 3:  # Onda parcial
            return 0.6
        else:
            return 0.3

    def get_latest_wave_signal(self, detected_waves: List[Dict]) -> Optional[Dict]:
        """
        Analiza las ondas detectadas y retorna la señal más reciente para trading.
        
        Args:
            detected_waves: Lista de ondas detectadas por analyze_elliott_waves()
            
        Returns:
            Diccionario con información de la señal o None si no hay señales
        """
        if not detected_waves:
            return None
        
        # Ordenar ondas por el último punto temporal (más reciente primero)
        sorted_waves = sorted(detected_waves, 
                            key=lambda w: max(w.get('z', [0])), 
                            reverse=True)
        
        latest_wave = sorted_waves[0]
        
        # Determinar el tipo de señal basado en la onda más reciente
        signal_info = {
            'wave_direction': latest_wave['direction'],
            'wave_type': latest_wave['type'],
            'wave_points': len(latest_wave.get('x', [])),
            'confidence': latest_wave.get('confidence', 0.0),
            'suggested_action': self._determine_trading_action(latest_wave),
            'wave_data': latest_wave
        }
        
        return signal_info

    def _determine_trading_action(self, wave: Dict) -> str:
        """
        Determina la acción de trading sugerida basada en la onda detectada.
        
        Esta es una lógica básica que se puede refinar posteriormente.
        """
        direction = wave.get('direction', '')
        wave_count = len(wave.get('x', []))
        
        # Lógica básica: buscar finales de ondas correctivas para entradas
        if direction == 'DOWNWARD' and wave_count >= 5:
            # Final de onda correctiva bajista -> posible entrada LONG
            return 'CONSIDER_LONG'
        elif direction == 'UPWARD' and wave_count >= 5:
            # Final de onda impulsiva alcista -> posible salida LONG o entrada SHORT
            return 'CONSIDER_SHORT'
        else:
            return 'HOLD'

    def print_wave_summary(self, detected_waves: List[Dict]) -> None:
        """Imprime un resumen legible de las ondas detectadas."""
        if not detected_waves:
            print("No se detectaron ondas de Elliott.")
            return
        
        print(f"\n=== RESUMEN DE ONDAS DE ELLIOTT ===")
        print(f"Total de ondas detectadas: {len(detected_waves)}")
        
        for i, wave in enumerate(detected_waves):
            direction = wave.get('direction', 'UNKNOWN')
            wave_count = len(wave.get('x', []))
            confidence = wave.get('confidence', 0.0)
            
            print(f"\nOnda #{i+1}:")
            print(f"  Dirección: {direction}")
            print(f"  Puntos: {wave_count}")
            print(f"  Confianza: {confidence:.2f}")
            print(f"  Precios: {wave.get('x', [])}")
            
        print(f"{'='*35}")