#!/usr/bin/python
# -*- utf-8 -*-

# Panda3D imoprts
from direct.task import Task
from direct.interval.IntervalGlobal import *
from direct.showbase.DirectObject import DirectObject
from direct.actor.Actor import Actor
from direct.fsm.FSM import FSM
from panda3d.core import (
    CollisionSegment,
    CollisionSphere,
    CollisionNode,
    LPoint3f,
    LVecBase4,
    LVecBase2,
    AmbientLight,
    PerspectiveLens,
    DirectionalLight,
    KeyboardButton,
    AudioSound,
    CardMaker
    )

# sys import
import random,sys,traceback
import json
import time,threading

# self import
from Hero import *
from Room import *
import Queue
from direct.showbase import ShowBase
from __builtin__ import map
from DefaultConfigVal import *

from MapDraw import MiniMap

_LEAPMOTION = True
try:
    from LeapMotion import *
except Exception as e:
    traceback.print_exc()
    _LEAPMOTION = False

mapPath = 'ArchiveFiles/'

class MapManager(FSM,DirectObject):
    def __init__(self,name='map-manager'):
        FSM.__init__(self,name)
        '''
        index            关卡
        room             当前房间对象
        rooms            当前关卡的房间信息
        hero             当前的英雄信息
        masterRoomVisitedNum   当前通过的主线房间个数
        curRoomCode      当前的房间号
        '''
        self.index=0
        self.gameNP = render.attachNewNode('game')
        self.room=None
        self.rooms=[]
        self.hero=None
        self.masterRoomVisitedNum = 0
        self.preRoomCode = 0
        self._init_accept()
        self.videoDict={}

        # 保存英雄初始信息
        self.initHeroInfo = None

    def loadResource(self):
        '''
        加载地图资源
        '''
        self.room=Room(mapPath,self.gameNP)
        self.hero = Hero(LVecBase3f(0,0,0),parent=self.gameNP)
        self.room.setHero(self.hero)
        self.initHeroInfo = Hero.ToDict(self.hero)
        # 加载中场视频、结束视频
        video,card=loadVideo('middle.mp4')
        self.videoDict['middle']={'video':video,'card':card}
        video,card=loadVideo('end.mp4')
        self.videoDict['end']={'video':video,'card':card}

        base.LEAPMOTION = True
        if _LEAPMOTION:
            base.leapMotion = LeapListener()
        else:
            base.LEAPMOTION = False
            
    def getArchiveContent(self):
        json.dumps(MapManager.ToDict(self))

    def setArchiveContent(self,content):
        self.reInit(json.loads(content,encoding='utf-8'))

    @staticmethod
    def ToDict(self):
        return {
            "index":self.index,
            "hero":Hero.ToDict(self.hero),
            "masterRoomVisitedNum":self.masterRoomVisitedNum,
            "rooms":
                map(RoomInformation.ToDict,self.rooms),
            "preRoomCode":self.preRoomCode,
            "buffState":self.room.buffList.ToDict(self.room.buffList)
            }

    @staticmethod
    def ToMap(dict):
        mapManager = MapManager()
        mapManager.index = dict['index']
        mapManager.hero =  Hero.ToHero(dict['hero'])
        mapManager.masterRoomVisitedNum=dict['masterRoomVisitedNum']
        mapManager.rooms=map(RoomInformation.ToRoomInformation,dict['rooms'])
        return mapManager

    def reInit(self,dict):
        #清除之前的数据

        #重新初始化
        self.index = dict['index']
        self.hero.reInit(dict['hero'])
        self.masterRoomVisitedNum = dict['masterRoomVisitedNum']
        self.rooms = map(RoomInformation.ToRoomInformation,dict['rooms'])
        self.preRoomCode = dict['preRoomCode']
        self.room.buffList.reInit(self.room.buffList,dict['buffState'])


    def __str__(self):
        indexStr = 'index={}'
        roomsStr = 'rooms={}'
        heroStr = 'hero={}'
        masterRoomVisitedNumStr='masterRoomVisitedNumStr={}'

        strs = 'save={\n'
        strs += indexStr.format(self.index)

        strs += '\n'
        strs += heroStr.format(self.hero)

        strs += '\n'
        strs += roomsStr.format('\n'.join(map(RoomInformation.__str__,self.rooms)))

        strs += '\n'
        strs += masterRoomVisitedNumStr.format(self.masterRoomVisitedNum)

        strs += '\n}'
        return strs
    __repr__ = __str__

    def _init_accept(self):
        self.accept('room-next',self._accept_room_next)
        self.accept('game-start',self._accept_game_start)
        if Debug:#调试模式
            self.accept('g',self._accept_gate_next)
        self.accept('gate-next',self._accept_gate_next)

    def _functionHeper(self,roomCode,state=0):
        if not (state == 0):
            return state
        if roomCode == -1:
            return 0
        if self.rooms[roomCode].isVisited:
            return 1
        elif self.rooms[roomCode].typeStr=='boss':
            return 2
        elif self.rooms[roomCode].typeStr=='leap':
            return 3
        else:
            return 4

    def function(self,number):
        arr = [0,0,0,0,0,0,0,0,0]
        arr[4] = 1
        nowinfo = self.rooms[number]

        north = nowinfo.doorDict['north']
        south = nowinfo.doorDict['south']
        west = nowinfo.doorDict['west']
        east = nowinfo.doorDict['east']
        if not north == -1:
            arr[1] = self._functionHeper(north)
            left = self.rooms[north].doorDict['west']
            right = self.rooms[north].doorDict['east']
            arr[0] = self._functionHeper(left,arr[0])
            arr[2] = self._functionHeper(right,arr[2])

        if not south == -1:
            arr[7] = self._functionHeper(south)
            left = self.rooms[south].doorDict['west']
            right = self.rooms[south].doorDict['east']
            arr[6] = self._functionHeper(left,arr[6])
            arr[8] = self._functionHeper(right,arr[8])

        if not west == -1:
            arr[3] = self._functionHeper(west)
            north = self.rooms[west].doorDict['north']
            south = self.rooms[west].doorDict['south']
            arr[0] = self._functionHeper(north,arr[0])
            arr[6] = self._functionHeper(south,arr[6])

        if not east == -1:
            arr[5] = self._functionHeper(east)
            north = self.rooms[east].doorDict['north']
            south = self.rooms[east].doorDict['south']
            arr[2] = self._functionHeper(north,arr[2])
            arr[8] = self._functionHeper(south,arr[8])
        return arr

    def _accept_game_start(self,renew=False):
        '''
        处理 开始游戏 事件
        '''
        self.room.setRoomInformation(self.rooms[self.preRoomCode])

        if renew:
            logging.info('reinit hero  ==================')
            self.hero.reInit(self.initHeroInfo,True)

        self.room.setHeroPos(self.room._getInitHeroPos())

        self.room.request('RoomInit')
        self.room.setHeroPos(self.room._getInitHeroPos())
        t = threading.Thread(target=self._beforeStart,name='beforeStart')
        t.start()

    def _beforeStart(self):
        arr = self.function(self.room.roomInformation.roomCode)
        MiniMap(path=mapPath).drawMap(arr)
        self.room._initRoom()

    @print_func_time
    def _accept_room_next(self,pos,roomCode):
        '''
        处理 进入下一个房间 事件
        '''
        logging.info('roomCode{}'.format(roomCode))
        if roomCode < len(self.rooms):
            self.preRoomCode = self.room.roomInformation.roomCode
            if not self.rooms[self.preRoomCode].isVisited and self.rooms[self.preRoomCode].typeStr=='master':
                self.masterRoomVisitedNum+=1
            self.rooms[self.preRoomCode].isVisited=True

            if not self.rooms[roomCode].isVisited:
                # 生成怪物信息
                self.genMonsterInfo(roomCode)

            # 设置房间信息
            arr = self.function(roomCode)
            self.room.setRoomInformation(self.rooms[roomCode])

            self.room.request('RoomInit')
            self.room.setHeroPos(self.room._getInitHeroPos(self._getOppositiveDir(pos)))
            t = threading.Thread(target=self._beforeStart,name='beforeStart')
            t.start()
        else:
            print 'out of range'

    @print_func_time
    def _accept_gate_next(self):
        logging.info('index:{}'.format(self.index))
        if self.index==0:#第一关结束
            # 播放中场动画
            # 重新初始化 地图信息
            # 开始游戏
            self.gameNP.hide()
            card = self.videoDict['middle']['card']
            video = self.videoDict['middle']['video']
            delayTime = self.videoDict['middle']['video'].length()
            if Debug:
                delayTime=0
            Sequence(
                Func(self.room.request,'Blank'),
                Parallel(
                    Func(self.genMap),
                    Func(card.show),
                    Func(video.play),
                    ),
                Wait(delayTime),
                Parallel(
                    Func(card.hide),
                    Func(video.stop),
                    Func(self._accept_game_start),#开始游戏
                    Func(self.gameNP.show),
                    )
                ).start()
            self.index+=1
        elif self.index==1:#第二关结束
            # 播放结束动画
            # 输出开发人员名单
            # 回到主菜单
            card = self.videoDict['end']['card']
            video = self.videoDict['end']['video']
            delayTime = self.videoDict['end']['video'].length()
            if Debug:
                delayTime=0
            Sequence(
                Func(self.room.request,'Idle'),
                Parallel(
                    Func(card.show),
                    Func(video.play),
                    ),
                Wait(delayTime),
                Parallel(
                    Func(card.hide),
                    Func(video.stop),
                    Func(base.messenger.send,'game-end')
                    )
                ).start()
            self.index=0 # 重新开始

    def genMonsterInfo(self,roomCode,masterRoomNum=DefaultMasterRoomNum):
        roomInfo = self.rooms[roomCode]
        extraHPRate = self.index+1
        if roomInfo.typeStr=='boss':
            bossMonsters = ['Minotaur','MechanicalSpider']
            #print 'boss'
            roomInfo.monsterDict[bossMonsters[self.index]]=LVector2i(1,extraHPRate)
        elif roomInfo.typeStr=='leap':
            leapMonsters = ["Slime","Robot"]
            monsterNum = MonsterNums[1]
            monsterType = leapMonsters[random.randint(0,len(leapMonsters)-1)]
            roomInfo.monsterDict[monsterType]=LVector2i(monsterNum,extraHPRate)
            #print 'leap'
        else:
            # 怪物种类列表

            littleMonsters = {
                0:['Slime','BigSlime','Bat'],
                1:['Robot','BigRobot','FlyingRobot']
            }
            littleMonsters = littleMonsters[self.index]
            middleMonsters = {
                0:['Skull','Caterpillar','Mole','MagicalTower'],
                1:['MechanicalHead','Train','DrillRobot','EletricTower']
            }
            middleMonsters = middleMonsters[self.index]

            # 确定难度等级
            level = self.masterRoomVisitedNum / len(levels)
            # 确定怪物数量
            monsterNum = random.randint(levels[level][0],levels[level][1])

            monsterDistribution=DefaultMonsterDistributions[self.masterRoomVisitedNum]
            # 小型怪物的数量

            littleNum = int(monsterNum*monsterDistribution)
            # 中型怪物的数量
            middleNum = monsterNum-littleNum
            # 每种怪物随机数量
            leftNum = littleNum
            for typeStr in littleMonsters:
                roomInfo.monsterDict[typeStr]=LVecBase2i(0,extraHPRate)

            for i in range(0,littleNum):
                index = random.randint(0,len(littleMonsters)-1)
                roomInfo.monsterDict[littleMonsters[index]][0]+=1

            for typeStr in middleMonsters:
                roomInfo.monsterDict[typeStr]=LVecBase2i(0,extraHPRate)
            lastOne = roomInfo.monsterDict[middleMonsters[-1]]
            for i in range(0,middleNum):
                index = random.randint(0,len(middleMonsters)-1)
                if index==len(middleMonsters)-1 and lastOne[0]==1:# 保证魔法塔只有一个
                    index=0
                roomInfo.monsterDict[middleMonsters[index]][0]+=1

    def isGen_leap(self,i,maxNum):
        # i越接近maxNum，概率越大,当i小于maxNum/2时，概率《0.5
        p = random.randint(0,i)*1.0/maxNum
        if p > 0.5:
            return True
        else:
            return False
        pass

    def genMap(self,masterRoomNum = DefaultMasterRoomNum,branchRoomNum = DefaultBranchRoomNum):
        '''
        generate map : rooms

        directions code
                north 0
        west 3          east 1
                south 2
        '''
        # 重新初始化 关卡中信息
        self.preRoomCode=0
        self.masterRoomVisitedNum=0
        self.rooms=[]

        directions = {'north':LVecBase2(0,-1),'east':LVecBase2(1,0),'south':LVecBase2(0,1),'west':LVecBase2(-1,0)}
        int2directions = ['north','east','south','west']

        map_a = 2*(masterRoomNum+branchRoomNum)+1
        map = [([-1]*map_a) for i in range(map_a)]

        pos = LVecBase2(map_a/2,map_a/2)
        poses = []

        # 确定房间延时方向,即限制directions 为连续的两个位置
        i = random.randint(0,len(directions)-1)
        temp = {}
        temp[int2directions[i]]=directions[int2directions[i]]
        i = (i+1) %(len(directions)-1)
        temp[int2directions[i]]=directions[int2directions[i]]
        master_directions=temp
        # 生成主线房间
        i = 0
        while True:
            roomInfo = RoomInformation()
            roomInfo.roomCode = i

            self.rooms.append(roomInfo)
            if i == 0:# init
                roomInfo.typeStr = 'init'
            elif i==masterRoomNum:# boss
                roomInfo.typeStr = 'boss'
            else:# master
                roomInfo.typeStr = 'master'

            map[int(pos.get_y())][int(pos.get_x())] = roomInfo.roomCode
            poses.append(LVecBase2(pos.get_x(),pos.get_y()))
            options = []
            for k,v in master_directions.items():
                temp = pos+v
                if map[int(temp.get_y())][int(temp.get_x())]==-1:
                    options.append(k)
            try:
                dirIndex = random.randint(0,len(options)-1)
            except ValueError:
                traceback.print_exc()
                break;

            dir = options[dirIndex]
            pos += master_directions[dir]

            i+=1
            if i > masterRoomNum:
                break;

        # 检测是否连接leapmotion设备
        if base.LEAPMOTION:
            if not base.leapMotion.controller.is_connected:
                base.LEAPMOTION = False
        print 'base.LEAPMOTION',base.LEAPMOTION
        # 生成支线房间
        #print 'leap:',base.LEAPMOTION,LEAPMOTION_ROOM
        i=1
        branchMaxNum = 2*(masterRoomNum+1)
        branch_directions = directions
        for j in range(0,masterRoomNum):
            pos = poses[j]
            for dir in branch_directions.values():
                temp = pos+dir
                x = int(temp.get_x())
                y = int(temp.get_y())
                if x>=0 and y>=0 and x<map_a and y<map_a:
                    if map[y][x]==-1:
                        roomInfo = RoomInformation()
                        roomInfo.roomCode = i+masterRoomNum
                        i+=1
                        self.rooms.append(roomInfo)
                        if self.isGen_leap(i,branchMaxNum) and LEAPMOTION_ROOM and base.LEAPMOTION:# leap
                            roomInfo.typeStr='leap'
                        else:# branch
                            roomInfo.typeStr='branch'
                        map[y][x] = roomInfo.roomCode
                        poses.append(LVecBase2(x,y))
        # i = 1
        # index = random.randint(1,len(self.rooms)-1)
        # while i <= branchRoomNum and i >= 1:
        #     pos = poses[index]
        #     options = []
        #     for k,v in branch_directions.items():
        #         temp = pos+v
        #         x = int(temp.get_x())
        #         y = int(temp.get_y())

        #         if x>=0 and y>=0 and x<map_a and y<map_a and map[y][x]==-1:
        #             options.append(k)
        #     try:
        #         dirIndex = random.randint(0,len(options)-1)
        #     except ValueError:
        #         traceback.print_exc()
        #         index = random.randint(1,len(self.rooms)-1)
        #         continue

        #     dir = options[dirIndex]
        #     temp = pos + branch_directions[dir]

        #     roomInfo = RoomInformation()
        #     roomInfo.roomCode = i+masterRoomNum

        #     self.rooms.append(roomInfo)
        #     if i==branchRoomNum:
        #         roomInfo.typeStr = 'leap'
        #     else:
        #         roomInfo.typeStr = 'branch'

        #     map[int(temp.get_y())][int(temp.get_x())] = roomInfo.roomCode
        #     poses.append(LVecBase2(temp.get_x(),temp.get_y()))
        #     index=random.randint(1,len(self.rooms)-1)

        # strs = '     '
        # for x in range(0,map_a):
        #     strs +='%3i'%x
        # print strs
        # y=0
        # for l in map:
        #     strs = '%4d:'%y
        #     for p in l:
        #         strs+= '%3i'%p
        #     print strs
        #     y+=1

        ##
        for i in range(0,len(poses)):
            '''
            设置房间信息中，门所通向的房间
            '''
            for k,v in directions.items():
                temp = poses[i]+v
                self.rooms[i].doorDict[k]=map[int(temp.get_y())][int(temp.get_x())]
        # for room in self.rooms:
        #     print room

    def _getRandomDir(self,without=None):
        directions = ['north','east','south','west']

        while True:
            temp = directions[random.randint(0,len(directions)-1)]
            isContain=False
            if without:
                for dir in without:
                    if dir == temp:
                        isContain=True
                        break;
            if not isContain:
                return temp

    def _getOppositiveDir(self,dir):
        directions = {'north':'south','east':'west','south':'north','west':'east'}
        return directions[dir]

    def _getRandomType(self,without=['init']):
        typeStrs = ['init',1,2,3,4,5,6,'leap','boss']
        while True:
            temp = typeStrs[random.randint(0,len(typeStrs)-1)]
            isContain=False
            if without:
                for t in without:
                    if t == temp:
                        isContain=True
                        break;
            if not isContain:
                return temp
