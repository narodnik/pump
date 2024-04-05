import asyncio
import aioconsole 
import os
from bleak import BleakClient
from bleak.uuids import uuid16_dict
from datetime import datetime

dirname = "ecg"

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

""" Predefined UUID (Universal Unique Identifier) mapping are based on Heart Rate GATT service Protocol that most
Fitness/Heart Rate device manufacturer follow (Polar H10 in this case) to obtain a specific response input from 
the device acting as an API """

uuid16_dict = {v: k for k, v in uuid16_dict.items()}

## UUID for model number ##
MODEL_NBR_UUID = "0000{0:x}-0000-1000-8000-00805f9b34fb".format(
    uuid16_dict.get("Model Number String")
)


## UUID for manufacturer name ##
MANUFACTURER_NAME_UUID = "0000{0:x}-0000-1000-8000-00805f9b34fb".format(
    uuid16_dict.get("Manufacturer Name String")
)

## UUID for battery level ##
BATTERY_LEVEL_UUID = "0000{0:x}-0000-1000-8000-00805f9b34fb".format(
    uuid16_dict.get("Battery Level")
)

## UUID for connection establishment with device ##
PMD_SERVICE = "FB005C80-02E7-F387-1CAD-8ACD2D8DF0C8"

## UUID for Request of stream settings ##
PMD_CONTROL = "FB005C81-02E7-F387-1CAD-8ACD2D8DF0C8"

## UUID for Request of start stream ##
PMD_DATA = "FB005C82-02E7-F387-1CAD-8ACD2D8DF0C8"

## UUID for Request of ECG Stream ##
ECG_WRITE = bytearray([0x02, 0x00, 0x00, 0x01, 0x82, 0x00, 0x01, 0x01, 0x0E, 0x00])

## For Polar H10  sampling frequency ##
ECG_SAMPLING_FREQ = 130

OUTLET = []

## Bit conversion of the Hexadecimal stream
def data_conv(sender, data: bytearray):
    print(data)
    if data[0] == 0x00:
        #print(".")
        step = 3
        samples = data[10:]
        offset = 0
        while offset < len(samples):
            ecg = convert_array_to_signed_int(samples, offset, step)
            offset += step
            print(ecg)
            append_record(ecg)
            
def convert_array_to_signed_int(data, offset, length):
    return int.from_bytes(
        bytearray(data[offset : offset + length]), byteorder="little", signed=True,
    )

async def main(address):
    async with BleakClient(address) as client:
        print("---------Looking for Device------------ ")

        await client.is_connected()
        print("---------Device connected--------------")

        model_number = await client.read_gatt_char(MODEL_NBR_UUID)
        print("Model Number: {0}".format("".join(map(chr, model_number))), flush=True)

        manufacturer_name = await client.read_gatt_char(MANUFACTURER_NAME_UUID)
        print("Manufacturer Name: {0}".format("".join(map(chr, manufacturer_name))), flush=True)

        battery_level = await client.read_gatt_char(BATTERY_LEVEL_UUID)
        print("Battery Level: {0}%".format(int(battery_level[0])), flush=True)

        
        await client.read_gatt_char(PMD_CONTROL)
        print("Collecting GATT data...")

        await client.write_gatt_char(PMD_CONTROL, ECG_WRITE)
        print("Writing GATT data...")

        ## ECG stream started
        await client.start_notify(PMD_DATA, data_conv)

        print("Collecting ECG data...")

        await aioconsole.ainput('Running: Press a key to quit')
        await client.stop_notify(PMD_DATA)
        print("Stopping ECG data...")
        print("[CLOSED] application closed.")

asyncio.run(main(ADDRESS))

