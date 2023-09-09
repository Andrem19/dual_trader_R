import threading
from models.settings import Settings
from models.position import Position

current_position = Position.create_empty()
settings_gl = Settings('BTCUSDT', 5)
settings_gl.from_json()
handler_lock = False
global_var_lock = threading.Lock()
stop_flag = False
pos_exist = False