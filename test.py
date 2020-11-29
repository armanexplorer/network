import random

TOTAL_TURNS = 2
ROW_NUMBER = 4
COL_NUMBER = 20
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

print(init_answers)
print()
print(bit_array)