# Contenido completo del archivo

# Contenido completo
import websocket
import json
import pandas as pd
import threading
import time
from typing import Callable, List
# Importación absoluta
from config.settings import KLINE_COLUMNS
# La definición de KLINE_COLUMNS se ha movido a settings.py

class BinanceWebsocketClient:
    """
    Cliente para conectarse al Websocket de Binance y gestionar los datos de las klines.
    """
    # El resto del archivo permanece exactamente igual...
    def __init__(self, url: str, initial_df: pd.DataFrame = None, callback: Callable[[pd.DataFrame], None] = None):
        """
        Inicializa el cliente del Websocket.
        """
        self.url = url
        self.callback = callback
        self.wsapp = None
        
        if initial_df is not None and not initial_df.empty:
            self.df = initial_df
            if not self.df.empty and 'Close_time' in self.df.columns:
                 print(f"Cliente Websocket inicializado con {len(self.df)} velas pre-cargadas, hasta {self.df['Close_time'].iloc[-1]}.")
            else:
                 print(f"Cliente Websocket inicializado con {len(self.df)} velas pre-cargadas.")
        else:
            self.df = pd.DataFrame(columns=KLINE_COLUMNS)
            print("Cliente Websocket inicializado con un DataFrame vacío.")
        print(f"Cliente Websocket inicializado para URL: {self.url}")

    def _on_open(self, wsapp):
        print("¡Conexión de Websocket abierta!")

    def _on_error(self, wsapp, error):
        print(f"Error en Websocket: {error}")

    def _on_close(self, wsapp, close_status_code, close_msg):
        print("¡Conexión de Websocket cerrada!")

    def _on_message(self, wsapp, message):
        json_message = json.loads(message)
        candle_data = json_message.get('k')

        if not candle_data:
            return

        is_candle_closed = candle_data['x']

        if is_candle_closed:
            new_candle_close_time = pd.to_datetime(candle_data['T'], unit='ms')

            if not self.df.empty:
                last_known_close_time = self.df['Close_time'].iloc[-1]
                if new_candle_close_time <= last_known_close_time:
                    # Silenciado para no generar ruido, pero se puede activar para debug
                    # print(f"Vela duplicada o antigua recibida ({new_candle_close_time}). Ignorando.")
                    return
            
            # print(f"\nNueva vela cerrada para {candle_data['s']} en {new_candle_close_time}")
            
            new_row_data = {
                'Open_time': pd.to_datetime(candle_data['t'], unit='ms'),
                'Open': float(candle_data['o']),
                'High': float(candle_data['h']),
                'Low': float(candle_data['l']),
                'Close': float(candle_data['c']),
                'Volume': float(candle_data['v']),
                'Close_time': new_candle_close_time,
                'Quote_asset_volume': float(candle_data['q']),
                'Number_of_trades': int(candle_data['n']),
                'Taker_buy_base_asset_volume': float(candle_data['V']),
                'Taker_buy_quote_asset_volume': float(candle_data['Q']),
                'Ignore': candle_data['B']
            }
            
            new_row_df = pd.DataFrame([new_row_data])
            self.df = pd.concat([self.df, new_row_df], ignore_index=True)
            
            # print(f"DataFrame actualizado. Total de velas: {len(self.df)}")
            # print(self.df.tail(1))

            if self.callback:
                self.callback(self.df.copy())
    
    def start(self):
        print("Iniciando conexión de Websocket...")
        self.wsapp = websocket.WebSocketApp(self.url,
                                            on_open=self._on_open,
                                            on_message=self._on_message,
                                            on_error=self._on_error,
                                            on_close=self._on_close)
        
        wst = threading.Thread(target=self.wsapp.run_forever, daemon=True)
        wst.start()
        print("El hilo del Websocket ha comenzado. Esperando mensajes...")

    def stop(self):
        if self.wsapp:
            print("Cerrando conexión de Websocket...")
            self.wsapp.close()