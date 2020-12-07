# -*- coding:utf8 -*-

import sys
import os

sys.path.append(os.getcwd())
import lib
import time
from run.config.UserConfig import UserConfig

if __name__ == '__main__':
    time.sleep(1)
    args = sys.argv
    if len(args) != 2 and len(args) != 3:
        print("请输入正确的参数，支持：create,grave,repair,finder,commit")
        os._exit(0)
    op = args[1]

    delay = 4
    if len(args) == 3:
        delay = args[2]
    if op == "finder":
        delay = 0

    if 6 < delay < 2:
        print("延时需要在2-5秒内")
        os._exit(0)

    player = lib.Player()
    control = lib.Control(lib.DD())
    recorder = lib.PathRecorder(player=player, control=control,delay=delay)

    if op == "create":
        recorder.create_file()
    elif op == "grave":
        recorder.record_grave()
    elif op == "repair":
        recorder.record_repair()
    elif op == "commit":
        recorder.commit()
    elif op == "finder":
        recorder.record_finder()
    else:
        print("不支持的操作：" + str(op))
