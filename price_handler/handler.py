from pybit.unified_trading import WebSocket
from time import sleep
from models.current_price import CPrice
from models.settings import Settings
from models.position import Position
import exchange_workers.exchanges as ex
from exchange_workers.bybit_http import BybitAPI
import main as m
import threading

global_var_lock = threading.Lock()
ws = None
position_exist = False
last_price = 0
duration_sec = 0
cur_pos = None
set = None
sl_price = 0
change_sl_skip_min = False
first_trailing_triger = False

def handle_price(message):
    global position_exist, last_price, duration_sec, set, first_trailing_triger, sl_price
    last_price = message['data']['lastPrice']
    print(f'last_pr: {last_price}')
    with m.global_var_lock:
        position_exist = m.pos_exist
        print(f'set vars in handler: {position_exist}')
        if position_exist:
            cur_pos = m.current_position
            duration_sec = m.current_position.duration
    print(f'last price: {last_price}')
    if position_exist:
        print('before handle_trailing_stop')
        if cur_pos.signal == 1:
            handle_trailing_stop(cur_pos, last_price, set, sl_price)
    else:
        first_trailing_triger = False
        change_sl_skip_min = False
        sl_price = 0




async def run_close_handler(settings: Settings):
    print('close handler')        
    global ws, position_exist, duration_sec, change_sl_skip_min, cur_pos, set, first_trailing_triger, sl_price
    with m.global_var_lock:
        set = m.settings_gl
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
        with m.global_var_lock:
            position_exist = m.pos_exist
            if position_exist:
                cur_pos = m.current_position
                duration_sec = m.current_position.duration
            else:
                first_trailing_triger = False
                change_sl_skip_min = False
                sl_price = 0
        # print(f'dur_sec: {duration_sec} - skip_min: {set.skip_min} chen_skip_min: {change_sl_skip_min}')
        if duration_sec >= set.skip_min * 60 and not change_sl_skip_min and not first_trailing_triger:
            print('stop_lose move')
            change_sl_skip_min = True
            buy_sel = 'Buy' if cur_pos.signal == 1 else 'Sell'
            sl_price = cur_pos.price_open * (1-set.close_perc)
            BybitAPI.cancel_orders()
            slres = BybitAPI.sl(set.coin, cur_pos.amount, sl_price)
            print(slres)
            if slres == 'OK':
                change_sl_skip_min = True
        if duration_sec >= set.target_len * set.t * 60 and not first_trailing_triger:
            await ex.close_order_timefinish(settings, cur_pos.signal)


def handle_trailing_stop(cur_pos: Position, last_price: float, set: Settings, sl_price: float):
        global first_trailing_triger
        print(f'handle_trailing_stop: {cur_pos} - {last_price} - {sl_price}')
        if cur_pos.signal == 1:
            if last_price > cur_pos.price_open * (1+set.trailing_stop_triger) and not first_trailing_triger:
                BybitAPI.cancel_orders()
                sl_price = last_price * (1-set.trailing_stop_dist)
                res = BybitAPI.sl(set.coin, cur_pos.amount, sl_price)
                if res == 'OK':
                    first_trailing_triger = True
            if first_trailing_triger and last_price > sl_price * (1+set.trailing_stop_dist*2):
                sl_price = last_price * (1-set.trailing_stop_dist)
                BybitAPI.cancel_orders()
                res = BybitAPI.sl(set.coin, cur_pos.amount, sl_price)
        elif cur_pos.signal == 2:
            if last_price < cur_pos.price_open * (1-set.trailing_stop_triger) and not first_trailing_triger:
                BybitAPI.cancel_orders()
                sl_price = last_price * (1+set.trailing_stop_dist)
                res = BybitAPI.sl(set.coin, cur_pos.amount, sl_price)
                if res:
                    first_trailing_triger = True
            if first_trailing_triger and last_price < sl_price * (1-set.trailing_stop_dist*2):
                sl_price = last_price * (1+set.trailing_stop_dist)
                BybitAPI.cancel_orders()
                res = BybitAPI.sl(set.coin, cur_pos.amount, sl_price)
