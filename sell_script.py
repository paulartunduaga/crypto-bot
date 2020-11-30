import asyncio
import websockets
import json

CL_ID = 'xxxx'
CL_SECRET = 'xxxx'
REQ_URL = 'wss://www.deribit.com/ws/api/v2/'

acc_token = ''


msg = {
    "jsonrpc": "2.0",
    "id": 1,
    "params": {}
}


def auth_and_sell():

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



    async def stop_market(websocket, instrument):
        global msg
        global acc_token
        msg["id"] += 1
        msg["method"] = "private/close_position"
        msg["params"] = {
        "access_token": acc_token,
        "instrument_name": instrument,
        "type" : "market",
        "reduce_only" : "true"
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
            if response["result"][0]["direction"] == 'buy':
                response2 = await stop_market(websocket, "BTC-PERPETUAL")
                return response2


    

    asyncio.run(main())

auth_and_sell()
