# signal_generators/elliott_wave_strategy.py
"""
ElliottWaveStrategy - Estrategia de Scalping basada en Ondas de Elliott

Esta estrategia utiliza el análisis estructural de ondas de Elliott para 
generar señales de trading de alta frecuencia optimizadas para scalping.
"""

import pandas as pd
from typing import Dict, List, Optional
from analysis_engines.taew_analyzer import TaewAnalyzer


class ElliottWaveStrategy:
    """
    Estrategia de trading basada en análisis de Ondas de Elliott.
    
    Optimizada para scalping con:
    - Detección rápida de finales de ondas
    - Señales de alta probabilidad
    - Gestión eficiente de memoria
    - Timeframes cortos
    """
    
    def __init__(self, 
                 min_wave_confidence: float = 0.7,
                 scalping_mode: bool = True,
                 wave_analysis_lookback: int = 50,
                 enable_both_directions: bool = True):
        """
        Inicializa la estrategia de Elliott Wave para scalping.
        
        Args:
            min_wave_confidence: Confianza mínima requerida para generar señales (0.0-1.0)
            scalping_mode: Si True, optimiza para operaciones rápidas
            wave_analysis_lookback: Número de velas a analizar (menor = más rápido)
            enable_both_directions: Si True, permite señales LONG y SHORT
        """
        self.min_wave_confidence = min_wave_confidence
        self.scalping_mode = scalping_mode
        self.wave_analysis_lookback = wave_analysis_lookback
        self.enable_both_directions = enable_both_directions
        
        # Configurar TaewAnalyzer para scalping
        min_wave_length = 10 if scalping_mode else 20
        
        self.taew_analyzer = TaewAnalyzer(
            min_wave_length=min_wave_length,
            enable_both_directions=enable_both_directions
        )
        
        # Cache para optimización
        self.last_analysis_length = 0
        self.last_signal = 'HOLD'
        self.last_wave_signal = None
        
        # Configuración específica para scalping
        if scalping_mode:
            self.signal_cooldown = 5  # Evitar señales muy frecuentes
            self.last_signal_bar = -999
        
        # Compatibilidad con PortfolioManager existente
        # El PortfolioManager espera este atributo de las estrategias anteriores
        self.middle_band_col = None  # No usamos Bollinger Bands, pero mantenemos compatibilidad
        
        print(f"ElliottWaveStrategy inicializada:")
        print(f"  - Modo scalping: {scalping_mode}")
        print(f"  - Confianza mínima: {min_wave_confidence}")
        print(f"  - Lookback: {wave_analysis_lookback} velas")
        print(f"  - Direcciones: {'Ambas' if enable_both_directions else 'Solo LONG'}")

    def check_signal(self, df: pd.DataFrame) -> str:
        """
        Analiza el DataFrame y genera señales basadas en ondas de Elliott.
        
        Args:
            df: DataFrame con datos OHLCV
            
        Returns:
            str: Señal generada ('BUY', 'SELL', 'HOLD')
        """
        # Validaciones básicas
        if df.empty or len(df) < self.wave_analysis_lookback:
            return 'HOLD'
        
        try:
            # Optimización para scalping: usar solo datos recientes
            if self.scalping_mode:
                analysis_df = df.tail(self.wave_analysis_lookback).copy()
            else:
                analysis_df = df.copy()
            
            # Optimización: evitar recálculo si los datos no han cambiado significativamente
            if len(analysis_df) == self.last_analysis_length and self.scalping_mode:
                return self.last_signal
            
            # Configurar índice temporal para el analyzer
            if 'Close_time' in analysis_df.columns:
                analysis_df.set_index('Close_time', inplace=True)
            elif analysis_df.index.name != 'Close_time':
                # Si no hay Close_time, usar el índice existente
                pass
            
            # Ejecutar análisis de ondas
            detected_waves = self.taew_analyzer.analyze_elliott_waves(
                analysis_df, price_column='Close'
            )
            
            # Generar señal basada en las ondas detectadas
            signal = self._generate_trading_signal(detected_waves, analysis_df)
            
            # Actualizar cache
            self.last_analysis_length = len(analysis_df)
            self.last_signal = signal
            
            return signal
            
        except Exception as e:
            print(f"Error en ElliottWaveStrategy.check_signal: {e}")
            return 'HOLD'

    def _generate_trading_signal(self, detected_waves: List[Dict], df: pd.DataFrame) -> str:
        """
        Genera señales de trading basadas en las ondas detectadas.
        
        Args:
            detected_waves: Lista de ondas detectadas por TaewAnalyzer
            df: DataFrame con datos de precios
            
        Returns:
            str: Señal de trading ('BUY', 'SELL', 'HOLD')
        """
        if not detected_waves:
            return 'HOLD'
        
        # Obtener la señal más reciente del analyzer
        latest_signal_info = self.taew_analyzer.get_latest_wave_signal(detected_waves)
        
        if not latest_signal_info:
            return 'HOLD'
        
        # Verificar confianza mínima
        confidence = latest_signal_info.get('confidence', 0.0)
        if confidence < self.min_wave_confidence:
            return 'HOLD'
        
        # Obtener acción sugerida
        suggested_action = latest_signal_info.get('suggested_action', 'HOLD')
        
        # Filtros adicionales para scalping
        if self.scalping_mode:
            # Verificar cooldown entre señales
            current_bar = len(df) - 1
            if current_bar - self.last_signal_bar < self.signal_cooldown:
                return 'HOLD'
            
            # Validar momentum adicional para scalping
            if not self._validate_scalping_conditions(df, suggested_action):
                return 'HOLD'
        
        # Convertir acción de Elliott Wave a señal de trading
        trading_signal = self._convert_wave_action_to_signal(suggested_action)
        
        if trading_signal != 'HOLD':
            self.last_signal_bar = len(df) - 1
            self.last_wave_signal = latest_signal_info
        
        return trading_signal

    def _convert_wave_action_to_signal(self, wave_action: str) -> str:
        """
        Convierte la acción sugerida por Elliott Wave a señal de trading.
        
        Args:
            wave_action: Acción sugerida ('CONSIDER_LONG', 'CONSIDER_SHORT', 'HOLD')
            
        Returns:
            str: Señal de trading ('BUY', 'SELL', 'HOLD')
        """
        conversion_map = {
            'CONSIDER_LONG': 'BUY',
            'CONSIDER_SHORT': 'SELL',
            'HOLD': 'HOLD'
        }
        
        return conversion_map.get(wave_action, 'HOLD')

    def _validate_scalping_conditions(self, df: pd.DataFrame, action: str) -> bool:
        """
        Validaciones adicionales específicas para scalping.
        
        Args:
            df: DataFrame con datos de precios
            action: Acción propuesta
            
        Returns:
            bool: True si las condiciones de scalping se cumplen
        """
        if len(df) < 5:
            return False
        
        try:
            recent_data = df.tail(5)
            
            # Validar volatilidad mínima para scalping
            price_range = recent_data['High'].max() - recent_data['Low'].min()
            avg_price = recent_data['Close'].mean()
            volatility = price_range / avg_price
            
            # Requerir volatilidad mínima del 0.5% para scalping
            if volatility < 0.005:
                return False
            
            # Validar volumen si está disponible
            if 'Volume' in df.columns:
                recent_volume = recent_data['Volume'].mean()
                if recent_volume <= 0:
                    return False
            
            # Validación direccional específica
            if action == 'CONSIDER_SHORT':
                # Para SHORT: verificar que el precio reciente esté alto
                latest_close = recent_data['Close'].iloc[-1]
                recent_high = recent_data['High'].max()
                if latest_close < recent_high * 0.98:  # Al menos cerca del máximo reciente
                    return False
            
            elif action == 'CONSIDER_LONG':
                # Para LONG: verificar que el precio reciente esté bajo
                latest_close = recent_data['Close'].iloc[-1]
                recent_low = recent_data['Low'].min()
                if latest_close > recent_low * 1.02:  # Al menos cerca del mínimo reciente
                    return False
            
            return True
            
        except Exception as e:
            print(f"Error validando condiciones de scalping: {e}")
            return False

    def get_strategy_info(self) -> Dict:
        """
        Retorna información sobre el estado actual de la estrategia.
        
        Returns:
            Dict: Información de estado de la estrategia
        """
        return {
            'strategy_name': 'ElliottWaveStrategy',
            'mode': 'scalping' if self.scalping_mode else 'standard',
            'min_confidence': self.min_wave_confidence,
            'lookback_period': self.wave_analysis_lookback,
            'last_signal': self.last_signal,
            'last_wave_signal': self.last_wave_signal,
            'both_directions': self.enable_both_directions
        }

    def reset_cache(self):
        """
        Resetea el cache interno de la estrategia.
        Útil para reiniciar el análisis o cambiar de activo.
        """
        self.last_analysis_length = 0
        self.last_signal = 'HOLD'
        self.last_wave_signal = None
        self.last_signal_bar = -999
        self.taew_analyzer.last_processed_length = 0
        self.taew_analyzer.cached_waves = []
        
        print("Cache de ElliottWaveStrategy reseteado")

    def get_take_profit_price(self, current_candle: pd.Series, direction: str) -> float:
        """
        Calcula el precio de take profit para Elliott Wave basado en la estructura de ondas.
        
        Args:
            current_candle: Serie con datos de la vela actual
            direction: Dirección del trade ('LONG' o 'SHORT')
            
        Returns:
            float: Precio de take profit calculado
        """
        try:
            # Para Elliott Wave, usamos un enfoque de projección de precio
            # basado en la volatilidad reciente y la estructura de ondas
            
            current_price = current_candle['Close']
            
            # Usar High/Low reciente como referencia para proyecciones
            if direction == 'LONG':
                # Para LONG: objetivo es un nivel de resistencia proyectado
                # Usar el rango reciente como guía
                recent_range = current_candle.get('High', current_price) - current_candle.get('Low', current_price)
                take_profit = current_price + (recent_range * 1.5)  # Proyección 1.5x el rango
                
            elif direction == 'SHORT':
                # Para SHORT: objetivo es un nivel de soporte proyectado
                recent_range = current_candle.get('High', current_price) - current_candle.get('Low', current_price)
                take_profit = current_price - (recent_range * 1.5)  # Proyección 1.5x el rango
                
            else:
                take_profit = current_price  # Fallback
            
            return take_profit
            
        except Exception as e:
            print(f"Error calculando take profit Elliott Wave: {e}")
            return current_candle['Close']  # Fallback al precio actual

    def update_parameters(self, **kwargs):
        """
        Actualiza parámetros de la estrategia dinámicamente.
        
        Args:
            **kwargs: Parámetros a actualizar
        """
        if 'min_wave_confidence' in kwargs:
            self.min_wave_confidence = kwargs['min_wave_confidence']
            print(f"Confianza mínima actualizada a: {self.min_wave_confidence}")
        
        if 'wave_analysis_lookback' in kwargs:
            self.wave_analysis_lookback = kwargs['wave_analysis_lookback']
            print(f"Lookback actualizado a: {self.wave_analysis_lookback}")
        
        if 'scalping_mode' in kwargs:
            self.scalping_mode = kwargs['scalping_mode']
            print(f"Modo scalping: {self.scalping_mode}")