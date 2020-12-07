# wow classic bot

## 简介
- 本人程序员奶爸，喜欢wow，无奈带娃没时间玩，所以写了一个bot帮我打怪练级，精力有限没空维护，故开源,主要编程序语言为python，部分使用lua，少量使用C#。
该bot提供了一个编写bot的框架，在此基础上方便进行相关功能的开发，我主要是用来打怪练级，跑希利苏斯声望。

## 功能支持
- 多分辨率支持(1080p,4K都行)
- 自动导航寻路，支持夸地图，不支持夸大陆
- 路径录制
- 多手段智能寻怪
- 区域打怪
- 自动跑尸
- 自动修理出售
- 技能管理
- 智能施法
- 背包管理
- 自动宏
- 远程监控
- 自动聊天
- GM对话自动检测
- 密语检测
- 自动邮件通知
- 运行截图
- 组队模式

## 使用方法
- 将 addon 目录的 DataToColor 插件安装到wow，进入游戏后顶部会看到彩色数据条
- 游戏内将wow缩放取消，gama设置为1，设置好各个功能按键
- 配置run\config\UserConfig.py中各项参数
- 配置run\record\path_data\DynamicConfig.py 参数，并录制区域范围，跑尸路径和修理路径，录制脚本为run\record\record_v2.py
- 编写战斗文件，我提供了qs的战斗文件，参见：run\combat\QS.py
- 角色来到区域，启动QS.py 开搞

## 代码结构说明
- addon: 插件目录
- lib: 系统目录
    + base ：基类文件
    + bag：背包管理
    + chat：聊天模块
    + confg : 系统配置（与插件关联）
    + control： 控制模块
    + db: 数据库
    + marco: 自动宏
    + NameFinder: C#写个一个库，可以根据怪物姓名版颜色寻怪
    + navigation : 导航系统（包括自动寻路，自动寻怪，区域打怪，自动跑尸，自动修理）
    + pixel ： 插件数据转程序数据
    + recorder： 路径录制工具
    + specailUnit: 一些特殊的单位（我放了个希利苏斯跑战地任务的单位）
    + spell： 技能管理器，自动施法
    + struct： 一些程序内要用到的数据结构
    + tools： 一些工具，如发邮件，系统监控
- run: 用户目录
    + combat：存放战斗文件
    + config：用户配置文件
    + img： 一些要用到的图片
    + record： 路点录制工具和文件存放
    + web： 一个web监控界面
- tmp: 临时目录
    + logs：存放程序运行日志
    + ocr：存放图片识别信息
    + screenshots：存放屏幕截图
    
- 如有疑问，请联系49783121@qq.com        
     
