# -*- coding:utf8 -*-

import sys
import os

sys.path.append(os.getcwd())
import lib
import time

if __name__ == '__main__':
    time.sleep(2)
    control = lib.Control(lib.DD())
    player = lib.Player()

    from run.record.path_data.DynamicConfig import DynamicConfig

    for p in DynamicConfig.repair_path:
        targetPos = lib.WorldPoint(p[2],p[3])
        lib.WorldPathFinding(control,player).walk(targetPos=targetPos,combat_exit=True)
