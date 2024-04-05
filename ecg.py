#!/usr/bin/python
import asyncio
import aioconsole 
import os
from datetime import datetime
from polarh10 import PolarH10

dirname = "ibi_ecg"

def today_datestr():
    now = datetime.now()
    # We only want the last 2 digits
    year = str(now.year)[2:]
    return f"{now.day:02d}{now.month:02d}{year}"

def today_filename():
    return date_filename(today_datestr())

def date_filename(datestr):
    return f"{dirname}/ecg_{datestr}.wkt"

def append_record(ecg):
    try:
        os.mkdir(dirname)
    except FileExistsError:
        pass
    filename = today_filename()
    with open(filename, "a") as fd:
        now_time = datetime.now().time()
        fd.write(f"{now_time}  {ecg}\n")

ADDRESS = "E6:07:3D:AA:ED:02"

# https://github.com/kbre93/every-breath-you-take/

# Sample rates
IBI_UPDATE_LOOP_PERIOD = 0.01 # s, time to sleep between IBI updates

# HRV signal parameters
IBI_MIN_FILTER = 300 # ms
IBI_MAX_FILTER = 1600 # ms

async def main(address):
    polar_sensor = PolarH10(ADDRESS)
    await polar_sensor.connect()
    await polar_sensor.get_device_info()
    await polar_sensor.print_device_info()

    await polar_sensor.start_hr_stream()

    while True:
        await asyncio.sleep(IBI_UPDATE_LOOP_PERIOD)
        
        # Updating IBI history
        while not polar_sensor.ibi_queue_is_empty():
            t, ibi = polar_sensor.dequeue_ibi() # t is when value was added to the queue
            
            # Skip unreasonably low or high values
            if ibi < IBI_MIN_FILTER or ibi > IBI_MAX_FILTER:
                continue

            # convert from numpy float
            ibi = float(ibi[0])
            append_record(ibi)

    # never happens lol
    await self.polar_sensor.disconnect()

asyncio.run(main(ADDRESS))

