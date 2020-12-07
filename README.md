# wow classic bot

## 【中文版】 (https://github.com/shmilyzxt/pb/blob/main/README_CN.md)

##  Introduction
- a wow classic pixel bot written by python and lua.

## Features
- muti resolution ratio support (1080p,4K,...)
- pathfinding
- path recording
- area fighting
- auto grave run
- auto repair
- spell manage,auto spell
- bag manage
- auto marco
- remote monitor
- auto chat
- auto mail notice
- screentshoots
- team support

## How to use?
- put addon\DataToColor to your wow classic Addons folder .
- in game, cancel Interface scaling and set gama = 1.
- modify run\config\UserConfig.py fit for you.
- modify run\record\path_data\DynamicConfig.py  and record: area coordinates,grave path,repair path，you can use run\record\record_v2.py to do these.
- codeing your own combat loop,for example：run\combat\QS.py
- in game,put your character in the area, and run run\combat\QS.py,enjoy!

## Project structure introduce
- addon: the addon
- lib: system folder
    + base ：base
    + bag：bag and item manage
    + chat：chat module
    + confg : system config , depend on the addon
    + control： control module
    + db: database
    + marco: marco
    + NameFinder: a libraty wirtten by C# for find enemy by it's namepad color.
    + navigation : navigation module,the most important module.
    + pixel ： addon data to python data (read in game data)
    + recorder： path recorder
    + spell： sepll manager , auto spell
    + struct： some data struct
    + tools： some tools ,like sendmail ,monitor
- run: user folder
    + combat：my combat loop
    + config：user config
    + img： some imgs
    + record： dynamic config
    + web： a web monitor
- tmp: temp floder
    + logs：logs
    + ocr：ocr data
    + screenshots：screenshots
    
- any questions,contact:49783121@qq.com    
     
