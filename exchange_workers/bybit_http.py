from decouple import config
import requests
import time
import hashlib
import hmac
import uuid
import json

class BybitAPI:
    @staticmethod
    def HTTP_Request(endPoint, method, payload, Info):
        global time_stamp
        time_stamp = str(int(time.time() * 10 ** 3))
        signature = BybitAPI.genSignature(payload)
        headers = {
            'X-BAPI-API-KEY': BybitAPI.api_key,
            'X-BAPI-SIGN': signature,
            'X-BAPI-SIGN-TYPE': '2',
            'X-BAPI-TIMESTAMP': time_stamp,
            'X-BAPI-RECV-WINDOW': BybitAPI.recv_window,
            'Content-Type': 'application/json'
        }
        if(method == "POST"):
            response = BybitAPI.httpClient.request(method, BybitAPI.url + endPoint, headers=headers, data=payload)
        else:
            response = BybitAPI.httpClient.request(method, BybitAPI.url + endPoint + "?" + payload, headers=headers)
        # print(response.text)
        # print(Info + " Elapsed Time: " + str(response.elapsed))
        return response.text
        
    
    @staticmethod
    def genSignature(payload):
        param_str = str(time_stamp) + BybitAPI.api_key + BybitAPI.recv_window + payload
        hash = hmac.new(bytes(BybitAPI.secret_key, "utf-8"), param_str.encode("utf-8"), hashlib.sha256)
        signature = hash.hexdigest()
        return signature

    @staticmethod
    def place_order(pl_min: bool, symb: str, buy_sell: str, amount_coins: float, k: float = 0.0001, TP_perc = None, SL_perc = None):
        kof = k
        current_price = BybitAPI.get_last_price(symb)
        endpoint = "/v5/order/create"
        method = "POST"
        orderLinkId = uuid.uuid4().hex

        trig_price = 0
        if pl_min:
            trig_price = current_price * (1+kof) if buy_sell == 'Sell' else current_price * (1-kof)
        else:
            trig_price = current_price * (1-kof) if buy_sell == 'Sell' else current_price * (1+kof)

        params = {
            "category": "linear",
            "symbol": symb,
            "side": buy_sell,
            "positionIdx": 0,
            "orderType": "Limit",
            "qty": str(round(amount_coins, 3)),
            "price": str(round(trig_price, 3)),
            "isLeverage": 5,
            "timeInForce": "GTC",
            "orderLinkId": orderLinkId
        }

        if TP_perc is not None:
            tp = trig_price * (1 + TP_perc) if buy_sell == 'Buy' else trig_price * (1 - TP_perc)
            params["takeProfit"] = str(round(tp, 3))
        if SL_perc is not None:
            sl = trig_price * (1 - SL_perc) if buy_sell == 'Buy' else trig_price * (1 + SL_perc)
            params["stopLoss"] = str(round(sl, 3))
        params_str = json.dumps(params)

        result = BybitAPI.HTTP_Request(endpoint, method, params_str, "Create")
        data = json.loads(result)
        return data
    
    @staticmethod
    def get_position_info(symbol: str):
        endpoint = f'/v5/position/list'
        payload = 'category=linear&symbol=' + symbol
        method = 'GET'
        try:
            result = BybitAPI.HTTP_Request(endpoint, method, payload, "get_position")
            data = json.loads(result)
            
            if 'result' in data and 'list' in data['result'] and len(data['result']['list']) > 0:
                position_info = data['result']['list'][0]
                return position_info
            else:
                return None
        except Exception as e:
            print(f"Error occurred: {e}")
            return None
        
    @staticmethod
    def get_balance(coin: str):
        endpoint = '/v5/account/wallet-balance'
        payload = 'accountType=UNIFIED&coin=' + coin
        method = 'GET'
        try:
            result = BybitAPI.HTTP_Request(endpoint, method, payload, "get_position")
            data = json.loads(result)
            
            if 'result' in data and 'list' in data['result'] and len(data['result']['list']) > 0:
                wallet_info = data['result']['list'][0]
                return float(wallet_info['totalEquity'])
            else:
                return None
        except Exception as e:
            print(f"Error occurred: {e}")
            return None

    # @staticmethod
    # def modify_order(orderLinkId: str, coin: str, buy_sell: str, amount_coins: int, open_price: float, TP_perc = None, SL_perc = None):
    #     endpoint = '/v5/order/amend'
    #     method = 'POST'

    #     params = {
    #     "category": "linear",
    #     "orderId":"32fce206-8396-4fa2-b0ac-4f85ea8565e1",
    #     "symbol": coin,
    #     "orderLinkId": orderLinkId,
    #     "qty": str(amount_coins),
    #     }
    #     params_str = json.dumps(params)
    #     BybitAPI.HTTP_Request(endpoint, method, params_str, "Change_TP_SL")
    
    @staticmethod
    def tp_sl(coin: str, buy_sell: str, amount_coins: int, open_price: float, TP_perc = None, SL_perc = None):
        endpoint = '/v5/position/trading-stop'
        method = 'POST'

        params = {
            "category":"linear",
            "symbol": coin,
            "tpTriggerBy": "MarkPrice",
            "slTriggerBy": "IndexPrice",
            "tpslMode": "Partial",
            "tpOrderType": "Limit",
            "slOrderType": "Limit",
            "tpSize": str(amount_coins),
            "slSize": str(amount_coins),
            "positionIdx": 0
        }

        if TP_perc is not None:
            tp = open_price * (1 + TP_perc) if buy_sell == 'Buy' else open_price * (1 - TP_perc)
            params["takeProfit"] = str(round(tp, 3))
            params["tpLimitPrice"] = str(round(tp, 3))
            if TP_perc == 0:
                params["takeProfit"] = str(0)
        if SL_perc is not None:
            sl = open_price * (1 - SL_perc) if buy_sell == 'Buy' else open_price * (1 + SL_perc)
            params["stopLoss"] = str(round(sl, 3))
            params["slLimitPrice"] = str(round(sl, 3))
            if SL_perc == 0:
                params["stopLoss"] = str(0)
        
        params_str = json.dumps(params)
        response = BybitAPI.HTTP_Request(endpoint, method, params_str, "Change_TP_SL")
        date = json.loads(response)
        print(date)
        if 'retMsg' in date and date['retMsg'] == 'OK':
            return 'OK'
        else:
            return None
        
    @staticmethod
    def sl(coin: str, amount_coins: int, stop_loss_price: float):
        endpoint = '/v5/position/trading-stop'
        method = 'POST'

        params = {
            "category":"linear",
            "symbol": coin,
            "slTriggerBy": "IndexPrice",
            "tpslMode": "Partial",
            "slOrderType": "Limit",
            "tpSize": str(amount_coins),
            "slSize": str(amount_coins),
            "positionIdx": 0
        }


        params["stopLoss"] = str(round(stop_loss_price, 3))
        params["slLimitPrice"] = str(round(stop_loss_price, 3))
        tp = stop_loss_price * (1 + 0.02)
        # params["takeProfit"] = str(round(tp, 3))
        # params["tpLimitPrice"] = str(round(tp, 3))
        
        params_str = json.dumps(params)
        response = BybitAPI.HTTP_Request(endpoint, method, params_str, "Change_TP_SL")
        date = json.loads(response)
        print(date)
        if 'retMsg' in date and date['retMsg'] == 'OK':
            return 'OK'
        else:
            return None
        
    @staticmethod
    def trailing_stop(trail_stop: bool, coin: str, buy_sell: str, amount_coins: int, open_price: float, TS_dist: float, TS_trig: float, TP_perc = None, SL_perc = None):
        endpoint = '/v5/position/trading-stop'
        method = 'POST'
        triger = open_price * (1 + TS_trig) if buy_sell == 'Buy' else open_price * (1 - TS_trig)

        params = {
            "category":"linear",
            "symbol": coin,
            "tpTriggerBy": "MarkPrice",
            "slTriggerBy": "IndexPrice",
            "tpslMode": "Partial",
            "tpOrderType": "Limit",
            "slOrderType": "Limit",
            "tpSize": str(amount_coins),
            "slSize": str(amount_coins),
            "positionIdx": 0
        }
        if trail_stop:
            params['trailingStop'] = str(TS_dist)
            params['activePrice'] = str(round(triger, 3))
            sl = open_price * (1 - SL_perc) if buy_sell == 'Buy' else open_price * (1 + SL_perc)
            params["stopLoss"] = str(round(sl, 3))
            params["slLimitPrice"] = str(round(sl, 3))
            if SL_perc == 0:
                params["stopLoss"] = str(0)
            tp = open_price * (1 + TP_perc) if buy_sell == 'Buy' else open_price * (1 - TP_perc)
            params["takeProfit"] = str(round(tp, 3))
            params["tpLimitPrice"] = str(round(tp, 3))
            if TP_perc == 0:
                params["takeProfit"] = str(0)
        else:
            if TP_perc is not None:
                tp = open_price * (1 + TP_perc) if buy_sell == 'Buy' else open_price * (1 - TP_perc)
                params["takeProfit"] = str(round(tp, 3))
                params["tpLimitPrice"] = str(round(tp, 3))
                if TP_perc == 0:
                    params["takeProfit"] = str(0)
            if SL_perc is not None:
                sl = open_price * (1 - SL_perc) if buy_sell == 'Buy' else open_price * (1 + SL_perc)
                params["stopLoss"] = str(round(sl, 3))
                params["slLimitPrice"] = str(round(sl, 3))
                if SL_perc == 0:
                    params["stopLoss"] = str(0)
        
        params_str = json.dumps(params)
        response = BybitAPI.HTTP_Request(endpoint, method, params_str, "Change_TP_SL")
        date = json.loads(response)
        print(date['retMsg'])
        if 'retMsg' in date and date['retMsg'] == 'OK':
            return 'OK'
        else:
            return None

    @staticmethod
    def get_last_price(symbol):
        url = f"{BybitAPI.url}/v5/market/tickers?category=inverse&symbol=" + symbol
        response = requests.get(url).json()
        
        if response["retCode"] == 0:
            if len(response["result"]["list"]) > 0:
                return float(response["result"]["list"][0]["lastPrice"])
            else:
                return None
        else:
            return None
    
    @staticmethod
    def cancel_orders(symbol=None, order_id=None):
        cancel_type = "Cancel all"
        endpoint="/v5/order/cancel-all"
        method="POST"
        if symbol is not None and order_id is not None:
            orderLinkId = uuid.uuid4().hex
            pr= {
                "category":"linear",
                "symbol": symbol,
                "orderLinkId": orderLinkId,
                "orderId":order_id
                }
            params = json.dumps(pr)
            endpoint="/v5/order/cancel"
            cancel_type = "Cancel"
        else:
            params='{"category": "linear","symbol": null,"settleCoin": "USDT"}'

        BybitAPI.HTTP_Request(endpoint,method,params,cancel_type)
    
    @staticmethod
    def get_kline(coin: str, number_candles: int, interv: int):
        end = int(time.time() * 1000)  # current timestamp in milliseconds
        start = end - (number_candles * interv * 60 * 1000)  # calculate start timestamp
        endpoint= f'/v5/market/kline?category=inverse&symbol={coin}&interval={interv}&limit={number_candles}'
        url = BybitAPI.url + endpoint
        response = requests.get(url).json()

        new_list = [[int(x[0]), float(x[1]), float(x[2]), float(x[3]), float(x[4]), float(x[5])] for x in response['result']['list']]
        reversed_list = new_list[::-1]
        return reversed_list


BybitAPI.api_key = config("BBAPI")
BybitAPI.secret_key = config("BBSECRET")
BybitAPI.httpClient = requests.Session()
BybitAPI.recv_window = str(5000)
BybitAPI.url = "https://api.bybit.com"