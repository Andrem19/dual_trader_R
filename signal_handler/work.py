from models.settings import Settings
from models.position import Position
import exchange_workers.exchanges as ex
from exchange_workers.bybit_http import BybitAPI
import helpers.telegr as tel
import helpers.services as ser
import helpers.saldo as sal
import datetime
import shared_vars as sv
import time
import os


async def open_position(settngs_gl: Settings, signal: int):
    try:
        timest = datetime.datetime.now().timestamp()
        res, cur_pos = await ex.place_order(settngs_gl, signal)
        print(res)
        if res:
            with sv.global_var_lock:
                sv.current_position = cur_pos
                sv.pos_exist = True
                print(f'm.pos_exist: {sv.pos_exist}')
        else:
            message = f'Position wasn\'t open'
            print(message)
            await tel.send_inform_message(message, '', None)
        while res:
            time.sleep(5)
            time_format = "%Y-%m-%d %H:%M:%S"
            time_obj = datetime.datetime.strptime(sv.current_position.time_open, time_format)
            duration = datetime.datetime.now() - time_obj
            duration_seconds = duration.total_seconds()
            sv.current_position.duration = duration_seconds
            responce = BybitAPI.get_position_info(settngs_gl.coin)
            if float(responce['size']) > 0:
                res = True
                if timest + settngs_gl.message_timer < datetime.datetime.now().timestamp():
                        await handle_message(responce, duration)
                        timest = datetime.datetime.now().timestamp()
            else:
                with sv.global_var_lock:
                    sv.pos_exist = False
                res = False
                await handle_positions(settngs_gl.coin)
                sv.current_position.to_empty()

    except Exception as e:
        print(f'Error: {e}')
        await tel.send_inform_message(f'Error: {e}', '', False)
        pass


async def handle_message(response, duration):
    message = f'unrealisedPnl: {response["unrealisedPnl"]}\nduration: {duration}'
    print(message)
    await tel.send_inform_message(message, '', None)

async def handle_positions(coin):
    positions: list[Position] = ser.read_deser_positions(coin)
    saldos = sal.load_saldo()
    if len(positions) > 0:
        path = f'positions/position_{coin}.json'
        os.remove(path)
        new_balance = BybitAPI.get_balance('USDT')
        positions[-1].new_balance = round(new_balance, 4)
        positions[-1].time_close = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        prof = positions[-1].new_balance - positions[-1].old_balance
        positions[-1].profit = round(prof, 4)
        positions[-1].duration = ser.convert_seconds_to_period(float(sv.current_position.duration))
        new_saldo = saldos[-1][1] + prof
        sal.add_saldo([datetime.datetime.now().timestamp()*1000, new_saldo], f'db/saldo_{coin}.txt')
        ser.add_pos_to_db(positions[-1], f'db/positions_{coin}.txt')
        await tel.send_inform_message(f'Position was closed successfully: {str(positions[-1])}', '', None)
        