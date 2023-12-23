from math import ceil

raw_data = ''
count = 64  # \

with open('font.txt', 'r') as file:
    while line := file.readline()[2:].strip():
        raw_data += line

raw_data += '0' * (ceil(count * 36 / 8) * 8 - len(raw_data))

data = list()

for i in range(len(raw_data) // 8):
    data.append(int(raw_data[i * 8:i * 8 + 8], 2))

with open('ppaa.ppf', 'wb') as file:
    file.write(bytes(data))
