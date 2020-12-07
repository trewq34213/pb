# -*- coding:utf8 -*-

import sys
import os

sys.path.append(os.getcwd())
import lib
import time
from run.config.UserConfig import UserConfig

time.sleep(2)
player = lib.Player()
control = lib.Control(lib.DD())
recorder = lib.PathRecorder(player=player, control=control)
recorder.start_record()
