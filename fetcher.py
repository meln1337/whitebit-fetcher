import sys
import time
import json
import websocket
import requests

if len(sys.argv) == 1:
    print("You have not specified the mode, please enter both or trades or orderbooks")
    exit()
elif sys.argv[1] == "both":
    mode = "both"
elif sys.argv[1] == "trades":
    mode = "trades"
elif sys.argv[1] == "orderbooks":
    mode = "orderbooks"
else:
    print("You have entered the wrong mode, please enter both or trades or orderbooks")
    exit()

def current_milli_time():
    return round(time.time() * 1000)

exchange = "whitebit"

res = requests.get("https://whitebit.com/api/v4/public/ticker")
res = res.json()
symbols = list(res.keys())

trades_request = json.dumps({
    "id": 9,
    "method": "trades_subscribe",
    "params": [
        *symbols,
        100
    ]
})

def print_trades(data):
    params = data["params"]
    symbol = params[0]
    symbol = symbol.replace("_", "-")
    trades = params[1]
    for trade in trades:
        ts = current_milli_time()
        price = trade["price"]
        amount = trade["amount"]
        side = "B" if trade["type"] == "buy" else "S"
        print(f"! {ts} {exchange} {symbol} {side} {price} {amount}")
def print_orderbooks(data):
    params = data["params"]
    full_reload = params[0]
    symbol = params[2]
    symbol = symbol.replace("_", "-")
    asks = params[1]["asks"]
    ts = current_milli_time()
    pq = "|".join([f"{ask[1]}@{ask[0]}" for ask in asks])
    print(f"$ {ts} {exchange} {symbol} S {pq} {'R' if full_reload else ''}")
    bids = params[1]["bids"]
    pq = "|".join([f"{bid[1]}@{bid[0]}" for bid in bids])
    print(f"$ {ts} {exchange} {symbol} B {pq} {'R' if full_reload else ''}")

def trades_sub(ws):
    ws.send(trades_request)

def orderbooks_sub(ws):
    for symbol in symbols:
        orderbooks_request = json.dumps({
            "id": 12,
            "method": "depth_subscribe",
            "params": [
                symbol,
                100,
                "0",
                True
            ]
        })
        ws.send(orderbooks_request)

ws = websocket.create_connection("wss://api.whitebit.com/ws")

if mode == "trades":
    trades_sub(ws)

    while True:
        data = ws.recv()
        data = json.loads(data)
        try:
            print_trades(data)
        except:
            pass

elif mode == "orderbooks":
    orderbooks_sub(ws)
    while True:
        data = ws.recv()
        data = json.loads(data)
        try:
            print_orderbooks(data)
        except:
            pass
else:
    trades_sub(ws)
    orderbooks_sub(ws)

    while True:
        data = ws.recv()
        data = json.loads(data)
        try:
            if data["method"] == "trades_update":
                print_trades(data)

            elif data["method"] == "depth_update":
                print_orderbooks(data)
        except:
            pass

ws.close()