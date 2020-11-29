import asyncio
from random import Random
import traceback
import random
import websockets
import json
# from aio_timers import Timer


class Round:
    def __init__(self, round_number, bit_array, time, answer, rscore):
        self.round_number = round_number
        self.bit_array = bit_array
        self.time = time
        self.answer = answer
        self.rscore = rscore


class Player:
    def __init__(self, name, ws):
        self.name = name
        self.answer: list = []
        self.score = 0
        self.ws = ws

t = 3
x = 3
players_list = []
round_counter = 1

MIN_PLAYER = 3
TOTAL_TURNS = 5
ROW_NUMBER = 4
COL_NUMBER = 20
CONST_TIME_TO_ANSWER = 30

bit_array = list()
colors = [0,1]      # 0 is grey and 1 is blue
init_answers = []
for i in range(TOTAL_TURNS):
    l = list()
    s = 0
    for j in range(ROW_NUMBER):
        ans_num_in_row = random.choice(range(5,10))
        s += ans_num_in_row
        l.append(random.choices(colors, weights=[COL_NUMBER-ans_num_in_row,ans_num_in_row], k=COL_NUMBER))
    bit_array.append(l)
    init_answers.append(s)

round_list = [Round(round_number=1, bit_array=bit_array[0], time=CONST_TIME_TO_ANSWER, answer=init_answers[0], rscore=5),
              Round(round_number=2, bit_array=bit_array[1], time=CONST_TIME_TO_ANSWER, answer=init_answers[1], rscore=10),
              Round(round_number=3, bit_array=bit_array[2], time=CONST_TIME_TO_ANSWER, answer=init_answers[2], rscore=15),
              Round(round_number=4, bit_array=bit_array[3], time=CONST_TIME_TO_ANSWER, answer=init_answers[3], rscore=20),
              Round(round_number=5, bit_array=bit_array[4], time=CONST_TIME_TO_ANSWER, answer=init_answers[4], rscore=25)]


def exception_to_string(excp):
    stack = traceback.extract_stack()[:-3] + traceback.extract_tb(excp.__traceback__)  # add limit=??
    pretty = traceback.format_list(stack)
    return ''.join(pretty) + '\n  {} {}'.format(excp.__class__, excp)


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
            # leftmsg = f"{p.name} Left!"
            # print(f"> {leftmsg}")
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
    global x
    if x == 3:
        x -= 1
    elif x == 2:
        x -= 1
    else:
        x = 3
        if players_list:  # asyncio.wait doesn't accept an empty list
            message = state_event()
            # print("inside notify_state")
            print(message)
            await asyncio.wait([player.ws.send(message) for player in players_list])


async def notify_state_submit(cp):
    message = json.dumps({"player_name": cp.name, "answer": cp.answer[round_counter - 1]})
    # print("after a submit: ")
    # print(message)
    await asyncio.wait([player.ws.send(message) for player in players_list])


async def callback(task2):
    global round_counter
    global round_list
    global players_list
    round_winners_name = []
    try:
        await asyncio.sleep(round_list[round_counter-1].time)
        for p in players_list:

            try:
                if p.answer[round_counter - 1] == round_list[round_counter].answer:
                    round_winners_name.append(p.name)
            except:
                pass
        # print("after a round: ")
        # print(f"time over")
        task2.cancel()
        await notify_state()
        round_plus()
    except Exception as e:
        print(exception_to_string(e))

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
    # print("after answer msg await")
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


async def hello(websocket, path):
    global round_counter
    global round_list
    global players_list
    name = await websocket.recv()
    await register(websocket, name)
    # try:
    while len(players_list) != MIN_PLAYER:
        await asyncio.sleep(1)

  
    

    while round_counter < TOTAL_TURNS:
        main_packet = {
            "init": True,
            "data": bit_array[round_counter-1]
        }
        await websocket.send(json.dumps(main_packet))
        # print("start")
        try:
            task2 = asyncio.create_task(answer(websocket))
            task1 = asyncio.create_task(callback(task2))
            await task1
            await task2
        except:
            pass
        # print("end of while")

    if round_counter == TOTAL_TURNS:
        max_score = 0
        winners_name = []

        for p in players_list:
            if p.score > max_score:
                max_score = p.score
        for p in players_list:
            if p.score == max_score:
                winners_name.append(p.name)

        score_list = {}
        for p in players_list:
            score_list[p.name] = p.score

        message = json.dumps({"winner": winners_name, "scores": score_list})
        await asyncio.wait([player.ws.send(message) for player in players_list])

        await unregister(websocket)


# finally:
#     await unregister(websocket)


start_server = websockets.serve(hello, "localhost", 5000)

asyncio.get_event_loop().run_until_complete(start_server)
asyncio.get_event_loop().run_forever()
