# -*- coding:utf8 -*-
from lib.struct.PixelPonit import PixelPoint
from lib.control.Driver import Driver
import time
import random
from ctypes import windll
from pykeyboard import PyKeyboard
import win32api,win32ui,win32con,win32gui
import pyperclip
k=PyKeyboard()



class Pyinput(Driver):
    vk = {
        '5': '5', 'c': 'c', 'n': 'n', 'z': 'z', '3': '3', '1': '1', 'd': 'd', '0': '0', 'l': 'l', '8': 208,
        'w': 'w', 'u': 'u', '4': '4', 'e': 'e', '[': '[', 'f': 'f', 'y': 'y', 'x': 'x', 'g': 'g', 'v': 'v',
        'r': 'r', 'i': 'i', 'a': 'a', 'm': 'm', 'h': 'h', '.': '.', ',': ',', ']': ']', '/': '/', '6': '6',
        '2': '2', 'b': 'b', 'k': 'k', '7': '7', 'q': 'q', "'": "'", '\\': 313, 'j': 'j', '`': '`', '9': '9',
        'p': 'p', 'o': 'o', 't': 't', '-': '-', '=': '=', 's': 's', ';': ';', 'tab': k.tab_key, 'enter': k.enter_key,
        'alt': k.alt_key,' ':' ',';':';','ctrl':k.control_key,'esc':k.escape_key,"f1": k.function_keys[1], "f2": k.function_keys[2],
        "f3": k.function_keys[3], "f4": k.function_keys[4], "f5": k.function_keys[5],"f8": k.function_keys[8]
    }

    # 需要组合shift的按键。
    vk2 = {
        '"': "'", '#': '3', ')': '0', '^': '6', '?': '/', '>': '.', '<': ',', '+': '=', '*': '8', '&': '7',
        '{': '[', '_': '-', '|': '\\', '~': '`', ':': ';', '$': '4', '}': ']', '%': '5', '@': '2', '!': '1',
        '(': '9'
    }

    def __init__(self):
        #lib_path = "lib/control/DD94687.64.dll"  # 你存入该文件的路径
        #self.DD = windll.LoadLibrary(lib_path)
        print("load PYinput")

    def __auto_sleep(self, min=0.1, max=0.3):
        time.sleep(random.uniform(min, max))

    def __defin_sleep(self, t):
        time.sleep(t)



    def __mov(self, ponit: PixelPoint):
        x = ponit.x + int(random.random() * random.uniform(4, 5))
        y = ponit.y + int(random.random() * random.uniform(4, 5))
        win32api.SetCursorPos((x, y))
        time.sleep(0.1)
        win32api.mouse_event(win32con.MOUSEEVENTF_LEFTDOWN |
                             win32con.MOUSEEVENTF_LEFTUP, x, y, 0, 0)
        time.sleep(0.1)

    # 键盘按下放开,t 为持续时间，为0表示自动
    def tap_key(self, key, t=0.2):
        print("tab_key:" + key)
        k.press_key(self.vk[key])
        time.sleep(t)
        k.release_key(self.vk[key])


    # 按下某个键，用于持续按
    def tap_key_down(self, key, t=0):
        print("tab_key_down:" + key)
        k.press_key(self.vk[key])
        if t == 0:
            self.__auto_sleep()
        else:
            self.__defin_sleep(t)

    # 放开某个键
    def tap_key_up(self, key, t=0):
        print("tab_key_up:" + key)
        k.release_key(self.vk[key])
        if t == 0:
            self.__auto_sleep()
        else:
            self.__defin_sleep(t)

    # 输入连续字符串
    def tap_str(self, str,t=0):
        print("tab_str:" + str)
        k.type_string(str)
        if t == 0:
            self.__auto_sleep()
        else:
            time.sleep(t)

    # 点击左键
    def move_click(self, ponit: PixelPoint, t):

        x = ponit.x + int(random.random() * 5)
        y = ponit.y + int(random.random() * 5)
        win32api.SetCursorPos((x, y))
        time.sleep(0.1)
        win32api.mouse_event(win32con.MOUSEEVENTF_LEFTDOWN |
                             win32con.MOUSEEVENTF_LEFTUP, x, y, 0, 0)
        time.sleep(0.1)
        if t == 0:
            time.sleep(random.random() * 50 + 60)  # 每隔一分多钟就点
        else:
            time.sleep(t)
        return 0

    # 点击右键
    def move_click_right(self, ponit: PixelPoint, t):
        x = ponit.x + int(random.random() * 5)
        y = ponit.y + int(random.random() * 5)
        win32api.SetCursorPos((x, y))
        time.sleep(0.5)
        win32api.mouse_event(win32con.MOUSEEVENTF_RIGHTDOWN |
                             win32con.MOUSEEVENTF_RIGHTUP, x, y, 0, 0)
        if t == 0:
            time.sleep(2)  # 每隔一分多钟就点
        else:
            time.sleep(t)
        return 0

    # 只是点击右键
    def right_click(self,t):
        raise Exception("奔哥还没有实现这个方法")

    # 滚轮向下绑定与目标互动按键，自动跑向目标
    def wheel_down(self, t=0):
        print("wheel_down:" + str(t))
        pos=[686, 327]
        x = pos[0] + int(random.random() * 5)
        y = pos[1] + int(random.random() * 5)
        win32api.SetCursorPos((x, y))
        win32api.mouse_event(win32con.MOUSEEVENTF_WHEEL, x, y, -1, win32con.WHEEL_DELTA)
        if t == 0:
            time.sleep(random.random() * 50 + 60)  # 每隔一分多钟就点
        else:
            time.sleep(t)
        return 0

    # 滚轮向上绑定选定最近敌人按键，Tab
    def wheel_up(self, t):
        pos = [686, 327]
        x = pos[0] + int(random.random() * 5)
        y = pos[1] + int(random.random() * 5)
        win32api.SetCursorPos((x, y))
        win32api.mouse_event(win32con.MOUSEEVENTF_WHEEL, x, y, 1, win32con.WHEEL_DELTA)
        if t == 0:
            time.sleep(random.random() * 50 + 60)  # 每隔一分多钟就点
        else:
            time.sleep(t)
        return 0

    # 鼠标中键绑定选中上一个敌对目标，为了捡东西
    def move_click_middle(self, pos, t):
        x = pos[0] + int(random.random() * 5)
        y = pos[1] + int(random.random() * 5)
        win32api.SetCursorPos((x, y))
        win32api.mouse_event(win32con.MOUSEEVENTF_MIDDLEDOWN |
                             win32con.MOUSEEVENTF_MIDDLEUP, x, y, 0, 0)
        if t == 0:
            time.sleep(1)  # 每隔一分多钟就点
        else:
            time.sleep(t)
        return 0

    # 右转50度
    def turn_right(self, t=0.3):
        k.press_key('J')
        time.sleep(t)
        k.release_key('J')

    # 左转50盾
    def turn_left(self, t=0.3):
        k.press_key('h')
        time.sleep(t)
        k.release_key('h')

    #复制str，并把它发送到游戏里面
    def copy_paste_send(self,str,start_enter=True,end_enter=True):
        pyperclip.copy(str)
        if start_enter is True:
            self.tap_key("enter", 1)
        k.press_key(k.control_key)
        k.tap_key("v")
        k.release_key(k.control_key)


        if end_enter is True:
            self.tap_key("enter", 1)
