from models.settings import Settings
from exchange_workers.bybit_http import BybitAPI
from models.position import Position
import helpers.telegram as tel
import datetime
import asyncio
import time

# 1 - buy 2 - sell
async def place_order(settings: Settings, buy_sell: int):
    bs = 'Buy' if buy_sell == 1 else 'Sell'
    order_id = ''
    
    if settings.exchange == 'BB':
        response = BybitAPI.place_order(True, settings.coin, bs, settings.amount_coins, settings.order_in_perc, TP_perc=None, SL_perc=settings.super_close)
        
        if 'retMsg' in response and response['retMsg'] == 'OK':
            order_id = response['result']['orderId']
            open_time = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
            
            while True:
                resp = BybitAPI.get_position_info(settings.coin)
                
                if float(resp['size']) > 0:
                    old_balance = BybitAPI.get_balance('USDT')
                    current_position = Position(settings.coin, open_time , float(resp['avgPrice']), old_balance, settings.amount_coins)
                    
                    current_position.to_json()
                    await tel.send_inform_message(f'Position was taken successfully: {str(current_position)}', '', False)
                    return True, current_position
                
                time.sleep(10)
                time_format = "%Y-%m-%d %H:%M:%S"
                time_obj = datetime.datetime.strptime(open_time, time_format)
                duration = datetime.datetime.now() - time_obj
                duration_seconds = duration.total_seconds()
                
                print(f'trying to take position {duration}')
                await tel.send_inform_message(f'Trying to take position {duration}', '', False)
                
                if duration_seconds > 600:
                    break
            
            BybitAPI.cancel_orders(settings.coin, order_id)
            await tel.send_inform_message('Position doesn\'t exist after order', '', False)
            return False, None
        
        else:
            print('some problem to place order')
    
    elif settings.exchange == 'BN':
        pass

async def change_SL_after_first_cand(settings: Settings, buy_sell, current_position: Position):
    bs = 'Buy' if buy_sell == 1 else 'Sell'
    if settings.exchange == 'BB':
        BybitAPI.cancel_orders()
        time.sleep(1)
        resp = None
        if not settings.trailing_stop:
            resp = BybitAPI.tp_sl(settings.coin, bs, settings.amount_coins, float(current_position.price_open), TP_perc=settings.target_perc, SL_perc=settings.close_perc)
        else:
            current_price = BybitAPI.get_last_price(settings.coin)
            if current_price < (1 + settings.trailing_stop_triger) * current_position.price_open:
                resp = BybitAPI.trailing_stop(True, settings.coin, 'Buy', settings.amount_coins, current_position.price_open, settings.trailing_stop_dist, settings.trailing_stop_triger, TP_perc=settings.target_perc*2, SL_perc=settings.close_perc)
            else:
                await tel.send_inform_message('Trailing Stop already trigered', '', False)
                return True
        if resp is not None and resp == 'OK':
            await tel.send_inform_message('Sl successfuly changed', '', False)
            return True
        else:
            await tel.send_inform_message('Cant change tp/sl something wrong', '', False)
            return False
    elif settings.exchange == 'BN':
        pass

async def close_order_timefinish(settings: Settings, signal: int):
    bs = 'Sell' if signal == 1 else 'Buy'
    response = BybitAPI.place_order(False, settings.coin, bs, settings.amount_coins, settings.order_in_perc)
    if 'retMsg' in response and response['retMsg']  == 'OK':
            order_id = response['result']['orderId']
            time.sleep(5)
            resp = BybitAPI.get_position_info(settings.coin)
            if int(resp['size']) > 0:
                print('Something wrong cant close position')
                await tel.send_inform_message('Something wrong cant close position', '', False)
                BybitAPI.cancel_orders(settings.coin, order_id)
                return False
            elif int(resp['size']) == 0:
                await tel.send_inform_message('Position close successfuly', '', False)
                return True