import random

TOTAL_TURNS = 5
ROW_NUMBER = 10
COL_NUMBER = 10
bit_array = list()
colors = [0,1]      # 0 is grey and 1 is blue
for i in range(TOTAL_TURNS):
    l = list()
    for j in range(ROW_NUMBER):
        l.append(random.choices(colors, weights=[1,1], k=COL_NUMBER))
    bit_array.append(l)

print(bit_array[0])
print(bit_array[1])