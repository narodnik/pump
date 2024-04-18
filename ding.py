#!/usr/bin/python
import os, sys, time

word = sys.argv[1]
if word[-1] == "s":
    sleep_time = int(word[:-1])
else:
    sleep_time = int(word)
    sleep_time *= 60

time.sleep(sleep_time)

os.system("mpv /home/narodnik/src/pump/ding-ding.webm")

