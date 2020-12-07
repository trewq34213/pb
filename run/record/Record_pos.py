# -*- coding:utf8 -*-

import sys
import os

sys.path.append(os.getcwd())
import lib
import time

if __name__ == '__main__':
    player = lib.Player()
    control = lib.Control(lib.DD())
    recorder = lib.PathRecorder(player=player, control=control,delay=0.5)
    print(recorder.inner_record())

