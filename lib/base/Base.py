# -*- coding:utf8 -*-

import os
import time
import win32gui  # 要安装pywin32
import pyautogui
import ctypes
from abc import ABC


class Base:
    def __init__(self):
        self.ver = '1.0'

    @staticmethod
    def log(msg, file=None):
        print(msg)
        if file is not None:
            file.open()
            print(msg, file=file)
            file.close()

    # 获取屏幕颜色
    @staticmethod
    def get_color_RGB(x, y):
        user32 = ctypes.windll.user32
        hdc = user32.GetDC(None)
        gdi32 = ctypes.windll.gdi32
        pixel = gdi32.GetPixel(hdc, x, y)
        win32gui.ReleaseDC(None, hdc)
        r = pixel & 0x0000ff
        g = (pixel & 0x00ff00) >> 8
        b = pixel >> 16
        return [r, g, b]

    # 获取屏幕颜色10进制数字
    @staticmethod
    def get_color_INT(x, y):
        rgb = Base.get_color_RGB(x, y)
        hex_num = Base.RGB_to_Hex(rgb)
        int_num = int(hex_num, 16)
        return int_num

    # RGB格式颜色转换为16进制颜色格式
    @staticmethod
    def RGB_to_Hex(rgb):
        color = "0x"
        for i in rgb:
            num = int(i)
            # 将R、G、B分别转化为16进制拼接转换并大写  hex() 函数用于将10进制整数转换成16进制，以字符串形式表示
            color += str(hex(num))[-2:].replace('x', '0').upper()
        return color

    # 16进制颜色格式颜色转换为RGB格式
    @staticmethod
    def Hex_to_RGB(hex):
        r = int(hex[1:3], 16)
        g = int(hex[3:5], 16)
        b = int(hex[5:7], 16)
        rgb = str(r) + ',' + str(g) + ',' + str(b)
        return rgb

    # 截屏
    @staticmethod
    def screenshot(name, basepath="/tmp/screenshots/", region=False):
        dir = os.getcwd() + basepath + Base.getFormatTime(False)
        print(dir)
        if (os.path.exists(dir) == False):
            os.mkdir(dir)
        file = dir + "/" + name + "_" + Base.getFormatTime(True) + ".jpg"
        if not region:
            pyautogui.screenshot(file)
        else:
            pyautogui.screenshot(file, region=region)
        return file

    # 获取日期时间字符串
    @staticmethod
    def getFormatTime(withHour=True):
        timeArray = time.localtime(int(time.time()))
        if withHour == True:
            return time.strftime("%Y-%m-%d %H-%M-%S", timeArray)
        return time.strftime("%Y-%m-%d", timeArray)
