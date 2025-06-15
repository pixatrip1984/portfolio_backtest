# signal_generators/elliott_wave_strategy_v2.py
"""
ElliottWaveStrategy V2 - Versión Optimizada

Estrategia mejorada que corrige el sesgo direccional y se adapta a diferentes
condiciones de mercado usando filtros de tendencia inteligentes.
"""

import pandas as pd
import numpy as np
from typing import Dict, List, Optional
from analysis_engines.taew_analyzer import TaewAnalyzer


class ElliottWaveStrategyV2:
    """
    Estrategia Elliott Wave optimizada con:
    - Detección de tendencia principal
    - Sesgo direccional adaptativo
    - Filtros de calidad mejorados
    - Lógica bidireccional balanceada
    """
    
    def __init__(self, 
                 min_wave_confidence: float = 0.75,  # Reducido para más señales
                 scalping_mode: bool = True,
                 wave_analysis_lookback: int = 100,
                 trend_filter_enabled: bool = True,
                 trend_lookback: int = 50,
                 adaptive_direction: bool = True):
        """
        Inicializa la estrategia Elliott Wave V2.
        
        Args:
            min_wave_confidence: Confianza mínima (reducida para más señales)
            scalping_mode: Modo scalping optimizado
            wave_analysis_lookback: Período de análisis de ondas
            trend_filter_enabled: Activar filtro de tendencia principal
            trend_lookback: Período para determinar tendencia
            adaptive_direction: Adaptar dirección según tendencia
        """
        self.min_wave_confidence = min_wave_confidence
        self.scalping_mode = scalping_mode
        self.wave_analysis_lookback = wave_analysis_lookback
        self.trend_filter_enabled = trend_filter_enabled
        self.trend_lookback = trend_lookback
        self.adaptive_direction = adaptive_direction
        
        # Configurar TaewAnalyzer
        min_wave_length = 8 if scalping_mode else 15  # Más permisivo
        
        self.taew_analyzer = TaewAnalyzer(
            min_wave_length=min_wave_length,
            enable_both_directions=True  # Siempre bidireccional
        )
        
        # Cache optimizado
        self.last_analysis_length = 0
        self.last_signal = 'HOLD'
        self.last_trend_direction = 'NEUTRAL'
        self.last_wave_signal = None
        
        # Configuración de scalping mejorada
        if scalping_mode:
            self.signal_cooldown = 3  # Reducido para más actividad
            self.last_signal_bar = -999
        
        # Compatibilidad con PortfolioManager
        self.middle_band_col = None
        
        print(f"ElliottWaveStrategy V2 inicializada:")
        print(f"  - Modo scalping: {scalping_mode}")
        print(f"  - Confianza mínima: {min_wave_confidence}")
        print(f"  - Filtro de tendencia: {trend_filter_enabled}")
        print(f"  - Dirección adaptativa: {adaptive_direction}")
        print(f"  - Lookback ondas: {wave_analysis_lookback}")

    def check_signal(self, df: pd.DataFrame) -> str:
        """
        Analiza el DataFrame y genera señales adaptativas basadas en Elliott Wave.
        """
        if df.empty or len(df) < self.wave_analysis_lookback:
            return 'HOLD'
        
        try:
            # Preparar datos para análisis
            analysis_df = df.tail(self.wave_analysis_lookback).copy() if self.scalping_mode else df.copy()
            
            # Optimización: evitar recálculo innecesario
            if len(analysis_df) == self.last_analysis_length and self.scalping_mode:
                return self.last_signal
            
            # Configurar índice temporal
            if 'Close_time' in analysis_df.columns:
                analysis_df.set_index('Close_time', inplace=True)
            
            # 1. Determinar tendencia principal
            trend_direction = self._determine_market_trend(analysis_df)
            
            # 2. Ejecutar análisis de ondas Elliott
            detected_waves = self.taew_analyzer.analyze_elliott_waves(
                analysis_df, price_column='Close'
            )
            
            # 3. Generar señal adaptativa
            signal = self._generate_adaptive_signal(detected_waves, analysis_df, trend_direction)
            
            # Actualizar cache
            self.last_analysis_length = len(analysis_df)
            self.last_signal = signal
            self.last_trend_direction = trend_direction
            
            return signal
            
        except Exception as e:
            print(f"Error en ElliottWaveStrategy V2: {e}")
            return 'HOLD'

    def _determine_market_trend(self, df: pd.DataFrame) -> str:
        """
        Determina la tendencia principal del mercado.
        
        Returns:
            str: 'BULLISH', 'BEARISH', o 'NEUTRAL'
        """
        if not self.trend_filter_enabled or len(df) < self.trend_lookback:
            return 'NEUTRAL'
        
        try:
            # Usar EMA_21 si está disponible, sino calcular
            if 'EMA_21' in df.columns:
                ema = df['EMA_21'].iloc[-self.trend_lookback:]
            else:
                ema = df['Close'].ewm(span=21).mean().iloc[-self.trend_lookback:]
            
            # Análisis de pendiente de EMA
            ema_slope = (ema.iloc[-1] - ema.iloc[-10]) / ema.iloc[-10] if len(ema) >= 10 else 0
            
            # Posición del precio respecto a EMA
            current_price = df['Close'].iloc[-1]
            current_ema = ema.iloc[-1]
            price_vs_ema = (current_price - current_ema) / current_ema
            
            # Análisis de momentum reciente
            recent_prices = df['Close'].iloc[-10:]
            price_momentum = (recent_prices.iloc[-1] - recent_prices.iloc[0]) / recent_prices.iloc[0]
            
            # Combinar señales para determinar tendencia
            bullish_signals = 0
            bearish_signals = 0
            
            # Señal 1: Pendiente EMA
            if ema_slope > 0.01:  # 1% de pendiente alcista
                bullish_signals += 1
            elif ema_slope < -0.01:  # 1% de pendiente bajista
                bearish_signals += 1
            
            # Señal 2: Precio vs EMA
            if price_vs_ema > 0.005:  # Precio 0.5% por encima de EMA
                bullish_signals += 1
            elif price_vs_ema < -0.005:  # Precio 0.5% por debajo de EMA
                bearish_signals += 1
            
            # Señal 3: Momentum de precio
            if price_momentum > 0.02:  # 2% de momentum alcista
                bullish_signals += 1
            elif price_momentum < -0.02:  # 2% de momentum bajista
                bearish_signals += 1
            
            # Determinar tendencia principal
            if bullish_signals >= 2:
                return 'BULLISH'
            elif bearish_signals >= 2:
                return 'BEARISH'
            else:
                return 'NEUTRAL'
                
        except Exception as e:
            print(f"Error determinando tendencia: {e}")
            return 'NEUTRAL'

    def _generate_adaptive_signal(self, detected_waves: List[Dict], df: pd.DataFrame, trend: str) -> str:
        """
        Genera señales adaptativas basadas en ondas y tendencia principal.
        """
        if not detected_waves:
            return 'HOLD'
        
        # Obtener señal base de Elliott Wave
        latest_signal_info = self.taew_analyzer.get_latest_wave_signal(detected_waves)
        
        if not latest_signal_info:
            return 'HOLD'
        
        # Verificar confianza mínima
        confidence = latest_signal_info.get('confidence', 0.0)
        if confidence < self.min_wave_confidence:
            return 'HOLD'
        
        base_action = latest_signal_info.get('suggested_action', 'HOLD')
        
        # NUEVA LÓGICA ADAPTATIVA
        if self.adaptive_direction and trend != 'NEUTRAL':
            adapted_signal = self._adapt_signal_to_trend(base_action, trend, detected_waves[-1])
        else:
            # Lógica tradicional mejorada
            adapted_signal = self._improve_traditional_logic(base_action, detected_waves, df)
        
        # Filtros de scalping
        if self.scalping_mode:
            if not self._validate_scalping_conditions_v2(df, adapted_signal):
                return 'HOLD'
            
            # Cooldown entre señales
            current_bar = len(df) - 1
            if current_bar - self.last_signal_bar < self.signal_cooldown:
                return 'HOLD'
        
        # Convertir a señal de trading
        trading_signal = self._convert_action_to_signal(adapted_signal)
        
        if trading_signal != 'HOLD':
            self.last_signal_bar = len(df) - 1
            self.last_wave_signal = latest_signal_info
        
        return trading_signal

    def _adapt_signal_to_trend(self, base_action: str, trend: str, latest_wave: Dict) -> str:
        """
        Adapta la señal de Elliott Wave según la tendencia principal.
        """
        wave_direction = latest_wave.get('direction', '')
        
        # NUEVA LÓGICA: Aprovechar correcciones en tendencias fuertes
        if trend == 'BULLISH':
            # En tendencia alcista, buscar oportunidades LONG
            if base_action == 'CONSIDER_SHORT' and wave_direction == 'UPWARD':
                # Final de onda alcista en tendencia alcista = posible corrección = oportunidad LONG
                return 'CONSIDER_LONG'  # INVERSIÓN INTELIGENTE
            elif base_action == 'CONSIDER_LONG':
                return 'CONSIDER_LONG'  # Mantener señales LONG
            
        elif trend == 'BEARISH':
            # En tendencia bajista, buscar oportunidades SHORT
            if base_action == 'CONSIDER_LONG' and wave_direction == 'DOWNWARD':
                # Final de onda bajista en tendencia bajista = posible rebote = oportunidad SHORT
                return 'CONSIDER_SHORT'  # INVERSIÓN INTELIGENTE
            elif base_action == 'CONSIDER_SHORT':
                return 'CONSIDER_SHORT'  # Mantener señales SHORT
        
        # Si no hay adaptación clara, usar lógica mejorada
        return base_action

    def _improve_traditional_logic(self, base_action: str, detected_waves: List[Dict], df: pd.DataFrame) -> str:
        """
        Mejora la lógica tradicional para generar más señales LONG.
        """
        if not detected_waves:
            return base_action
        
        latest_wave = detected_waves[-1]
        wave_direction = latest_wave.get('direction', '')
        wave_points = len(latest_wave.get('x', []))
        
        # NUEVA LÓGICA: Buscar finales de ondas correctivas para entradas
        if wave_direction == 'DOWNWARD' and wave_points >= 5:
            # Final de onda bajista completa = oportunidad LONG
            return 'CONSIDER_LONG'
        elif wave_direction == 'UPWARD' and wave_points >= 5:
            # Mantener lógica SHORT para ondas alcistas completas, pero con filtros
            current_price = df['Close'].iloc[-1]
            recent_high = df['High'].tail(10).max()
            
            # Solo SHORT si estamos cerca de máximos recientes
            if current_price >= recent_high * 0.99:
                return 'CONSIDER_SHORT'
            else:
                return 'HOLD'  # No operar si no estamos en zona de resistencia
        
        return base_action

    def _validate_scalping_conditions_v2(self, df: pd.DataFrame, action: str) -> bool:
        """
        Validaciones mejoradas para scalping.
        """
        if len(df) < 5:
            return False
        
        try:
            recent_data = df.tail(10)  # Más datos para mejor análisis
            
            # 1. Volatilidad mínima (reducida para más señales)
            price_range = recent_data['High'].max() - recent_data['Low'].min()
            avg_price = recent_data['Close'].mean()
            volatility = price_range / avg_price
            
            if volatility < 0.003:  # Reducido de 0.5% a 0.3%
                return False
            
            # 2. Validación direccional mejorada
            latest_close = recent_data['Close'].iloc[-1]
            
            if action == 'CONSIDER_LONG':
                # Para LONG: verificar que no estemos en máximos extremos
                recent_high = recent_data['High'].max()
                if latest_close > recent_high * 0.98:  # Muy cerca del máximo
                    return False
                    
            elif action == 'CONSIDER_SHORT':
                # Para SHORT: verificar que estemos en zona alta
                recent_low = recent_data['Low'].min()
                if latest_close < recent_low * 1.02:  # Muy cerca del mínimo
                    return False
            
            # 3. RSI para evitar extremos (si disponible)
            if 'RSI_14' in df.columns:
                current_rsi = recent_data['RSI_14'].iloc[-1]
                if action == 'CONSIDER_LONG' and current_rsi > 75:  # Muy sobrecomprado
                    return False
                elif action == 'CONSIDER_SHORT' and current_rsi < 25:  # Muy sobrevendido
                    return False
            
            return True
            
        except Exception as e:
            print(f"Error en validación scalping V2: {e}")
            return False

    def _convert_action_to_signal(self, action: str) -> str:
        """Convierte acción Elliott Wave a señal de trading."""
        conversion_map = {
            'CONSIDER_LONG': 'BUY',
            'CONSIDER_SHORT': 'SELL',
            'HOLD': 'HOLD'
        }
        return conversion_map.get(action, 'HOLD')

    def get_take_profit_price(self, current_candle: pd.Series, direction: str) -> float:
        """
        Calcula take profit optimizado para Elliott Wave V2.
        """
        try:
            current_price = current_candle['Close']
            
            # Take profit más conservador para mejor win rate
            if direction == 'LONG':
                recent_range = current_candle.get('High', current_price) - current_candle.get('Low', current_price)
                take_profit = current_price + (recent_range * 1.2)  # Reducido de 1.5x a 1.2x
                
            elif direction == 'SHORT':
                recent_range = current_candle.get('High', current_price) - current_candle.get('Low', current_price)
                take_profit = current_price - (recent_range * 1.2)  # Reducido de 1.5x a 1.2x
                
            else:
                take_profit = current_price
            
            return take_profit
            
        except Exception as e:
            print(f"Error calculando take profit V2: {e}")
            return current_candle['Close']

    def get_strategy_info(self) -> Dict:
        """Información del estado de la estrategia V2."""
        return {
            'strategy_name': 'ElliottWaveStrategy_V2',
            'version': '2.0',
            'mode': 'scalping' if self.scalping_mode else 'standard',
            'min_confidence': self.min_wave_confidence,
            'trend_filter': self.trend_filter_enabled,
            'adaptive_direction': self.adaptive_direction,
            'last_trend': self.last_trend_direction,
            'last_signal': self.last_signal,
            'last_wave_signal': self.last_wave_signal
        }

    def reset_cache(self):
        """Resetea cache de la estrategia V2."""
        self.last_analysis_length = 0
        self.last_signal = 'HOLD'
        self.last_trend_direction = 'NEUTRAL'
        self.last_wave_signal = None
        self.last_signal_bar = -999
        self.taew_analyzer.last_processed_length = 0
        self.taew_analyzer.cached_waves = []
        print("Cache de ElliottWaveStrategy V2 reseteado")

    def update_parameters(self, **kwargs):
        """Actualiza parámetros dinámicamente."""
        for param, value in kwargs.items():
            if hasattr(self, param):
                setattr(self, param, value)
                print(f"Parámetro {param} actualizado a: {value}")