import cursor
import datetime
import sys
import time
import os

os.system("clear")
cursor.hide()
try:
    while True:
        print("\r%s" % datetime.datetime.now().strftime('%M:%S'), end="")
        time.sleep(1)
except KeyboardInterrupt:
    print()
    cursor.show()

