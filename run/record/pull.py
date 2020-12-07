# -*- coding:utf8 -*-

import sys
import os

sys.path.append(os.getcwd())
import lib
import time

args = sys.argv
if len(args) != 2:
    print("请输入正确的ID参数")
    os._exit(0)
id = args[1]
lib.PathRecorder.pull(id)