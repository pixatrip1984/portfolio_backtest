# analysis_engines/__init__.py
"""
Motor de Análisis Estructural - Fase 2 del Proyecto

Este paquete contiene los motores de análisis avanzado basados en 
la estructura del mercado, incluyendo el análisis de Ondas de Elliott.
"""

from .taew_analyzer import TaewAnalyzer

__all__ = ['TaewAnalyzer']