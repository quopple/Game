#!/usr/bin/python

# -*- utf-8 -*-

# system imports
import random,sys,traceback,os,os.path,time,threading
# Panda3D imports
from direct.interval.IntervalGlobal import *
from direct.showbase.DirectObject import DirectObject
from direct.actor.Actor import Actor
from direct.fsm.FSM import FSM
from panda3d.core import *


# self imports
from Monster import *
from Hero import Hero
from blood import (HeroBlood,BossBlood)
from Map import Map
from BuffState import BuffState
from direct.task import Task
from DefaultConfigVal import *

from VideoHelper import *
from Item import *
from Cube import *
#from Shadow import *

offX = 1
offY = 1
offZ = 2

class Door(DirectObject):
    transforms = {'north':(0,DefaultRoomY/2-offY,offZ,0,0,0),
                  'south':(0,-(DefaultRoomY/2-offY),offZ,180,0,0),
                  'west':(-(DefaultRoomX/2-offX),0,offZ,90,0,0),
                  'east':(DefaultRoomX/2-offX,0,offZ,270,0,0),
                  }
    def __init__(self,pos='',roomCodeToReach=-1,parent=None):
        '''
        载入模型和动画，并将nodepath节点绑定到parent上
        设置碰撞事件
        '''
        self.model=None
        self.pos=''
        self.roomCodeToReach=0
        self.isOpen=False
        self.boundingBox=None
        if not parent:
            parent = base.render
        self.parent = parent

        #-----------------------
        self.pos=pos
        self.roomCodeToReach = roomCodeToReach

        self._initModel()
        self._initCollision()

    def _initModel(self):
        '''
        初始化模型
        '''
        pathStr = "Model/{}"

        if not self.roomCodeToReach == -1:
            modelName = "model_door_middle"
            self.model = Cube.makeCube(1,self.parent)
        else:
            self.model =  self.parent.attachNewNode('door')

        self.model.setPosHpr(*Door.transforms[self.pos])
        self.model.hide()

    def _initCollision(self):
        '''
        初始化碰撞体
        '''
        self.colliderNodePath = None
        self.colliderName = 'door'
        if not self.roomCodeToReach==-1:
            colliderSolid = CollisionBox(LPoint3(0,0,0),2,0.5,2)
            colNode = CollisionNode(self.colliderName)
            colNode.addSolid(colliderSolid)
            colNode.setFromCollideMask( CollideMask.bit(DefaultMonsterMaskVal)|CollideMask.bit(DefaultHeroMaskVal))
            colNode.setIntoCollideMask( CollideMask.bit(DefaultMonsterMaskVal)|CollideMask.bit(DefaultHeroMaskVal))
            self.colliderNodePath = self.model.attachNewNode(colNode)
            #self.colliderNodePath.show()
            base.cTrav.addCollider(self.colliderNodePath,base.cHandler)

    def open(self):
        '''
        播放动画
        '''
        self.model.hprInterval(1.5, (360, 360, 360)).loop()

    def show(self):
        '''
        显示模型
        '''
        self.model.show()

    def hide(self):
        '''
        隐藏模型
        '''
        self.model.hide()

class RoomInformation(object):
    '''
    modelName   房间模型名称
    roomCode    房间号
    typeStr     房间类型
    isVisited   是否被访问过
    doorList    房间内 四个门 信息列表
    monsterList 房间内 怪物   信息列表:类型：（数量、额外的血量）
    itemList    房间内 道具   信息列表
    '''
    def __init__(self):
        self.modelName = ""
        self.roomCode=0
        self.typeStr='0'
        self.isVisited=False
        self.doorDict={'north':-1,'south':-1,'west':-1,'east':-1}
        self.monsterDict={}
        #----------------------
    @staticmethod
    def ToDict(roomInformation):
        return {
            "modelName":roomInformation.modelName,
            "roomCode":roomInformation.roomCode,
            "typeStr":roomInformation.typeStr,
            "isVisited":roomInformation.isVisited,
            "doorDict":roomInformation.doorDict
            }
    @staticmethod
    def ToRoomInformation(dict):
        roomInformation = RoomInformation()
        roomInformation.modelName=dict['modelName']
        roomInformation.roomCode=dict['roomCode']
        roomInformation.typeStr = dict['typeStr']
        roomInformation.isVisited=dict['isVisited']
        roomInformation.doorDict=dict['doorDict']

        return roomInformation

    def __str__(self):
        strs = '''
        {
            "modelName":"%s"
            "roomCode":"%d",
            "typeStr":"%s",
            "doorDict":{
                "%s"
                }
        }
        '''
        doorsStr = ''
        for k,v in self.doorDict.items():
            doorsStr += '"%s":%d,'%(k,v)
        doorsStr = doorsStr[:-1]

        return strs % (self.modelName,self.roomCode,self.typeStr,doorsStr)
    __repr__ = __str__

class Room(FSM,DirectObject):

    ### constructor
    def __init__(self,mapPath='',parentNP=None):
        '''
        scale            模型的缩放比例
        model            模型的NodePath
        roomInformation  房间信息
        audioDict        3d音效     类实例字典
        videoDict        video      类实例字典
        cardDict         承载video纹理
        doorList         Door       类实例列表
        monsterList      Monster    类实例列表
        itemList         Item       类实例列表
        bulletList       BulletList 类实例列表
        hero             Hero       类实例
        heroBlood        HeroBlood  类实例
        bossBlood        BossBlood  类实例
        map              Map        类实例

        载入模型和动画，并将nodepath节点绑定到render上
        设置光照
        载入视频、音频
        '''
        FSM.__init__(self, "FSM-Room")
        #self.defaultTransitions = {
        #    'Idle':['RoomInit','Play'],
        #    'RoomInit':['Idle','Play'],
        #    'Play':['Idle'],
        #    }

        self.scale=1
        self.model=None
        self.roomInformation=RoomInformation()
        self.audioDict={}
        self.videoDict={}
        self.cardDict={}
        self.doorList=[]
        self.monsterList=[]
        self.itemList=[]
        self.bulletList=[]
        self.hero = None

        self.heroBlood = None
        self.BossBlood = None
        self.map = Map(mapPath)
        self.buffList = BuffState()

        self.curbgm = None

        self.alight = None
        self.Spotlight = None

        self.leapCameraZ= 48

        self.isInited = False
        # lock
        self.lock = threading.Lock()
        # 鼠标位置在屏幕上的位置
        self.newPos=[0,0]
        self.init_updateRay = None
        #---------------------------
        # 房间信息
        self.roomParentNP = parentNP
        if self.roomParentNP==None:
            self.roomParentNP=render
        # 道具信息
        self.itemInfoList=['Damage','Ray','Shotgun','AoeDamage','Life','MaxLife','MoveSpeed','AttackSpeed','BulletSpeed','BulletSize','BulletRange']
        self.itemParentNP = None
        # 房间模型列表
        self.modelNameList = []
        self._initModelNameList()

        self._initBlood()

        self._initLight()

        self._initAudio()
        self._initVideo()

        #leap光标
        self.leapCursor=loader.loadModel("Model/model_leapcursor")
        self.leapCursor.reparentTo(render)
        self.leapCursor.setScale(1)

    ###
    ### FSM
    @print_func_time
    def enterIdle(self):
        '''
        播放过场视频
        '''
        #self.playVideo('idle')
        self.buffList.clear()
        pass

    @print_func_time
    def exitIdle(self):
        '''
        停止播放过场视频
        '''
        #self.stopVideo('idle')
        pass
    @print_func_time
    def enterRoomInit(self):
        '''
        播放过场视频
        初始化房间内的模型
        '''
        if NeedRoomInitVideo:
            self.playVideo('init',True)

    @print_func_time
    def exitRoomInit(self):
        '''
        停止播放过场视频
        '''
        if NeedRoomInitVideo:
            self.stopVideo('init')

    @print_func_time
    def enterPlay(self):
        '''
        显示模型

        显示英雄血条

        播放游戏中音效
        初始化 响应事件
        初始化 英雄控制
        设置主循环事件
        '''
        if self.roomInformation.typeStr=='leap':
            self.hero.model.setZ(-100)
            self.leapAttackNum=6
            self.leapTurn=1
            self.hero.model.hide()
            base.leapMotion.enable=True
            self.init_updateRay = self.hero.updateRay
            self.hero.updateRay = self.updateRay
            self.leapCursor.show()
            self.leapCursor.setPos(self.model.getPos())
        else:
            self.hero.model.setZ(self.model.getZ())
            self.leapAttackNum=0
            self.hero.model.show()
            self.leapCursor.hide()
        
        self.model.show()
        self.heroBlood.show()
        self.buffList.show()
        self._accept_hero_hpchange(self.hero.HP)
        self._accept_hero_maxhpchange(self.hero.maxHP)

        if self.roomInformation.typeStr=='boss':
            self.bossBlood.show()

        self.map.changeMap()
        self.map.show()

        self.playSounds()
        self._initAccept()
        for k,v in self.hero.keyMap.items():
            self.hero.keyMap[k]=False

        base.taskMgr.add(self._main_loop,'room-main-loop')

    @print_func_time
    def exitPlay(self):
        '''
        隐藏模型
        影藏英雄血条
        停止游戏中音效
        清除 响应事件
        清除 主循环事件
        '''
        if self.hero.updateRay == self.updateRay:
            self.hero.updateRay = self.init_updateRay
        if self.roomInformation.typeStr=='leap':
            base.leapMotion.enable=False

        for monster in self.monsterList:
            monster.detachSound()
            monster.removeModel()
        for item in self.itemList:
            item._destroy()
        self.itemParentNP.removeNode()
        self.model.removeNode()
        if not (self.hero == None):
            self.hero.model.hide()
        self.heroBlood.hide()
        self.buffList.hide()
        if self.roomInformation.typeStr=='boss':
            self.bossBlood.hide()
        self.map.hide()
        self.stopSounds()
        base.messenger.ignoreAll(self)
        base.taskMgr.remove('room-main-loop')
    @print_func_time
    def enterBlank(self):
        pass

    ### end FSM
    #### public interface

    def setRoomInformation(self,information):
        self.roomInformation = information
        self._initModel(self.roomParentNP)

    def setHero(self,hero=None,pos=LVecBase3(0,0,0)):
        '''
        将主角对象放入房间
        并初始化主角的位置
        '''
        self.hero = hero
        if not self.hero == None:
            self.hero.model.setPos(pos)
    def setHeroPos(self,pos=LVecBase3(0,0,0)):
        if not self.hero == None:
            self.hero.model.setPos(pos)

    def playSounds(self):
        '''
        循环播放房间背景音乐
        '''
        if self.audioDict.has_key('bg') and self.audioDict['bg']:
            sounds = self.audioDict['bg']
            index = random.randint(0,len(sounds)-1)
            self.curbgm = sounds[index]
            self.curbgm.setLoop(True)
            self.curbgm.play()

    def stopSounds(self):
        '''
        暂停背景音乐
        '''
        if not self.curbgm==None:
            self.curbgm.stop()

    def playVideo(self,videoName,loop=False):
        if self.videoDict.has_key(videoName) and self.videoDict[videoName]:
            self.cardDict[videoName].show()
            idleVideo = self.videoDict[videoName]
            idleVideo.setLoop(loop)
            idleVideo.play()

    def getVideoTime(self,videoName):
        if self.videoDict.has_key(videoName) and self.videoDict[videoName]:
            idleVideo = self.videoDict[videoName]
            if videoName =='init' and (not NeedRoomInitVideo):
                return 0
            else:
                return idleVideo.length()
        else:
            return 0

    def stopVideo(self,videoName):
        if self.videoDict.has_key(videoName) and self.videoDict[videoName]:
            self.videoDict[videoName].setTime(0)
            self.videoDict[videoName].stop()
            self.cardDict[videoName].hide()
    ####

    ##### private interface
    def _initModelNameList(self):
        '''
        初始化房间模型列表
        '''
        self.modelNameList=[]
        self.basedir = os.path.join(sys.path[0],"Model/Scene")
        for parent,dirnames,filenames in os.walk(self.basedir):
            for filename in filenames:
                self.modelNameList.append(os.path.splitext(filename)[0])
        # 去掉boss房间
        try:
            i = self.modelNameList.index(bossRoomModelName)
            del self.modelNameList[i]
        except Exception as e:
            return

    def _initModel(self,parent=None):
        '''
        初始化房间模型
        '''

        self.collisionName = 'room'

        modelName = self.modelNameList[random.randint(0,len(self.modelNameList)-1)]
        if self.roomInformation.modelName=="":
            self.roomInformation.modelName = modelName
        else:
            modelName = self.roomInformation.modelName
        if self.roomInformation.typeStr=='boss':
            modelName = bossRoomModelName

        modelPathStr = "Model/Scene/{}"
        self.model = loader.loadModel(
            modelPathStr.format(modelName))

        self.model.setScale(self.scale)
        if parent==None:
            self.model.reparentTo(render)
        else:
            self.model.reparentTo(parent)

        base.camera.lookAt(self.model) 

        # room BG
        texFileName = 'Model/picture/roomBG.png'
        tex = loader.loadTexture(texFileName)

        cm = CardMaker("room bg")
        a = 200
        cm.setFrame(-a,a,-a,a)
        # Tell the CardMaker to create texture coordinates that take into
        # account the padding region of the texture.
        cm.setUvRange(tex)
        # Now place the card in the scene graph and apply the texture to it.
        card = render.attachNewNode(cm.generate())
        card.setPosHpr(LVecBase3(0,0,-2),LVecBase3(0,-90,0))
        card.setTexture(tex)

    @print_func_time
    def _initRoom(self):
        '''
        利用信息初始化，房间内的门，怪物，道具
        '''
        sTime = time.time()
        # 清除已存在的怪物、道具、门
        self.isInited = False
        self._clearOtherModel()

        # 添加新的怪物等模型信息
        self.itemParentNP = self.model.attachNewNode('room-item')
        self._addDoors()
        self._addMonsters()
        self._initEnemies()
        self.isInited = True
        diffTime = time.time()-sTime
        delayTime = 0

        if diffTime<InitRoomMinTime:
            delayTime=InitRoomMinTime-diffTime
        time.sleep(delayTime)
        self._accept_try_to_play()

    def _accept_try_to_play(self):
        self.lock.acquire()
        try:
            if self.isInited:
                self.request('Play')
                self.isInited=False
                return
        finally:
            self.lock.release()
    def _initBlood(self):
        """
        初始化英雄血条
        初始化boss血条
        """
        self.heroBlood = HeroBlood()
        self.bossBlood = BossBlood()

    def _initAccept(self):
        '''
        初始化房间后
        设置监听事件
        '''
        self.accept('hero-HPChange', self._accept_hero_hpchange)
        self.accept('hero-maxHPChange', self._accept_hero_maxhpchange)
        self.accept('hero-die', self._accept_hero_die)

        self.accept('bullet-create',self._accept_bullet_create)

        self.accept('monster-create',self._accept_monster_create)
        self.accept('monster-die',self._accept_monster_die)
        self.accept('monster-HPChange',self._accept_monster_hpchange)
        self.accept('monster-maxHPChange',self._accept_monster_maxhpchange)

        if self.roomInformation.typeStr=='boss':
            self.acceptOnce('boss-die',self._accept_boss_die)
        # 怪物死光事件
        self.acceptOnce('room-empty',self._accept_room_emtpy)

        self.accept('global-damage',self._accept_global_damage)
        self.accept('monster-into-bullet',self._accept_monster_into_bullet)
        self.accept('hero-into-bullet',self._accept_hero_into_bullet)
        self.accept('hero-into-monster',self._accept_hero_into_monster)

        # 转发 事件
        events = {'forward':('w','w-up'),'back':('s','s-up'),'left':('a','a-up'),'right':('d','d-up'),'fire':('mouse1','mouse1-up')}
        if self.roomInformation.typeStr == 'leap':
            # 接收鼠标新位置
            self.accept('new-pos',self._accept_new_pos_leap)
            self.accept('fire',self._accept_leap_attack)
            self.accept('pick',self._accept_leap_pick)
            self.accept('j',self._accept_leap_attack)
            self.accept('k',self._accept_leap_pick)
        else:
            for k,v in events.items():
                self.accept(v[0],self._accept_hero_control,[k,1])
            for k,v in events.items():
                self.accept(v[1],self._accept_hero_control,[k,0])

        if Debug:# 调试模式下
            # 相机位置调整
            self.accept('u',self._accept_camera_control,[1,1])
            self.accept('p',self._accept_camera_control,[1,-1])
            self.accept('i',self._accept_camera_control,[2,1])
            self.accept('o',self._accept_camera_control,[2,-1])

        if Debug:# 调试模式下
            # 聚光灯与环境光调整模式切换
            self.LightMode = 0
            self.accept('tab',self._accept_light_control)
            # 聚光灯颜色调整
            self.accept(',',self._accept_SpotLight_control,[-0.1])
            self.accept('.',self._accept_SpotLight_control,[0.1])
        if Debug:
            # 子弹速度调整
            self.accept('n',self._accept_bullet_control,[-0.1])
            self.accept('m',self._accept_bullet_control,[0.1])
        if Debug:
            # 调整leapmotion房间中camera的高度
            self.accept('v',self._accept_leap_camera_control,[-1])
            self.accept('b',self._accept_leap_camera_control,[1])

    def _accept_leap_camera_control(self,val):
        self.leapCameraZ +=val;
        print self.leapCameraZ
    def _accept_new_pos_leap(self,pos):
        self.newPos = LPoint3(pos[0],pos[1],0)
        self.newPos*=2
        self.newPos-=1
        #print self.newPos

    def _accept_bullet_control(self,val):
        defaultHeroBulletSpeed+=val
    def _accept_light_control(self):
        self.ignore(',')
        self.ignore('.')
        if self.LightMode==0:
            self.accept(',',self._accept_SpotLight_control,[-0.1])
            self.accept('.',self._accept_SpotLight_control,[0.1])
            self.LightMode = 1
        elif self.LightMode==1:
            self.accept(',',self._accept_ambientLight_control,[-0.1])
            self.accept('.',self._accept_ambientLight_control,[0.1])
            self.LightMode = 0

    def _accept_ambientLight_control(self,val):
        color = self.alight.node().getColor()
        print "ambientLight:",color
        temp=LVector4(val,val,val,0)+color
        self.alight.node().setColor(temp)

    def _accept_SpotLight_control(self,val):
        color = self.Slight.node().getColor()
        print "SpotLight:",color
        temp=LVector4(val,val,val,0)+color
        self.Slight.node().setColor(temp)

    def _accept_camera_control(self,index,val):
        pos = base.camera.getPos()
        pos[index]+=val
        base.camera.setPos(pos)
        base.camera.lookAt(LPoint3(0,0,0))
        print 'camera pos:',base.camera.getPos()

    def _accept_hero_control(self,key,val):
        self.hero.keyMap[key]=val

    def _accept_leap_pick(self):
        if not (self.roomInformation.typeStr == 'leap'):
            return
        if len(self.monsterList) >0:
            return  
        self.hero.model.setPos(self.leapCursor.getX(),self.leapCursor.getY(),0)
        self.hero.model.hide()
        self.hero.model.setPos(self.leapCursor.getX(),self.leapCursor.getY(),0)

    def _accept_leap_attack(self):
        if not (self.roomInformation.typeStr == 'leap'):
            return
        pos=self.leapCursor.getPos()
        self.hero.leapAttack(pos+LPoint3(0,0,20),1.5,1.2)

    def _initLight(self):
        '''
        初始化光照
        '''
        #self.shadow = Shadow()

        self.alight = render.attachNewNode(AmbientLight("Ambient"))

        self.alight.node().setColor(LVector4(*alightColor))
        render.setLight(self.alight)

        # 聚光灯
        self.Slight = render.attachNewNode(Spotlight("Spot"))
        a = 45
        self.Slight.setPos(LPoint3(a,0,a))
        self.Slight.lookAt(LPoint3(0,0,0))
        self.Slight.node().setColor(LVector4(*SlightColor))
        self.Slight.node().setScene(render)
        self.Slight.node().setShadowCaster(True)
        #self.Slight.node().showFrustum()
        self.Slight.node().getLens().setFov(40)
        self.Slight.node().getLens().setNearFar(10, 100)
        render.setLight(self.Slight)        



        # 点光源
        # p=0.5
        # x=10
        # y=10
        # z=10
        # self.plight = render.attachNewNode(PointLight("Point"))
        # self.plight.node().setColor(VBase4(p,p,p,1))
        # self.plight.node().setScene(render)
        # self.plight.node().setShadowCaster(True)

        # self.plight.setPos(x,y,z)
        # render.setLight(self.plight)

        # self.plight = render.attachNewNode(PointLight("Point"))
        # self.plight.node().setColor(VBase4(p,p,p,1))
        # self.plight.node().setScene(render)
        # self.plight.node().setShadowCaster(True)
        # self.plight.setPos(-x,-y,z)
        # render.setLight(self.plight)

        # 平行光
        # Now we create a directional light. Directional lights add shading from a
        # given angle. This is good for far away sources like the sun
        # self.directionalLight = render.attachNewNode(
        #     DirectionalLight("directionalLight"))
        # a = 0.5
        # self.directionalLight.node().setColor((a, a, a, 1))
        # a = 50
        # # The direction of a directional light is set as a 3D vector
        # self.directionalLight.node().setDirection(LVector3(0, a, -a))
        # # These settings are necessary for shadows to work correctly
        # self.directionalLight.setPos(LPoint3(0,a,a))
        # dlens = self.directionalLight.node().getLens()
        # # dlens.setFilmSize(41, 21)
        # # dlens.setNearFar(50, 75)
        # render.setLight(self.directionalLight)
        # # self.directionalLight.node().showFrustum()
        # self.directionalLight.node().setShadowCaster(True, 512, 512)

        # Important! Enable the shader generator.
        render.setShaderAuto()

    def _initAudio(self):
        '''
        初始化音效
        '''
        soundPathStr = "Audio/{}"

       # 背景音乐
        self.audioDict['bg']= []
        bgmName = 'musicStage{}.ogg'
        for i in range(1,11):
            self.audioDict['bg'].append(loader.loadMusic(soundPathStr.format(bgmName.format(i))))

    def _initVideo(self):
        '''
        初始化视频
        '''
        key = 'idle'
        self.videoDict[key],self.cardDict[key]= loadVideo('idle.mp4')
        key = 'init'
        self.videoDict[key],self.cardDict[key]= loadVideo('init.mp4')

    def _getInitHeroPos(self,pos='center'):
        '''
        pos: 'north','south','west','east','center'
        返回指定方位的坐标
        '''
        X = DefaultRoomX
        Y = DefaultRoomY
        absX = X/2
        absY = Y/2
        offX = 5
        offY = 5
        x = absX-offX
        y = absY-offY
        positions={'north':LPoint3f(0,y,0),
                   'south':LPoint3f(0,-y,0),
                   'west':LPoint3f(-x,0,0),
                   'east':LPoint3f(x,0,0),
                   'center':LPoint3f(0,0,0)
                   }
        return positions[pos]

    ##

    def _addDoors(self):
        '''
        根据 roomInformation，向房间中添加 door
        '''
        for pos,roomCodeToReach in self.roomInformation.doorDict.items():
            door = Door(pos,roomCodeToReach,self.model)
            self.doorList.append(door)

        inEvent = '{}-into-{}'.format(self.hero.colliderName,'door')
        self.accept(inEvent,self._accept_door_open)
        self.accept('n',self._accept_door_open)

    def _addLeapMonsters(self):
        '''
        根据设定产生下一波怪
        '''

        bulletNum=[0,6,12,18,0]
        monsterType=['Slime','Robot']

        self.leapTurn=self.leapTurn+1
        self.leapAttackNum=bulletNum[self.leapTurn]
        if self.leapTurn==4:
            #产生道具
            #print "leap room succ"
            pass

        positions = self._CalNPos(MonsterNums[self.leapTurn])
        if positions ==[]:
            return
        for x in xrange(0,MonsterNums[self.leapTurn]):
            monster=MonsterFactory.create(monsterType[random.randint(0,len(monsterType)-1)],positions[x],self.hero.model)
            if not (monster == None):
                self._accept_monster_create([monster])

    def updateRay(self):
        '''
        leapmotion房间根据给定位置设置射线
        '''
        self.hero.pickerRay.setFromLens(base.camNode, self.newPos[0], self.newPos[1])

    def updateCursorByleap(self):
        # print self.hero.mousePos
        self.leapCursor.setPos(self.hero.mousePos)

    def _addMonsters(self):
        '''
        根据 roomInformation，向房间中添加 monster
        '''
        num_sum = 0
        for v in self.roomInformation.monsterDict.values():
            num_sum+=v[0]
        if num_sum==0:
            return
        positions = self._CalNPos(num_sum)
        if not positions==[]:
            i=0
            for typeStr,v in self.roomInformation.monsterDict.items():
                if v[0]==0:
                    continue
                for x in range(0,v[0]):
                    monster = MonsterFactory.create(typeStr,positions[i],self.hero.model,v[1])
                    if not monster == None:
                        self.monsterList.append(monster)
                        i+=1
                    else:
                        self.roomInformation.monsterDict[typeStr][0]-=1
    ##

    def _initEnemies(self):
        # if not self.hero == None:
        #     for monster in self.monsterList:
        #         self.hero.setEnemy(monster)
        pass

    def _setHero_Enemy(self,enemy):
        # if not self.hero == None:
        #     self.hero.setEnemy(enemy)
        pass
    def _setMonster_Enemy(self,enemy):
        pass
    ##
    def _clearOtherModel(self):
        '''
        清除房间内已有的模型等信息
        '''
        for door in self.doorList:
            door.model.removeNode()
       #     door.model.cleanup()
            door.ignoreAll()
            door.removeAllTasks()

        for monster in self.monsterList:
            monster.detachSound()
            monster.removeModel()

        for item in self.itemList:
            try:
                # 更新房间内道具信息
                i = self.itemList.index(item)
                del self.itemList[i]
                item._destroy()
            except BaseException :
                logging.debug("_clearOtherModel error: {}".format(traceback.format_exc()))

        self.doorList=[]
        self.monsterList=[]
        self.itemList=[]

    ##
    def _CalNPos(self,n,xlen=DefaultRoomX,ylen=DefaultRoomY,a=4,wall_width=2):
        '''

        '''
        absX = xlen/3
        absY = ylen/3

        # 方位 原点 : 左上，左下，右上，右下
        dirs= [LPoint3(-absX,-absY,0),LPoint3(-absX,absY,0),LPoint3(0,-absY,0),LPoint3(0,absY,0)]
        # 每个方位的 出怪点：最多为16个，每个方位四个
        preparePositions=[]
        max_num = 16
        if not self.model==None:
            locatorName = '**/locator{}'
            for i in range(0,max_num):
                temp = self.model.find(locatorName.format(i+1))
                if not temp.isEmpty():
                    preparePositions.append(temp.getPos())
        if len(preparePositions)==0:
            posNum = max_num/4
            # 每个出怪点的相对每个方位的原点的坐标
            aX = absX/4
            aY = absY/4
            monsterPosRelOrigin=[LPoint3(aX-a,aY-a,0),LPoint3(aX-a,aY+a,0),LPoint3(aX+a,aY-a,0),LPoint3(aX+a,aY+a,0)]
            for i in range(0,len(dirs)-1):
                for pos in monsterPosRelOrigin:
                    preparePositions.append(dirs[i]+pos)

        if n > max_num:
            n=max_num
        n = int(n)
        return preparePositions[0:n]

    def _isContain(self,positions,given_pos,a):
        '''
        检测矩阵重叠（包括边重叠）
        1、列出两矩阵”不重叠“的条件
        2、取反
        3、根据 的摩根定律 变形
        检查已有点列表中，所形成的各个矩阵是否已经包含所给点所形成的矩阵
        '''
        for pos in positions:
           if (given_pos.getX()+ a >= pos.getX() and
               pos.getX() + a      >= given_pos.getX() and
               given_pos.getY() + a>= pos.getY() and
               pos.getY() + a      >= given_pos.getY()
               ):
               return True
        return False

    def _accept_hero_hpchange(self,newValue):
        self.heroBlood.setLifeBarValue(newValue)

    def _accept_hero_maxhpchange(self,newValue):
        self.heroBlood.setLifeBarMaxValue(newValue)

    def _accept_monster_hpchange(self,newValue):
        self.bossBlood.setLifeBarValue(newValue)

    def _accept_monster_maxhpchange(self,newValue):
        self.bossBlood.setLifeBarMaxValue(newValue)

    def _accept_hero_die(self):
        self.request('Idle')
        base.messenger.send("hero-death")

    def _accept_boss_die(self):
        Sequence(
                Func(self.ignoreAll),
                Func(self.request,'Blank'),
                Func(base.messenger.send,'gate-next')
                ).start()

    def _accept_room_emtpy(self):
        for door in self.doorList:
            door.show()
            door.open()

    ##
    def _accept_bullet_create(self,bullet):
        self.bulletList.append(bullet)

    def _accept_monster_create(self,monsters):
        for monster in monsters:
            if isinstance(monster,Monster):
                if monster.typeStr==None:
                    continue
                self.monsterList.append(monster)
                if self.roomInformation.monsterDict.has_key(monster.typeStr):
                    self.roomInformation.monsterDict[monster.typeStr][0]+=1
                else:
                    self.roomInformation.monsterDict[monster.typeStr]=LVecBase2(1,0)

    def _accept_door_open(self,entry=None):
        '''
        检测当前房间是否还有怪物存活
        如果没有，就播放“open”动画，并通告“room-next”事件
        '''
        if self._isEmpty():
            door = self._getDoorByMinDistanceWithHero()
            if door.roomCodeToReach==-1 or door.isOpen:
                return
            # 换到下一个房间
            Sequence(
                Func(self.ignoreAll),
                Func(self.request,'Blank'),
                Func(base.messenger.send,'room-next',[door.pos,door.roomCodeToReach])
                ).start()

    def _getDoorByMinDistanceWithHero(self):
        door = None
        lens = 2494967495
        for d in self.doorList:
            pos = d.model.getPos(self.hero.model)
            if lens > pos.length():
                lens=pos.length()
                door = d
        return door

    def _accept_monster_die(self,pos):
        '''
        获取怪物位置
        根据道具信息，创建道具
        '''
        # 根据概率产生道具
        if ItemFactory.isGen(self.roomInformation.roomCode):
            pos.setZ(0)
            index = random.randint(0,len(self.itemInfoList)-1)
            item = ItemFactory.create(self.itemInfoList[index],pos,self.hero,self.buffList,self.itemParentNP)
            if not item==None:
                self.itemList.append(item)
        pass


    def _accept_monster_into_bullet(self,entry):
        Bullet.onCollision(entry)
    def _accept_hero_into_bullet(self,entry):
        Bullet.onCollision(entry)
    def _accept_hero_into_monster(self,entry):
        Monster.onTouch(entry)
    def _accept_global_damage(self,damage_value):
        for monster in self.monsterList:
            monster.decreaseHP(damage_value)

    #
    def _isEmpty(self):
        empty=True
        for num in self.roomInformation.monsterDict.values():
            if num[0]:
                empty=False
                break;
        return empty
    ##
    def _main_loop(self,task):
        '''
        房间主循环
        '''
        #摄像机调整
        if self.roomInformation.typeStr=='leap':
            if self.hero != None:
                self.hero.updateRay()
            if base.camera.getY()<0:
                base.camera.setPos(0,base.camera.getY()+1,base.camera.getZ()+1)
                base.camera.lookAt(self.model)
                return Task.cont
            if base.camera.getZ()<self.leapCameraZ:
                base.camera.setPos(0,0,base.camera.getZ()+1)
                base.camera.lookAt(self.model)
                return Task.cont
            elif base.camera.getZ()>self.leapCameraZ:
                base.camera.setPos(0,0,base.camera.getZ()-1)
                base.camera.lookAt(self.model)
                return Task.cont
            self.updateCursorByleap()
        else:
            if not self.hero == None:
                self.hero.update()
            if base.camera.getZ()>36:
                base.camera.setPos(0,base.camera.getY()-1,base.camera.getZ()-1)
                base.camera.lookAt(self.model)
                return Task.cont
            if base.camera.getY()>-33:
                base.camera.setPos(0,base.camera.getY()-1,36)
                base.camera.lookAt(self.model)
                return Task.cont            
        


        tempList=[]
        # 更新子弹
        curTime = time.time()
        for bullet in self.bulletList:
            bullet.update(curTime)
            # todo 检测bullet 声明周期
            if not bullet.expires==-1:
                tempList.append(bullet)
        del self.bulletList
        self.bulletList = tempList
        # 检查道具
        for item in self.itemList:
            if item.item.isEmpty():
                try:
                    # 更新房间内道具信息
                    i = self.itemList.index(item)
                    del self.itemList[i]
                except BaseException :
                    traceback.print_exc()
        empty = True
        if not self._isEmpty():
            for monster in self.monsterList:
                if not self.model.isEmpty():
                    #monster.beforeUpdate()
                    empty=False
        if not empty:
            base.AIworld.update()
        for monster in self.monsterList:
            monster.update()
            if monster.model.isEmpty():
                try:
                    # 更新房间内怪物信息
                    i = self.monsterList.index(monster)
                    del self.monsterList[i]
                    # 对应类型的怪物数量减一
                    self.roomInformation.monsterDict[monster.typeStr][0]-=1
                except BaseException :
                    traceback.print_exc()
                if len(self.monsterList)==0 and self.roomInformation.typeStr=='leap' and self.leapTurn<4 :
                    self._addLeapMonsters()
        if self._isEmpty():
            base.messenger.send('room-empty')
            if self.roomInformation.typeStr=='boss':
                base.messenger.send('boss-die')
        return Task.cont








