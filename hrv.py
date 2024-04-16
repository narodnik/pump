#!/usr/bin/python

import datetime, sys
import matplotlib.pyplot as plt

if len(sys.argv) != 2:
    print("gief filename")
    sys.exit(-1)

data = open(sys.argv[1]).read()
data = data.split("\n")
data = [line.split(" ") for line in data]
# Strip ''
data = [[item for item in line if item] for line in data]
# Remove blank rows
data = [row for row in data if row]
for row in data:
    assert len(row) == 2

# Apply conversion
data = [(datetime.time.fromisoformat(time), float(ibi)) for time, ibi in data]

# Don't allow big jumps
data2 = []
ringbuf = [y for _, y in data[:5]]
def ringbuf_push(ringbuf, num):
    ringbuf.pop(0)
    ringbuf.append(num)
for x, y in data[5:]:
    avg = sum(ringbuf)/5
    ringbuf_push(ringbuf, y)
    if abs(y - avg) > 60:
        continue
    data2.append((x, y))

x_data, y_data = zip(*data2)

# Convert x_data to UNIX timestamp
start_time = x_data[0]

def to_micros(time):
    return (((time.hour*60 + time.minute)*60 + time.second)*10**6 +
            time.microsecond)

x_data = [to_micros(x) for x in x_data]

# Convert y_data to BPM
y_data = [y/1000 for y in y_data]
y_data = [60/y for y in y_data]

plt.plot(x_data, y_data)

#plt.savefig("/tmp/weight.jpg")
plt.show()
