import asyncio
import websockets
import json
import time

CL_ID = 'xxxxx'
CL_SECRET = 'xxxxx'
REQ_URL = 'wss://www.deribit.com/ws/api/v2/'

acc_token = ''

msg = {
    "jsonrpc": "2.0",
    "id": 1,
    "params": {}
}

def auth_and_buy():

    async def auth_api(): 
        global msg
        global acc_token
        msg["method"] = "public/auth"
        msg["params"] = {
            "grant_type": "client_credentials",
            "client_id": CL_ID,
            "client_secret": CL_SECRET,
            "scope": "session:test"
        }

        async with websockets.connect(REQ_URL) as websocket:
            await websocket.send(json.dumps(msg))
            while websocket.open:
                response = await websocket.recv()
                response_json = json.loads(response)
                acc_token = response_json["result"]["access_token"]
                return ""

    async def check_for_position(websocket):
        global msg
        global acc_token
        msg["method"] = "private/get_positions"
        msg["params"] = {
            "currency": "BTC",
            "access_token": acc_token
            }

        await websocket.send(json.dumps(msg))
        while websocket.open:
            checks = await websocket.recv()
            response_json = json.loads(checks)
            return response_json       


    async def buy(websocket, instrument):
        global msg
        global acc_token
        msg["id"] += 1
        msg["method"] = "private/buy"
        msg["params"] = {
        "access_token": acc_token,
        "instrument_name": instrument,
        "type" : "market",
        "amount" : 30
        }   
        await websocket.send(json.dumps(msg))
        while websocket.open:
            response = await websocket.recv()
            time.sleep(3)
            result1 = json.loads(response)
            price = 0.9 * result1["result"]["trades"][0]["price"]
            price = float("{:.2f}".format(price))
            return price
        



    async def stop_market(websocket, instrument, price):
        global msg
        global acc_token
        msg["id"] += 1
        msg["method"] = "private/sell"
        msg["params"] = {
        "access_token": acc_token,
        "instrument_name": instrument,
        "type" : "market",
        "price" : price
        }
        await websocket.send(json.dumps(msg))
        while websocket.open:
            response = await websocket.recv()
            return response


    async def main():
        global msg
        await auth_api()
        async with websockets.connect(REQ_URL) as websocket:
            response = await check_for_position(websocket)
            result = response["result"]
            if result == [] or response["result"][0]["direction"] == 'zero':
                response = await buy(websocket, "BTC-PERPETUAL")
                response1 = await stop_market(websocket, "BTC-PERPETUAL", response)
                return 
            return ""




    asyncio.run(main())

auth_and_buy()
    