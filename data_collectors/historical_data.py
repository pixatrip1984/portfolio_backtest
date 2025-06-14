import pandas as pd
from binance.client import Client
# La importación de settings y KLINE_COLUMNS ahora es absoluta
from config.settings import KLINE_COLUMNS
# La definición de KLINE_COLUMNS se ha movido a settings.py

def get_historical_klines(symbol: str, interval: str, limit: int = 500) -> pd.DataFrame:
    # ... (El código de esta función no cambia)
    print(f"Obteniendo {limit} velas históricas para {symbol} en intervalo de {interval}...")
    client = Client() 
    klines = client.get_klines(symbol=symbol.upper(), interval=interval, limit=limit)
    df = pd.DataFrame(klines, columns=KLINE_COLUMNS)
    df['Open_time'] = pd.to_datetime(df['Open_time'], unit='ms')
    df['Close_time'] = pd.to_datetime(df['Close_time'], unit='ms')
    numeric_columns = ['Open', 'High', 'Low', 'Close', 'Volume', 'Quote_asset_volume', 
                       'Taker_buy_base_asset_volume', 'Taker_buy_quote_asset_volume']
    df[numeric_columns] = df[numeric_columns].apply(pd.to_numeric, axis=1)
    df['Number_of_trades'] = df['Number_of_trades'].astype(int)
    print(f"Se obtuvieron {len(df)} velas históricas exitosamente.")
    return df

def get_extended_historical_klines(symbol: str, interval: str, start_str: str) -> pd.DataFrame:
    # ... (El código de esta función no cambia)
    client = Client()
    print(f"Obteniendo datos históricos extendidos para {symbol} desde {start_str}...")
    klines_generator = client.get_historical_klines_generator(symbol, interval, start_str)
    df = pd.DataFrame(klines_generator, columns=KLINE_COLUMNS)
    df['Open_time'] = pd.to_datetime(df['Open_time'], unit='ms')
    df['Close_time'] = pd.to_datetime(df['Close_time'], unit='ms')
    numeric_columns = ['Open', 'High', 'Low', 'Close', 'Volume', 'Quote_asset_volume', 
                       'Taker_buy_base_asset_volume', 'Taker_buy_quote_asset_volume']
    df[numeric_columns] = df[numeric_columns].apply(pd.to_numeric, axis=1)
    df['Number_of_trades'] = df['Number_of_trades'].astype(int)
    df.drop_duplicates(subset='Close_time', keep='first', inplace=True)
    df.sort_values(by='Close_time', inplace=True)
    print(f"Se obtuvieron {len(df)} velas históricas desde {start_str} exitosamente.")
    return df