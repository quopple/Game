#!usr/bin/python
# coding:utf-8

# Panda3D imports
from direct.showbase.DirectObject import DirectObject
from direct.actor.Actor import Actor
from panda3d.core import CollisionSphere,CollisionNode,CollideMask , AudioSound
from panda3d.core import CollisionRay,CollisionPlane,LPlane
from Monster import *
from panda3d.core import BitMask32, CardMaker, Vec4, Quat
from random import randint, random

# Game imports
from MovableObject import MovableObject
from Bullet import *
#from Monster import Monster
from DefaultConfigVal import *
import copy
import time
import math


HeroModelPath = "Model/Hero/"
HeroSoundPath = "Audio/"


class Hero(DirectObject,MovableObject):
    def __init__(self,pos = (0,0,0) ,scale = 1,parent=None):
        DirectObject.__init__(self)
        MovableObject.__init__(self)

        # 英雄属性
        self._maxHP = defaultHeroHP
        self._HP = defaultHeroHP
        self._attackPower = defaultHeroAttackPower
        self._attackSpeed = defaultHeroAttackSpeed
        self.isMoving = False
        self._moveSpeed = defaultHeroMoveSpeed
        self.mousePos=(0,0,0)
        self.leapAttackTime=-1
        #英雄被击闪烁
        self.invincible=False #是否无敌
        self.changeTime=-1 #下次变换形态时间
        self.recoveryTime=-1 #恢复正常的时间
        self.isHide=False

        ########## set model size hero
        self.bullet = SphereBullet()#(intoMask = CollideMask.bit(DefaultMonsterMaskVal))
        if not self.bullet.model.isEmpty():
            self.bullet.model.removeNode()
        self.attackMode = "Common"

        self.lastAttackTime = 0 # to enable shoutting at the beginning
        self.position = pos

        self.initAttackMethod = self.attack

        #'model_dierguanBOSS',{ #
        # 英雄模型和相应动画
        self.model = Actor(
            HeroModelPath + "model_mainChara", {
               "Walk": HeroModelPath + "anim_mainChara_running_attack",
               #"Attack": HeroModelPath + "anim_mainChara_standing",
               "Hit": HeroModelPath + "anim_mainChara_standing",
               "Die": HeroModelPath + "anim_mainChara_standing"
            }
        )
        if parent==None:
            self.model.reparentTo( base.render)
        else:
            self.model.reparentTo(parent)
        self.model.setPos(self.position)
        self.lastPos = self.position
        self.scale = scale
        self.model.setScale(scale)
        self.model.hide()
        # 设置碰撞检测
        self.colliderName = "hero"
        characterSphere = CollisionSphere(0,0,2,1)
        characterColNode = CollisionNode( self.colliderName)
        characterColNode.addSolid(characterSphere)
        characterColNode.setFromCollideMask( CollideMask.bit(DefaultHeroMaskVal)^CollideMask.bit(defaultHeroInMonsterMaskVal))

        # print characterColNode.getFromCollideMask()
        self.colliderNodePath = self.model.attachNewNode(characterColNode)
        #self.colliderNodePath.show()
        #将对象添加到nodepath中  用于在碰撞事件处理中获取对象
        self.colliderNodePath.setPythonTag("Hero",self)
        base.cTrav.addCollider(self.colliderNodePath,base.cHandler)
        #用于处理英雄与墙壁的碰撞
        characterSphere2 = CollisionSphere(0,0,2,1)
        characterColNode2 = CollisionNode( self.colliderName)
        characterColNode2.addSolid(characterSphere2)
        self.colliderNodePath2 = self.model.attachNewNode(characterColNode2)
        self.modelGroundHandler = CollisionHandlerQueue()
        base.cTrav.addCollider(self.colliderNodePath2,self.modelGroundHandler)
        # #用于支持英雄与怪物的物理碰撞
        characterSphere3 = CollisionSphere(0,0,2,1)
        characterColNode3 = CollisionNode( self.colliderName)
        characterColNode3.addSolid(characterSphere3)

        self.colliderNodePath3 = self.model.attachNewNode(characterColNode3)
        base.cPusher.addCollider(self.colliderNodePath3, self.model)
        #用于支持鼠标控制英雄的朝向----------------
        self.angle = 0
        self.pickerName = 'mouseRay'
        self.pickerNode = CollisionNode(self.pickerName)
        self.pickerNP = camera.attachNewNode(self.pickerNode)
        self.pickerNode.setFromCollideMask( CollideMask.bit(5))
        self.pickerNode.setIntoCollideMask(CollideMask.allOff())

        self.pickerRay = CollisionRay()
        self.pickerNode.addSolid(self.pickerRay)
        #self.pickerNP.show()
        base.cTrav.addCollider(self.pickerNP, base.cHandler)

        self.pickedName = 'mousePlane'
        self.pickedNode = CollisionNode(self.pickedName)
        self.pickedNP = render.attachNewNode(self.pickedNode)
        self.pickedNode.setFromCollideMask(CollideMask.allOff())
        self.pickedNode.setIntoCollideMask(CollideMask.bit(5))

        self.pickedPlane = CollisionPlane(LPlane(LVector3f(0,0,1),LPoint3f(0,0,2)))
        self.pickedNode.addSolid(self.pickedPlane)
        #self.pickedNP.show()

        #------------------------------------

        #加载英雄的各种音效
        self.sounds["GetItem"] = loader.loadSfx(HeroSoundPath + "getItem.wav")
        self.sounds["Die"] = loader.loadSfx(HeroSoundPath + "robot_death.wav")
        self.sounds["Attack"] = loader.loadSfx(HeroSoundPath + "bullet_shooting.wav")

        #键位字典
        self.keyMap = {
            "left": 0, "right": 0, "forward": 0, "back": 0, "fire": 0}

        self._initAccept()

    def _initAccept(self):
        againEvent = '{}-again-{}'
        self.accept(againEvent.format(self.pickerName,self.pickedName),self._accept_ray_into_plane)

    def _accept_ray_into_plane(self,entry):
        pos = entry.getSurfacePoint(render)
        self.mousePos=LPoint3(pos[0],pos[1],pos[2])
        x, y = pos.get_x()-self.model.getPos().get_x(),pos.get_y()-self.model.getPos().get_y()
        angle = math.atan2(y, x)
        angle = angle * 180 / math.pi+90
        self.angle = angle
        
    # maxHP
    @property
    def maxHP(self):
        return self._maxHP
    @maxHP.setter
    def maxHP(self,value):
        if value > defaultHeroMaxHPMax:
            value = defaultHeroMaxHPMax
        self._maxHP = value
    # HP
    @property
    def HP(self):
        return self._HP
    @HP.setter
    def HP(self,value):
        if value > self._maxHP:
            value = self._maxHP
        self._HP = value

    # attackPower
    @property
    def attackPower(self):
        return self._attackPower
    @attackPower.setter
    def attackPower(self,value):
        if value > defaultHeroAttackPowerMax:
            value = defaultHeroAttackPowerMax
        self._attackPower = value

    # attackSpeed
    @property
    def attackSpeed(self):
        return self._attackSpeed
    @attackSpeed.setter
    def attackSpeed(self,value):
        if value > defaultHeroAttackSpeedMax:
            value = defaultHeroAttackSpeedMax
        self._attackSpeed = value

    # moveSpeed
    @property
    def moveSpeed(self):
        return self._moveSpeed
    @moveSpeed.setter
    def moveSpeed(self,value):
        if value > defaultHeroMoveSpeedMax:
            value = defaultHeroMoveSpeedMax
        self._moveSpeed=value

    def setPos(self,pos):
        self.position = pos
        self.model.setPos(pos)

    def setScale(self,scale):
        self.scale = scale
        self.model.setScale(scale)

    def setEnemy(self, enemy):
        if isinstance(enemy,Monster):
            #inEvent = "{}-into-{}".format(enemy.colliderName,self.colliderName )
            inEvent = "{}-into-{}".format(self.colliderName,enemy.colliderName )
            self.accept(inEvent, self.underAttack )
        if isinstance(enemy,Bullet):
            inEvent = "{}-into-{}".format(self.colliderName, enemy.colliderName )
            base.cHandler.addInPattern(inEvent)
            enemy.accept( inEvent,enemy.action )

    def move(self):
        dt = base.globalClock.getDt()

        x = self.model.getX()
        y = self.model.getY()
        dis = self._moveSpeed * dt
        #控制移动
        if self.keyMap['forward']:
            y += dis
        if self.keyMap['back']:
            y -= dis
        if self.keyMap['left']:
            x -= dis
        if self.keyMap['right']:
            x += dis
        if x == self.model.getX() and y == self.model.getY():
            if self.isMoving:
                self.model.stop()
                self.model.pose("walk", 0)
                self.isMoving = False
        elif not self.isMoving:
            self.model.loop('Walk')
            self.isMoving=True

        self.model.setX(x)
        self.model.setY(y)

        # 控制面朝向
        self.updateDirection()

        #是否与房间（墙壁）碰撞
        base.cTrav.traverse(base.render)
        entries = list( self.modelGroundHandler.getEntries())
        entries.sort(key=lambda x: x.getSurfacePoint(base.render).getZ())

        backup = False
        for entry in entries :
            if entry.getIntoNode().getName() == "room":
                backup = True
                break

        if backup:
            self.model.setPos( self.lastPos )
        else:
            self.lastPos = self.model.getPos()

        #base.camera.setPos(self.model.getX(), self.model.getY()+20, 20)
        #base.camera.lookAt(self.model)

    def updateDirection(self):
        self.model.setH(self.angle)

    def updateRay(self):
        '''
        在主循环中更新 人物朝向控制射线的方向
        '''
        if base.mouseWatcherNode.hasMouse():
            mpos = base.mouseWatcherNode.getMouse()
            self.pickerRay.setFromLens(base.camNode, mpos.getX(), mpos.getY())

    def attack(self,taskTime):
        '''
        taskTime 无效参数，可以重新赋值
        '''
        angle = self.angle
        # 是否过了攻击冷却期
        currTime = time.time()
        split = currTime - self.lastAttackTime
        if standarHitRate * 1.0 / self.attackSpeed > split:
            return

        # 更新上一次攻击的时间
        self.lastAttackTime = currTime

        # 播放攻击动画
        self.model.play("Attack")
        # 播放攻击音效
        self.sounds["Attack"].play()

        # 子弹位置
        pos = self.model.getPos()
        bullet = self.bullet.copy()#SphereBullet()#copy.deepcopy(self.bullet)
        bullet.model.reparentTo(render)
        bullet.setPos(pos)
        bullet.setZ(2) # bullet.getZ() +

        # 子弹生命周期（消亡的时间）
        bullet.setExpires(currTime + bullet.bulletLife) #bullet.bulletLife
        # 子弹飞行方向

        bullet.setAngle(angle)

        # 子弹伤害值 （ 子弹本身伤害值 + 英雄攻击力 ）
        bullet.damage += self.attackPower
        bullet.model.show()
        # 注册子弹
        base.messenger.send("bullet-create", [bullet])
    def leapAttack(self,pos,size,speed):
        if self.leapAttackTime>time.time():
            return
        self.leapAttackTime=time.time()+2
        bullet=LeapBullet(pos,DefaultMonsterMaskVal,size,speed)
        base.messenger.send("bullet-create", [bullet])

    def update(self):
        self.updateInvincible()
        self.updateRay()
        self.move()
        self.updateDirection()

        if self.keyMap["fire"]:
            self.attack(time.time)
            self.keyMap["fire"] = False
    def updateInvincible(self):#处理无敌状态
        if self.recoveryTime>time.time():
            self.invincible=True
            if self.changeTime<time.time():
                if self.isHide:
                    self.isHide=False
                    self.model.show()
                    self.changeTime=time.time()+0.2
                else:
                    self.isHide=True
                    self.model.hide()
                    self.changeTime=time.time()+0.2
        else:
            self.model.show()
            self.invincible=False
    def underAttack(self,val=defaultHeroHitByMonsterDamageVal):
        if self.invincible==True:
            return
        self.model.play("Hit")
        self.decreaseHP(val)
        self.recoveryTime=time.time()+1.5

    def decreaseHP(self,val):

        self.HP -= val
        if self.HP < 0:
            self.HP = 0
        base.messenger.send("hero-HPChange",[self.HP])
        if self.HP == 0:
            if Debug:
                return
            self.die()

    def increaseHP(self,val):
        self.HP += val
        if self.HP > self.maxHP:
            self.HP = self.maxHP
        base.messenger.send("hero-HPChange", [self.HP])

    def increaseMaxHP(self,val):
        self.maxHP += val
        base.messenger.send("hero-maxHPChange", [self.maxHP])

    def die(self):
        self.doMethodLater(self.model.getDuration("Die"),self.destroy,"hero-die")
        self.model.play("Die")
        self.sounds["Die"].play()
        # 防止继续移动 旋转
        self.ignoreAll()
        base.taskMgr.remove("hero-Loop")

    def destroy(self,task):
        base.messenger.send("hero-die")

    @staticmethod
    def ToDict(hero):
        dict = {}
        dict["maxHP"] = hero.maxHP
        dict["HP"] = hero.HP
        dict["attackPower"] = hero.attackPower
        dict["attackSpeed"] = hero.attackSpeed
        dict["moveSpeed"] = hero._moveSpeed
        dict["bullet"] = hero.bullet.ToDict(hero.bullet)
        dict["pos"] = [hero.position[0],hero.position[1],hero.position[2]]
        dict["scale"] = hero.scale
        dict["attackMode"] = hero.attackMode
        return dict

    @staticmethod
    def ToHero(dict):
        hero = Hero()
        hero.maxHP = dict["maxHP"]
        hero.HP = dict["HP"]
        hero.attackPower = dict["attackPower"]
        hero.attackSpeed = dict["attackSpeed"]
        hero.setPos( LVecBase3f(dict["pos"][0],dict['pos'][1],dict['pos'][2]))
        hero.setScale( dict["scale"] )
        hero._moveSpeed = dict["moveSpeed"]
        hero.attackMode = dict["attackMode"]
        hero.bullet = BulletFactory.getBullet( dict["bullet"] ,hero)

        return hero

    def reInit(self,dict,renew=False):
        self.maxHP = dict["maxHP"]
        self.HP = dict["HP"]
        self.attackPower = dict["attackPower"]
        self.attackSpeed = dict["attackSpeed"]
        self._moveSpeed = dict["moveSpeed"]
        self.attackMode = dict["attackMode"]
        self.bullet = BulletFactory.getBullet( dict["bullet"] ,self)
        self.setPos( LVecBase3f(dict["pos"][0],dict['pos'][1],dict['pos'][2]))
        self.setScale( dict["scale"] )
        if renew:
            self.attack = self.initAttackMethod
        self._initAccept()
