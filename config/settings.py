# Contenido completo del archivo

import os
import sys
from dotenv import load_dotenv

# --- ANCLA DEL PROYECTO ---
# Esta es la pieza clave para la portabilidad.
# Determina la ruta absoluta a la carpeta raíz del proyecto.
# os.path.dirname(__file__) -> /ruta/a/config
# os.path.dirname(...) -> /ruta/a/
PROJECT_ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))

# Añadimos la raíz del proyecto al sys.path para hacer las importaciones absolutas.
# Esto nos permitirá hacer 'from data_collectors import ...' desde cualquier archivo.
if PROJECT_ROOT not in sys.path:
    sys.path.append(PROJECT_ROOT)

# Cargar las variables de entorno desde el archivo .env en la raíz
dotenv_path = os.path.join(PROJECT_ROOT, '.env')
if os.path.exists(dotenv_path):
    load_dotenv(dotenv_path)

# --- Binance Configuration ---
BINANCE_API_KEY = os.getenv("BINANCE_API_KEY")
BINANCE_API_SECRET = os.getenv("BINANCE_API_SECRET")

# --- Trading Configuration ---
SYMBOL = os.getenv("SYMBOL", "btcusdt")
INTERVAL = os.getenv("INTERVAL", "1m")

# --- Websocket Configuration ---
WEBSOCKET_URL = f"wss://stream.binance.com:9443/ws/{SYMBOL.lower()}@kline_{INTERVAL}"

# --- CONSTANTE DE DATOS CENTRALIZADA ---
KLINE_COLUMNS = ['Open_time', 'Open', 'High', 'Low', 'Close', 'Volume', 
                 'Close_time', 'Quote_asset_volume', 'Number_of_trades',
                 'Taker_buy_base_asset_volume', 'Taker_buy_quote_asset_volume', 'Ignore']

# Ya no necesitamos imprimir esto cada vez que se importa el archivo.
# print("Configuración cargada:")
# print(f"Símbolo: {SYMBOL}")
# print(f"Intervalo: {INTERVAL}")
# print(f"URL Websocket: {WEBSOCKET_URL}")