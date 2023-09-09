from models.settings import Settings
from exchange_workers.bybit_http import BybitAPI
from models.position import Position
import helpers.telegr as tel
import datetime
import asyncio
import time

# 1 - buy 2 - sell
async def place_order(settings: Settings, buy_sell: int):
    bs = 'Buy' if buy_sell == 1 else 'Sell'
    order_id = ''
    
    if settings.exchange == 'BB':
        response = BybitAPI.place_order(False, settings.coin, bs, settings.amount_coins, settings.order_in_perc, TP_perc=None, SL_perc=settings.super_close)
        
        if 'retMsg' in response and response['retMsg'] == 'OK':
            order_id = response['result']['orderId']
            open_time = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
            
            while True:
                resp = BybitAPI.get_position_info(settings.coin)
                
                if float(resp['size']) > 0:
                    old_balance = BybitAPI.get_balance('USDT')
                    current_position = Position(settings.coin, open_time , float(resp['avgPrice']), old_balance, settings.amount_coins, buy_sell)

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