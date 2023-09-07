from models.settings import Settings
from models.position import Position
import exchange_workers.exchanges as ex
from exchange_workers.bybit_http import BybitAPI
import helpers.telegram as tel
import helpers.services as ser
import helpers.saldo as sal
import main as m
import datetime
import time
import os

print()

async def open_position(settngs_gl: Settings, signal: int):
    try:
        timest = datetime.datetime.now().timestamp()
        res, cur_pos = await ex.place_order(settngs_gl, signal)
        if res:
            with m.global_var_lock:
                m.current_position = cur_pos
                m.price.position_exist = True
        else:
            message = f'Position wasn\'t open'
            print(message)
            await tel.send_inform_message(message, '', None)
        while res:
            time.sleep(5)
            time_format = "%Y-%m-%d %H:%M:%S"
            time_obj = datetime.datetime.strptime(cur_pos.time_open, time_format)
            duration = datetime.datetime.now() - time_obj
            duration_seconds = duration.total_seconds()
            responce = BybitAPI.get_position_info(settngs_gl.coin)
            if float(responce['size']) > 0:
                res = True
                if timest + settngs_gl.message_timer < datetime.datetime.now().timestamp():
                        await handle_message(responce, duration)
                        timest = datetime.datetime.now().timestamp()
            else:
                with m.global_var_lock:
                    m.price.position_exist = False
                res = False
    except Exception as e:
        print(f'Error: {e}')
        await tel.send_inform_message(f'Error: {e}', '', False)
        pass


async def handle_message(response, duration):
    message = f'unrealisedPnl: {response["unrealisedPnl"]}\nduration: {duration}'
    print(message)
    await tel.send_inform_message(message, '', None)