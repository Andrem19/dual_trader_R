import json
from datetime import datetime

class Position:
    def __init__(self, coin, timeopen, priceopen, old_balance, amount, sig):
        self.time_open = timeopen
        self.amount = amount
        self.signal = sig
        self.coin = coin
        self.duration = 0
        self.price_open = priceopen
        self.time_close = ''
        self.old_balance = old_balance
        self.new_balance = None
        self.profit = None

    def to_json(self):
        with open(f"positions/position_{self.coin}.json", "a") as file:
            json.dump(self.__dict__, file)
            file.write('\n')
    
    def from_json(self, data: dict):
        for key, value in data.items():
            setattr(self, key, value)
    
    def __str__(self):
        attributes = ['coin', 'time_open', 'price_open', 'amount', 'duration', 'signal', 'time_close', 'old_balance', 'new_balance', 'profit']
        attribute_values = [getattr(self, attr) for attr in attributes]
        
        attribute_strings = []
        for attribute, value in zip(attributes, attribute_values):
            attribute_strings.append(f'{attribute}: {value}')
        
        return f"Position({', '.join(attribute_strings)})"
    
    def to_empty(self):
        self.time_open = ''
        self.amount = ''
        self.coin = ''
        self.price_open = ''
        self.time_close = ''
        self.old_balance = ''
        self.signal = 0
        self.duration = 0
        self.doubling_counter = ''
        self.new_balance = None
        self.profit = None
    
    @staticmethod
    def parse_to_pretty_string(positions):
        pretty_string = ""
        for position in positions:
            pretty_string += str(position) + "\n"
        return pretty_string
    @staticmethod
    def create_empty():
        return Position('', '', '', '', '', '')
