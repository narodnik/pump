#!/usr/bin/python
import asyncio
import os
from datetime import datetime

from kivy.app import async_runTouchApp
from kivy.lang.builder import Builder

from android.permissions import request_permissions, Permission 
from android.storage import primary_external_storage_path
perms = [
    Permission.BLUETOOTH_CONNECT,
    Permission.BLUETOOTH_SCAN,
    Permission.WRITE_EXTERNAL_STORAGE,
    Permission.READ_EXTERNAL_STORAGE
]
request_permissions(perms)

from polarh10 import PolarH10

dirname = "Download/share/ecg"

kv = '''
BoxLayout:
    orientation: 'vertical'
    Label:
        id: label
        text: 'null'
        font_size: self.width/20
'''

def today_datestr():
    now = datetime.now()
    # We only want the last 2 digits
    year = str(now.year)[2:]
    return f"{now.day:02d}{now.month:02d}{year}"

def today_filename():
    return date_filename(today_datestr())

def date_filename(datestr):
    return os.path.join(
        primary_external_storage_path(),
        dirname,
        f"ecg_{datestr}.wkt"
    )

def append_record(ecg):
    try:
        os.mkdir(os.path.join(primary_external_storage_path(), dirname))
    except FileExistsError:
        pass
    filename = today_filename()
    with open(filename, "a") as fd:
        now_time = datetime.now().time()
        fd.write(f"{now_time}  {ecg}\n")

async def run_app(root, other_task):
    await async_runTouchApp(root, async_lib='asyncio')
    print('App done')
    other_task.cancel()

ADDRESS = "E6:07:3D:AA:ED:02"

# https://github.com/kbre93/every-breath-you-take/

# Sample rates
IBI_UPDATE_LOOP_PERIOD = 0.01 # s, time to sleep between IBI updates

# HRV signal parameters
IBI_MIN_FILTER = 300 # ms
IBI_MAX_FILTER = 1600 # ms

async def monitor_hr(root):
    polar_sensor = PolarH10(ADDRESS)
    await polar_sensor.connect()
    try:
        await run_sensor(root, polar_sensor)
    except asyncio.CancelledError as e:
        await polar_sensor.disconnect()
        print('Wasting time was canceled', e)

async def run_sensor(root, polar_sensor):
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
            # value is in ms
            ibi = float(ibi[0])
            append_record(ibi)
            ibi /= 1000
            bpm = int(60/ibi)
            root.ids.label.text = f"{ibi:.3f} ({bpm})"

root = Builder.load_string(kv)
other_task = asyncio.ensure_future(monitor_hr(root))

loop = asyncio.get_event_loop()
loop.run_until_complete(
    asyncio.gather(run_app(root, other_task), other_task)
)
loop.close()
