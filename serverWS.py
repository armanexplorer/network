import asyncio
import websockets
import json

#comment

answers = dict()
async def hello(websocket, path):
    
        name = await websocket.recv()
        answers[name] = []
        print(f"< {name}")

        greeting = f"Hello {name}!"
        await websocket.send(json.dumps(greeting))
        print(f"> {greeting}")

        while True:
            mes = await websocket.recv()
            print(f"< {mes}")
            answers[name].append(mes)
            # await websocket.send(mes)
            await websocket.send(json.dumps(answers))

start_server = websockets.serve(hello, "localhost", 5000)

asyncio.get_event_loop().run_until_complete(start_server)
asyncio.get_event_loop().run_forever()