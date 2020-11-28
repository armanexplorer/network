import asyncio
import websockets
import json
from aio_timers import Timer


class Round:
    def __init__(self, round_number, url, time, answer, rscore):
        self.round_number = round_number
        self.url = url
        self.time = time
        self.answer = answer
        self.rscore = rscore


class Player:
    def __init__(self, name, ws):
        self.name = name
        self.answer: list = []
        self.score = 0
        self.ws = ws


round_counter = 1
players_list = []
round_list = [Round(round_number=1, url='', time=5, answer=10, rscore=5),
              Round(round_number=2, url='', time=5, answer=11, rscore=10),
              Round(round_number=2, url='', time=4, answer=12, rscore=15),
              Round(round_number=4, url='', time=3, answer=13, rscore=20),
              Round(round_number=3, url='', time=3, answer=14, rscore=25)]


async def register(websocket, name):
    print(f"< {name}")
    greeting = f"Hello {name}!"
    await websocket.send(json.dumps(greeting))
    print(f"> {greeting}")
    p = Player(name, websocket)
    players_list.append(p)
    await notify_users()


async def unregister(websocket):
    p: Player
    for p in players_list:
        if p.ws == websocket:
            leftmsg = f"{p.name} Left!"
            print(f"> {leftmsg}")
            players_list.remove(p)
    await notify_users()


def state_event():
    global round_counter
    score_list = {}
    for p in players_list:
        score_list[p.name] = p.score
    return json.dumps({"round": round_counter, "scores": score_list})


def users_event():
    return json.dumps({"users": len(players_list)})


async def notify_users():
    if players_list:  # asyncio.wait doesn't accept an empty list
        message = users_event()
        await asyncio.wait([player.ws.send(message) for player in players_list])


async def notify_state():
    if players_list:  # asyncio.wait doesn't accept an empty list
        message = state_event()
        await asyncio.wait([player.ws.send(message) for player in players_list])


async def callback():
    global round_counter
    round_winners_name = []

    for p in players_list:
        try:
            if p.answer[round_counter - 1] == round_list[round_counter].answer:
                round_winners_name.append(p.name)
        except:
            pass

    message = json.dumps([ob.__dict__ for ob in round_winners_name])
    await asyncio.wait([player.ws.send(message) for player in players_list])


async def hello(websocket, path):
    global round_counter
    name = await websocket.recv()
    await register(websocket, name)
    try:
        # await asyncio.sleep(10, result=None, *, loop=None)
        while len(players_list) != 3:
            await asyncio.sleep(1)
            # message = json.dumps("Players aren't enough!")
            # await asyncio.wait([player.ws.send(message) for player in players_list])

        # timer is scheduled here
        timer = Timer(round_list[round_counter].time, callback)

        # wait until the callback has been executed
        await timer.wait()

        await websocket.send(state_event())
        async for message in websocket:
            # data = json.loads(message)
            current_player = 0
            for p in players_list:
                if p.ws == websocket:
                    current_player = p
            current_player.answer.append(int(message))

            for r in round_list:
                if r.round_number == round_counter:
                    if current_player.answer[round_counter - 1] == r.answer:
                        current_player.score += r.rscore
                        break

            await notify_state()

            round_counter += 1

            if round_counter == 6:
                max_score = 0
                winners_name = []

                for p in players_list:
                    if p.score > max_score:
                        max_score = p.score
                for p in players_list:
                    if p.score == max_score:
                        winners_name.append(p.name)

                message = json.dumps([ob.__dict__ for ob in winners_name])
                await asyncio.wait([player.ws.send(message) for player in players_list])

                await unregister(websocket)

    finally:
        await unregister(websocket)


start_server = websockets.serve(hello, "localhost", 5000)

asyncio.get_event_loop().run_until_complete(start_server)
asyncio.get_event_loop().run_forever()


'''''
    # answers[name] = []
    # p.answer = []


'''''
'''''
    while True:
        await websocket.send(json.dumps([ob.__dict__ for ob in players_list]))
        answer = await websocket.recv()
        print(f"< {answer}")
        p.answer.append(answer)

        for r in round_list:
            if r.round_number == round_counter:
                if p.answer[round_counter-1] == r.answer:
                    p.score += r.rscore

        # await websocket.send(mes)

        print(json.dumps([ob.__dict__ for ob in players_list]))

        # round_counter +=1
'''''

