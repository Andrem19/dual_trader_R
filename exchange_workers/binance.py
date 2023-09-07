import requests

def get_kline(coin: str, number_candles: int, interv: int):

    endpoint = f'/api/v3/klines?symbol={coin}&interval={interv}m&limit={number_candles}'
    url = 'https://api.binance.com' + endpoint
    response = requests.get(url).json()

    new_list = [[x[0], float(x[1]), float(x[2]), float(x[3]), float(x[4]), float(x[5])] for x in response]
    return new_list