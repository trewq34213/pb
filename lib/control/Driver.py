# -*- coding:utf8 -*-
import abc
from lib.struct.PixelPonit import PixelPoint


# 控制操作抽象基类
class Driver(abc.ABC):

    # 键盘按下放开,t 为持续时间，为0表示自动
    @abc.abstractmethod
    def tap_key(self, key, t=0):
        pass

    # 按下某个键，用于持续按
    @abc.abstractmethod
    def tap_key_down(self, key, t=0):
        pass

    # 放开某个键
    @abc.abstractmethod
    def tap_key_up(self, key, t=0):
        pass

    # 输入连续字符串
    @abc.abstractmethod
    def tap_str(self, str):
        pass

    # 点击左键
    @abc.abstractmethod
    def move_click(self, point: PixelPoint, t):
        pass

    # 点击右键
    @abc.abstractmethod
    def move_click_right(self, point: PixelPoint, t):
        pass

    # 滚轮向下
    @abc.abstractmethod
    def wheel_down(self, t=0):
        pass

    # 滚轮向上绑
    @abc.abstractmethod
    def wheel_up(self, t):
        pass

    # 鼠标中键按下
    @abc.abstractmethod
    def move_click_middle(self, point: PixelPoint, t):
        pass

    # 右转45度
    @abc.abstractmethod
    def turn_right(self, t=0.3):
        pass

    # 左转45盾
    @abc.abstractmethod
    def turn_left(self, t=0.3):
        pass

    # 随机左右转随机角度
    # @abc.abstractmethod
    # def turn_random(self):
    #     pass

    # 复制一段话并输入
    @abc.abstractmethod
    def copy_paste_send(self,str,start_enter=True,end_enter=True):
        pass
