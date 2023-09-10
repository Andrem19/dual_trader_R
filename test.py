from exchange_workers.bybit_http import BybitAPI

BybitAPI.place_order(False, 'GALAUSDT', 'Sell', 0, 0.0002, TP_perc=None, SL_perc=None)