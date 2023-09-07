from pybit.unified_trading import WebSocket
from time import sleep
from models.current_price import CPrice
from models.settings import Settings
import main as m
import threading
import json

global_var_lock = threading.Lock()
ws = None

def handle_price(message):
    with m.global_var_lock:
        m.price.coin = message['data']['symbol']
        m.price.price = message['data']['lastPrice']
    print(message['data']['symbol'])
    print(message['data']['lastPrice'])

def run_close_handler(settings: Settings):
    print('close handler')
    global ws
    ws = WebSocket(
        testnet=False,
        channel_type="linear",
        )
        
    ws.ticker_stream(
        symbol=settings.coin,
        callback=handle_price
        )
    while not m.stop_flag:
        sleep(1)
