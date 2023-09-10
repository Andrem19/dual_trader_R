import json

class Settings:
    def __init__(self, coin, tm):
        self.exchange: str = 'BB'
        self.name: str = ''
        self.coin: str = coin
        self.message_timer: int = 15
        self.t: int = tm
        self.target_len: int = 2
        self.base_amount_usdt: float = 20
        self.amount_usdt: float = 20
        self.skip_min: int = 4
        self.target_perc: float = 0.008
        self.trailing_stop: bool = True
        self.trailing_stop_triger: float = 0.003
        self.trailing_stop_dist: float = 0.0005
        self.close_perc: float = 0.003
        self.super_close: float = 0.005
        self.order_in_perc: float = 0.0001
        self.border_saldo: str = '03.09.23'


    def to_json(self):
        with open(f"settings/settings_{self.coin}_{self.t}.json", "w") as file:
            json.dump(self.__dict__, file)
    
    def from_json(self):
        with open(f"settings/settings_UNIVERSAL_{self.t}.json", "r") as file:
            data = json.load(file)
            for key, value in data.items():
                setattr(self, key, value)

# set = Settings('GALAUSDT', 5)
# set.to_json()
# set.from_json()
# print(set.__dict__)