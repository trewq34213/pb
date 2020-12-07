----------------------------------------------------------------------------
-- DataToColor - display player position as color
----------------------------------------------------------------------------
-- GetMapZones(continentIndex)
DataToColor = {}
DataToColor = LibStub("AceAddon-3.0"):NewAddon("AceConsole-3.0", "AceEvent-3.0", "AceTimer-3.0", "AceComm-3.0", "AceSerializer-3.0")

DATA_CONFIG = {
    ACCEPT_PARTY_REQUESTS = false, -- O
    DECLINE_PARTY_REQUESTS = true, -- O
    RIGHT = true,
    DUEL = false,
    GOSSIP = true,
    REZ = true,
    HIDE_SHAPESHIFT_BAR = true,
    AUTO_REPAIR_ITEMS = true, -- O
    AUTO_LEARN_TALENTS = true, -- O
    AUTO_TRAIN_SPELLS = true, -- O
    AUTO_RESURRECT = true,
    SELL_WHITE_ITEMS = true
}

--TODO List of talents that will be trained
local talentList = {
    "Improved Frostbolt",
    "Ice Shards",
    "Frostbite",
    "Piercing Ice",
    "Improved Frost Nova",
    "Shatter",
    "Arctic Reach",
    "Ice Block",
    "Ice Barrier",
    "Winter's Chill",
    "Frost Channeling",
    "Frost Warding",
    "Elemental Precision",
    "Permafrost",
    "Improved Fireball",
    "Improved Fire Blast"
}

local CORPSE_RETRIEVAL_DISTANCE = 40
local ASSIGN_MACROS = true

-- 有多少人在攻击我变量
local who_is_attacking_me = {}
local current_time

-- 有人密我变量
local sombody_whisper_me = 0

-- Trigger between emitting game data and frame location data
SETUP_SEQUENCE = false
-- Exit process trigger
EXIT_PROCESS_STATUS = 0

-- 要查找的物品id变量
FIND_ITEM_ID = 0

-- Assigns various macros if user changes variable to true
ASSIGN_MACROS_INITIALIZE = false
-- Total number of data frames generated
local NUMBER_OF_FRAMES = 150
-- Set number of pixel rows
local FRAME_ROWS = 1
-- Size of data squares in px. Varies based on rounding errors as well as dimension size. Use as a guideline, but not 100% accurate.
local CELL_SIZE = 5
-- Spacing in px between data squares.
local CELL_SPACING = 0
-- Item slot trackers initialization
local itemNum = 0
local slotNum = 0
local equipNum = 0
local globalCounter = 0
-- Global table of all items player has
local items = {}
local itemsPlaceholderComparison = {}
local enchantedItemsList = {}
-- How often item frames change
local ITEM_ITERATION_FRAME_CHANGE_RATE = 6
local MAX_BAG_SLOTS = 20

-- Action bar configuration for which spells are tracked
local MAIN_MIN = 13
local MAIN_MAX = 24 --13-24 第二动作条
local BOTTOM_LEFT_MIN = 61 --61-72 左下动作条
local BOTTOM_LEFT_MAX = 72

DataToColor.frames = nil
DataToColor.r = 0

-- Note: Coordinates where player is standing (max: 10, min: -10)
-- Note: Player direction is in radians (360 degrees = 2π radians)
-- Note: Player health/mana is taken out of 100% (0 - 1)

-- Character's name
local CHARACTER_NAME = UnitName("player")

-- List of possible subzones to which a player's hearthstone may be bound
local HearthZoneList = { "CENARION HOLD", "VALLEY OF TRIALS", "THE CROSSROADS", "RAZOR HILL", "DUROTAR", "ORGRIMMAR", "CAMP TAURAJO", "FREEWIND POST", "GADGETZAN", "SHADOWPREY VILLAGE", "THUNDER BLUFF", "UNDERCITY", "CAMP MOJACHE", "COLDRIDGE VALLEY", "DUN MOROGH", "THUNDERBREW DISTILLERY", "IRONFORGE", "STOUTLAGER INN", "STORMWIND CITY", "SOUTHSHORE", "LAKESHIRE", "STONETALON PEAK", "GOLDSHIRE", "SENTINEL HILL", "DEEPWATER TAVERN", "THERAMORE ISLE", "DOLANAAR", "ASTRANAAR", "NIJEL'S POINT", "CRAFTSMEN'S TERRACE", "AUBERDINE", "FEATHERMOON STRONGHOLD", "BOOTY BAY", "WILDHAMMER KEEP", "DARKSHIRE", "EVERLOOK", "RATCHET", "LIGHT'S HOPE CHAPEL" }
local EnchantmentStrings = {}

function DataToColor:slashCommands()
    SLASH_DC1 = "/dc";
    SLASH_DC2 = "/datatocolor";
    SlashCmdList["DC"] = StartSetup;
end

-- Function to quickly log info to wow console
function DataToColor:log(msg)
    DEFAULT_CHAT_FRAME:AddMessage(msg) -- alias for convenience
end

function StartSetup()
    if not SETUP_SEQUENCE then
        SETUP_SEQUENCE = true
    else
        SETUP_SEQUENCE = false
    end
end

function DataToColor:error(msg)
    self:log("|cff0000ff" .. msg .. "|r")
    self:log(msg)
    self:log(debugstack())
    error(msg)
end

-- Automatic Modulo function for Lua 5 and earlier
function Modulo(val, by)
    return val - math.floor(val / by) * by
end

-- Check if two tables are identical
function ValuesAreEqual(t1, t2, ignore_mt)
    local ty1 = type(t1)
    local ty2 = type(t2)
    if ty1 ~= ty2 then return false end
    -- non-table types can be directly compared
    if ty1 ~= 'table' and ty2 ~= 'table' then return t1 == t2 end
    -- as well as tables which have the metamethod __eq
    local mt = getmetatable(t1)
    if not ignore_mt and mt and mt.__eq then return t1 == t2 end
    for k1, v1 in pairs(t1) do
        local v2 = t2[k1]
        if v2 == nil or not ValuesAreEqual(v1, v2) then return false end
    end
    for k2, v2 in pairs(t2) do
        local v1 = t1[k2]
        if v1 == nil or not ValuesAreEqual(v1, v2) then return false end
    end
    return true
end

-- Discover player's direction in radians (360 degrees = 2π radians)
function DataToColor:GetPlayerFacing()
    local p = Minimap
    local m = ({ p:GetChildren() })[9]
    local facing = GetPlayerFacing()
    if facing then
        return facing
    else
        return 0
    end
end

-- This function runs when addon is initialized/player logs in
-- Decides length of white box
function DataToColor:OnInitialize()
    self:CreateFrames(NUMBER_OF_FRAMES)
    self:log("DataToColor已加载：涛哥幸苦写代码，不带涛哥下副本，你过意的去么？")
    self:slashCommands();
end

function integerToColor(i)
    if i ~= math.floor(i) then
        error("The number passed to 'integerToColor' must be an integer")
    end

    if i > (256 * 256 * 256 - 1) then -- the biggest value to represent with 3 bytes of colour
        error("Integer too big to encode as color")
    end

    -- r,g,b are integers in range 0-255
    local b = Modulo(i, 256)
    i = math.floor(i / 256)
    local g = Modulo(i, 256)
    i = math.floor(i / 256)
    local r = Modulo(i, 256)

    -- then we turn them into 0-1 range
    return { r / 255, g / 255, b / 255 }
end

-- This function is able to pass numbers in range 0 to 9.99999 (6 digits)
-- converting them to a 6-digit integer.
function fixedDecimalToColor(f)
    if f > 9.99999 then
        -- error("Number too big to be passed as a fixed-point decimal")
        return { 0 }
    elseif f < 0 then
        return { 0 }
    end

    local f6 = tonumber(string.format("%.5f", 1))
    local i = math.floor(f * 100000)
    return integerToColor(i)
end

-- Pass in a string to get the upper case ASCII values. Converts any special character with ASCII values below 100
function DataToColor:StringToASCIIHex(str)
    -- Converts string to upper case so only 2 digit ASCII values
    str = string.sub(string.upper(str), 0, 6)
    -- Sets string to an empty string
    local ASCII = ''
    -- Loops through all of string passed to it and converts to upper case ASCII values
    for i = 1, string.len(str) do
        -- Assigns the specific value to a character to then assign to the ASCII string/number
        local c = string.sub(str, i, i)
        -- Concatenation of old string and new character
        ASCII = ASCII .. string.byte(c)
    end
    return tonumber(ASCII)
end

-- Function to mass generate all of the initial frames for the pixel reader
function DataToColor:CreateFrames(n)
    -- Note: Use single frame and update color on game update call
    local function UpdateFrameColor(elapsed)
        -- set the frame color to random values
        xCoordi, yCoordi = self:GetCurrentPlayerPosition()
        if xCoordi == nil or yCoordi == nil then
            xCoordi = 0
            yCoordi = 0
        end
        -- Makes a 5px by 5px square. Might be 6x5 or 6x5.
        -- This is APPROXIMATE MATH. startingFrame is the x start, startingFramey is the "y" start (both starts are in regard to pixel position on the main frame)
        function MakePixelSquareArr(col, slot)
            if type(slot) ~= "number" or slot < 0 or slot >= NUMBER_OF_FRAMES then
                self:error("Invalid slot value")
            end

            if type(col) ~= "table" then
                self:error("Invalid color value (" .. tostring(col) .. ")")
            end

            self.frames[slot + 1]:SetBackdropColor(col[1], col[2], col[3], 1)
        end

        -- Number of loops is based on the number of generated frames declared at beginning of script
        for i = 1, NUMBER_OF_FRAMES - 1 do
            MakePixelSquareArr({ 63 / 255, 0, 63 / 255 }, i)
        end
        if not SETUP_SEQUENCE then
            self:HandleEvents()

            MakePixelSquareArr(integerToColor(0), 0)
            -- The final data square, reserved for additional metadata.
            MakePixelSquareArr(integerToColor(2000001), NUMBER_OF_FRAMES - 1)

            -- 坐标朝向
            MakePixelSquareArr(fixedDecimalToColor(xCoordi * 10), 1) --1 任务x坐标
            MakePixelSquareArr(fixedDecimalToColor(yCoordi * 10), 2) --2 任务y坐标
            MakePixelSquareArr(fixedDecimalToColor(DataToColor:GetPlayerFacing()), 3) -- 人物朝向弧度
            MakePixelSquareArr(fixedDecimalToColor(self:CorpsePosition("x") * 10), 4) -- 尸体x坐标
            MakePixelSquareArr(fixedDecimalToColor(self:CorpsePosition("y") * 10), 5) -- 尸体y坐标

            --生命值，魔法值
            MakePixelSquareArr(integerToColor(self:getHealthMax("player")), 6) --最大生命值
            MakePixelSquareArr(integerToColor(self:getHealthCurrent("player")), 7) --当前生命值
            MakePixelSquareArr(integerToColor(self:getManaMax("player")), 8) --最大魔法值(怒气)
            MakePixelSquareArr(integerToColor(self:getManaCurrent("player")), 9) --当前魔法值
            MakePixelSquareArr(integerToColor(self:getManaMax("target")), 62) --敌人最大魔法值(怒气)
            MakePixelSquareArr(integerToColor(self:getManaCurrent("target")), 63) --敌人当前魔法值
            -- 玩家bool--
            MakePixelSquareArr(integerToColor(self:Base2ConverterPlayer()), 10) --各种状态bool

            --人物等级
            MakePixelSquareArr(integerToColor(self:getPlayerLevel()), 11) --人物等级

            -- Start combat/NPC related variables --
            MakePixelSquareArr(integerToColor(self:isInRange()), 12) -- Represents if target is within 20, 30, 35, or greater than 35 yards
            MakePixelSquareArr(integerToColor(self:getHealthMax("target")), 13) -- 目标最大生命值
            MakePixelSquareArr(integerToColor(self:getHealthCurrent("target")), 14) -- 目标当前生命值

            -- Amount of money in coppers
            MakePixelSquareArr(integerToColor(Modulo(self:getMoneyTotal(), 1000000)), 15) -- 金币1
            MakePixelSquareArr(integerToColor(floor(self:getMoneyTotal() / 1000000)), 16) -- 金币2  gold= gold1 + gold2 * 1000000
            -- Start main action page (page 1)
            MakePixelSquareArr(integerToColor(self:spellStatus()), 17) -- 技能状态
            MakePixelSquareArr(integerToColor(self:spellAvailable()), 18) -- 技能是否可用?
            MakePixelSquareArr(integerToColor(self:notEnoughMana()), 19) -- 是否有足够魔法
            MakePixelSquareArr(integerToColor(self:spellInRange()), 64) -- 是否在范围内

            -- buff区
            MakePixelSquareArr(integerToColor(self:checkPlayerBuff()), 20) -- 玩家buff
            MakePixelSquareArr(integerToColor(self:checkPlayerDebuff()), 21) -- 玩家debuff
            MakePixelSquareArr(integerToColor(self:checkTargetBuff()), 22) -- 目标buff
            MakePixelSquareArr(integerToColor(self:checkTargetDebuff()), 23) -- 目标debuff

            MakePixelSquareArr(integerToColor(sombody_whisper_me), 24) -- 有人密我
            MakePixelSquareArr(integerToColor(self:howManyAreAttackingMe(elapsed)), 25) -- 攻击我的敌人数量
            MakePixelSquareArr(integerToColor(self:GetCombatPoint()), 26) -- 连击点数
            MakePixelSquareArr(integerToColor(self:GameTime()), 27) -- 游戏时间
            MakePixelSquareArr(integerToColor(self:GetGossipIcons()), 28) -- 对话框打开时的可用对话选项
            MakePixelSquareArr(integerToColor(self:TargetClass()), 29) -- 目标职业
            MakePixelSquareArr(integerToColor(self:PlayerClass()), 30) -- 玩家职业
            MakePixelSquareArr(integerToColor(self:isSkinnable()), 31) -- Returns 1 if creature is unskinnable
            MakePixelSquareArr(integerToColor(self:getTargetLevel()), 32) -- 目标等级
            MakePixelSquareArr(integerToColor(self:Base2ConverterTarget()), 33) --目标状态bool

            -- 各个背包的格子数，以及是否满了
            MakePixelSquareArr(integerToColor(self:bagSlotsAndIsFull(0)), 34)
            MakePixelSquareArr(integerToColor(self:bagSlotsAndIsFull(1)), 35)
            MakePixelSquareArr(integerToColor(self:bagSlotsAndIsFull(2)), 36)
            MakePixelSquareArr(integerToColor(self:bagSlotsAndIsFull(3)), 37)
            MakePixelSquareArr(integerToColor(self:bagSlotsAndIsFull(4)), 38)

            -- 目标uuid
            MakePixelSquareArr(integerToColor(self:getTargetUUID()), 39)
            MakePixelSquareArr(integerToColor(self:shapeshiftForm()), 57) -- Shapeshift id https://wowwiki.fandom.com/wiki/API_GetShapeshiftForm
            MakePixelSquareArr(integerToColor(self:IsTargetOfTargetPlayerAsNumber()), 58) -- IsTargetOfTargetPlayerAsNumber
            MakePixelSquareArr(integerToColor(self:FindBagItem()), 59) -- 背包某个物品的数量
            MakePixelSquareArr(integerToColor(self:hasItemBit()), 125) --背包物品检测，一个色块可以检测24个物品
            --MakePixelSquareArr(integerToColor(self:hearthZoneID()), 32) -- Returns subzone of that is currently bound to hearhtstone

            -- 宠物 130开始
            MakePixelSquareArr(integerToColor(self:getHealthMax("pet")), 130) --最大生命值
            MakePixelSquareArr(integerToColor(self:getHealthCurrent("pet")), 131) --当前生命值
            MakePixelSquareArr(integerToColor(self:getManaMax("pet")), 132) --最大魔法值(怒气)
            MakePixelSquareArr(integerToColor(self:getManaCurrent("pet")), 133) --当前魔法值
            MakePixelSquareArr(integerToColor(self:Base2ConverterPet()), 134) -- 宠物状态

            -- TODO 下面部分有待研究
            -- Begin Items section --
            -- there are 5 item slots: main backpack and 4 pouches
            -- Indexes one slot from each bag each frame. SlotN (1-16) and bag (0-4) calculated here:
            if Modulo(globalCounter, ITEM_ITERATION_FRAME_CHANGE_RATE) == 0 then
                itemNum = itemNum + 1
                equipNum = equipNum + 1
                -- Reseting global counter to prevent integer overflow
                if globalCounter > 10000 then
                    globalCounter = 1000
                end
            end
            -- Controls rate at which item frames change.
            globalCounter = globalCounter + 1

            if itemNum >= MAX_BAG_SLOTS + 1 then
                itemNum = 1
            end

            -- Uses data pixel positions 40-49
            for bagNo = 0, 4 do
                -- Returns item ID and quantity
                MakePixelSquareArr(integerToColor(self:itemName(bagNo, itemNum)), 40 + bagNo * 2) -- 40 42 44 46 48
                -- Return item slot number
                MakePixelSquareArr(integerToColor(bagNo + itemNum - bagNo), 41 + bagNo * 2) -- 41 43 45 47 49
                MakePixelSquareArr(integerToColor(self:itemInfo(bagNo, itemNum)), 50 + bagNo) -- 50-54
            end
            -- Worn inventory start.
            -- Starts at beginning once we have looked at all desired slots.
            if equipNum - 19 == 0 then
                equipNum = 1
            end
            local equipName = self:equipName(equipNum)
            -- Equipment ID
            MakePixelSquareArr(integerToColor(equipName), 55)
            -- Equipment slot
            MakePixelSquareArr(integerToColor(equipNum), 56)

            -- 70 -80 10个像素为玩家名称
            local start = 70
            local palyerNameTable = self:GetPlayerNameColorTable()
            for k, v in ipairs(palyerNameTable) do
                if start < 80 then
                    MakePixelSquareArr(v, start)
                    start = start + 1
                end
            end

            -- 80-90 10个像素为目标名称
            local start = 80
            local targetNameTable = self:GetTargetNameColorTable()
            for k, v in ipairs(targetNameTable) do
                if start < 90 then
                    MakePixelSquareArr(v, start)
                    start = start + 1
                end
            end

            -- 90-100 10个像素为所在区域GetZoneName
            local start = 90
            local zoneNameTable = self:GetZoneNameColorTable()
            for k, v in ipairs(zoneNameTable) do
                if start < 100 then
                    MakePixelSquareArr(v, start)
                    start = start + 1
                end
            end

            -- 100-124 1-4号队友数据，每个队友占6个色块
            local start = 100
            for i = 0, 23, 6 do
                local now_slot = start + i
                local index = i / 6 + 1 -- 第几个队友 1-4，每个队友占6个色块

                -- 队友坐标
                local x, y = self:GetPartyPosition(index)
                MakePixelSquareArr(fixedDecimalToColor(x * 10), now_slot) --x坐标
                MakePixelSquareArr(fixedDecimalToColor(y * 10), now_slot + 1) --y坐标

                --队友尸体坐标
                local cx, cy = self:partyCorpsePosition(index)
                MakePixelSquareArr(fixedDecimalToColor(cx * 10), now_slot + 2) --尸体x坐标
                MakePixelSquareArr(fixedDecimalToColor(cy * 10), now_slot + 3) --尸体y坐标

                --生命/power百分比
                local php, mhp = self:partyHPMPPercent(index)
                local r = math.floor(php * 100)
                local g = math.floor(mhp * 100)
                MakePixelSquareArr({ r / 255, g / 255, 0 }, now_slot + 4)

                -- 各种bool状态
                MakePixelSquareArr(integerToColor(self:Base2ConverterParty(index)), now_slot + 5)
            end
        end
        if SETUP_SEQUENCE then
            -- Emits meta data in data square index 0 concerning our estimated cell size, number of rows, and the numbers of frames
            MakePixelSquareArr(integerToColor(CELL_SIZE * 100000 + 1000 * FRAME_ROWS + NUMBER_OF_FRAMES), 0)
            -- Assign pixel squares a value equivalent to their respective indices.
            for i = 1, NUMBER_OF_FRAMES - 1 do
                MakePixelSquareArr(integerToColor(i), i)
            end
        end
        -- Note: Use this area to set color for individual pixel frames
        -- Cont: For example self.frames[0] = playerXCoordinate while self.frames[1] refers to playerXCoordinate
    end

    -- Function used to generate a single frame
    local function setFramePixelBackdrop(f)
        f:SetBackdrop({
            bgFile = "Interface\\AddOns\\DataToColor\\white.tga",
            insets = { top = 0, left = 0, bottom = 0, right = 0 },
        })
    end

    local function genFrame(name, x, y)
        local f = CreateFrame("Frame", name, UIParent)
        f:SetPoint("TOPLEFT", x * (CELL_SIZE + CELL_SPACING), -y * (CELL_SIZE + CELL_SPACING))
        f:SetHeight(CELL_SIZE)
        f:SetWidth(CELL_SIZE) -- Change this to make white box wider
        setFramePixelBackdrop(f)
        f:SetFrameStrata("DIALOG")
        return f
    end

    n = n or 0

    local frame = 1 -- try 1
    local frames = {}

    -- background frame
    local backgroundframe = genFrame("frame_0", 0, 0)
    backgroundframe:SetHeight(FRAME_ROWS * (CELL_SIZE + CELL_SPACING))
    backgroundframe:SetWidth(floor(n / FRAME_ROWS) * (CELL_SIZE + CELL_SPACING))
    backgroundframe:SetFrameStrata("HIGH")

    --    local windowCheckFrame = CreateFrame("Frame", "frame_windowcheck", UIParent)
    --    windowCheckFrame:SetPoint("TOPLEFT", 120, -200)
    --    windowCheckFrame:SetHeight(5)
    --    windowCheckFrame:SetWidth(5)
    --    windowCheckFrame:SetFrameStrata("LOW")
    --    setFramePixelBackdrop(windowCheckFrame)
    --    windowCheckFrame:SetBackdropColor(0.5, 0.1, 0.8, 1)
    --
    --    -- creating a new frame to check for open BOE and BOP windows
    --    local bindingCheckFrame = CreateFrame("Frame", "frame_bindingcheck", UIParent)
    --    -- 90 and 200 are the x and y offsets from the default "CENTER" position
    --    bindingCheckFrame:SetPoint("CENTER", 90, 200)
    --    -- Frame height as 5px
    --    bindingCheckFrame:SetHeight(5)
    --    -- Frame width as 5px
    --    bindingCheckFrame:SetWidth(5)
    --    -- sets the priority of the Frame
    --    bindingCheckFrame:SetFrameStrata("LOW")
    --    setFramePixelBackdrop(bindingCheckFrame)
    --    -- sets the rgba color format
    --    bindingCheckFrame:SetBackdropColor(0.5, 0.1, 0.8, 1)

    -- Note: Use for loop based on input to generate "n" number of frames
    for frame = 0, n - 1 do
        local y = Modulo(frame, FRAME_ROWS) -- those are grid coordinates (1,2,3,4 by  1,2,3,4 etc), not pixel coordinates
        local x = floor(frame / FRAME_ROWS)
        -- Put frame information in to an object/array
        frames[frame + 1] = genFrame("frame_" .. tostring(frame), x, y)
    end

    -- Assign self.frames to frame list generated above
    self.frames = frames
    self.frames[1]:SetScript("OnUpdate", function(self, elapsed) UpdateFrameColor(elapsed) end)
    self.frames[1]:RegisterEvent("PLAYER_REGEN_DISABLED") --注册进入战斗事件
    self.frames[1]:RegisterEvent("PLAYER_REGEN_ENABLED") -- 注册离开战斗事件
    self.frames[1]:RegisterEvent("CHAT_MSG_WHISPER") -- 注册有人密我事件
    self.frames[1]:SetScript("OnEvent", function(self, event, ...)
        if event == "COMBAT_LOG_EVENT_UNFILTERED" then
            local time_stamp, a, b, target_id, source_name, source_flags, d, player_id, dest_name = CombatLogGetCurrentEventInfo(event)
            if not current_time or time_stamp > current_time then
                current_time = time_stamp
            end

            if dest_name == CHARACTER_NAME and target_id and bit.band(source_flags, COMBATLOG_OBJECT_TYPE_NPC) == COMBATLOG_OBJECT_TYPE_NPC then --如果目标是我并且源是个玩家，则加入攻击table，如果需要判断怪物使用：COMBATLOG_OBJECT_TYPE_NPC
                who_is_attacking_me[target_id] = current_time
            end
        elseif event == "PLAYER_REGEN_DISABLED" then -- 进入战斗，显示插件
            frames[1]:RegisterEvent("COMBAT_LOG_EVENT_UNFILTERED") -- 注册战斗记录事件
        elseif event == "PLAYER_REGEN_ENABLED" then --离开战斗，清空攻击我的列表
            wipe(who_is_attacking_me)
            current_time = nil
            frames[1]:UnregisterEvent("COMBAT_LOG_EVENT_UNFILTERED")
        elseif event == "CHAT_MSG_WHISPER" then
            sombody_whisper_me = sombody_whisper_me + 1
        end
    end)
end

--多少人攻击我
function DataToColor:howManyAreAttackingMe(elapsed)
    local n = 0
    for k, v in pairs(who_is_attacking_me) do
        --			print(k,v)
        if v > current_time - 3 then
            n = n + 1
        else
            who_is_attacking_me[k] = nil
        end
    end
    return n
end

-- 目标连击点数
function DataToColor:GetCombatPoint()
    local p = GetComboPoints("player", "target")
    if p == nil then
        return 0
    end
    return p
end

-- 获取目标的ID
function DataToColor:getTargetUUID()
    local guid = UnitGUID("target")
    if guid == nil then
        return 0
    end
    local ret = ""
    for i = 1, string.len(guid), 1 do
        local sub = string.sub(guid, i, i + 1)
        ret = ret .. string.format("%X", string.byte(sub))
    end

    local g = 0
    for i = 1, string.len(ret), 4 do
        g = g + tonumber(string.sub(ret, i, i + 4), 16)
    end
    for i = 1, string.len(ret), 3 do
        g = g + tonumber(string.sub(ret, i, i + 3), 16)
    end
    for i = 1, string.len(ret), 2 do
        g = g + tonumber(string.sub(ret, i, i + 2), 16)
    end
    for i = 1, string.len(ret), 1 do
        g = g + tonumber(string.sub(ret, i, i + 1), 16)
    end
    return g
end

-- Use Astrolabe function to get current player position
-- party1 可以表示第一个队友
function DataToColor:GetCurrentPlayerPosition()
    local map = C_Map.GetBestMapForUnit("player")
    if map ~= nil then
        local position = C_Map.GetPlayerMapPosition(map, "player")
        -- Resets map to correct zone ... removed in 8.0.1, needs to be tested to see if zone auto update
        -- SetMapToCurrentZone()
        return position:GetXY()
    else
        return 0, 0
    end
end

-- Base 2 converter for up to 24 boolean values to a single pixel square.

--玩家的各种状态
function DataToColor:Base2ConverterPlayer()
    -- 1, 2, 4, 8, 16, 32, 64, 128, 256, 512, 1024, 2048, 4096, 8192, 16384
    local outdoor = 0
    if IsOutdoors() then
        outdoor = 1
    end

    local playerCasting = 0 --玩家施法
    local playerChanneld = 0 --玩家引导
    local playerInterupable = 1 --目标是否可打断

    --玩家施法
    local name, text, texture, startTimeMS, endTimeMS, isTradeSkill, castID, notInterruptible, spellId = CastingInfo("player")
    if name then
        playerCasting = 1
    end

    --玩家引导
    local name, text, texture, startTimeMS, endTimeMS, isTradeSkill, notInterruptible, spellId = ChannelInfo("player")
    if name then
        playerChanneld = 1
    end

    local inRaid = IsInRaid()
    local inGroup = IsInGroup() -- 注意：该函数在小队或者团队都会返回true，如果要检测团队要先用IsInRaid()

    if inRaid then
        inRaid = 1
    else
        inRaid = 0
    end

    local inParty = 0
    if inGroup and inRaid == 0 then
        local inParty = 1
    end

    --希利苏斯占地任务id=8507完成状态
    local xlss_quest_8507_complete = 0
    if IsQuestComplete(8507) == true then
        xlss_quest_8507_complete = 1
    end

    -- 骑行状态
    local mount = 0
    if IsMounted() == true then
        mount = 1
    end

    return self:MakeIndexBase2(self:deadOrAlive(), 0) +
            self:MakeIndexBase2(self:PlayerIsGhost(), 1) +
            self:MakeIndexBase2(self:playerCombatStatus(), 2) +
            self:MakeIndexBase2(outdoor, 3) +
            self:MakeIndexBase2(playerCasting, 4) +
            self:MakeIndexBase2(playerChanneld, 5) +
            self:MakeIndexBase2(playerInterupable, 6) +
            self:MakeIndexBase2(inParty, 7) +
            self:MakeIndexBase2(inRaid, 8) +
            self:MakeIndexBase2(xlss_quest_8507_complete, 9) +
            self:MakeIndexBase2(mount, 10) +
            self:MakeIndexBase2(0, 11) +
            self:MakeIndexBase2(self:needSign(), 12) +
            self:MakeIndexBase2(self:needManaBottom(), 13) +
            self:MakeIndexBase2(self:needRedBottom(), 14) +
            self:MakeIndexBase2(self:needCookie(), 15) +
            self:MakeIndexBase2(self:needWater(), 16) +
            self:MakeIndexBase2(self:needFood(), 17) +
            self:MakeIndexBase2(self:needManaGem(), 18) +
            self:MakeIndexBase2(self:needBandage(), 19) +
            self:MakeIndexBase2(self:GetInventoryBroken(), 20) +
            self:MakeIndexBase2(self:IsPlayerFlying(), 21) +
            self:MakeIndexBase2(self:checkTalentPoints(), 22) +
            self:MakeIndexBase2(self:ProcessExitStatus(), 23)
end

--宠物状态bool
function DataToColor:Base2ConverterPet()
    local happiness, damagePercentage, loyaltyRate = GetPetHappiness() -- 猎人宠物专用
    if happiness == nil then
        happiness = 3 -- 1 = unhappy, 2 = content, 3 = happy
    end
    return self:MakeIndexBase2(UnitExists("pet") == true and 1 or 0, 0) +
            self:MakeIndexBase2(UnitIsDead("pet") == true and 1 or 0, 1) +
            self:MakeIndexBase2(UnitAffectingCombat("pet") == true and 1 or 0, 2) +
            self:MakeIndexBase2(self:IsPetVisible(), 3) +
            self:MakeIndexBase2(happiness, 4) +
            self:MakeIndexBase2(self:GetPetActionCooldown(4), 5) +
            self:MakeIndexBase2(self:GetPetActionCooldown(5), 6) +
            self:MakeIndexBase2(self:GetPetActionCooldown(6), 7) +
            self:MakeIndexBase2(self:GetPetActionCooldown(7), 8) +
            self:MakeIndexBase2(0, 9) +
            self:MakeIndexBase2(0, 10) +
            self:MakeIndexBase2(0, 11) +
            self:MakeIndexBase2(0, 12) +
            self:MakeIndexBase2(0, 13) +
            self:MakeIndexBase2(0, 14) +
            self:MakeIndexBase2(0, 15) +
            self:MakeIndexBase2(0, 16) +
            self:MakeIndexBase2(0, 17) +
            self:MakeIndexBase2(0, 18) +
            self:MakeIndexBase2(0, 19) +
            self:MakeIndexBase2(0, 20) +
            self:MakeIndexBase2(0, 21) +
            self:MakeIndexBase2(0, 22) +
            self:MakeIndexBase2(self:ProcessExitStatus(), 23)
end

-- 宠物技能栏冷却情况 0 不可用 1 可用
function DataToColor:GetPetActionCooldown(index)
    if index < 4 or index > 7 then
        return 1
    end
    local startTime, duration, enable = GetPetActionCooldown(index)
    if duration == 0 then
        return 1
    end
    return 0
end

-- 玩家buff
function DataToColor:checkPlayerBuff()
    return self:MakeIndexBase2(self:GetBuffs("奥术智慧"), 0) +
            self:MakeIndexBase2(self:GetBuffs("霜甲术"), 1) +
            self:MakeIndexBase2(self:GetBuffs("冰甲术"), 2) +
            self:MakeIndexBase2(self:GetBuffs("寒冰护体"), 3) +
            self:MakeIndexBase2(self:GetBuffs("拯救祝福"), 4) +
            self:MakeIndexBase2(self:GetBuffs("荆棘术"), 5) +
            self:MakeIndexBase2(self:GetBuffs("命令圣印"), 6) +
            self:MakeIndexBase2(self:GetBuffs("正义圣印"), 7) +
            self:MakeIndexBase2(self:GetBuffs("十字军圣印"), 8) +
            self:MakeIndexBase2(self:GetBuffs("战斗怒吼"), 9) +
            self:MakeIndexBase2(self:GetBuffs("进食充分"), 10) +
            self:MakeIndexBase2(self:GetBuffs("力量祝福"), 11) +
            self:MakeIndexBase2(self:GetBuffs("真言术：韧"), 12) +
            self:MakeIndexBase2(self:GetBuffs("野性印记"), 13) +
            self:MakeIndexBase2(self:GetBuffs("智慧祝福"), 14) +
            self:MakeIndexBase2(self:GetBuffs("牺牲祝福"), 15) +
            self:MakeIndexBase2(self:GetBuffs("反击风暴"), 16) +
            self:MakeIndexBase2(self:GetBuffs("鲁莽"), 17) +
            self:MakeIndexBase2(self:GetBuffs("回春术"), 18) +
            self:MakeIndexBase2(self:GetBuffs("真言术：盾"), 19) +
            self:MakeIndexBase2(self:GetBuffs("虔诚光环"), 20) +
            self:MakeIndexBase2(self:GetBuffs("惩罚光环"), 21) +
            self:MakeIndexBase2(self:GetBuffs("心灵之火"), 22) +
            self:MakeIndexBase2(self:ProcessExitStatus(), 23)
end

--玩家debuff
function DataToColor:checkPlayerDebuff()
    return self:MakeIndexBase2(self:GetPlayerDebuffs("新近包扎"), 0) +
            self:MakeIndexBase2(self:GetPlayerDebuffs("自律"), 1) +
            self:MakeIndexBase2(self:GetPlayerDebuffs("疲劳"), 2) +
            self:MakeIndexBase2(self:GetPlayerDebuffs("虚弱灵魂"), 3) +
            self:MakeIndexBase2(0, 4) +
            self:MakeIndexBase2(0, 5) +
            self:MakeIndexBase2(0, 6) +
            self:MakeIndexBase2(0, 7) +
            self:MakeIndexBase2(0, 8) +
            self:MakeIndexBase2(0, 9) +
            self:MakeIndexBase2(0, 10) +
            self:MakeIndexBase2(0, 11) +
            self:MakeIndexBase2(0, 12) +
            self:MakeIndexBase2(0, 13) +
            self:MakeIndexBase2(0, 14) +
            self:MakeIndexBase2(0, 15) +
            self:MakeIndexBase2(0, 16) +
            self:MakeIndexBase2(0, 17) +
            self:MakeIndexBase2(0, 18) +
            self:MakeIndexBase2(0, 19) +
            self:MakeIndexBase2(0, 20) +
            self:MakeIndexBase2(0, 21) +
            self:MakeIndexBase2(0, 22) +
            self:MakeIndexBase2(self:ProcessExitStatus(), 23)
end

--目标的各种状态
function DataToColor:Base2ConverterTarget()
    -- 1, 2, 4, 8, 16, 32, 64, 128, 256, 512, 1024, 2048, 4096, 8192, 16384
    local targetCasting = 0 --目标施法
    local targetChanneld = 0 --目标引导
    local targetInterupable = 1 --目标是否可打断

    --目标施法
    --[[local name, text, texture, startTimeMS, endTimeMS, isTradeSkill, castID, notInterruptible, spellId = CastingInfo("target")
    if name then
        targetCasting = 1
        if notInterruptible then
            targetInterupable = 0
        end
    end]]

    --目标引导
    --[[local name, text, texture, startTimeMS, endTimeMS, isTradeSkill, notInterruptible, spellId = ChannelInfo("target")
    if name then
        targetChanneld = 1
        if notInterruptible then
            targetInterupable = 0
        end
    end]]

    return self:MakeIndexBase2(self:targetCombatStatus(), 0) +
            self:MakeIndexBase2(self:TargetIsDead(), 1) +
            self:MakeIndexBase2(self:TargetIsEnemy(), 2) +
            self:MakeIndexBase2(self:TargetCanAttach(), 3) +
            self:MakeIndexBase2(self:IsTargetOfTargetPlayer(), 4) +
            self:MakeIndexBase2(self:TargetIsElite(), 5) +
            self:MakeIndexBase2(self:TargetIsPlayer(), 6) +
            self:MakeIndexBase2(targetCasting, 7) +
            self:MakeIndexBase2(targetChanneld, 8) +
            self:MakeIndexBase2(targetInterupable, 9) +
            self:MakeIndexBase2(0, 10) +
            self:MakeIndexBase2(0, 11) +
            self:MakeIndexBase2(0, 12) +
            self:MakeIndexBase2(0, 13) +
            self:MakeIndexBase2(0, 14) +
            self:MakeIndexBase2(0, 15) +
            self:MakeIndexBase2(0, 16) +
            self:MakeIndexBase2(0, 17) +
            self:MakeIndexBase2(0, 18) +
            self:MakeIndexBase2(0, 19) +
            self:MakeIndexBase2(0, 20) +
            self:MakeIndexBase2(0, 21) +
            self:MakeIndexBase2(0, 22) +
            self:MakeIndexBase2(self:ProcessExitStatus(), 23)
end

-- 目标buff
function DataToColor:checkTargetBuff()
    return self:MakeIndexBase2(self:GetTargetBuffs("奥术智慧"), 0) +
            self:MakeIndexBase2(self:GetTargetBuffs("霜甲术"), 1) +
            self:MakeIndexBase2(self:GetTargetBuffs("冰甲术"), 2) +
            self:MakeIndexBase2(self:GetTargetBuffs("寒冰护体"), 3) +
            self:MakeIndexBase2(self:GetTargetBuffs("拯救祝福"), 4) +
            self:MakeIndexBase2(self:GetTargetBuffs("荆棘术"), 5) +
            self:MakeIndexBase2(self:GetTargetBuffs("命令圣印"), 6) +
            self:MakeIndexBase2(self:GetTargetBuffs("正义圣印"), 7) +
            self:MakeIndexBase2(self:GetTargetBuffs("十字军圣印"), 8) +
            self:MakeIndexBase2(self:GetTargetBuffs("战斗怒吼"), 9) +
            self:MakeIndexBase2(self:GetTargetBuffs("进食充分"), 10) +
            self:MakeIndexBase2(self:GetTargetBuffs("力量祝福"), 11) +
            self:MakeIndexBase2(self:GetTargetBuffs("真言术：韧"), 12) +
            self:MakeIndexBase2(self:GetTargetBuffs("野性印记"), 13) +
            self:MakeIndexBase2(self:GetTargetBuffs("智慧祝福"), 14) +
            self:MakeIndexBase2(self:GetTargetBuffs("牺牲祝福"), 15) +
            self:MakeIndexBase2(self:GetTargetBuffs("恶魔皮肤"), 16) +
            self:MakeIndexBase2(self:GetTargetBuffs("鲁莽"), 17) +
            self:MakeIndexBase2(self:GetTargetBuffs("盾墙"), 18) +
            self:MakeIndexBase2(self:GetTargetBuffs("真言术：盾"), 19) +
            self:MakeIndexBase2(self:GetTargetBuffs("光明祝福"), 20) +
            self:MakeIndexBase2(self:GetTargetBuffs("惩罚光环"), 21) +
            self:MakeIndexBase2(self:GetTargetBuffs("心灵之火"), 22) +
            self:MakeIndexBase2(self:ProcessExitStatus(), 23)
end

--目标debuff
function DataToColor:checkTargetDebuff()
    return self:MakeIndexBase2(self:GetTargetDebuffs("新近包扎"), 0) +
            self:MakeIndexBase2(self:GetTargetDebuffs("自律"), 1) +
            self:MakeIndexBase2(self:GetTargetDebuffs("疲劳"), 2) +
            self:MakeIndexBase2(self:GetTargetDebuffs("虚弱灵魂"), 3) +
            self:MakeIndexBase2(self:GetTargetDebuffs("挫志怒吼"), 4) +
            self:MakeIndexBase2(self:GetTargetDebuffs("断筋"), 5) +
            self:MakeIndexBase2(self:GetTargetDebuffs("撕裂"), 6) +
            self:MakeIndexBase2(self:GetTargetDebuffs("流血"), 7) +
            self:MakeIndexBase2(self:GetTargetDebuffs("月火术"), 8) +
            self:MakeIndexBase2(self:GetTargetDebuffs("精灵之火（野性）"), 9) +
            self:MakeIndexBase2(0, 10) +
            self:MakeIndexBase2(0, 11) +
            self:MakeIndexBase2(0, 12) +
            self:MakeIndexBase2(0, 13) +
            self:MakeIndexBase2(0, 14) +
            self:MakeIndexBase2(0, 15) +
            self:MakeIndexBase2(0, 16) +
            self:MakeIndexBase2(0, 17) +
            self:MakeIndexBase2(0, 18) +
            self:MakeIndexBase2(0, 19) +
            self:MakeIndexBase2(0, 20) +
            self:MakeIndexBase2(0, 21) +
            self:MakeIndexBase2(0, 22) +
            self:MakeIndexBase2(self:ProcessExitStatus(), 23)
end

--背包物品检测
function DataToColor:hasItemBit()
    return self:MakeIndexBase2(self:hasItem(23024), 0) + -- 准备好的占地任务文件，希利苏斯跑声望任务用
            self:MakeIndexBase2(0, 1) +
            self:MakeIndexBase2(0, 2) +
            self:MakeIndexBase2(0, 3) +
            self:MakeIndexBase2(0, 4) +
            self:MakeIndexBase2(0, 5) +
            self:MakeIndexBase2(0, 6) +
            self:MakeIndexBase2(0, 7) +
            self:MakeIndexBase2(0, 8) +
            self:MakeIndexBase2(0, 9) +
            self:MakeIndexBase2(0, 10) +
            self:MakeIndexBase2(0, 11) +
            self:MakeIndexBase2(0, 12) +
            self:MakeIndexBase2(0, 13) +
            self:MakeIndexBase2(0, 14) +
            self:MakeIndexBase2(0, 15) +
            self:MakeIndexBase2(0, 16) +
            self:MakeIndexBase2(0, 17) +
            self:MakeIndexBase2(0, 18) +
            self:MakeIndexBase2(0, 19) +
            self:MakeIndexBase2(0, 20) +
            self:MakeIndexBase2(0, 21) +
            self:MakeIndexBase2(self:hasItem(6948), 22) + -- 炉石
            self:MakeIndexBase2(self:ProcessExitStatus(), 23)
end

-- 检测姿态，返回一个数字
function DataToColor:shapeshiftForm()
    local form = GetShapeshiftForm(true)
    if form == nil then
        form = 0
    end;
    return form;
end

-- 背包中是否有某个物品id
function DataToColor:hasItem(id)
    local itemId
    local itemCount
    local itemQulity
    for i = 0, 4 do -- 5个包
        local bagSlots = GetContainerNumSlots(i)
        for j = 1, bagSlots do
            _, itemCount, _, itemQulity, _, _, _, _, _, itemId = GetContainerItemInfo(i, j)
            if itemId == id then
                return 1
            end
        end
    end
    return 0
end

-- Returns bitmask values.
-- MakeIndexBase2(true, 4) --> returns 16
-- MakeIndexBase2(false, 9) --> returns 0
function DataToColor:MakeIndexBase2(bool, power)
    if bool ~= nil and bool > 0 then
        return math.pow(2, power)
    else return 0
    end
end

-- Grabs current target's name (friend or foe)
function DataToColor:GetTargetName(partition)
    -- Uses wow function to get target string
    local target = GetUnitName("target")
    if target ~= nil then
        target = DataToColor:StringToASCIIHex(target)
        if partition < 3 then
            return tonumber(string.sub(target, 0, 6))
        else if target > 999999 then
            return tonumber(string.sub(target, 7, 12))
        end
        end
        return 0
    end
    return 0
end

-- 获取目标名称的颜色table
function DataToColor:GetTargetNameColorTable()
    -- Uses wow function to get target string
    local target = GetUnitName("target")
    if target ~= nil then
        return Utf8StringToColor(target)
    end
    return {}
end

-- 获取玩家名称的颜色table
function DataToColor:GetPlayerNameColorTable()
    -- Uses wow function to get target string
    local player = GetUnitName("player")
    if player ~= nil then
        return Utf8StringToColor(player)
    end
    return {}
end

-- Finds maximum amount of health player can have
function DataToColor:getHealthMax(unit)
    local health = UnitHealthMax(unit)
    return health
end

-- Finds axact amount of health player current has
function DataToColor:getHealthCurrent(unit)
    local health = UnitHealth(unit)
    return health
end

-- Finds maximum amount of mana a character can store
function DataToColor:getManaMax(unit)
    local manaMax = UnitPowerMax(unit)
    return manaMax
end

-- Finds exact amount of mana player is storing
function DataToColor:getManaCurrent(unit)
    local mana = UnitPower(unit)
    return mana
end

-- Finds player current level
function DataToColor:getPlayerLevel()
    return UnitLevel("player")
end

--获取目标等级，如果目标等级未知或者？？，返回999
function DataToColor:getTargetLevel()
    local level = UnitLevel("target")
    if level == -1 then
        level = 999
    end
    return level
end

-- Finds the total amount of money.
function DataToColor:getMoneyTotal()
    return GetMoney()
end

-- Finds if target is attackable with the fireball which is the longest distance spell.
-- Fireball or a spell with equivalent range must be in slot 2 for this to work
function DataToColor:isInRange()
    -- Assigns arbitrary value (50) to note the target is not within range
    local range = 50
    if IsActionInRange(1) then range = 25 end --冲锋25码
    if IsActionInRange(61) then range = 5 end -- 近战距离可用，5码内
    return range
end

-- A function used to check which items we have.
-- Find item IDs on wowhead in the url: e.g: http://www.wowhead.com/item=5571/small-black-pouch. Best to confirm ingame if possible, though.
function DataToColor:itemName(bag, slot)
    local item = 0
    local icon, itemCount, locked, quality, readable, lootable, itemLink, isFiltered, noValue, itemID = GetContainerItemInfo(bag, slot)
    if itemID then
        if itemCount > 100 then itemCount = 100 end
        item = itemID + itemCount * 100000
    end
    items[(bag * MAX_BAG_SLOTS) + slot] = item
    return item
end

function DataToColor:itemInfo(bag, slot)
    local itemCount;
    _, itemCount, _, _, _, _, _ = GetContainerItemInfo(bag, slot);
    local value = 0;
    if itemCount ~= nil and itemCount > 0 then
        local isSoulBound = C_Item.IsBound(ItemLocation:CreateFromBagAndSlot(bag, slot));
        if isSoulBound == true then value = 1 end
    else
        value = 2;
    end
    return value;
end

-- Returns item id from specific index in global items table
function DataToColor:returnItemFromIndex(index)
    return items[index]
end

function DataToColor:enchantedItems()
    if ValuesAreEqual(items, itemsPlaceholderComparison) then
    end
end

function DataToColor:equipName(slot)
    local equip
    if GetInventoryItemLink("player", slot) == nil then
        equip = 0
    else _, _, equip = string.find(GetInventoryItemLink("player", slot), "(m:%d+)")
        equip = string.gsub(equip, 'm:', '')
    end
    if equip == nil then equip = 0
    end
    return tonumber(equip)
end

-- -- Function to tell if a spell is on cooldown and if the specified slot has a spell assigned to it
-- -- Slot ID information can be found on WoW Wiki. Slots we are using: 1-12 (main action bar), Bottom Right Action Bar maybe(49-60), and  Bottom Left (61-72)
-- 使用的24个空的技能状态

function DataToColor:spellStatus()
    local statusCount = 0
    for i = MAIN_MIN, MAIN_MAX do -- 13-24号技能(动作条2，比知道为啥战士动作条1-12不准)
        -- Make spellAvailable and spellStatus one function in future
        local status, b, available = GetActionCooldown(i)
        if status == 0 and available == 1 then
            statusCount = statusCount + (2 ^ (i - 13))
        end
    end
    for i = BOTTOM_LEFT_MIN, BOTTOM_LEFT_MAX do -- 左下技能
        local status, b, available = GetActionCooldown(i)
        if status == 0 and available == 1 then
            statusCount = statusCount + (2 ^ (i - 49))
        end
    end
    return statusCount
end

-- Finds if spell is equipped
function DataToColor:spellAvailable()
    local availability = 0
    for i = MAIN_MIN, MAIN_MAX do
        local _, _, available = GetActionCooldown(i)
        if available == 1 then
            availability = availability + (2 ^ (i - 13))
        end
    end
    for i = BOTTOM_LEFT_MIN, BOTTOM_LEFT_MAX do
        local _, _, available = GetActionCooldown(i)
        if available == 1 then
            availability = availability + (2 ^ (i - 49))
        end
    end
    return availability
end

-- Returns base two representation of if we have enough mana to cast a specified spells. Slots 1-11 and slots 61-71
function DataToColor:notEnoughMana()
    local notEnoughMana = 0
    -- Loops through main action bar slots 1-12
    for i = MAIN_MIN, MAIN_MAX do
        local _, notEnough = IsUsableAction(i)
        if notEnough == 1 or notEnough == true then
            notEnoughMana = notEnoughMana + (2 ^ (i - 13))
        end
    end
    -- Loops through bottom left action bar slots 61-72
    for i = BOTTOM_LEFT_MIN, BOTTOM_LEFT_MAX do
        local _, notEnough = IsUsableAction(i)
        if notEnough == 1 or notEnough == true then
            notEnoughMana = notEnoughMana + (2 ^ (i - 49))
        end
    end
    return notEnoughMana
end

-- 检测动作条中的技能是否在范围内
--只检测技能，物品等其他东西忽略
function DataToColor:spellInRange()
    local inrange = 0
    for i = MAIN_MIN, MAIN_MAX do
        local r = IsActionInRange(i)
        if r then
            inrange = inrange + (2 ^ (i - 13))
        end
    end
    for i = BOTTOM_LEFT_MIN, BOTTOM_LEFT_MAX do
        local r = IsActionInRange(i)
        if r then
            inrange = inrange + (2 ^ (i - 49))
        end
    end
    return inrange
end

-- Function to tell how many bag slots we have in each bag
function DataToColor:bagSlots(bag)
    bagSlots = GetContainerNumSlots(bag)
    return bagSlots
end

--获取背包格子数以及空余数量
function DataToColor:bagSlotsAndIsFull(bag)
    local slots
    slots = self:bagSlots(bag)

    if slots == nil or slots == 0 then -- 该位置没有背包
        return 0
    end

    local enmpty = 0
    for i = 1, slots, 1 do
        local unknow1, itemCount, locked, quality, readable, lootable, name, unknow8, unknow9, itemId
        unknow1, itemCount, locked, quality, readable, lootable, name, unknow8, unknow9, itemId = GetContainerItemInfo(bag, i)
        if itemId == nil then
            enmpty = enmpty + 1
        end
    end

    return slots * 100 + enmpty
end

-- Finds passed in string to return profession level
function DataToColor:GetProfessionLevel(skill)
    local numskills = GetNumSkillLines();
    for c = 1, numskills do
        local skillname, _, _, skillrank = GetSkillLineInfo(c);
        if (skillname == skill) then
            return tonumber(skillrank);
        end
    end
    return 0;
end

-- Checks target to see if  target has a specified debuff
function DataToColor:GetTargetDebuffs(debuff)
    for i = 1, 5 do local db = UnitDebuff("target", i);
        if db ~= nil then
            if string.find(db, debuff) then
                return 1
            end
        end
    end
    return 0
end

-- Checks target to see if  target has a specified debuff
function DataToColor:GetPlayerDebuffs(debuff)
    for i = 1, 5 do local db = UnitDebuff("player", i);
        if db ~= nil then
            if string.find(db, debuff) then
                return 1
            end
        end
    end
    return 0
end

-- Checks target to see if  target has a specified debuff
function DataToColor:GetTargetDebuffs(debuff)
    for i = 1, 5 do local db = UnitDebuff("target", i);
        if db ~= nil then
            if string.find(db, debuff) then
                return 1
            end
        end
    end
    return 0
end

-- Returns zone name
function DataToColor:GetZoneName(partition)
    local zone = DataToColor:StringToASCIIHex(GetZoneText())
    if zone and tonumber(string.sub(zone, 7, 12)) ~= nil then
        -- Returns first 3 characters of zone
        if partition < 3 then
            return tonumber(string.sub(zone, 0, 6))
            -- Returns characters 4-6 of zone
        elseif partition >= 3 then
            return tonumber(string.sub(zone, 7, 12))
        end
    end
    -- Fail safe to prevent nil
    return 1
end

function DataToColor:GetZoneNameColorTable()
    local zoneText = GetZoneText()
    return Utf8StringToColor(zoneText)
end

-- Game time on a 24 hour clock
function DataToColor:GameTime()
    local hours, minutes = GetGameTime()
    hours = (hours * 100) + minutes
    return hours
end

function DataToColor:GetGossipIcons()
    -- Checks if we have options available
    local option = GetGossipOptions()
    -- Checks if we have an active quest in the gossip window
    local activeQuest = GetGossipActiveQuests()
    -- Checks if we have a quest that we can pickup
    local availableQuest = GetGossipAvailableQuests()
    local gossipCode
    -- 0 表示没有对话选项
    if option == nil and activeQuest == nil and availableQuest == nil then
        gossipCode = 0
        -- 1 表示有对话选项但都不是任务
    elseif option ~= nil and activeQuest == nil and availableQuest == nil then
        gossipCode = 1
        -- 2 表示只有任务选项
    elseif option == nil and (activeQuest ~= nil or availableQuest) ~= nil then
        gossipCode = 2
        -- Code 3 表示同时有任务选项和对话选项
    elseif option ~= nil and (activeQuest ~= nil or availableQuest) ~= nil then
        gossipCode = 3
        -- -- Error catcher
    else
        gossipCode = 0
    end
    return gossipCode
end

--return the x and y of corpse and resurrect the player if he is on his corpse
--the x and y is 0 if not dead
--runs the RetrieveCorpse() function to ressurrect
function DataToColor:CorpsePosition(coord)
    -- Assigns death coordinates
    local cX
    local cY
    if UnitIsGhost("player") then
        local map = C_Map.GetBestMapForUnit("player")
        if C_DeathInfo.GetCorpseMapPosition(map) ~= nil then
            cX, cY = C_DeathInfo.GetCorpseMapPosition(map):GetXY()
        end
    end
    if coord == "x" then
        if cX ~= nil then
            return cX
        else
            return 0
        end
    end
    if coord == "y" then
        if cY ~= nil then
            return cY
        else
            return 0
        end
    end
end

--returns class of player
function DataToColor:PlayerClass()
    -- UnitClass returns class and the class in uppercase e.g. "Mage" and "MAGE"
    local class, CC, index = UnitClass("player")
    return index
end

--returns class of target
--None = 0
--Warrior = 1
--Paladin = 2
--Hunter = 3
--Rogue = 4
--Priest = 5
--DeathKnight = 6
--Shaman = 7
--Mage = 8
--Warlock = 9
--Monk = 10
--Druid = 11
--Demon Hunter = 12
function DataToColor:TargetClass()
    local class, CC, index = UnitClass("target")
    if index ~= nil then
        return index
    end
    return 0
end

-- party的信息------------------------------------------------
-- party是否战斗
function DataToColor:partyCombatStatus(i)
    local unitId = "party" .. i
    local combatStatus = UnitAffectingCombat(unitId)
    -- if target is in combat, return 0 for bitmask
    if combatStatus then
        return 1
        -- if target is not in combat, return 1 for bitmask
    else return 0
    end
end

-- party是否死亡
function DataToColor:partyIsDead(i)
    local unitId = "party" .. i
    local targStatus = UnitIsDead(unitId)
    if targStatus then
        return 1
    else
        return 0
    end
end

-- party坐标
-- party1 可以表示第一个队友 i=1-4
function DataToColor:GetPartyPosition(i)
    local unitId = "party" .. i
    local map = C_Map.GetBestMapForUnit(unitId)
    local position = C_Map.GetPlayerMapPosition(map, unitId)
    -- Resets map to correct zone ... removed in 8.0.1, needs to be tested to see if zone auto update
    -- SetMapToCurrentZone()
    return position:GetXY()
end

-- party尸体坐标
function DataToColor:partyCorpsePosition(i)
    local uintId = "party" .. i
    local cX
    local cY
    if UnitIsGhost(uintId) then
        local map = C_Map.GetBestMapForUnit(uintId)
        if C_DeathInfo.GetCorpseMapPosition(map) ~= nil then
            cX, cY = C_DeathInfo.GetCorpseMapPosition(map):GetXY()
        end
    end

    if cX == nil then
        cX = 0
    end
    if cY == nil then
        cY = 0
    end
    return cX, cY
end

-- party 生命和power百分比
function DataToColor:partyHPMPPercent(i)
    local unit = "party" .. i
    local health = UnitHealth(unit)
    local healthMax = UnitHealthMax(unit)
    local healthPercent = 0

    if healthMax > 0 then
        healthPercent = health / healthMax
    end

    local mana = UnitPower(unit)
    local manaMax = UnitPowerMax(unit)
    local manaPercent = 0

    if manaMax > 0 then
        manaPercent = mana / manaMax
    end

    healthPercent = tonumber(string.format("%.2f", healthPercent))
    manaPercent = tonumber(string.format("%.2f", manaPercent))
    return healthPercent, manaPercent
end

-- partyi的各种bool
function DataToColor:Base2ConverterParty(i)
    -- 1, 2, 4, 8, 16, 32, 64, 128, 256, 512, 1024, 2048, 4096, 8192, 16384
    return self:MakeIndexBase2(self:partyCombatStatus(i), 0) +
            self:MakeIndexBase2(self:partyIsDead(i), 1) +
            self:MakeIndexBase2(0, 2) +
            self:MakeIndexBase2(0, 3) +
            self:MakeIndexBase2(0, 4) +
            self:MakeIndexBase2(0, 5) +
            self:MakeIndexBase2(0, 6) +
            self:MakeIndexBase2(0, 7) +
            self:MakeIndexBase2(0, 8) +
            self:MakeIndexBase2(0, 9) +
            self:MakeIndexBase2(0, 10) +
            self:MakeIndexBase2(0, 11) +
            self:MakeIndexBase2(0, 12) +
            self:MakeIndexBase2(0, 13) +
            self:MakeIndexBase2(0, 14) +
            self:MakeIndexBase2(0, 15) +
            self:MakeIndexBase2(0, 16) +
            self:MakeIndexBase2(0, 17) +
            self:MakeIndexBase2(0, 18) +
            self:MakeIndexBase2(0, 19) +
            self:MakeIndexBase2(0, 20) +
            self:MakeIndexBase2(0, 21) +
            self:MakeIndexBase2(0, 22) +
            self:MakeIndexBase2(0, 23)
end

-----------------------------------------------------------------
-- Boolean functions --------------------------------------------
-- Only put functions here that are part of a boolean sequence --
-- Sew BELOW for examples ---------------------------------------
-----------------------------------------------------------------

-- Finds if player or target is in combat
function DataToColor:targetCombatStatus()
    local combatStatus = UnitAffectingCombat("target")
    -- if target is in combat, return 0 for bitmask
    if combatStatus then
        return 1
        -- if target is not in combat, return 1 for bitmask
    else return 0
    end
end

-- 目标是否死亡
function DataToColor:TargetIsDead()
    local targStatus = UnitIsDead("target")
    if targStatus then
        return 1
    else
        return 0
    end
end

--目标是否敌对
function DataToColor:TargetIsEnemy()
    local t = UnitIsEnemy("player", "target")
    if t then
        return 1
    else
        return 0
    end
end

--目标是否是玩家
function DataToColor:TargetIsPlayer()
    local t = UnitIsPlayer("target")
    if t then
        return 1
    else
        return 0
    end
end

--目标是否可以攻击
function DataToColor:TargetCanAttach()
    local t = UnitCanAttack("player", "target")
    if t then
        return 1
    else
        return 0
    end
end

--目标是否是精英
function DataToColor:TargetIsElite()
    local t = UnitClassification("target")
    if t ~= "normal" then
        return 1
    else
        return 0
    end
end

-- 玩家是否死亡（等待释放灵魂或者已经释放灵魂）
function DataToColor:deadOrAlive()
    local deathStatus = UnitIsDeadOrGhost("player")
    if deathStatus then
        return 1
    else
        return 0
    end
end

--玩家是否是灵魂状态
function DataToColor:PlayerIsGhost()
    local t = UnitIsGhost("player")
    if t then
        return 1
    else
        return 0
    end
end

-- Checks the number of talent points we have available to spend
function DataToColor:checkTalentPoints()
    if UnitCharacterPoints("player") > 0 then
        return 1
    else return 0
    end
end

function DataToColor:playerCombatStatus()
    local combatStatus = UnitAffectingCombat("player")
    -- if player is not in combat, convert nil to 0
    if combatStatus then
        return 1
    else
        return 0
    end
end

-- Iterates through index of buffs to see if we have the buff is passed in
function DataToColor:GetBuffs(buff)
    for i = 1, 10 do
        local b = UnitBuff("player", i);
        if b ~= nil then
            if string.find(b, buff) then
                return 1
            end
        end
    end
    return 0
end

-- 目标是否有buff
function DataToColor:GetTargetBuffs(buff)
    for i = 1, 10 do
        local b = UnitBuff("target", i);
        if b ~= nil then
            if string.find(b, buff) then
                return 1
            end
        end
    end
    return 0
end

-- Returns the slot in which we have a fully degraded item
function DataToColor:GetInventoryBroken()
    for i = 1, 18 do
        local isBroken = GetInventoryItemBroken("player", i)
        if isBroken == true then
            return 1
        end
    end
    return 0
end

-- Checks if we are on a taxi
function DataToColor:IsPlayerFlying()
    local taxiStatus = UnitOnTaxi("player")
    if taxiStatus then
        return 1
    end
    -- Returns 0 if not on a wind rider beast
    return 0
end

-- 希利苏斯战地任务需要签名的信为1
function DataToColor:needSign()
    if GetActionCount(13) == 1 then
        return 1
    else return 0
    end
end

-- 蓝瓶小于5
function DataToColor:needManaBottom()
    if GetActionCount(17) < 5 then
        return 1
    else return 0
    end
end

-- 红瓶小于5
function DataToColor:needRedBottom()
    if GetActionCount(18) < 5 then
        return 1
    else return 0
    end
end

-- 烹饪小于10
function DataToColor:needCookie()
    if GetActionCount(19) < 10 then
        return 1
    else return 0
    end
end

-- 水小于10
function DataToColor:needWater()
    if GetActionCount(20) < 10 then
        return 1
    else return 0
    end
end

-- 面包小于10
function DataToColor:needFood()
    if GetActionCount(21) < 10 then
        return 1
    else return 0
    end
end

-- 绷带小于10
function DataToColor:needBandage()
    if GetActionCount(22) < 10 then
        return 1
    else return 0
    end
end

-- 法师魔法宝石或者ss糖
function DataToColor:needManaGem()
    if GetActionCount(23) < 1 then
        return 1
    else return 0
    end
end

function DataToColor:IsTargetOfTargetPlayerAsNumber()
    if not (UnitName("targettarget")) then return 2 end; -- target has no target
    if CHARACTER_NAME == UnitName("target") then return 0 end; -- targeting self
    if UnitName("pet") == UnitName("targettarget") then return 4 end; -- targetting my pet
    if CHARACTER_NAME == UnitName("targettarget") then return 1 end; -- targetting me
    if UnitName("pet") == UnitName("target") and UnitName("targettarget") ~= nil then return 5 end;
    return 3;
end

-- Returns true if target of our target is us
function DataToColor:IsTargetOfTargetPlayer()
    if CHARACTER_NAME == UnitName("targettarget") and CHARACTER_NAME ~= UnitName("target") then
        return 1
    else
        return 0
    end
end

-- 判断目标是否可以剥皮
function DataToColor:isSkinnable()
    local creatureType = UnitCreatureType("target")
    if creatureType == nil then
        return 0
    end
    -- Demons COULD be included in this list, but there are some skinnable demon dogs.
    if creatureType == "人形生物" or creatureType == "元素生物" or creatureType == "机械" or creatureType == "图腾" then
        return 0
    end
    return 1
end

function DataToColor:IsPetVisible()
    if UnitIsVisible("pet") and not UnitIsDead("pet") then
        return 1
    else return 0
    end
end

-- A variable which can trigger a process exit on the node side with this macro:
-- /script EXIT_PROCESS_STATUS = 1
function DataToColor:ProcessExitStatus()
    -- Check if a process exit has been requested
    if EXIT_PROCESS_STATUS == 1 then
        -- If a process exit has been requested, resets global frame tracker to zero in order to give node time to read frames
        if globalCounter > 200 then
            self:log('Manual exit request processing...')
            globalCounter = 0
        end
    end
    -- Number of frames until EXIT_PROCESS_STATUS returns to false so that node process can begin again
    if globalCounter > 100 and EXIT_PROCESS_STATUS ~= 0 then
        EXIT_PROCESS_STATUS = 0
    end
    return EXIT_PROCESS_STATUS
end

-- find bag item
-- 使用 /script FIND_ITEM_ID=要查找的物品id
function DataToColor:FindBagItem()
    local count = 0
    if FIND_ITEM_ID > 0 then
        for bag = 0, 4 do
            for slot = 1, GetContainerNumSlots(bag) do
                local icon, itemCount, locked, quality, readable, lootable, itemLink, isFiltered, noValue, itemID = GetContainerItemInfo(bag, slot)
                if itemID == FIND_ITEM_ID then
                    count = count + itemCount
                end
            end
        end
    end
    return count
end

-- Returns sub zone ID based on index of subzone in constant variable
function DataToColor:hearthZoneID()
    local index = {}
    local hearthzone = string.upper(GetBindLocation())
    for k, v in pairs(HearthZoneList) do
        index[v] = k
    end
    if index[hearthzone] ~= nil then
        return index[hearthzone]
        --else self:log(hearthzone .. "is not registered. Please add it to the table in D2C.")
    end
end

-----------------------------------------------------------------------------
-- Begin Event Section -- -- Begin Event Section -- -- Begin Event Section --
-- Begin Event Section -- -- Begin Event Section -- -- Begin Event Section --
-- Begin Event Section -- -- Begin Event Section -- -- Begin Event Section --
-- Begin Event Section -- -- Begin Event Section -- -- Begin Event Section --
-----------------------------------------------------------------------------
function DataToColor:HandleEvents()
    -- Resurrect player
    if DATA_CONFIG.AUTO_RESURRECT then
        self:ResurrectPlayer()
    end
    -- Handles group accept/decline
    if DATA_CONFIG.ACCEPT_PARTY_REQUESTS or DATA_CONFIG.DECLINE_PARTY_REQUESTS then
        self:HandlePartyInvite()
    end
    -- Handles item repairs when talking to item repair NPC
    if DATA_CONFIG.AUTO_REPAIR_ITEMS then
        self:RepairItems()
    end
    -- Handles learning talents, only works after level 10
    if DATA_CONFIG.AUTO_LEARN_TALENTS then
        self:LearnTalents()
    end
    -- Handles train new spells and talents
    if DATA_CONFIG.AUTO_TRAIN_SPELLS then
        self:CheckTrainer()
    end
end

-- Declines/Accepts Party Invites.
function DataToColor:HandlePartyInvite()
    -- Declines party invite if configured to decline
    if DATA_CONFIG.DECLINE_PARTY_REQUESTS then
        DeclineGroup()
    else if DATA_CONFIG.ACCEPT_PARTY_REQUESTS then
        AcceptGroup()
    end
    end
    -- Hides the party invite pop-up regardless of whether we accept it or not
    StaticPopup_Hide("PARTY_INVITE")
end

-- Repairs items if they are broken
-- 大脚插件可以搞定
function DataToColor:RepairItems()
    if CanMerchantRepair() and GetRepairAllCost() > 0 then
        if GetMoney() >= GetRepairAllCost() then
            RepairAllItems()
        end
    end
end

-- Automatically learns predefined talents
function DataToColor:LearnTalents()
    if UnitCharacterPoints("player") > 0 then
        -- Grabs global list of talents we want to learn
        for i = 0, table.getn(talentList), 1 do
            -- Iterates through each talent tab (e.g. "Arcane, Fire, Frost")
            for j = 0, 3, 1 do
                -- Loops through all of the talents in each individual tab
                for k = 1, GetNumTalents(j), 1 do
                    -- Grabs API info of a specified talent index
                    local name, iconPath, tier, column, currentRank, maxRank, isExceptional, meetsPrereq, previewRank, meetsPreviewPrereq = GetTalentInfo(j, k)
                    local tabId, tabName, tabPointsSpent, tabDescription, tabIconTexture = GetTalentTabInfo(j)
                    local _, _, isLearnable = GetTalentPrereqs(j, k)
                    -- DEFAULT_CHAT_FRAME:AddMessage("hello" .. tier)
                    -- Runs API call to learn specified talent. Skips over it if we already have the max rank.
                    if name == talentList[i] and currentRank ~= maxRank and meetsPrereq then
                        -- Checks if we have spent enough points in the prior tiers in order to purchase talent. Otherwie moves on to next possible spell
                        if tabPointsSpent ~= nil and tabPointsSpent >= (tier * 5) - 5 then
                            LearnTalent(j, k)
                            return
                        end
                    end
                end
            end
        end
    end
end

local iterator = 0

-- List desired spells and professions to be trained here.
function ValidSpell(spell)
    local spellList = {
        "Conjure Food",
        "Conjure Water",
        "Conjure Mana Ruby",
        "Mana Shield",
        "Arcane Intellect",
        "Fire Blast",
        "Fireball",
        "Frostbolt",
        "Counterspell",
        "Ice Barrier",
        "Evocation",
        "Frost Armor",
        "Frost Nova",
        "Ice Armor",
        "Remove Lesser Curse",
        "Blink",
        "Apprentice Skinning",
        "Journeyman Skinning",
        "Expert Skinning",
        "Artisan Skinning",
        "Apprentice Fishing",
        "Journeyman Fishing"
    }
    -- Loops through all spells to see if we have a matching spells with the one passed in
    for i = 0, table.getn(spellList), 1 do
        if spellList[i] == spell then
            return true
        end
    end
    return false
end

-- Used purely for training spells and professions
function DataToColor:CheckTrainer()
    iterator = iterator + 1
    if Modulo(iterator, 30) == 1 then
        -- First checks that the trainer gossip window is open
        -- DEFAULT_CHAT_FRAME:AddMessage(GetTrainerServdiceInfo(1))
        if GetTrainerServiceInfo(1) ~= nil and DATA_CONFIG.AUTO_TRAIN_SPELLS then
            -- LPCONFIG.AUTO_TRAIN_SPELLS = false
            local allAvailableOptions = GetNumTrainerServices()
            local money = GetMoney()
            local level = UnitLevel("player")

            -- Loops through every spell on the list and checks if we
            -- 1) Have the level to train that spell
            -- 2) Have the money want to train that spell
            -- 3) Want to train that spell
            for i = 1, allAvailableOptions, 1 do
                local spell = GetTrainerServiceInfo(i)
                if spell ~= nil and ValidSpell(spell) then
                    if GetTrainerServiceLevelReq(i) <= level then
                        if GetTrainerServiceCost(i) <= money then
                            -- DEFAULT_CHAT_FRAME:AddMessage(" buying spell" .. tostring(i) )
                            BuyTrainerService(i)
                            -- Closes skinning trainer, fishing trainer menu, etc.
                            -- Closes after one profession purchase. Impossible to buy profession skills concurrently.
                            if IsTradeskillTrainer() then
                                print("not close Trainer")
                                -- CloseTrainer() --关闭训练师窗口
                                -- LPCONFIG.AUTO_TRAIN_SPELLS = true
                            end
                            -- DEFAULT_CHAT_FRAME:AddMessage(allAvailableOptions .. tostring(i) )
                            -- if not (allAvailableOptions == i) then
                            -- TrainSpells()
                            return
                            -- end
                            -- An error messages for the rare case where we don't have enough money for a spell but have the level for it.
                        else if GetTrainerServiceCost(i) > money then
                        end
                        end
                    end
                end
            end
            -- DEFAULT_CHAT_FRAME:AddMessage('between')
            -- Automatically closes menu after we have bought all spells we need to buy
            -- CloseTrainer()
            -- LPCONFIG.AUTO_TRAIN_SPELLS = true
        end
    end
end

--the x and y is 0 if not dead
--runs the RetrieveCorpse() function to ressurrect
function DataToColor:ResurrectPlayer()
    if Modulo(iterator, 50) == 1 then
        if UnitIsDeadOrGhost("player") then
            -- Accept Release Spirit immediately after dying
            if not UnitIsGhost("player") and UnitIsGhost("player") ~= nil then
                RepopMe() -- 释放
            end
            if UnitIsGhost("player") then
                local map = C_Map.GetBestMapForUnit("player")
                if C_DeathInfo.GetCorpseMapPosition(map) ~= nil then
                    local cX, cY = C_DeathInfo.GetCorpseMapPosition(map):GetXY()
                    local x, y = self:GetCurrentPlayerPosition()
                    -- Waits so that we are in range of specified retrieval distance, and ensures there is no delay timer before attemtping to resurrect
                    if math.abs(cX - x) < CORPSE_RETRIEVAL_DISTANCE / 1000 and math.abs(cY - y) < CORPSE_RETRIEVAL_DISTANCE / 1000 and GetCorpseRecoveryDelay() == 0 then
                        DEFAULT_CHAT_FRAME:AddMessage('尸体就在附近，涛哥正帮你自动复活...')
                        -- Accept Retrieve Corpsse when near enough
                        RetrieveCorpse() -- 复活
                    end
                end
            end
        end
    end
end

-- 我自己加的两个方法，让汉字能转成色块
--将汉字转成rgb
--支持输入一串汉字，转换成对应的rgb table
function Utf8StringToColor(words)
    local tcolors = {}
    local t = Utf8to32(words)
    for k, v in ipairs(t)
    do
        if v ~= 0 then
            table.insert(tcolors, integerToColor(v))
        end
    end
    return tcolors
end

--http://lua-users.org/wiki/LuaUnicode
--将汉字转换成整形unicode
function Utf8to32(utf8str)
    assert(type(utf8str) == "string")
    local res, seq, val = {}, 0, nil
    for i = 1, #utf8str do
        local c = string.byte(utf8str, i)
        if seq == 0 then
            table.insert(res, val)
            seq = c < 0x80 and 1 or c < 0xE0 and 2 or c < 0xF0 and 3 or
                    c < 0xF8 and 4 or --c < 0xFC and 5 or c < 0xFE and 6 or
                    error("invalid UTF-8 character sequence")
            val = bit.band(c, 2 ^ (8 - seq) - 1)
        else
            val = bit.bor(bit.lshift(val, 6), bit.band(c, 0x3F))
        end
        seq = seq - 1
    end
    table.insert(res, val)
    table.insert(res, 0)
    return res
end

xxxxxx1 = Utf8StringToColor(UnitName("player"))
xxxxxx2 = Utf8StringToColor("老夫子")
print(xxxxxx1)
print(xxxxxx2)

--  IsOutdoors()
--  spell, _, _, _, _,_, _, castID, _ = UnitCastingInfo("uintId")  施放法术信息
--  name, _, text, _, _, _, _, _ = UnitChannelInfo("uintId")        引导法术信息