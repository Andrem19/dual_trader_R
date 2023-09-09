from pybit.unified_trading import WebSocket
from time import sleep
from models.current_price import CPrice
from models.settings import Settings
from models.position import Position
import exchange_workers.exchanges as ex
from exchange_workers.bybit_http import BybitAPI
import shared_vars as m
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
close_position_SL=False

def handle_price(message):
    global position_exist, last_price, duration_sec, set, first_trailing_triger, sl_price
    last_price = float(message['data']['lastPrice'])
    print(last_price)
    with m.global_var_lock:
        position_exist = m.pos_exist
        if position_exist:
            cur_pos = m.current_position
            duration_sec = m.current_position.duration
    if position_exist:
        if last_price > cur_pos.price_open * (1+set.trailing_stop_triger) and not first_trailing_triger:
            handle_t_s(cur_pos, last_price, set, set.trailing_stop_dist)
        elif (duration_sec >= set.skip_min * 60 and last_price < cur_pos.price_open * (1-set.close_perc) and not first_trailing_triger) or (duration_sec >= set.target_len * set.t * 60 and not first_trailing_triger):
            handle_t_s(cur_pos, last_price, set, set.order_in_perc*2)
        if first_trailing_triger:
            handle_trailing_stop(cur_pos, last_price, set)
    else:
        first_trailing_triger = False
        change_sl_skip_min = False
        sl_price = 0




async def run_close_handler(settings: Settings):  
    global ws, position_exist, duration_sec, change_sl_skip_min, cur_pos, set, first_trailing_triger, sl_price, last_price, close_position_SL
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
    
    while m.pos_exist:
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
        if duration_sec >= set.skip_min * 60 and not change_sl_skip_min and not first_trailing_triger and position_exist:
            change_sl_skip_min = True
            sl_price = cur_pos.price_open * (1-set.close_perc)
            sLimit_price = sl_price * (1 - 0.0005)
            BybitAPI.cancel_orders()
            slres = BybitAPI.sl(set.coin, cur_pos.amount, sl_price, sLimit_price)
            if slres == 'OK':
                change_sl_skip_min = True


def handle_trailing_stop(cur_pos: Position, last_price: float, set: Settings):
        global sl_price, duration_sec
        # print(f'handle_trailing_stop: {cur_pos} - {last_price} - {sl_price}')
        if cur_pos.signal == 1:
            if last_price > sl_price * (1+set.trailing_stop_dist*2):
                sl_price = last_price * (1-set.trailing_stop_dist)
                sLimit_price = sl_price * (1 - 0.0005)
                BybitAPI.cancel_orders()
                res = BybitAPI.sl(set.coin, cur_pos.amount, sl_price, sLimit_price)
        elif cur_pos.signal == 2:
            if last_price < sl_price * (1-set.trailing_stop_dist*2):
                sl_price = last_price * (1+set.trailing_stop_dist)
                sLimit_price = sl_price * (1 + 0.0005)
                BybitAPI.cancel_orders()
                res = BybitAPI.sl(set.coin, cur_pos.amount, sl_price, sLimit_price)

def handle_t_s(cur_pos: Position, last_price: float, set: Settings, dist: float):
    global first_trailing_triger, sl_price, duration_sec
    if cur_pos.signal == 1:
        BybitAPI.cancel_orders()
        sl_price = last_price * (1-dist)
        sLimit_price = sl_price * (1 - 0.0005)
        res = BybitAPI.sl(set.coin, cur_pos.amount, sl_price, sLimit_price)
        if res == 'OK':
            first_trailing_triger = True
    elif cur_pos.signal == 2:
        BybitAPI.cancel_orders()
        sl_price = last_price * (1+dist)
        sLimit_price = sl_price * (1 + 0.0005)
        res = BybitAPI.sl(set.coin, cur_pos.amount, sl_price, sLimit_price)
        if res == 'OK':
            first_trailing_triger = True