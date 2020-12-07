# 多线程函数

import datetime
import time
import os
from lib.tools.mail import sendmail
from lib.tools.WechatTemplate import WechatTemplate
import lib
import pyautogui
from run.config.UserConfig import UserConfig

# from tools.mysql import Mysql

date = lib.Base().getFormatTime(False)


# 掉线检测
# def checkOffine(offline_flag, sleep):
#     while True:
#         print("offline checking")
#         if offlineOcr(OFFLINE_ORC_REGION):
#             print("掉线了：" + " " + str(datetime.datetime.now()))
#             offline_flag.value = 1
#             return
#         time.sleep(sleep)


# 找怪截屏
def threading_screenshoot(i, name):
    lib.Base().screenshot(name)
    # print("截图完成" + str(datetime.datetime.now()))
    exit(0)


# checker截图进程
def checker_screenshot(i, sleep=30):
    while True:
        print("check screenshot")
        dir = os.getcwd() + "/tmp/screenshots/" + date + "/checker"
        if not os.path.exists(dir):
            os.makedirs(dir)
        file = dir + "/cherker_" + str(i) + "_" + lib.Base().getFormatTime(True) + ".jpg"
        pyautogui.screenshot(file)

        # print("checker截图完成" + str(datetime.datetime.now()))
        time.sleep(sleep)


# GM对话检测进程
def checker_gm(sleep, gmtalk_flag):
    while True:
        print("GM TALK checking ...")
        a = pyautogui.locateOnScreen('run/img/gm_talk.png')
        if a is not None:
            gmtalk_flag.value = 1
            print("send")
            # tpl = WechatTemplate(first="GM TALK", kw1=date, kw2="", kw3="", kw4="", kw5="", remark="")
            # tpl.post_data()

            sendmail(UserConfig.email, "GM talk to you", "", lib.Base.screenshot("gm_talk"))
            time.sleep(5)
            os.system("C:\Windows\System32\shutdown.exe -s -t  30 ")  # 关机
            time.sleep(60)
            exit(0)
        time.sleep(sleep)

# def jump(pos, sleep=5, times=5):
#     while True:
#         move_click_middle(pos, 1)
#         time.sleep(sleep)
