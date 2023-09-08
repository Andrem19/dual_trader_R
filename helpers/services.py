import json
import os
from datetime import datetime
from models.position import Position

def read_deser_positions(coin: str) -> list[Position]:
    positions = []
    file_path = f'positions/position_{coin}.json'

    # Check if file exists
    print('read deser pos')
    if os.path.isfile(file_path):
        with open(file_path, 'r') as file:
            for line in file:
                data = json.loads(line)
                position = Position(data['coin'], data['time_open'], data['price_open'], data['old_balance'], data['amount'], data['signal'])
                position.new_balance = data['new_balance']
                position.profit = data['profit']
                position.duration = data['duration']
                position.time_close = data['time_close'] if data['time_close'] else None
                positions.append(position)

    return positions

def add_pos_to_db(item: Position, path):
    with open(path, 'a') as file:
        json.dump(item.__dict__, file)
        file.write('\n')

def convert_to_timestamp(date_string):
    if date_string == '0':
        return 0
    try:
        dt = datetime.strptime(date_string, '%d.%m.%y')
        timestamp = dt.timestamp() * 1000
        return int(timestamp)
    except ValueError:
        return -1

def filter_list_by_timestamp(input_list, timestamp):
    if timestamp == 0:
        return input_list
    filtered_list = []
    for item in input_list:
        if item[0] >= timestamp:
            filtered_list.append(item)
    return filtered_list

def convert_seconds_to_period(seconds: float):
    hours = seconds // 3600
    minutes = (seconds % 3600) // 60
    seconds = round(seconds % 60, 2)

    period = f"{hours:02}:{minutes:02}:{seconds:02}"
    return period
