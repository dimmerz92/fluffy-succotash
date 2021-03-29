import websocket, json, pprint
import binance_functions as bf
import talib as ta
import numpy as np
import datetime as dt

## DATA STREAM ##
SOCKET = "wss://stream.binance.com:9443/ws/ethusdt@kline_4h"

## GLOBAL VARIABLES ##
start = 19
position = "sell"
closes = np.zeros(20)
## WEBSOCKET FUNCTIONS ##
def on_open(ws):
    print("Connection opened at", dt.datetime.now())

def on_close(ws):
    print("Connection closed at", dt.datetime.now())

def on_message(ws, message):
    global start, position, closes  

    json_message = json.loads(message)
    candle = json_message["k"]
    is_candle_closed = candle["x"]
    close = float(candle["c"])

    if is_candle_closed:
        # 20 period close window
        closes = np.roll(closes, -1)
        closes[-1] = close
        
        if start < 20:
            start += 1

        if start == 20:
            # 8 period EMA
            ema8 = ta.EMA(closes, 8)
            ema8 = ema8[-1]
        
            # 20 period EMA
            ema20 = ta.EMA(closes, 20)
            ema20 = ema20[-1]

            ## BUY
            if position == "buy":
                if ema8 > ema20:
                    order = bf.buy("ETHUSDT", "USDT")
                    bf.csv_append("tradelog.csv", order)
                    position = "sell"

            ## SELL                
            elif position == "sell":
                if ema8 < ema20:
                    order = bf.sell("ETHUSDT", "ETH")
                    bf.csv_append("tradelog.csv", order)
                    position = "buy"

ws = websocket.WebSocketApp(SOCKET, on_open=on_open, on_close=on_close, on_message=on_message)
while True:
    ws.run_forever() 
