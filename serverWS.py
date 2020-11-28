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
t = 3
players_list = []
round_list = [Round(round_number=1, url='', time=10, answer=10, rscore=5),
              Round(round_number=2, url='', time=10, answer=11, rscore=10),
              Round(round_number=3, url='', time=10, answer=12, rscore=15),
              Round(round_number=4, url='', time=10, answer=13, rscore=20),
              Round(round_number=5, url='', time=10, answer=14, rscore=25)]


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
        # print("inside notify_state")
        print(message)
        await asyncio.wait([player.ws.send(message) for player in players_list])


async def notify_state_submit(cp):
    message = json.dumps({"player name": cp.name, "answer": cp.answer[round_counter - 1]})
    # print("after a submit: ")
    # print(message)
    await asyncio.wait([player.ws.send(message) for player in players_list])


async def callback():
    global round_counter
    global round_list
    global players_list
    round_winners_name = []

    await asyncio.sleep(5)
    for p in players_list:

        try:
            if p.answer[round_counter - 1] == round_list[round_counter].answer:
                round_winners_name.append(p.name)
        except:
            pass

    # print("after a round: ")
    print(f"time over")
    await notify_state()
    # message = json.dumps([ob.__dict__ for ob in round_winners_name])
    #
    # print("winners: ")
    # print(message)
    # await asyncio.wait([player.ws.send(message) for player in players_list])


def round_plus():
    global round_counter
    global t
    if t == 3:
        t -= 1
    elif t == 2:
        t -= 1
    else:
        t = 3
        round_counter += 1


async def answer(websocket):

    message = await websocket.recv()
    print("after answer msg await")
    # async for message in websocket:
    current_player = 0
    for p in players_list:
        if p.ws == websocket:
            current_player = p
    current_player.answer.append(int(message))

    # give scores to player
    for r in round_list:
        if r.round_number == round_counter:
            # print(round_counter)
            if current_player.answer[round_counter - 1] == r.answer:
                current_player.score += r.rscore
                break
    # notify
    # print("before notify_state")
    await notify_state_submit(current_player)
    round_plus()


async def hello(websocket, path):
    global round_counter
    global round_list
    global players_list
    name = await websocket.recv()
    await register(websocket, name)
    # try:
    while len(players_list) != 3:
        await asyncio.sleep(1)
    # while round_counter < 6:
    print(f"start")
    try:
        task1 = asyncio.create_task(callback())
        task2 = asyncio.create_task(answer(websocket))

        await task1
        await task2

    except:
        print("****")

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

    # finally:
    #     await unregister(websocket)


start_server = websockets.serve(hello, "localhost", 5000)

asyncio.get_event_loop().run_until_complete(start_server)
asyncio.get_event_loop().run_forever()