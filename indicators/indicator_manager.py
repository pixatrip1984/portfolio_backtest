# indicators/indicator_manager.py
# Versión simplificada con indicadores esenciales para ElliottWaveStrategy

import pandas as pd
import pandas_ta as ta

class IndicatorManager:
    """
    Gestor de indicadores simplificado que calcula solo los indicadores esenciales.
    
    Con la integración de python-taew, la librería realizará su propio análisis 
    internamente, pero mantenemos algunos indicadores básicos necesarios para
    el sistema de risk management.
    """
    
    def __init__(self):
        """
        Inicializa el gestor de indicadores en modo simplificado.
        """
        print("IndicatorManager inicializado en modo simplificado (con indicadores esenciales)")
        print("Nota: Cálculo optimizado para ElliottWaveStrategy")

    def calculate_indicators(self, df: pd.DataFrame) -> pd.DataFrame:
        """
        Calcula indicadores esenciales necesarios para el sistema.
        
        Args:
            df (pd.DataFrame): DataFrame con datos OHLCV
            
        Returns:
            pd.DataFrame: DataFrame con indicadores esenciales agregados
        """
        try:
            df_with_indicators = df.copy()
            
            # Renombramos a minúsculas para compatibilidad con pandas-ta
            df_with_indicators.rename(columns={
                "Open": "open", "High": "high", "Low": "low", "Close": "close", "Volume": "volume"
            }, inplace=True)
            
            # Calcular solo indicadores esenciales para el sistema
            
            # 1. ATR - Esencial para risk management (stop loss)
            if len(df_with_indicators) >= 14:
                df_with_indicators['ATR_14'] = ta.atr(
                    high=df_with_indicators['high'],
                    low=df_with_indicators['low'],
                    close=df_with_indicators['close'],
                    length=14
                )
            else:
                # Para datasets pequeños, usar un ATR sintético basado en volatilidad
                price_range = df_with_indicators['high'] - df_with_indicators['low']
                df_with_indicators['ATR_14'] = price_range.rolling(window=min(len(df_with_indicators), 5)).mean()
            
            # 2. RSI - Útil para filtros adicionales si necesario
            if len(df_with_indicators) >= 14:
                df_with_indicators['RSI_14'] = ta.rsi(
                    close=df_with_indicators['close'],
                    length=14
                )
            else:
                # RSI sintético para datasets pequeños
                df_with_indicators['RSI_14'] = 50.0  # Valor neutral
            
            # 3. EMAs simples para contexto de tendencia (opcional)
            if len(df_with_indicators) >= 21:
                df_with_indicators['EMA_21'] = ta.ema(
                    close=df_with_indicators['close'],
                    length=21
                )
            else:
                df_with_indicators['EMA_21'] = df_with_indicators['close']
            
            # Revertir los nombres a Mayúscula inicial
            df_with_indicators.rename(columns={
                "open": "Open", "high": "High", "low": "Low", "close": "Close", "volume": "Volume"
            }, inplace=True)
            
            # Asegurar que no hay valores NaN en indicadores críticos
            df_with_indicators['ATR_14'] = df_with_indicators['ATR_14'].fillna(
                df_with_indicators['ATR_14'].mean()
            )
            df_with_indicators['RSI_14'] = df_with_indicators['RSI_14'].fillna(50.0)
            df_with_indicators['EMA_21'] = df_with_indicators['EMA_21'].fillna(
                df_with_indicators['Close']
            )
            
            return df_with_indicators
            
        except Exception as e:
            print(f"Error calculando indicadores esenciales: {e}")
            # Fallback: agregar indicadores sintéticos mínimos
            df_fallback = df.copy()
            
            # ATR sintético basado en rango de precios
            price_range = df_fallback['High'] - df_fallback['Low']
            df_fallback['ATR_14'] = price_range.rolling(window=min(len(df_fallback), 5)).mean().fillna(price_range.mean())
            
            # Indicadores placeholder
            df_fallback['RSI_14'] = 50.0
            df_fallback['EMA_21'] = df_fallback['Close']
            
            return df_fallback
    
    def get_essential_indicators(self) -> list:
        """
        Retorna la lista de indicadores esenciales que calcula este manager.
        
        Returns:
            list: Lista de nombres de indicadores
        """
        return ['ATR_14', 'RSI_14', 'EMA_21']
    
    def validate_indicators(self, df: pd.DataFrame) -> bool:
        """
        Valida que todos los indicadores esenciales estén presentes.
        
        Args:
            df (pd.DataFrame): DataFrame a validar
            
        Returns:
            bool: True si todos los indicadores están presentes
        """
        essential_indicators = self.get_essential_indicators()
        
        for indicator in essential_indicators:
            if indicator not in df.columns:
                print(f"⚠️  Indicador faltante: {indicator}")
                return False
            
            # Verificar que no sean todos NaN
            if df[indicator].isna().all():
                print(f"⚠️  Indicador con todos NaN: {indicator}")
                return False
        
        return True