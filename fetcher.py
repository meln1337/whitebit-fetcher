import sys
import time
import json
import websocket
import requests

if len(sys.argv) == 1:
    print("You have not specified the mode, please enter double or trades or orderbooks")
    exit()
elif sys.argv[1] == "double":
    mode = "double"
elif sys.argv[1] == "trades":
    mode = "trades"
elif sys.argv[1] == "orderbooks":
    mode = "orderbooks"
else:
    print("You have entered the wrong mode, please enter double or trades or orderbooks")
    exit()

def current_milli_time():
    return round(time.time() * 1000)

exchange = "whitebit"

res = requests.get("https://whitebit.com/api/v4/public/ticker")
res = res.json()
symbols = list(res.keys())
print(symbols)
print(len(symbols))
# print("ZRX_USDT" in symbols)
# symbols.remove("ZRX_USDT")

trades_request = json.dumps({
    "id": 9,
    "method": "trades_subscribe",
    "params": [
        *symbols,
        100
    ]
})


if mode == "trades":
    ws_trades = websocket.create_connection("wss://api.whitebit.com/ws")
    ws_trades.send(trades_request)

    while True:
        try:
            data = ws_trades.recv()
            data = json.loads(data)
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
        except:
            pass

elif mode == "orderbooks":
    ws_orderbooks = websocket.create_connection("wss://api.whitebit.com/ws")

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
        ws_orderbooks.send(orderbooks_request)
        # print(f"Subscribed to {symbol}")

    i = 0

    while True:
        try:
            data = ws_orderbooks.recv()
            # print(data)
            # time.sleep(0.1)
            data = json.loads(data)
            params = data["params"]
            full_reload = params[0]
            symbol = params[2]
            symbol = symbol.replace("_", "-")
            asks = params[1]["asks"]
            ts = current_milli_time()
            pq = "|".join([f"{ask[0]}@{ask[1]}" for ask in asks])
            print(f"$ {ts} {exchange} {symbol} S {pq} {'R' if full_reload else ''}")
            bids = params[1]["bids"]
            pq = "|".join([f"{bid[0]}@{bid[1]}" for bid in bids])
            print(f"$ {ts} {exchange} {symbol} B {pq} {'R' if full_reload else ''}")

        except:
            pass
        i += 1
        print(i)
else:
