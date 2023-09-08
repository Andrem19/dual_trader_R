# from models.current_price import CPrice
# import price_handler.handler as ph
# import signal_handler.handler as sh
# import time
# import threading
# import tracemalloc
# from models.settings import Settings
# from models.position import Position


# COIN = 'DOTUSDT'
# T = 5
# price = CPrice()
# current_position = Position.create_empty()
# settings_gl = Settings(COIN, T)
# settings_gl.from_json()
# handler_lock = False
# global_var_lock = threading.Lock()

# def run_close_handler():
#     while True:
#         try:
#             ph.run_close_handler(settings_gl)
#         except Exception as e:
#             print(f"Error in run_close_handler: {e}")
#             time.sleep(5)  # Wait for 5 seconds before reconnecting
# def run_open_handler():
#     while True:
#         try:
#             sh.open_worker()
#         except Exception as e:
#             print(f"Error in run_close_handler: {e}")
#             time.sleep(5)  # Wait for 5 seconds before reconnecting

# def main():
#     global handler_lock, settings_gl, price, current_position

#     close_thread = threading.Thread(target=run_close_handler)
#     close_thread.start()
    
#     run_open_handler()

#     close_thread.join()
# if __name__ == '__main__':
#     tracemalloc.start()
#     main()
from models.current_price import CPrice
import price_handler.handler as ph
import signal_handler.handler as sh
import time
import threading
import tracemalloc
from models.settings import Settings
from models.position import Position
import signal
import asyncio
import os

COIN = 'FILUSDT'
T = 5
pos_exist = False
current_position = Position.create_empty()
settings_gl = Settings(COIN, T)
settings_gl.from_json()
handler_lock = False
global_var_lock = threading.Lock()
stop_flag = False

async def run_close_handler():
    while not stop_flag:  # Add the stop flag check
        try:
            await ph.run_close_handler(settings_gl)
        except Exception as e:
            if stop_flag:
                return
            print(f"Error in run_close_handler: {e}")
            time.sleep(5)  # Wait for 5 seconds before reconnecting

def run_open_handler():
    while not stop_flag:
        try:
            sh.open_worker()
        except Exception as e:
            if stop_flag:
                return
            print(f"Error in run_open_handler: {e}")
            time.sleep(5)  # Wait for 5 seconds before reconnecting


async def stop_program(signal, frame):
    global stop_flag, close_thread

    stop_flag = True
    print("\nStopping the program...")
    ph.ws.exit()
    await sh.app.stop()
    print("\nAfter  stopping the program...")
    os.kill(os.getpid(), signal)

def main():
    global handler_lock, settings_gl, pos_exist, current_position, stop_flag, close_thread  # Add stop_flag to global scope
    stop_flag = False  # Initialize the stop flag

    close_thread = threading.Thread(target=asyncio.run, args=(run_close_handler(),))
    close_thread.start()

    run_open_handler()

    stop_flag = True  # Set stop_flag to True to stop the close_thread
    close_thread.join()




if __name__ == '__main__':
    tracemalloc.start()
    signal.signal(signal.SIGINT, lambda *args: asyncio.create_task(stop_program(*args)))  # Register the keyboard interrupt handler
    main()
