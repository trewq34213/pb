# -*- coding:utf8 -*-

from lib.struct.PixelPonit import PixelPoint


class UserConfig:
    # 坐标与像素配置
    distance = 11.9  # 像素块宽度
    start_pos = PixelPoint(6, 29)  # 第一块像素中心点坐标


    # 属性配置
    email = "xxxxx@qq.com"  # 重要信息通知邮箱
    move_step = 0  # 找怪时向前走几次然后转身 （0-5）0 随机。1 原地
    time_without_enemy = 300  # 多长时间没有找到敌人报警（秒）
    time_enemy_full_life = 20  # 怪物多长时间不掉血放弃（秒）
    shut_time = 0  # 到几点关机，0表示不关机 ， 24小时制
    die_shut = 0  # 死亡后是否自动关机，0 否 1 是
    level_height_than_me = 2  # 高自己多少级的怪不打
    level_low_than_me = 8  # 低自己多级的怪不打
    point_confound_rang = 100  # 鼠标右键点击移动时的坐标浮动范围
    check_touch_by_other = 1  # 检车目标是否被被人摸过，如果调整过界面，请设置为0
    find_enemy_move_type = 0  # 找怪时的移动方式，0 使用鼠标右键移动， 1 使用键盘移动
    find_enemy_strategy = 4  # 寻怪策略 0：随机寻怪 1：圆形渐开线 2：方形渐开线 3：对角线 4:路点寻怪(如果没有录制寻怪路点，则 还是0)
    enemy_touch_by_other_pos = PixelPoint(310, 65)  # 判断敌人是否被别人摸过的坐标(目标名字颜色是灰色)
    attack_elite = False  # 是否攻击精英和稀有，默认位False
    use_name_finder = False # 是否使用name finder辅助寻怪
    enable_monitor = False # 是否开启网页监控

# 按键映射
    # 冒号左边是技能孔位，见图片
    # 冒号右边是键盘按键
    # 重要： 13-24号栏位是动作条2
    slot_to_key = {
        13: "1",
        14: "2",
        15: "3",
        16: "4",
        17: "5",  # 绑定蓝瓶
        18: "6",  # 绑定药瓶
        19: "7",  # 绑定烹饪食品
        20: "8",  # 绑定水
        21: "9",  # 绑定面包
        22: "0",  # 绑定绷带
        23: "-",  # 绑定法师的发力宝石，或者ss的糖
        24: "=",  # 绑定清除目标宏
        61: "q",
        62: "x",
        63: "e",
        64: "r",
        65: "f",
        66: "g",
        67: "c",
        68: "z",
        69: "t",
        70: "u",
        71: "y",
        72: "v",
    }

    # 按键绑定
    # 重要：这里不能改只能按照这个设置键位
    keyboard_bind = {
        "与目标交互": "'",  # 回车旁边那个单引号
        "选中上一个敌对目标": ";"  # 单引号旁边那个分号
    }
