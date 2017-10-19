# coding:utf-8

# Game imports
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
    AmbientLight,
    PerspectiveLens,
    DirectionalLight,
    KeyboardButton,
    AudioSound,
    CardMaker
    )
from panda3d.ai import *
import random
from MovableObject import MovableObject
from Bullet import *
from DefaultConfigVal import *

import math

MonsterModelPath = "Model/Monster/"
MonsterSoundPath = "Audio/Monster/"

class MonsterFactory(object):
    @staticmethod
    def create(typeStr,pos,target,extraHPRate=1.0):
        ret=None
        if typeStr=="Slime":
            ret=Slime(pos,target)
        if typeStr=="Robot":
            ret=Robot(pos,target)
        if typeStr=="BigSlime":
            ret=BigSlime(pos,target)
        if typeStr=="BigRobot":
            ret=BigRobot(pos,target)
        if typeStr=="Bat":
            ret=Bat(pos,target)
        if typeStr=="FlyingRobot":
            ret=FlyingRobot(pos,target)
        if typeStr=="MechanicalHead":
            ret=MechanicalHead(pos,target)
        if typeStr=="Skull":
            ret=Skull(pos,target)
        if typeStr=="MagicalTower":
            ret=MagicalTower(pos,target)
        if typeStr=="EletricTower":
            ret=EletricTower(pos,target)
        if typeStr=="Mole":
            ret=Mole(pos,target)
        if typeStr=="DrillRobot":
            ret=DrillRobot(pos,target)
        if typeStr=="Caterpillar":
            ret=Caterpillar(pos,target)
        if typeStr=="Train":
            ret=Train(pos,target)
        if typeStr=="Minotaur":
            ret=Minotaur(pos,target)
        if typeStr=="MechanicalSpider":
            ret=MechanicalSpider(pos,target)

        if ret==None:
            print("there is no monster call this")
        else:
            ret.HP*=extraHPRate
        return ret


class Monster(DirectObject,MovableObject):
    AINum=0
    def __init__ (self,pos):
        DirectObject.__init__(self)
        MovableObject.__init__(self)
        #属性
        self.index = defaultMonsterIndex
        self.MaxHP = defaultMonsterMaxHP
        self._HP = defaultMonsterHP
        self.attackPower = defaultMonsterAttackPower
        self.moveSpeed = defaultMonsterMoveSpeed
        self.isBoss = False
        self.IsAttacking = False
        self.position = pos
        self.state="alive"
        self.AIName=None
        self.AI="none"
        #被击闪烁
        self.isUnderAttack = False
        self.isHide = False
        self.showTime=-1
    @property
    def HP(self):
        return self._HP
    @HP.setter
    def HP(self,value):
        if value < 0:
            value = 0;
        self._HP = value
    @staticmethod
    def onTouch(entry):
        nodepath=entry.getIntoNodePath()
        monster=Monster.getMonster(nodepath)
        monster.touchAttack(entry)

    @staticmethod
    def setMonster(nodepath,monster):
        nodepath.setPythonTag("monster",monster)
    @staticmethod
    def getMonster(nodepath):
        return nodepath.getPythonTag("monster")
    @staticmethod
    def getHero(nodepath):
        return nodepath.getPythonTag("Hero")

    def touchAttack(self,entry):
        nodepath=entry.getFromNodePath()
        hero=self.getHero(nodepath)
        hero.underAttack(self.attackPower)


    def underAttack(self,val):
        self.isUnderAttack=True
        self.model.play("Hit")
        if not self.sounds["Hit"] is None:
            self.sounds["Hit"].play()
        self.decreaseHP(val)
        AISetting.pursue(self,self.moveSpeed,self.target)

    def decreaseHP(self,val):
        self.HP -= val
        print self.isBoss,self.HP
        if self.isBoss:
            base.messenger.send("monster-HPChange",[self.HP])
        if self.HP <= 0:
            self.die()
    def increaseHP(self,val):
        self.HP += val
        if self.HP > self.MaxHP:
            self.HP = self.MaxHP
        if self.isBoss:
            base.messenger.send("monster-HPChange", [self.HP])

    def die(self):
        if self.state!="alive":
            return
        #播放动画，完毕后设置死亡
        self.state="todie"

        self.ignoreAll()
        taskMgr.doMethodLater(0, self.setDie,"name",[])

    def setDie(self):
        self.state="die"
        pos=self.model.getPos()

        if PARTICLE:
            base.enableParticles()
            # 火焰
            self.particle_fire = ParticleEffect()
            self.particle_fire.loadConfig('assets/particles/fireish.ptf')
            self.particle_fire.setPos(self.model.getPos())
            self.particle_fire.setZ(defaultParticleZ)
            self.particle_fire.setH(defaultParticleAngle*180/math.pi)
            self.particle_fire.setScale(defaultParticleScale)
            # 烟雾
            self.particle_smoke = ParticleEffect()
            self.particle_smoke.loadConfig('assets/particles/smoke.ptf')
            self.particle_smoke.setPos(self.model.getPos())
            self.particle_smoke.setZ(defaultParticleZ)
            self.particle_smoke.setH(defaultParticleAngle*180/math.pi)
            self.particle_smoke.setScale(defaultParticleScale*0.5)
            Sequence(
                Func(self.particle_fire.start,render),
                Func(self.particle_smoke.start,render),
                Wait(defaultParticleInterTime),
                Func(self.removeModel),
                Wait(defaultParticleInterTime),
                Func(self.particle_fire.cleanup),
                Func(self.particle_smoke.cleanup),
                Func(base.messenger.send,'monster-die',[pos]),
                ).start()
        else:
            self.removeModel()
            base.messenger.send('monster-die',[pos])




    def isDie(self):
        if self.state=="die":
            return True
        else:
            return False
    def update(self):
        if self.state=="alive":
            self.updateUnderAttack()
            self.updateAI()
        elif self.state=="todie":
            self.removeAI()
            self.removeCollider()
            self.detachSound()
            self.state="dying"
    def updateUnderAttack (self):
        if self.isUnderAttack:
            self.isHide=True
            self.model.hide()
            self.isUnderAttack=False
            self.showTime=time.time()+defaultMonsterUnderAttackHideTime
        else:
            if self.isHide and self.showTime<time.time():
                self.model.show()
                self.isHide=False

    def removeModel(self):
        if not self.model.isEmpty():
            self.model.cleanup()
            self.model.removeNode()

class Slime(Monster):
    def __init__(self,pos,target):
        Monster.__init__(self,pos)
        self.MaxHP = defaultSlimeMaxHP
        self._HP = defaultSlimeHP
        self.attackPower = defaultSlimeAttackPower
        self.moveSpeed = defaultSlimeMoveSpeed
        #加载模型
        self.typeStr = 'Slime'
        self.model = Actor(
            MonsterModelPath + "model_slime",
            {
                "Walk": MonsterModelPath + "model_slime"
            #     "Attack": MonsterModelPath + "slime_attack",
            #     "Hit": MonsterModelPath + "slime_hit",
            #     "Die": MonsterModelPath + "slime_die"
            }
        )
        self.model.reparentTo( base.render)
        self.model.setPos(self.position)
        self.model.setScale(defaultSlimeScale)
        self.lastPosStack=[self.model.getPos()]

        #主碰撞体
        self.colliderName = 'monster'
        characterColNode = CollisionNode("monster")
        characterColNode.addSolid(CollisionSphere(0,0,defaultSlimeColliderZ,defaultSlimeColliderRadius))
        characterColNode.setFromCollideMask( CollideMask.bit(DefaultMonsterMaskVal) )#0
        characterColNode.setIntoCollideMask(CollideMask.bit(defaultHeroInMonsterMaskVal))#2
        Monster.setMonster(characterColNode,self)
        self.colliderNodePath = self.model.attachNewNode(characterColNode)
        self.colliderNodePath.setPythonTag("Monster",self)
        # self.colliderNodePath.show()
        base.cTrav.addCollider(self.colliderNodePath,base.cHandler)

        #怪物与墙壁碰撞
        self.wallHandler=CollisionHandlerQueue()
        wallCN=CollisionNode(self.colliderName)
        wallCN.addSolid(CollisionSphere(0,0,defaultSlimeColliderZ,defaultSlimeColliderRadius))
        wallCN.setFromCollideMask(CollideMask.bit(defaultMonsterInWallMaskVal)) #8
        wallCN.setIntoCollideMask(CollideMask.allOff())
        self.wallCNP=self.model.attachNewNode(wallCN)
        base.cTrav.addCollider(self.wallCNP,self.wallHandler)
        #音效
        self.sounds["Hit"] = base.audio3d.loadSfx(MonsterSoundPath + "SlimeGotHit.mp3")

        if not self.sounds["Hit"] is None:
            base.audio3d.attachSoundToObject(self.sounds["Hit"], self.model)

        #AI
        self.initAI(base.AIworld,target)
    def initAI(self,AIworld,target):
        self.AIworld=AIworld
        self.target=target
        #初始化为闲逛
        AISetting.wander(self,defaultSlimeWanderSpeed,defaultSlimeWanderRange)
        self.model.setPlayRate(defaultSlimeWalkRate,'Walk')
        self.model.loop("Walk")

    def updateAI(self):
        if self.AI=="wander":
            if getDistance(self.model.getPos(),self.target.getPos())<defaultSlimeDetectRangeVal:
                AISetting.pursue(self,defaultSlimePursueSpeed,self.target)


        if hasattr(self,'AIworld'):
            entries = list( self.wallHandler.getEntries())
            if len(entries) > 0:
                if self.lastPosStack!=[]:
                    self.model.setPos(self.lastPosStack.pop())
                    AISetting.wander(self,defaultSlimeWanderSpeed,defaultSlimeWanderRange,random.randint(defaultRandomWanderActMinNum,defaultRandomWanderActMaxNum),False)
            else:
                self.lastPosStack.append(self.model.getPos())
    def detachSound(self):
        base.audio3d.detachSound(self.sounds["Hit"])
    def removeCollider(self):
        self.colliderNodePath.removeNode()
        self.wallCNP.removeNode()
    def removeAI(self):
        self.AIworld.removeAiChar(self.AIName)
class Robot(Monster):
    def __init__(self,pos,target):
        Monster.__init__(self,pos)
        self.MaxHP = defaultRobotMaxHP
        self._HP = defaultRobotHP
        self.attackPower = defaultRobotAttackPower
        self.moveSpeed = defaultRobotMoveSpeed
        #加载模型
        self.typeStr = 'Robot'
        self.model = Actor(
            MonsterModelPath + "model_robot",
            {
                "Walk": MonsterModelPath + "model_robot",
            #     "Attack": MonsterModelPath + "slime_attack",
            #     "Hit": MonsterModelPath + "slime_hit",
            #     "Die": MonsterModelPath + "slime_die"
            }
        )
        self.model.reparentTo( base.render)
        self.model.setScale(defaultRobotScale)
        self.model.setPos(self.position)
        self.lastPosStack=[self.model.getPos()]
        #主碰撞体
        self.colliderName = 'monster'
        characterColNode = CollisionNode("monster")
        characterColNode.addSolid(CollisionSphere(0,0,defaultRobotColliderZ,defaultRobotColliderRadius))
        characterColNode.setFromCollideMask( CollideMask.bit(DefaultMonsterMaskVal) )#0
        characterColNode.setIntoCollideMask(CollideMask.bit(defaultHeroInMonsterMaskVal))#2
        self.colliderNodePath = self.model.attachNewNode(characterColNode)
        self.colliderNodePath.setPythonTag("Monster",self)
        # # self.colliderNodePath.show()
        Monster.setMonster(characterColNode,self)
        base.cTrav.addCollider(self.colliderNodePath,base.cHandler)

        #怪物与墙壁碰撞
        self.wallHandler=CollisionHandlerQueue()
        wallCN=CollisionNode(self.colliderName)
        wallCN.addSolid(CollisionSphere(0,0,defaultRobotColliderZ,defaultRobotColliderRadius))
        wallCN.setFromCollideMask(CollideMask.bit(defaultMonsterInWallMaskVal)) #8
        wallCN.setIntoCollideMask(CollideMask.allOff())
        self.wallCNP=self.model.attachNewNode(wallCN)
        base.cTrav.addCollider(self.wallCNP,self.wallHandler)
        #音效
        self.sounds["Hit"] = base.audio3d.loadSfx(MonsterSoundPath + "RobotGotHit.mp3")
        if not self.sounds["Hit"] is None:
            base.audio3d.attachSoundToObject(self.sounds["Hit"], self.model)

        #AI
        self.initAI(base.AIworld,target)
    def initAI(self,AIworld,target):
        self.AIworld=AIworld
        self.target=target
        #初始化为闲逛
        AISetting.wander(self,defaultRobotWanderSpeed,defaultRobotWanderRange)

        self.model.loop("Walk")
    def updateAI(self):
        if self.AI=="wander":
            if getDistance(self.model.getPos(),self.target.getPos())<defaultRobotDetectRangeVal:
                AISetting.pursue(self,defaultRobotPursueSpeed,self.target)


        if hasattr(self,'AIworld'):
            entries = list( self.wallHandler.getEntries())
            if len(entries) > 0:
                if self.lastPosStack!=[]:
                    self.model.setPos(self.lastPosStack.pop())
                    AISetting.wander(self,defaultRobotWanderSpeed,defaultRobotWanderRange,random.randint(defaultRandomWanderActMinNum,defaultRandomWanderActMaxNum),False)
            else:
                self.lastPosStack.append(self.model.getPos())
    def detachSound(self):
        base.audio3d.detachSound(self.sounds["Hit"])

    def removeCollider(self):
        self.colliderNodePath.removeNode()
        self.wallCNP.removeNode()
    def removeAI(self):
        self.AIworld.removeAiChar(self.AIName)
class BigSlime(Monster):
    def __init__(self,pos,target):
        Monster.__init__(self,pos)
        self.MaxHP = defaultBigSlimeMaxHP
        self._HP = defaultBigSlimeHP
        self.attackPower = defaultBigSlimeAttackPower
        self.moveSpeed = defaultBigSlimeMoveSpeed
        #加载模型
        self.typeStr = 'BigSlime'
        self.model = Actor(
            MonsterModelPath + "model_bigslime",
            {
                "Walk": MonsterModelPath + "model_bigslime",
            #     "Attack": MonsterModelPath + "slime_attack",
            #     "Hit": MonsterModelPath + "slime_hit",
            #     "Die": MonsterModelPath + "slime_die"
            }
        )
        self.model.reparentTo( base.render)
        self.model.setPos(self.position)
        self.model.setScale(defaultBigSlimeScale)
        self.lastPosStack=[self.model.getPos()]
        #主碰撞体
        self.colliderName = 'monster'
        characterColNode = CollisionNode("monster")
        characterColNode.addSolid(CollisionSphere(0,0,defaultBigSlimeColliderZ,defaultBigSlimeColliderRadius))
        characterColNode.setFromCollideMask( CollideMask.bit(DefaultMonsterMaskVal) )#0
        characterColNode.setIntoCollideMask(CollideMask.bit(defaultHeroInMonsterMaskVal))#2
        self.colliderNodePath = self.model.attachNewNode(characterColNode)
        self.colliderNodePath.setPythonTag("Monster",self)
        # # self.colliderNodePath.show()
        Monster.setMonster(characterColNode,self)
        base.cTrav.addCollider(self.colliderNodePath,base.cHandler)

        #怪物与墙壁碰撞
        self.wallHandler=CollisionHandlerQueue()
        wallCN=CollisionNode(self.colliderName)
        wallCN.addSolid(CollisionSphere(0,0,defaultBigSlimeColliderZ,defaultBigSlimeColliderRadius))
        wallCN.setFromCollideMask(CollideMask.bit(defaultMonsterInWallMaskVal)) #8
        wallCN.setIntoCollideMask(CollideMask.allOff())
        self.wallCNP=self.model.attachNewNode(wallCN)
        base.cTrav.addCollider(self.wallCNP,self.wallHandler)
        #音效
        self.sounds["Hit"] = base.audio3d.loadSfx(MonsterSoundPath + "BigSlimeGotHit.mp3")

        if not self.sounds["Hit"] is None:
            base.audio3d.attachSoundToObject(self.sounds["Hit"], self.model)

        #AI
        self.initAI(base.AIworld,target)
    def initAI(self,AIworld,target):
        self.AIworld=AIworld
        self.target=target
        #初始化为闲逛
        AISetting.wander(self,defaultBigSlimeWanderSpeed,defaultBigSlimeWanderRange)
        self.model.setPlayRate(defaultBigSlimeWalkRate,'Walk')
        self.model.loop("Walk")
    def updateAI(self):
        if self.AI=="wander":
            if getDistance(self.model.getPos(),self.target.getPos())<defaultBigSlimeDetectRangeVal:
                AISetting.pursue(self,defaultBigSlimePursueSpeed,self.target)


        if hasattr(self,'AIworld'):
            entries = list( self.wallHandler.getEntries())
            if len(entries) > 0:
                if self.lastPosStack!=[]:
                    self.model.setPos(self.lastPosStack.pop())
                    AISetting.wander(self,defaultBigSlimeWanderSpeed,defaultBigSlimeWanderRange,random.randint(defaultRandomWanderActMinNum,defaultRandomWanderActMaxNum),False)
            else:
                self.lastPosStack.append(self.model.getPos())
    def detachSound(self):
        base.audio3d.detachSound(self.sounds["Hit"])
    def removeCollider(self):
        self.colliderNodePath.removeNode()
        self.wallCNP.removeNode()
    def removeAI(self):
        self.AIworld.removeAiChar(self.AIName)
    def die(self):
        newPos=self.model.getPos()
        Monster.die(self)

        smallSlime1=MonsterFactory.create("Slime",newPos+(defaultBigSlimeGenSlimeDis,0,0),self.target)
        smallSlime2=MonsterFactory.create("Slime",newPos+(-defaultBigSlimeGenSlimeDis,0,0),self.target)
        base.messenger.send("monster-create",[[smallSlime1,smallSlime2]])
class BigRobot(Monster):
    def __init__(self,pos,target):
        Monster.__init__(self,pos)
        self.MaxHP = defaultBigRobotMaxHP
        self._HP = defaultBigRobotHP
        self.attackPower = defaultBigRobotAttackPower
        self.moveSpeed = defaultBigRobotMoveSpeed
        #加载模型
        self.typeStr = 'BigRobot'
        self.model = Actor(
            MonsterModelPath + "model_bigrobot",
            {
                "Walk": MonsterModelPath + "anim_doubleRobot"
            #     "Attack": MonsterModelPath + "slime_attack",
            #     "Hit": MonsterModelPath + "slime_hit",
            #     "Die": MonsterModelPath + "slime_die"
            }
        )
        self.model.reparentTo( base.render)
        self.model.setPos(self.position)
        self.model.setScale(defaultBigRobotScale)
        self.lastPosStack=[self.model.getPos()]
        #主碰撞体
        self.colliderName = 'monster'
        characterColNode = CollisionNode("monster")
        characterColNode.addSolid(CollisionSphere(0,0,defaultBigRobotColliderZ,defaultBigRobotColliderRadius))
        characterColNode.setFromCollideMask( CollideMask.bit(DefaultMonsterMaskVal) )#0
        characterColNode.setIntoCollideMask(CollideMask.bit(defaultHeroInMonsterMaskVal))#2
        self.colliderNodePath = self.model.attachNewNode(characterColNode)
        self.colliderNodePath.setPythonTag("Monster",self)
        # # self.colliderNodePath.show()
        Monster.setMonster(characterColNode,self)
        base.cTrav.addCollider(self.colliderNodePath,base.cHandler)

        #怪物与墙壁碰撞
        self.wallHandler=CollisionHandlerQueue()
        wallCN=CollisionNode(self.colliderName)
        wallCN.addSolid(CollisionSphere(0,0,defaultBigRobotColliderZ,defaultBigRobotColliderRadius))
        wallCN.setFromCollideMask(CollideMask.bit(defaultMonsterInWallMaskVal)) #8
        wallCN.setIntoCollideMask(CollideMask.allOff())
        self.wallCNP=self.model.attachNewNode(wallCN)
        base.cTrav.addCollider(self.wallCNP,self.wallHandler)
        #音效
        self.sounds["Hit"] = base.audio3d.loadSfx(MonsterSoundPath + "BigRobotGotHit.mp3")

        if not self.sounds["Hit"] is None:
            base.audio3d.attachSoundToObject(self.sounds["Hit"], self.model)

        #AI
        self.initAI(base.AIworld,target)
    def initAI(self,AIworld,target):
        self.AIworld=AIworld
        self.target=target
        #初始化为闲逛
        AISetting.wander(self,defaultBigRobotWanderSpeed,defaultBigRobotWanderRange)
        self.model.setPlayRate(defaultBigRobotWalkRate,'Walk')
        self.model.loop("Walk")
    def updateAI(self):
        if self.AI=="wander":
            if getDistance(self.model.getPos(),self.target.getPos())<defaultBigRobotDetectRangeVal:
                AISetting.pursue(self,defaultBigRobotPursueSpeed,self.target)

        if hasattr(self,'AIworld'):
            entries = list( self.wallHandler.getEntries())
            if len(entries) > 0:
                if self.lastPosStack!=[]:
                    self.model.setPos(self.lastPosStack.pop())
                    AISetting.wander(self,defaultBigRobotWanderSpeed,defaultBigRobotWanderRange,random.randint(defaultRandomWanderActMinNum,defaultRandomWanderActMaxNum),False)
            else:
                self.lastPosStack.append(self.model.getPos())
    def detachSound(self):
        base.audio3d.detachSound(self.sounds["Hit"])
    def removeCollider(self):
        self.colliderNodePath.removeNode()
        self.wallCNP.removeNode()
    def removeAI(self):
        self.AIworld.removeAiChar(self.AIName)
    def die(self):
        newPos=self.model.getPos()
        Monster.die(self)

        smallRobot1=MonsterFactory.create("Robot",newPos+(defaultBigRobotGenRobotDis,0,0),self.target)
        smallRobot2=MonsterFactory.create("Robot",newPos+(-defaultBigRobotGenRobotDis,0,0),self.target)
        base.messenger.send("monster-create",[[smallRobot1,smallRobot2]])
class Bat(Monster):
    def __init__(self,pos,target):
        Monster.__init__(self,pos)
        self.MaxHP = defaultBatMaxHP
        self._HP = defaultBatHP
        self.attackPower = defaultBatAttackPower
        self.moveSpeed = defaultBatMoveSpeed
        #加载模型
        self.typeStr = 'Bat'
        self.model = Actor(
            MonsterModelPath + "model_bat",
            {
                "Walk": MonsterModelPath + "model_bat"
            #     "Attack": MonsterModelPath + "slime_attack",
            #     "Hit": MonsterModelPath + "slime_hit",
            #     "Die": MonsterModelPath + "slime_die"
            }
        )
        self.model.reparentTo( base.render)
        self.model.setPos(self.position+(0,0,defaultBatModelZ))
        self.model.setScale(defaultBatScale)
        self.lastPosStack=[self.model.getPos()]
        #主碰撞体
        self.colliderName = 'monster'
        characterColNode = CollisionNode("monster")
        characterColNode.addSolid(CollisionSphere(0,0,defaultBatColliderZ,defaultBatColliderRadius))
        characterColNode.setFromCollideMask( CollideMask.bit(DefaultMonsterMaskVal) )#0
        characterColNode.setIntoCollideMask(CollideMask.bit(defaultHeroInMonsterMaskVal))#2
        self.colliderNodePath = self.model.attachNewNode(characterColNode)
        self.colliderNodePath.setPythonTag("Monster",self)
        # # self.colliderNodePath.show()
        Monster.setMonster(characterColNode,self)
        base.cTrav.addCollider(self.colliderNodePath,base.cHandler)

        #怪物与墙壁碰撞
        self.wallHandler=CollisionHandlerQueue()
        wallCN=CollisionNode(self.colliderName)
        wallCN.addSolid(CollisionSphere(0,0,defaultBatColliderZ,defaultBatColliderRadius))
        wallCN.setFromCollideMask(CollideMask.bit(defaultMonsterInWallMaskVal)) #8
        wallCN.setIntoCollideMask(CollideMask.allOff())
        self.wallCNP=self.model.attachNewNode(wallCN)
        base.cTrav.addCollider(self.wallCNP,self.wallHandler)
        #音效
        self.sounds["Hit"] = base.audio3d.loadSfx(MonsterSoundPath + "BatGotHit.mp3")
        self.sounds["Explode"] = base.audio3d.loadSfx(MonsterSoundPath + "BatExplode.mp3")
        if not self.sounds["Explode"] is None:
            base.audio3d.attachSoundToObject(self.sounds["Explode"], self.model)
        if not self.sounds["Hit"] is None:
            base.audio3d.attachSoundToObject(self.sounds["Hit"], self.model)

        #AI
        self.initAI(base.AIworld,target)
    def initAI(self,AIworld,target):
        self.AIworld=AIworld
        self.target=target
        #初始化为闲逛
        AISetting.wander(self,defaultBatWanderSpeed,defaultBatWanderRange)
        self.model.setPlayRate(defaultBatWalkRate,'Walk')
        self.model.loop("Walk")
    def updateAI(self):
        self.model.setH(self.model.getH()+90)

        if getDistance(self.model.getPos(),self.target.getPos())<defaultBatDetectExplodeRangeVal:
            self.die()
            return
        if self.AI=="wander":
            if getDistance(self.model.getPos(),self.target.getPos())<defaultBatDetectRangeVal:
                AISetting.pursue(self,defaultBatPursueSpeed,self.target)
        if self.AI=="pursue":
            self.model.setZ(defaultBatModelZ)
        if hasattr(self,'AIworld'):
            entries = list( self.wallHandler.getEntries())
            if len(entries) > 0:
                if self.lastPosStack!=[]:
                    self.model.setPos(self.lastPosStack.pop())
                    AISetting.wander(self,defaultBatWanderSpeed,defaultBatWanderRange,random.randint(defaultRandomWanderActMinNum,defaultRandomWanderActMaxNum),False)
            else:
                self.lastPosStack.append(self.model.getPos())
    def detachSound(self):
        base.audio3d.detachSound(self.sounds["Hit"])
        base.audio3d.detachSound(self.sounds["Explode"])
    def removeCollider(self):
        self.colliderNodePath.removeNode()
        self.wallCNP.removeNode()
    def removeAI(self):
        self.AIworld.removeAiChar(self.AIName)
    def die(self):
        myAnimControl = self.model.getAnimControl("ToExplode")
        len = 0
        if not myAnimControl == None:
            len = myAnimControl.getDuration('ToExplode')
            self.model.play("ToExplode")
        taskMgr.doMethodLater(len, self.explode,"name",[])

    def underAttack(self,val):
        self.isUnderAttack=True
        self.model.play("Hit")
        if not self.sounds["Hit"] is None:
            self.sounds["Hit"].play()
        self.decreaseHP(val)
        AISetting.pursue(self,defaultBatPursueSpeed,self.target)
    def explode(self):
        if self.state!="alive":
            return
        bullet=TrapDurativeBullet(self.model.getPos()+(0,0,defaultBatExplodeZ), time.time(), defaultBatExplodeAttackPower, defaultBatExplodeRange, DefaultHeroMaskVal,defaultBatExplodeLastTime,"bullet_boom")
        Monster.die(self)
        base.messenger.send("bullet-create", [bullet])
class FlyingRobot(Monster):
    def __init__(self,pos,target):
        Monster.__init__(self,pos)
        self.MaxHP = defaultFlyingRobotMaxHP
        self._HP = defaultFlyingRobotHP
        self.attackPower = defaultFlyingRobotAttackPower
        self.moveSpeed = defaultFlyingRobotMoveSpeed
        #加载模型
        self.typeStr = 'FlyingRobot'
        self.model = Actor(
            MonsterModelPath + "model_flyingrobot",
            {
                "Walk": MonsterModelPath + "model_flyingrobot"
            #     "Attack": MonsterModelPath + "slime_attack",
            #     "Hit": MonsterModelPath + "slime_hit",
            #     "Die": MonsterModelPath + "slime_die"
            }
        )
        self.model.reparentTo( base.render)
        self.model.setPos(self.position+(0,0,defaultFlyingRobotModelZ))
        self.model.setScale(defaultFlyingRobotScale)
        self.lastPosStack=[self.model.getPos()]
        #主碰撞体
        self.colliderName = 'monster'
        characterColNode = CollisionNode("monster")
        characterColNode.addSolid(CollisionSphere(0,0,defaultFlyingRobotColliderZ,defaultFlyingRobotColliderRadius))
        characterColNode.setFromCollideMask( CollideMask.bit(DefaultMonsterMaskVal) )#0
        characterColNode.setIntoCollideMask(CollideMask.bit(defaultHeroInMonsterMaskVal))#2
        self.colliderNodePath = self.model.attachNewNode(characterColNode)
        self.colliderNodePath.setPythonTag("Monster",self)
        # # self.colliderNodePath.show()
        Monster.setMonster(characterColNode,self)
        base.cTrav.addCollider(self.colliderNodePath,base.cHandler)

        #怪物与墙壁碰撞
        self.wallHandler=CollisionHandlerQueue()
        wallCN=CollisionNode(self.colliderName)
        wallCN.addSolid(CollisionSphere(0,0,defaultFlyingRobotColliderZ,defaultFlyingRobotColliderRadius))
        wallCN.setFromCollideMask(CollideMask.bit(defaultMonsterInWallMaskVal)) #8
        wallCN.setIntoCollideMask(CollideMask.allOff())
        self.wallCNP=self.model.attachNewNode(wallCN)
        base.cTrav.addCollider(self.wallCNP,self.wallHandler)
        #音效
        self.sounds["Hit"] = base.audio3d.loadSfx(MonsterSoundPath + "FlyingRobotGotHit.mp3")
        self.sounds["Explode"] = base.audio3d.loadSfx(MonsterSoundPath + "FlyingRobotExplode.mp3")
        if not self.sounds["Explode"] is None:
            base.audio3d.attachSoundToObject(self.sounds["Explode"], self.model)
        if not self.sounds["Hit"] is None:
            base.audio3d.attachSoundToObject(self.sounds["Hit"], self.model)

        #AI
        self.initAI(base.AIworld,target)
    def initAI(self,AIworld,target):
        self.AIworld=AIworld
        self.target=target
        #初始化为闲逛
        self.model.setPlayRate(defaultFlyingRobotWalkRate ,'Walk')
        AISetting.wander(self,defaultFlyingRobotWanderSpeed,defaultFlyingRobotWanderRange)
        self.model.loop("Walk")
    def updateAI(self):
        if getDistance(self.model.getPos(),self.target.getPos())<defaultFlyingRobotDetectExplodeRangeVal:
            self.explode()
            return
        if self.AI=="wander":
            if getDistance(self.model.getPos(),self.target.getPos())<defaultFlyingRobotDetectRangeVal:
                AISetting.pursue(self,defaultFlyingRobotPursueSpeed,self.target)
        if self.AI=="pursue":
            self.model.setZ(defaultFlyingRobotModelZ)
        if hasattr(self,'AIworld'):
            entries = list( self.wallHandler.getEntries())
            if len(entries) > 0:
                if self.lastPosStack!=[]:
                    self.model.setPos(self.lastPosStack.pop())
                    AISetting.wander(self,defaultFlyingRobotWanderSpeed,defaultFlyingRobotWanderRange,random.randint(defaultRandomWanderActMinNum,defaultRandomWanderActMaxNum),False)
            else:
                self.lastPosStack.append(self.model.getPos())
    def detachSound(self):
        base.audio3d.detachSound(self.sounds["Hit"])
        base.audio3d.detachSound(self.sounds["Explode"])
    def removeCollider(self):
        self.colliderNodePath.removeNode()
        self.wallCNP.removeNode()
    def removeAI(self):
        self.AIworld.removeAiChar(self.AIName)
    def die(self):
        myAnimControl = self.model.getAnimControl("ToExplode")
        len = 0
        if not myAnimControl == None:
            len = myAnimControl.getDuration('ToExplode')
            self.model.play("ToExplode")
        taskMgr.doMethodLater(len, self.explode,"name",[])
    def underAttack(self,val):
        self.isUnderAttack=True
        self.model.play("Hit")
        if not self.sounds["Hit"] is None:
            self.sounds["Hit"].play()
        self.decreaseHP(val)
        AISetting.pursue(self,defaultFlyingRobotPursueSpeed,self.target)
    def explode(self):
        if self.state!="alive":
            return
        bullet=TrapBullet(self.model.getPos()+(0,0,defaultFlyingRobotExplodeZ), time.time(), defaultFlyingRobotExplodeAttackPower, defaultFlyingRobotExplodeRange, DefaultHeroMaskVal,defaultFlyingRobotExplodeLastTime)
        Monster.die(self)
        base.messenger.send("bullet-create", [bullet])
class MechanicalHead(Monster):
    def __init__(self,pos,target):
        Monster.__init__(self,pos)
        self.MaxHP = defaultMechanicalHeadMaxHP
        self._HP = defaultMechanicalHeadHP
        self.attackPower = defaultMechanicalHeadAttackPower
        self.moveSpeed = defaultMechanicalHeadMoveSpeed

        self.attackTime=-1
        self.moveTime=-1
        self.attackRate=defaultMechanicalHeadAttackRate
        #加载模型
        self.typeStr = 'MechanicalHead'
        self.model = Actor(
            MonsterModelPath + "model_mechanicalhead"
            # {
            #     "Walk": MonsterModelPath + "slime_walk",
            #     "Attack": MonsterModelPath + "slime_attack",
            #     "Hit": MonsterModelPath + "slime_hit",
            #     "Die": MonsterModelPath + "slime_die"
            # }
        )
        self.model.reparentTo( base.render)
        self.model.setPos(self.position+(0,0,defaultMechanicalHeadModelZ))
        self.model.setScale(defaultMechanicalHeadScale)
        self.lastPosStack=[self.model.getPos()]

        #主碰撞体
        self.colliderName = 'monster'
        characterColNode = CollisionNode("monster")
        characterColNode.addSolid(CollisionSphere(0,0,defaultMechanicalHeadColliderZ,defaultMechanicalHeadColliderRadius))
        characterColNode.setFromCollideMask( CollideMask.bit(DefaultMonsterMaskVal) )#0
        characterColNode.setIntoCollideMask(CollideMask.bit(defaultHeroInMonsterMaskVal))#2
        self.colliderNodePath = self.model.attachNewNode(characterColNode)
        self.colliderNodePath.setPythonTag("Monster",self)
        # # self.colliderNodePath.show()
        Monster.setMonster(characterColNode,self)
        base.cTrav.addCollider(self.colliderNodePath,base.cHandler)

        #怪物与墙壁碰撞
        self.wallHandler=CollisionHandlerQueue()
        wallCN=CollisionNode(self.colliderName)
        wallCN.addSolid(CollisionSphere(0,0,defaultMechanicalHeadColliderZ,defaultMechanicalHeadColliderRadius))
        wallCN.setFromCollideMask(CollideMask.bit(defaultMonsterInWallMaskVal)) #8
        wallCN.setIntoCollideMask(CollideMask.allOff())
        self.wallCNP=self.model.attachNewNode(wallCN)
        base.cTrav.addCollider(self.wallCNP,self.wallHandler)
        #音效
        self.sounds["Hit"] = base.audio3d.loadSfx(MonsterSoundPath + "MechanicalHeadGotHit.mp3")
        self.sounds["Attack"] = base.audio3d.loadSfx(MonsterSoundPath + "MechanicalHeadAttack.mp3")
        if not self.sounds["Attack"] is None:
            base.audio3d.attachSoundToObject(self.sounds["Attack"], self.model)
        if not self.sounds["Hit"] is None:
            base.audio3d.attachSoundToObject(self.sounds["Hit"], self.model)

        #AI
        self.initAI(base.AIworld,target)
    def initAI(self,AIworld,target):
        self.AIworld=AIworld
        self.target=target
        #初始化为闲逛
        AISetting.wander(self,defaultMechanicalHeadWanderSpeed,defaultMechanicalHeadWanderRange)
        self.model.loop("Walk")
    def updateAI(self):

        if self.AI=="wander":
            if getDistance(self.model.getPos(),self.target.getPos())<defaultMechanicalHeadDetectRangeVal:
                AISetting.pursue(self,defaultMechanicalHeadPursueSpeed,self.target)

        if self.AI=="pursue" or self.AI=="flee":
            if getDistance(self.model.getPos(),self.target.getPos())<defaultMechanicalHeadDetectRangeVal:
                if not self.attack():
                    AISetting.flee(self,defaultMechanicalHeadFleeSpeed,self.target,defaultMechanicalHeadDetectRangeVal,defaultMechanicalHeadDetectRangeVal)
            else:
                AISetting.pursue(self,defaultMechanicalHeadPursueSpeed,self.target)

        if self.AI=="stop":
            if time.time()>self.moveTime:
                if getDistance(self.model.getPos(),self.target.getPos())<defaultMechanicalHeadDetectRangeVal:
                    AISetting.flee(self,defaultMechanicalHeadFleeSpeed,self.target,defaultMechanicalHeadDetectRangeVal,defaultMechanicalHeadDetectRangeVal)
                else:
                    AISetting.pursue(self,defaultMechanicalHeadPursueSpeed,self.target)

        if hasattr(self,'AIworld'):
            entries = list( self.wallHandler.getEntries())
            if len(entries) > 0:
                if self.lastPosStack!=[]:
                    self.model.setPos(self.lastPosStack.pop())
                    AISetting.wander(self,defaultMechanicalHeadWanderSpeed,defaultMechanicalHeadWanderRange,random.randint(defaultRandomWanderActMinNum,defaultRandomWanderActMaxNum),False)
            else:
                self.lastPosStack.append(self.model.getPos())
                self.model.setZ(defaultMechanicalHeadModelZ)

    def attack(self):#尝试攻击
        if time.time()>self.attackTime:
            AISetting.stop(self)
            self.moveTime=time.time()+defaultMechanicalHeadAttackToMoveTime
            # bullet=TrapBullet(self.model.getPos()+(0,0,-1), time.time(), self.attackPower, 3, DefaultHeroMaskVal,0.5)
            y=self.model.getY()-self.target.getY()
            x=self.model.getX()-self.target.getX()
            angle = math.atan2(y,x)
            angle = angle*180/math.pi -90
            bullet=SphereBullet(self.model.getPos(), time.time(), angle,DefaultHeroMaskVal, defaultMechanicalHeadBulletAttackPower,defaultMechanicalHeadBulletSize, defaultMechanicalHeadBulletSpeed, DefaultRangeVal,"bullet_monster.egg")
            base.messenger.send("bullet-create", [bullet])
            self.attackTime=time.time()+self.attackRate
            return True
        else:
            return False

    def detachSound(self):
        base.audio3d.detachSound(self.sounds["Hit"])
        base.audio3d.detachSound(self.sounds["Attack"])
    def removeCollider(self):
        self.colliderNodePath.removeNode()
        self.wallCNP.removeNode()
    def removeAI(self):
        self.AIworld.removeAiChar(self.AIName)
    def die(self):
        Monster.die(self)
class Skull(Monster):
    def __init__(self,pos,target):
        Monster.__init__(self,pos)
        self.MaxHP = defaultSkullMaxHP
        self._HP = defaultSkullHP
        self.attackPower = defaultSkullAttackPower
        self.moveSpeed = defaultSkullMoveSpeed

        self.attackTime=-1
        self.moveTime=-1
        self.attackRate=defaultSkullAttackRate
        #加载模型
        self.typeStr = 'Skull'
        self.model = Actor(
            MonsterModelPath + "model_skull"
            # {
            #     "Walk": MonsterModelPath + "slime_walk",
            #     "Attack": MonsterModelPath + "slime_attack",
            #     "Hit": MonsterModelPath + "slime_hit",
            #     "Die": MonsterModelPath + "slime_die"
            # }
        )
        self.model.reparentTo( base.render)
        self.model.setPos(self.position+(0,0,defaultSkullModelZ))
        self.model.setScale(defaultSkullScale)
        self.lastPosStack=[self.model.getPos()]

        #主碰撞体
        self.colliderName = 'monster'
        characterColNode = CollisionNode("monster")
        characterColNode.addSolid(CollisionSphere(0,0,defaultSkullColliderZ,defaultSkullColliderRadius))
        characterColNode.setFromCollideMask( CollideMask.bit(DefaultMonsterMaskVal) )#0
        characterColNode.setIntoCollideMask(CollideMask.bit(defaultHeroInMonsterMaskVal))#2
        self.colliderNodePath = self.model.attachNewNode(characterColNode)
        self.colliderNodePath.setPythonTag("Monster",self)
        # # self.colliderNodePath.show()
        Monster.setMonster(characterColNode,self)
        base.cTrav.addCollider(self.colliderNodePath,base.cHandler)

        #怪物与墙壁碰撞
        self.wallHandler=CollisionHandlerQueue()
        wallCN=CollisionNode(self.colliderName)
        wallCN.addSolid(CollisionSphere(0,0,defaultSkullColliderZ,defaultSkullColliderRadius))
        wallCN.setFromCollideMask(CollideMask.bit(defaultMonsterInWallMaskVal)) #8
        wallCN.setIntoCollideMask(CollideMask.allOff())
        self.wallCNP=self.model.attachNewNode(wallCN)
        base.cTrav.addCollider(self.wallCNP,self.wallHandler)
        #音效
        self.sounds["Hit"] = base.audio3d.loadSfx(MonsterSoundPath + "SkullGotHit.mp3")
        self.sounds["Attack"] = base.audio3d.loadSfx(MonsterSoundPath + "SkullAttack.mp3")
        if not self.sounds["Attack"] is None:
            base.audio3d.attachSoundToObject(self.sounds["Attack"], self.model)
        if not self.sounds["Hit"] is None:
            base.audio3d.attachSoundToObject(self.sounds["Hit"], self.model)

        #AI
        self.initAI(base.AIworld,target)
    def initAI(self,AIworld,target):
        self.AIworld=AIworld
        self.target=target
        #初始化为闲逛
        AISetting.wander(self,defaultSkullWanderSpeed,defaultSkullWanderRange)
        self.model.loop("Walk")
    def updateAI(self):

        if self.AI=="wander":
            if getDistance(self.model.getPos(),self.target.getPos())<defaultSkullDetectRangeVal:
                AISetting.pursue(self,defaultSkullPursueSpeed,self.target)

        if self.AI=="pursue" or self.AI=="flee":
            if getDistance(self.model.getPos(),self.target.getPos())<defaultSkullDetectRangeVal:
                if not self.attack():
                    AISetting.flee(self,defaultSkullFleeSpeed,self.target,defaultSkullDetectRangeVal,defaultSkullDetectRangeVal)
            else:
                AISetting.pursue(self,defaultSkullPursueSpeed,self.target)

        if self.AI=="stop":
            if time.time()>self.moveTime:
                if getDistance(self.model.getPos(),self.target.getPos())<defaultSkullDetectRangeVal:
                    AISetting.flee(self,defaultSkullFleeSpeed,self.target,defaultSkullDetectRangeVal,defaultSkullDetectRangeVal)
                else:
                    AISetting.pursue(self,defaultSkullPursueSpeed,self.target)

        if hasattr(self,'AIworld'):
            entries = list( self.wallHandler.getEntries())
            if len(entries) > 0:
                if self.lastPosStack!=[]:
                    self.model.setPos(self.lastPosStack.pop())
                    AISetting.wander(self,defaultSkullWanderSpeed,defaultSkullWanderRange,random.randint(defaultRandomWanderActMinNum,defaultRandomWanderActMaxNum),False)
            else:
                self.lastPosStack.append(self.model.getPos())
                self.model.setZ(defaultSkullModelZ)

    def attack(self):#尝试攻击
        if time.time()>self.attackTime:
            AISetting.stop(self)
            self.moveTime=time.time()+defaultSkullAttackToMoveTime
            y=self.model.getY()-self.target.getY()
            x=self.model.getX()-self.target.getX()
            angle = math.atan2(y,x)
            angle = angle*180/math.pi -90
            bullet=SphereBullet(self.model.getPos(), time.time(), angle,DefaultHeroMaskVal, defaultSkullBulletAttackPower,defaultSkullBulletSize, defaultSkullBulletSpeed, defaultSkullBulletRange,"bullet_monster.egg")
            base.messenger.send("bullet-create", [bullet])
            self.attackTime=time.time()+self.attackRate
            return True
        else:
            return False

    def detachSound(self):
        base.audio3d.detachSound(self.sounds["Hit"])
        base.audio3d.detachSound(self.sounds["Attack"])
    def removeCollider(self):
        self.colliderNodePath.removeNode()
        self.wallCNP.removeNode()
    def removeAI(self):
        self.AIworld.removeAiChar(self.AIName)
    def die(self):
        Monster.die(self)
class MagicalTower(Monster):
    def __init__(self,pos,target):
        Monster.__init__(self,pos)
        self.MaxHP = defaultMagicalTowerMaxHP
        self._HP = defaultMagicalTowerHP
        self.attackPower = defaultMagicalTowerAttackPower
        self.bullets=[]
        self.isAttack=False
        #加载模型
        self.typeStr = 'MagicalTower'
        self.model = Actor(
            MonsterModelPath + "model_magicaltower"
            # {
            #     "Walk": MonsterModelPath + "slime_walk",
            #     "Attack": MonsterModelPath + "slime_attack",
            #     "Hit": MonsterModelPath + "slime_hit",
            #     "Die": MonsterModelPath + "slime_die"
            # }
        )
        self.model.reparentTo( base.render)
        self.model.setPos(self.position)
        self.model.setScale(defaultMagicalTowerScale)
        self.lastPos=self.model.getPos()

        #主碰撞体
        self.colliderName = 'monster'
        characterColNode = CollisionNode("monster")
        characterColNode.addSolid(CollisionSphere(0,0,defaultMagicalTowerColliderZ,defaultMagicalTowerColliderRadius))
        characterColNode.setFromCollideMask( CollideMask.bit(DefaultMonsterMaskVal) )#0
        characterColNode.setIntoCollideMask(CollideMask.bit(defaultHeroInMonsterMaskVal))#2
        self.colliderNodePath = self.model.attachNewNode(characterColNode)
        self.colliderNodePath.setPythonTag("Monster",self)
        # # self.colliderNodePath.show()
        Monster.setMonster(characterColNode,self)
        base.cTrav.addCollider(self.colliderNodePath,base.cHandler)

        #音效
        self.sounds["Hit"] = base.audio3d.loadSfx(MonsterSoundPath + "MagicalTowerGotHit.mp3")
        self.sounds["Attack"] = base.audio3d.loadSfx(MonsterSoundPath + "MagicalTowerAttack.mp3")
        if not self.sounds["Attack"] is None:
            base.audio3d.attachSoundToObject(self.sounds["Attack"], self.model)
        if not self.sounds["Hit"] is None:
            base.audio3d.attachSoundToObject(self.sounds["Hit"], self.model)

        #AI
        self.initAI(base.AIworld,target)
    def initAI(self,AIworld,target):
        self.AIworld=AIworld
        self.target=target


    def updateAI(self):
        if not self.isAttack:
            self.attack()
            self.isAttack=True
        pass
    def underAttack(self,val):
        self.isUnderAttack=True
        self.model.play("Hit")
        if not self.sounds["Hit"] is None:
            self.sounds["Hit"].play()
        self.decreaseHP(val)

    def attack(self):
        r1=defaultMagicalTowerBulletRadius1
        r2=defaultMagicalTowerBulletRadius2
        r3=defaultMagicalTowerBulletRadius3
        bullets=[]
        bullets.append(AroundPermanentBullet(self,0,self.attackPower, defaultMagicalTowerAngleSpeed1 , defaultMagicalTowerBulletSize1 ,r1,DefaultHeroMaskVal))
        bullets.append(AroundPermanentBullet(self,120,self.attackPower, defaultMagicalTowerAngleSpeed1 , defaultMagicalTowerBulletSize1 ,r1,DefaultHeroMaskVal))
        bullets.append(AroundPermanentBullet(self,240,self.attackPower, defaultMagicalTowerAngleSpeed1 , defaultMagicalTowerBulletSize1 ,r1,DefaultHeroMaskVal))

        bullets.append(AroundPermanentBullet(self,0,self.attackPower, defaultMagicalTowerAngleSpeed2 , defaultMagicalTowerBulletSize2 ,r2,DefaultHeroMaskVal))
        bullets.append(AroundPermanentBullet(self,90,self.attackPower, defaultMagicalTowerAngleSpeed2 , defaultMagicalTowerBulletSize2 ,r2,DefaultHeroMaskVal))
        bullets.append(AroundPermanentBullet(self,180,self.attackPower, defaultMagicalTowerAngleSpeed2 , defaultMagicalTowerBulletSize2 ,r2,DefaultHeroMaskVal))
        bullets.append(AroundPermanentBullet(self,270,self.attackPower, defaultMagicalTowerAngleSpeed2 , defaultMagicalTowerBulletSize2 ,r2,DefaultHeroMaskVal))

        bullets.append(AroundPermanentBullet(self,0,self.attackPower, defaultMagicalTowerAngleSpeed3 , defaultMagicalTowerBulletSize3 ,r3,DefaultHeroMaskVal))
        bullets.append(AroundPermanentBullet(self,72,self.attackPower, defaultMagicalTowerAngleSpeed3 , defaultMagicalTowerBulletSize3 ,r3,DefaultHeroMaskVal))
        bullets.append(AroundPermanentBullet(self,144,self.attackPower, defaultMagicalTowerAngleSpeed3 , defaultMagicalTowerBulletSize3 ,r3,DefaultHeroMaskVal))
        bullets.append(AroundPermanentBullet(self,216,self.attackPower, defaultMagicalTowerAngleSpeed3 , defaultMagicalTowerBulletSize3 ,r3,DefaultHeroMaskVal))
        bullets.append(AroundPermanentBullet(self,288,self.attackPower, defaultMagicalTowerAngleSpeed3 , defaultMagicalTowerBulletSize3 ,r3,DefaultHeroMaskVal))
        for bullet in bullets:
            base.messenger.send("bullet-create", [bullet])

        self.bullets=bullets

    def detachSound(self):
        base.audio3d.detachSound(self.sounds["Hit"])
        base.audio3d.detachSound(self.sounds["Attack"])
    def removeCollider(self):
        self.colliderNodePath.removeNode()

    def removeAI(self):
        pass
    def die(self):
        Monster.die(self)
        if len(self.bullets)==0:
            return
        for bullet in self.bullets:
            bullet.setExpires(-1)
class EletricTower(Monster):
    def __init__(self,pos,target):
        Monster.__init__(self,pos)
        self.MaxHP = defaultEletricTowerMaxHP
        self._HP = defaultEletricTowerHP
        self.attackPower = defaultEletricTowerAttackPower
        self.bullets=[]
        self.isAttack=False
        #加载模型
        self.typeStr = 'EletricTower'
        self.model = Actor(
            MonsterModelPath + "model_eletrictower"
            # {
            #     "Walk": MonsterModelPath + "slime_walk",
            #     "Attack": MonsterModelPath + "slime_attack",
            #     "Hit": MonsterModelPath + "slime_hit",
            #     "Die": MonsterModelPath + "slime_die"
            # }
        )
        self.model.reparentTo( base.render)
        self.model.setPos(self.position)
        self.model.setScale(defaultEletricTowerScale)
        self.lastPos=self.model.getPos()

        #主碰撞体
        self.colliderName = 'monster'
        characterColNode = CollisionNode("monster")
        characterColNode.addSolid(CollisionSphere(0,0,defaultEletricTowerColliderZ,defaultEletricTowerColliderRadius))
        characterColNode.setFromCollideMask( CollideMask.bit(DefaultMonsterMaskVal) )#0
        characterColNode.setIntoCollideMask(CollideMask.bit(defaultHeroInMonsterMaskVal))#2
        self.colliderNodePath = self.model.attachNewNode(characterColNode)
        self.colliderNodePath.setPythonTag("Monster",self)
        # # self.colliderNodePath.show()
        Monster.setMonster(characterColNode,self)
        base.cTrav.addCollider(self.colliderNodePath,base.cHandler)

        #音效
        self.sounds["Hit"] = base.audio3d.loadSfx(MonsterSoundPath + "EletricTowerGotHit.mp3")
        self.sounds["Attack"] = base.audio3d.loadSfx(MonsterSoundPath + "EletricTowerAttack.mp3")
        if not self.sounds["Attack"] is None:
            base.audio3d.attachSoundToObject(self.sounds["Attack"], self.model)
        if not self.sounds["Hit"] is None:
            base.audio3d.attachSoundToObject(self.sounds["Hit"], self.model)

        #AI
        self.initAI(base.AIworld,target)
    def initAI(self,AIworld,target):
        self.AIworld=AIworld
        self.target=target


    def updateAI(self):
        if not self.isAttack:
            self.attack()
            self.isAttack=True
        pass
    def underAttack(self,val):
        self.isUnderAttack=True
        self.model.play("Hit")
        if not self.sounds["Hit"] is None:
            self.sounds["Hit"].play()
        self.decreaseHP(val)

    def attack(self):
        r1=defaultEletricTowerBulletRadius1
        r2=defaultEletricTowerBulletRadius2
        r3=defaultEletricTowerBulletRadius3
        bullets=[]
        bullets.append(AroundPermanentBullet(self,0,self.attackPower, defaultEletricTowerAngleSpeed1 , defaultEletricTowerBulletSize1 ,r1,DefaultHeroMaskVal))
        bullets.append(AroundPermanentBullet(self,120,self.attackPower, defaultEletricTowerAngleSpeed1 , defaultEletricTowerBulletSize1 ,r1,DefaultHeroMaskVal))
        bullets.append(AroundPermanentBullet(self,240,self.attackPower, defaultEletricTowerAngleSpeed1 , defaultEletricTowerBulletSize1 ,r1,DefaultHeroMaskVal))

        bullets.append(AroundPermanentBullet(self,0,self.attackPower, defaultEletricTowerAngleSpeed2 , defaultEletricTowerBulletSize2 ,r2,DefaultHeroMaskVal))
        bullets.append(AroundPermanentBullet(self,90,self.attackPower, defaultEletricTowerAngleSpeed2 , defaultEletricTowerBulletSize2 ,r2,DefaultHeroMaskVal))
        bullets.append(AroundPermanentBullet(self,180,self.attackPower, defaultEletricTowerAngleSpeed2 , defaultEletricTowerBulletSize2 ,r2,DefaultHeroMaskVal))
        bullets.append(AroundPermanentBullet(self,270,self.attackPower, defaultEletricTowerAngleSpeed2 , defaultEletricTowerBulletSize2 ,r2,DefaultHeroMaskVal))

        bullets.append(AroundPermanentBullet(self,0,self.attackPower, defaultEletricTowerAngleSpeed3 , defaultEletricTowerBulletSize3 ,r3,DefaultHeroMaskVal))
        bullets.append(AroundPermanentBullet(self,72,self.attackPower, defaultEletricTowerAngleSpeed3 , defaultEletricTowerBulletSize3 ,r3,DefaultHeroMaskVal))
        bullets.append(AroundPermanentBullet(self,144,self.attackPower, defaultEletricTowerAngleSpeed3 , defaultEletricTowerBulletSize3 ,r3,DefaultHeroMaskVal))
        bullets.append(AroundPermanentBullet(self,216,self.attackPower, defaultEletricTowerAngleSpeed3 , defaultEletricTowerBulletSize3 ,r3,DefaultHeroMaskVal))
        bullets.append(AroundPermanentBullet(self,288,self.attackPower, defaultEletricTowerAngleSpeed3 , defaultEletricTowerBulletSize3 ,r3,DefaultHeroMaskVal))
        for bullet in bullets:
            base.messenger.send("bullet-create", [bullet])

        self.bullets=bullets

    def detachSound(self):
        base.audio3d.detachSound(self.sounds["Hit"])
        base.audio3d.detachSound(self.sounds["Attack"])
    def removeCollider(self):
        self.colliderNodePath.removeNode()

    def removeAI(self):
        pass
    def die(self):
        Monster.die(self)
        if len(self.bullets)==0:
            return
        for bullet in self.bullets:
            bullet.setExpires(-1)
class DrillRobot(Monster):#
    def __init__(self,pos,target):
        Monster.__init__(self,pos)
        self.MaxHP = defaultDrillRobotMaxHP
        self._HP = defaultDrillRobotHP
        self.attackPower = defaultDrillRobotAttackPower
        #加载模型
        self.typeStr = 'DrillRobot'
        self.model = Actor(
            MonsterModelPath + "model_drillrobot",
            {
                "Walk": MonsterModelPath + "model_drillrobot"
            #     "Attack": MonsterModelPath + "slime_attack",
            #     "Hit": MonsterModelPath + "slime_hit",
            #     "Die": MonsterModelPath + "slime_die"
            }
        )
        self.model.reparentTo( base.render)
        self.model.setPos(self.position)
        self.model.setScale(defaultDrillRobotScale)
        self.drillTime=-1

        #主碰撞体
        self.colliderName = 'monster'
        characterColNode = CollisionNode("monster")
        characterColNode.addSolid(CollisionSphere(0,0,defaultDrillRobotColliderZ,defaultDrillRobotColliderRadius))
        characterColNode.setFromCollideMask( CollideMask.bit(DefaultMonsterMaskVal) )#0
        characterColNode.setIntoCollideMask(CollideMask.bit(defaultHeroInMonsterMaskVal))#2
        Monster.setMonster(characterColNode,self)
        self.colliderNodePath = self.model.attachNewNode(characterColNode)
        self.colliderNodePath.setPythonTag("Monster",self)
        # self.colliderNodePath.show()
        base.cTrav.addCollider(self.colliderNodePath,base.cHandler)

        #音效
        self.sounds["Hit"] = base.audio3d.loadSfx(MonsterSoundPath + "DrillRobotGotHit.mp3")
        self.sounds["Drill"] = base.audio3d.loadSfx(MonsterSoundPath + "DrillRobotDrill.mp3")
        if not self.sounds["Hit"] is None:
            base.audio3d.attachSoundToObject(self.sounds["Hit"], self.model)
        if not self.sounds["Drill"] is None:
            base.audio3d.attachSoundToObject(self.sounds["Drill"], self.model)
        #AI
        self.initAI(base.AIworld,target)
    def initAI(self,AIworld,target):
        self.AIworld=AIworld
        self.target=target
        self.AI="wander"
        # self.model.setPlayRate(defaultSlimeWalkRate,'Walk')
        self.model.loop("Walk")

    def underAttack(self,val):
        self.isUnderAttack=True
        self.model.play("Hit")
        if not self.sounds["Hit"] is None:
            self.sounds["Hit"].play()
        self.decreaseHP(val)
        self.AI="pursue"


    def updateAI(self):
        if self.AI=="wander":
            if getDistance(self.model.getPos(),self.target.getPos())<defaultDrillRobotDetectRangeVal:
                self.AI="pursue"
        if self.AI=="pursue":
            if time.time()>self.drillTime:
                self.toDrill()

    def toDrill(self):
        if self.state!="alive":
            return
        self.drillTime=time.time()+defaultDrillRobotDrillTime
        self.model.loop("ToDrill")
        taskMgr.doMethodLater(defaultDrillRobotToDrillTime, self.drill,"name",[])

    def drill(self):
        if self.state!="alive":
            return
        self.sounds["Drill"].play()
        self.disappear()
        pos=self.target.getPos()
        taskMgr.doMethodLater(defaultDrillRobotDrillToAppearTime, self.appear,"name",[pos])

    def disappear(self):
        if self.state!="alive":
            return
        self.model.setZ(-20)
    def appear(self,pos):
        if self.state!="alive":
            return
        self.sounds["Drill"].play()
        self.model.setPos(pos)

    def detachSound(self):
        base.audio3d.detachSound(self.sounds["Hit"])
        base.audio3d.detachSound(self.sounds["Drill"])
    def removeCollider(self):
        if not self.colliderNodePath.isEmpty():
            self.colliderNodePath.removeNode()

    def removeAI(self):
        pass
class Mole(Monster):#地鼠
    def __init__(self,pos,target):
        Monster.__init__(self,pos)
        self.MaxHP = defaultMoleMaxHP
        self._HP = defaultMoleHP
        self.attackPower = defaultMoleAttackPower
        #加载模型
        self.typeStr = 'Mole'
        self.model = Actor(
            MonsterModelPath + "model_mole"
            # {
            #     "Walk": MonsterModelPath + "slime_walk",
            #     "Attack": MonsterModelPath + "slime_attack",
            #     "Hit": MonsterModelPath + "slime_hit",
            #     "Die": MonsterModelPath + "slime_die"
            # }
        )
        self.model.reparentTo( base.render)
        self.model.setPos(self.position)
        self.model.setScale(defaultMoleScale)
        self.drillTime=-1

        #主碰撞体
        self.colliderName = 'monster'
        characterColNode = CollisionNode("monster")
        characterColNode.addSolid(CollisionSphere(0,0,defaultMoleColliderZ,defaultMoleColliderRadius))
        characterColNode.setFromCollideMask( CollideMask.bit(DefaultMonsterMaskVal) )#0
        characterColNode.setIntoCollideMask(CollideMask.bit(defaultHeroInMonsterMaskVal))#2
        Monster.setMonster(characterColNode,self)
        self.colliderNodePath = self.model.attachNewNode(characterColNode)
        self.colliderNodePath.setPythonTag("Monster",self)
        # self.colliderNodePath.show()
        base.cTrav.addCollider(self.colliderNodePath,base.cHandler)

        #音效
        self.sounds["Hit"] = base.audio3d.loadSfx(MonsterSoundPath + "MoleGotHit.mp3")
        self.sounds["Drill"] = base.audio3d.loadSfx(MonsterSoundPath + "MoleDrill.mp3")
        if not self.sounds["Hit"] is None:
            base.audio3d.attachSoundToObject(self.sounds["Hit"], self.model)
        if not self.sounds["Drill"] is None:
            base.audio3d.attachSoundToObject(self.sounds["Drill"], self.model)
        #AI
        self.initAI(base.AIworld,target)
    def initAI(self,AIworld,target):
        self.AIworld=AIworld
        self.target=target
        self.AI="wander"
    def underAttack(self,val):
        self.isUnderAttack=True
        self.model.play("Hit")
        if not self.sounds["Hit"] is None:
            self.sounds["Hit"].play()
        self.decreaseHP(val)
        self.AI="pursue"


    def updateAI(self):
        if self.AI=="wander":
            if getDistance(self.model.getPos(),self.target.getPos())<defaultMoleDetectRangeVal:
                self.AI="pursue"
        if self.AI=="pursue":
            if time.time()>self.drillTime:
                self.toDrill()

    def toDrill(self):
        if self.state!="alive":
            return
        self.drillTime=time.time()+defaultMoleDrillTime
        self.model.loop("ToDrill")
        taskMgr.doMethodLater(defaultMoleToDrillTime, self.drill,"name",[])

    def drill(self):
        if self.state!="alive":
            return
        self.sounds["Drill"].play()
        self.disappear()
        pos=self.target.getPos()
        taskMgr.doMethodLater(defaultMoleDrillToAppearTime, self.appear,"name",[pos])

    def disappear(self):
        if self.state!="alive":
            return
        self.model.setZ(-20)
    def appear(self,pos):
        if self.state!="alive":
            return
        self.sounds["Drill"].play()
        self.model.setPos(pos)

    def detachSound(self):
        base.audio3d.detachSound(self.sounds["Hit"])
        base.audio3d.detachSound(self.sounds["Drill"])
    def removeCollider(self):
        if not self.colliderNodePath.isEmpty():
            self.colliderNodePath.removeNode()

    def removeAI(self):
        pass
class Caterpillar(Monster):#毛毛虫
    def __init__(self,pos,target):
        Monster.__init__(self,pos)
        self.MaxHP = defaultCaterpillarMaxHP
        self._HP = defaultCaterpillarHP
        self.attackPower = defaultCaterpillarAttackPower
        self.moveSpeed = defaultCaterpillarMoveSpeed
        #加载模型
        self.typeStr = 'Caterpillar'
        self.model = Actor(
            MonsterModelPath + "model_caterpillar",
            {
                "Walk": MonsterModelPath + "model_caterpillar"
            #     "Attack": MonsterModelPath + "slime_attack",
            #     "Hit": MonsterModelPath + "slime_hit",
            #     "Die": MonsterModelPath + "slime_die"
            }
        )
        self.model.reparentTo( base.render)
        self.model.setPos(self.position)
        self.model.setScale(defaultCaterpillarScale)
        self.lastPosStack=[self.model.getPos()]
        self.attackTime=-1
        #主碰撞体
        self.colliderName = 'monster'
        characterColNode = CollisionNode(self.colliderName)
        characterColNode.addSolid(CollisionSphere(0,defaultCaterpillarColliderY1,defaultCaterpillarColliderZ,defaultCaterpillarColliderRadius))
        characterColNode.addSolid(CollisionSphere(0,defaultCaterpillarColliderY2,defaultCaterpillarColliderZ,defaultCaterpillarColliderRadius))
        characterColNode.setFromCollideMask( CollideMask.bit(DefaultMonsterMaskVal) )#0
        characterColNode.setIntoCollideMask(CollideMask.bit(defaultHeroInMonsterMaskVal))#2
        Monster.setMonster(characterColNode,self)
        self.colliderNodePath = self.model.attachNewNode(characterColNode)
        self.colliderNodePath.setPythonTag("Monster",self)
        # self.colliderNodePath.show()


        base.cTrav.addCollider(self.colliderNodePath,base.cHandler)

        #怪物与墙壁碰撞
        self.wallHandler=CollisionHandlerQueue()
        wallCN=CollisionNode(self.colliderName)
        wallCN.addSolid(CollisionSphere(0,0,defaultCaterpillarColliderZ,defaultCaterpillarColliderRadius))
        wallCN.setFromCollideMask(CollideMask.bit(defaultMonsterInWallMaskVal)) #8
        wallCN.setIntoCollideMask(CollideMask.allOff())
        self.wallCNP=self.model.attachNewNode(wallCN)
        base.cTrav.addCollider(self.wallCNP,self.wallHandler)
        #音效
        self.sounds["Hit"] = base.audio3d.loadSfx(MonsterSoundPath + "CaterpillarGotHit.mp3")

        if not self.sounds["Hit"] is None:
            base.audio3d.attachSoundToObject(self.sounds["Hit"], self.model)

        #AI
        self.initAI(base.AIworld,target)
    def initAI(self,AIworld,target):
        self.AIworld=AIworld
        self.target=target
        #初始化为闲逛
        self.model.setPlayRate(defaultCaterpillarWalkRate,'Walk')
        AISetting.wander(self,defaultCaterpillarWanderSpeed,defaultCaterpillarWanderRange,100)
        self.model.loop("Walk")

    def updateAI(self):
        self.model.setH(self.model.getH()+180)
        if self.attackTime<time.time():
            self.genVenom()

        if hasattr(self,'AIworld'):
            entries = list( self.wallHandler.getEntries())
            if len(entries) > 0:
                if self.lastPosStack!=[]:
                    self.model.setPos(self.lastPosStack.pop())
                    AISetting.wander(self,defaultCaterpillarWanderSpeed,defaultCaterpillarWanderRange,random.randint(defaultRandomWanderActMinNum,defaultRandomWanderActMaxNum),False)
            else:
                self.lastPosStack.append(self.model.getPos())
    def underAttack(self,val):
        self.isUnderAttack=True
        self.model.play("Hit")
        if not self.sounds["Hit"] is None:
            self.sounds["Hit"].play()
        self.decreaseHP(val)
    def genVenom(self):
        self.attackTime=time.time()+defaultCaterpillarGenVenomTime
        bullet=TrapDurativeBullet(self.model.getPos()+(0,0,defaultCaterpillarVenomZ), time.time(), defaultCaterpillarVenomPower, defaultCaterpillarVenomSize, DefaultHeroMaskVal,defaultCaterpillarVenomLastTime,"bullet_ven.egg")
        base.messenger.send("bullet-create", [bullet])
    def detachSound(self):
        base.audio3d.detachSound(self.sounds["Hit"])
    def removeCollider(self):
        if not self.colliderNodePath.isEmpty():
            self.colliderNodePath.removeNode()
        if not self.wallCNP.isEmpty():
            self.wallCNP.removeNode()
    def removeAI(self):
        self.AIworld.removeAiChar(self.AIName)
class Train(Monster):
    def __init__(self,pos,target):
        Monster.__init__(self,pos)
        self.MaxHP = defaultTrainMaxHP
        self._HP = defaultTrainHP
        self.attackPower = defaultTrainAttackPower
        self.moveSpeed = defaultTrainMoveSpeed
        #加载模型
        self.typeStr = 'Train'
        self.model = Actor(
            MonsterModelPath + "model_train"
            # {
            #     "Walk": MonsterModelPath + "slime_walk",
            #     "Attack": MonsterModelPath + "slime_attack",
            #     "Hit": MonsterModelPath + "slime_hit",
            #     "Die": MonsterModelPath + "slime_die"
            # }
        )
        self.model.reparentTo( base.render)
        self.model.setPos(self.position)
        self.model.setScale(defaultTrainScale)
        self.lastPosStack=[self.model.getPos()]
        self.attackTime=-1
        #主碰撞体
        self.colliderName = 'monster'
        characterColNode = CollisionNode(self.colliderName)
        characterColNode.addSolid(CollisionSphere(0,0,defaultTrainColliderZ,defaultTrainColliderRadius))
        characterColNode.setFromCollideMask( CollideMask.bit(DefaultMonsterMaskVal) )#0
        characterColNode.setIntoCollideMask(CollideMask.bit(defaultHeroInMonsterMaskVal))#2
        Monster.setMonster(characterColNode,self)
        self.colliderNodePath = self.model.attachNewNode(characterColNode)
        self.colliderNodePath.setPythonTag("Monster",self)
        # self.colliderNodePath.show()


        base.cTrav.addCollider(self.colliderNodePath,base.cHandler)

        #怪物与墙壁碰撞
        self.wallHandler=CollisionHandlerQueue()
        wallCN=CollisionNode(self.colliderName)
        wallCN.addSolid(CollisionSphere(0,0,defaultTrainColliderZ,defaultTrainColliderRadius))
        wallCN.setFromCollideMask(CollideMask.bit(defaultMonsterInWallMaskVal)) #8
        wallCN.setIntoCollideMask(CollideMask.allOff())
        self.wallCNP=self.model.attachNewNode(wallCN)
        base.cTrav.addCollider(self.wallCNP,self.wallHandler)
        #音效
        self.sounds["Hit"] = base.audio3d.loadSfx(MonsterSoundPath + "TrainGotHit.mp3")

        if not self.sounds["Hit"] is None:
            base.audio3d.attachSoundToObject(self.sounds["Hit"], self.model)

        #AI
        self.initAI(base.AIworld,target)
    def initAI(self,AIworld,target):
        self.AIworld=AIworld
        self.target=target
        #初始化为闲逛
        AISetting.wander(self,defaultTrainWanderSpeed,defaultTrainWanderRange,100)
        self.model.loop("Walk")

    def updateAI(self):
        if self.attackTime<time.time():
            self.genVenom()

        if hasattr(self,'AIworld'):
            entries = list( self.wallHandler.getEntries())
            if len(entries) > 0:
                if self.lastPosStack!=[]:
                    self.model.setPos(self.lastPosStack.pop())
                    AISetting.wander(self,defaultTrainWanderSpeed,defaultTrainWanderRange,random.randint(defaultRandomWanderActMinNum,defaultRandomWanderActMaxNum),False)
            else:
                self.lastPosStack.append(self.model.getPos())
    def underAttack(self,val):
        self.isUnderAttack=True
        self.model.play("Hit")
        if not self.sounds["Hit"] is None:
            self.sounds["Hit"].play()
        self.decreaseHP(val)
    def genVenom(self):
        self.attackTime=time.time()+defaultTrainGenVenomTime
        bullet=TrapDurativeBullet(self.model.getPos()+(0,0,defaultTrainVenomZ), time.time(),defaultTrainVenomPower, defaultTrainVenomSize, DefaultHeroMaskVal,defaultTrainVenomLastTime,"bullet_ven2")
        base.messenger.send("bullet-create", [bullet])
    def detachSound(self):
        base.audio3d.detachSound(self.sounds["Hit"])
    def removeCollider(self):
        if not self.colliderNodePath.isEmpty():
            self.colliderNodePath.removeNode()
        if not self.wallCNP.isEmpty():
            self.wallCNP.removeNode()
    def removeAI(self):
        self.AIworld.removeAiChar(self.AIName)
class Minotaur(Monster):
    def __init__(self,pos,target):
        Monster.__init__(self,pos)

        self.MaxHP = defaultMinotaurMaxHP
        self._HP = defaultMinotaurHP
        self.attackPower = defaultMinotaurAttackPower
        self.moveSpeed = defaultMinotaurMoveSpeed
        self.isSendBlood=False

        #加载模型
        self.typeStr = 'Minotaur'
        self.loadModel()
        self.model.reparentTo( base.render)
        self.model.setPos(self.position)
        self.model.setScale(defaultMinotaurScale)
        self.lastPos=self.model.getPos()
        self.attackTime=-1
        self.invincible=False
        self.skillAI="none"
        self.dashTime=-1

        self.isBoss=True


        #主碰撞体
        self.colliderName = 'monster'
        characterColNode = CollisionNode("monster")
        characterColNode.addSolid(CollisionSphere(0,0,defaultMinotaurColliderZ,defaultMinotaurColliderRadius))
        characterColNode.setFromCollideMask( CollideMask.bit(DefaultMonsterMaskVal) )#0
        characterColNode.setIntoCollideMask(CollideMask.bit(defaultHeroInMonsterMaskVal))#2
        Monster.setMonster(characterColNode,self)
        self.colliderNodePath = self.model.attachNewNode(characterColNode)
        self.colliderNodePath.setPythonTag("Monster",self)
        #self.colliderNodePath.show()
        base.cTrav.addCollider(self.colliderNodePath,base.cHandler)

        # #怪物与墙壁碰撞
        # self.wallHandler=CollisionHandlerQueue()
        # wallCN=CollisionNode(self.colliderName)
        # wallCN.addSolid(CollisionSphere(0,0,defaultMinotaurColliderZ,defaultMinotaurColliderRadius))
        # wallCN.setFromCollideMask(CollideMask.bit(defaultMonsterInWallMaskVal)) #8
        # wallCN.setIntoCollideMask(CollideMask.allOff())
        # self.wallCNP=self.model.attachNewNode(wallCN)
        # base.cTrav.addCollider(self.wallCNP,self.wallHandler)
        #音效
        self.sounds["Hit"] = base.audio3d.loadSfx(MonsterSoundPath + "MinotaurGotHit.mp3")
        self.sounds["Prepare"] = base.audio3d.loadSfx(MonsterSoundPath + "MinotaurPrepare.mp3")
        if not self.sounds["Hit"] is None:
            base.audio3d.attachSoundToObject(self.sounds["Hit"], self.model)
        if not self.sounds["Prepare"] is None:
            base.audio3d.attachSoundToObject(self.sounds["Prepare"], self.model)
        #AI
        self.initAI(base.AIworld,target)

    def loadModel(self):
        try:
            self.model = Actor(
                MonsterModelPath + "model_minotaur",
                {
                    "Walk": MonsterModelPath + "model_minotaur",
                    "Charge": MonsterModelPath + "anim_FirstBoss_charge"
                #     "Hit": MonsterModelPath + "slime_hit",
                #     "Die": MonsterModelPath + "slime_die"
                }
            )
        except BaseException as e:
            logging.debug("loadModel error: {}".format(traceback.format_exc()))
            HeroModelPath = "Model/Hero/"
            self.model = Actor(
                HeroModelPath + "model_mainChara", {
                   "Walk": HeroModelPath + "anim_mainChara_running_attack",
                   #"Attack": HeroModelPath + "anim_mainChara_standing",
                   "Charge": HeroModelPath + "anim_mainChara_standing"
                }
            )
    def initAI(self,AIworld,target):
        self.AIworld=AIworld
        self.target=target

        AISetting.pursue(self,self.moveSpeed,self.target)
        self.model.setPlayRate(defaultMinotaurWalkRate,'Walk')
        self.model.setPlayRate(defaultMinotaurChargeRate,'Charge')
        self.model.loop("Walk")


    def underAttack(self,val):
        print 'underAttack'
        # if self.invincible:
        #     return
        self.isUnderAttack=True
        self.model.play("Hit")
        if not self.sounds["Hit"] is None:
            self.sounds["Hit"].play()
        self.decreaseHP(val)

    def updateAI(self):
        if not self.isSendBlood:
            base.messenger.send("monster-maxHPChange",[self.MaxHP])
            base.messenger.send("monster-HPChange",[self.HP])
            self.isSendBlood=True

        if self.attackTime<time.time():
            self.useSkill()

        if self.skillAI=="dash":
            if self.dashTime<time.time() or getDistance(self.model.getPos(),self.dashTarget.model.getPos())<1:
                AISetting.pursue(self,defaultMinotaurPursueSpeed,self.target,False)
                self.skillAI="none"

        # if hasattr(self,'AIworld'):
        #     entries = list( self.wallHandler.getEntries())
        #     if len(entries) > 0:

        #         self.model.setPos(self.lastPos)
        #     else:
        #         self.lastPos=self.model.getPos()
    def useSkill(self):
        self.attackTime=time.time()+defaultMinotaurSkillTime
        skill=random.randint(1,3)

        self.model.loop("Charge")
        if skill==1:
            self.dash()
        elif skill==2:
            self.summon()
        elif skill==3:
            self.fire()

    def dash(self):
        if self.state!="alive":
            return
        self.invincible=True
        self.model.loop("Prepare")
        AISetting.stop(self)
        pos=self.target.getPos()
        taskMgr.doMethodLater(defaultMinotaurToDashTime, self.dash2,"name",[pos])
    def dash2(self,pos):
        if self.state!="alive":
            return
        self.skillAI="dash"
        self.model.loop("Walk")
        self.dashTime=time.time()+defaultMinotaurDashTime
        self.invincible=False
        self.dashTarget=TrapBullet(pos, time.time(), self.attackPower, 0.01, uselessMaskVal,defaultMinotaurDashTime+0.5)
        base.messenger.send("bullet-create", [self.dashTarget])
        AISetting.pursue(self,defaultMinotaurDashSpeed,self.dashTarget.model)
    def summon(self):
        if self.state!="alive":
            return
        self.invincible=True
        self.model.loop("Prepare")
        AISetting.stop(self)
        taskMgr.doMethodLater(defaultMinotaurToSummonTime, self.summon2,"name",[])
    def summon2(self):
        if self.state!="alive":
            return
        self.model.loop("Walk")
        self.invincible=False
        newPos=self.model.getPos()
        monsterStrs=['Slime','BigSlime','Bat','Skull','Caterpillar','Mole']


        monster1=MonsterFactory.create(monsterStrs[random.randint(0,len(monsterStrs)-1)],newPos+(defaultMinotaurSummonRange,0,0),self.target)
        monster2=MonsterFactory.create(monsterStrs[random.randint(0,len(monsterStrs)-1)],newPos+(-defaultMinotaurSummonRange,0,0),self.target)
        monster3=MonsterFactory.create(monsterStrs[random.randint(0,len(monsterStrs)-1)],newPos+(0,defaultMinotaurSummonRange,0),self.target)
        # AISetting.pursue(smallSlime1,defaultSlimePursueSpeed,self.target)
        # AISetting.pursue(smallSlime2,defaultSlimePursueSpeed,self.target)
        # AISetting.pursue(smallSlime3,defaultSlimePursueSpeed,self.target)

        base.messenger.send("monster-create",[[monster1,monster2,monster3]])
        AISetting.pursue(self,defaultMinotaurPursueSpeed,self.target)
    def fire(self):
        if self.state!="alive":
            return
        self.invincible=True
        self.model.loop("Prepare")
        AISetting.stop(self)
        taskMgr.doMethodLater(defaultMinotaurToFireTime, self.fire2,"name",[])
    def fire2(self):
        # if self.state!="alive":
        #     return
        # self.skillAI="fire"
        # self.invincible=False
        # self.model.loop("Walk")
        if PARTICLE:
            base.enableParticles()
            # 火焰
            self.particle_fire2 = ParticleEffect()
            self.particle_fire2.loadConfig('assets/particles/fireish.ptf')
            self.particle_fire2.setPos(self.model.getPos())
            self.particle_fire2.setZ(4)
            self.particle_fire2.setH(self.model.getH()-90)
            self.particle_fire2.setP(90)
            self.particle_fire2.setScale(defaultParticleScale*2,defaultParticleScale,defaultParticleScale*3)

        bullet=SectorBullet(self,time.time(),defaultMinotaurFirePower, defaultMinotaurFireRange, defaultMinotaurFireAngle, DefaultHeroMaskVal,defaultMinotaurFireTime)
        # bullet.model.hide()
        base.messenger.send("bullet-create", [bullet])

        Sequence(
                Func(self.particle_fire2.start,render),
                Wait(defaultMinotaurFireTime+0.2),
                Func(self.particle_fire2.cleanup),
                Func(self.fire3),
                ).start()

        # taskMgr.doMethodLater(defaultMinotaurFireTime+0.2, self.fire3,"name",[])
    def fire3(self):
        if self.state!="alive":
            return
        AISetting.pursue(self,self.moveSpeed,self.target)

    def detachSound(self):
        base.audio3d.detachSound(self.sounds["Hit"])
        base.audio3d.detachSound(self.sounds["Prepare"])
    def removeCollider(self):
        if not self.colliderNodePath.isEmpty():
            self.colliderNodePath.removeNode()

    def removeAI(self):
        self.AIworld.removeAiChar(self.AIName)
class MechanicalSpider(Monster):
    def __init__(self,pos,target):
        Monster.__init__(self,pos)
        self.MaxHP = defaultMechanicalSpiderMaxHP
        self._HP = defaultMechanicalSpiderHP
        self.attackPower = defaultMechanicalSpiderAttackPower
        self.moveSpeed = defaultMechanicalSpiderMoveSpeed
        base.messenger.send("monster-maxHPChange",[self.MaxHP])
        base.messenger.send("monster-HPChange",[self.HP])
        #加载模型
        self.typeStr = 'MechanicalSpider'
        self.loadModel()
        self.model.reparentTo( base.render)
        self.model.setPos(self.position)
        self.model.setScale(defaultMechanicalSpiderScale)
        self.lastPos=self.model.getPos()
        self.attackTime=-1
        self.invincible=False
        self.skillAI="none"
        self.isSendBlood=False
        self.isBoss=True


        self.recoveryTime=-1
        self.shootTime=-1
        #主碰撞体
        self.colliderName = 'monster'
        characterColNode = CollisionNode("monster")
        characterColNode.addSolid(CollisionSphere(0,0,defaultMechanicalSpiderColliderZ,defaultMechanicalSpiderColliderRadius))
        characterColNode.setFromCollideMask( CollideMask.bit(DefaultMonsterMaskVal) )#0
        characterColNode.setIntoCollideMask(CollideMask.bit(defaultHeroInMonsterMaskVal))#2
        Monster.setMonster(characterColNode,self)
        self.colliderNodePath = self.model.attachNewNode(characterColNode)
        self.colliderNodePath.setPythonTag("Monster",self)
        # self.colliderNodePath.show()
        base.cTrav.addCollider(self.colliderNodePath,base.cHandler)

        # #怪物与墙壁碰撞
        # self.wallHandler=CollisionHandlerQueue()
        # wallCN=CollisionNode(self.colliderName)
        # wallCN.addSolid(CollisionSphere(0,0,defaultMechanicalSpiderColliderZ,defaultMechanicalSpiderColliderRadius))
        # wallCN.setFromCollideMask(CollideMask.bit(defaultMonsterInWallMaskVal)) #8
        # wallCN.setIntoCollideMask(CollideMask.allOff())
        # self.wallCNP=self.model.attachNewNode(wallCN)
        # base.cTrav.addCollider(self.wallCNP,self.wallHandler)
        #音效
        self.sounds["Hit"] = base.audio3d.loadSfx(MonsterSoundPath + "MechanicalSpiderGotHit.mp3")
        self.sounds["Prepare"] = base.audio3d.loadSfx(MonsterSoundPath + "MechanicalSpiderPrepare.mp3")
        if not self.sounds["Hit"] is None:
            base.audio3d.attachSoundToObject(self.sounds["Hit"], self.model)
        if not self.sounds["Prepare"] is None:
            base.audio3d.attachSoundToObject(self.sounds["Prepare"], self.model)
        #AI
        self.initAI(base.AIworld,target)
    def loadModel(self):
        try:
            self.model = Actor(
                MonsterModelPath + "model_mechanicalspider",
                {
                    "Walk": MonsterModelPath + "model_mechanicalspider",
                    "Charge": MonsterModelPath + "anim_SecondBoss_charge",
                    "Recovery": MonsterModelPath + "anim_SecondBoss_HP"
                #     "Die": MonsterModelPath + "slime_die"
                }
            )
        except BaseException as e:
            logging.debug("loadModel error: {}".format(traceback.format_exc()))
            HeroModelPath = "Model/Hero/"
            self.model = Actor(
                HeroModelPath + "model_mainChara", {
                   "Walk": HeroModelPath + "anim_mainChara_running_attack",
                   #"Attack": HeroModelPath + "anim_mainChara_standing",
                   "Charge": HeroModelPath + "anim_mainChara_standing",
                   "Recovery":HeroModelPath + "anim_mainChara_standing",
                }
            )
    def initAI(self,AIworld,target):
        self.AIworld=AIworld
        self.target=target
        self.model.setPlayRate(defaultMechanicalSpiderWalkRate,'Walk')
        self.model.setPlayRate(defaultMechanicalSpiderChargeRate,'Charge')
        self.model.setPlayRate(defaultMechanicalSpiderRecoveryRate,'Recovery')
        AISetting.pursue(self,self.moveSpeed,self.target)

        self.model.loop("Walk")

    def underAttack(self,val):
        if self.invincible:
            return
        self.isUnderAttack=True
        self.model.play("Hit")
        if not self.sounds["Hit"] is None:
            self.sounds["Hit"].play()
        self.decreaseHP(val)

    def updateAI(self):
        if not self.isSendBlood:
            base.messenger.send("monster-maxHPChange",[self.MaxHP])
            base.messenger.send("monster-HPChange",[self.HP])
            self.isSendBlood=True
        if self.attackTime<time.time() and self.skillAI=="none":
            self.useSkill()
        if self.skillAI=="fall":
            dt = base.globalClock.getDt()
            self.model.setZ(self.model.getZ()+dt*defaultMechanicalSpiderFlySpeed)
        if self.skillAI=="recovery":
            if self.recoveryTime<time.time():
                self.increaseHP(defaultMechanicalSpiderRecoveryHp)
                self.recoveryTime=time.time()+defaultMechanicalSpiderRecoveryTime
            if self.weakpoint1.state=="die" and self.weakpoint2.state=="die" and self.weakpoint3.state=="die":
                self.recovery3()
        if self.skillAI=="shoot":
            if self.shootTime<time.time():
                self.shootTime=time.time()+defaultMechanicalSpiderShootTime
                for x in xrange(1,4):
                    angle=random.randint(1,360)
                    bullet=SphereBullet(self.model.getPos()+(0,0,1), time.time(), angle,DefaultHeroMaskVal,defaultMechanicalSpiderShootPower,defaultMechanicalSpiderShootSize,defaultMechanicalSpiderShootSpeed, DefaultRangeVal,"bullet_monster.egg")
                    base.messenger.send("bullet-create", [bullet])



        # if self.skillAI=="none" and hasattr(self,'AIworld'):
        #     entries = list( self.wallHandler.getEntries())
        #     if len(entries) > 0:

        #         self.model.setPos(self.lastPos)
        #     else:
        #         self.lastPos=self.model.getPos()
    def useSkill(self):
        self.attackTime=time.time()+defaultMechanicalSpiderSkillTime
        skill=random.randint(1,3)
        self.model.loop("Charge")
        # skill=1
        if skill==1:
            self.fall()
        elif skill==2:
            self.shoot()
        elif skill==3:
            self.recovery()
    def fall(self):
        if self.state!="alive":
            return
        self.invincible=True
        self.model.loop("Prepare")
        AISetting.stop(self)
        pos=self.target.getPos()
        taskMgr.doMethodLater(defaultMechanicalSpiderToFlyTime, self.fall2,"name",[pos])
    def fall2(self,pos):
        if self.state!="alive":
            return
        self.invincible=False
        self.skillAI="fall"


        taskMgr.doMethodLater(defaultMechanicalSpiderFlyTime, self.fall3,"name",[pos])
    def fall3(self,pos):
        if self.state!="alive":
            return
        self.skillAI="none"
        self.model.loop("Walk")
        self.model.setPos(pos)
        self.lastPos=pos
        AISetting.pursue(self,defaultMechanicalSpiderPursueSpeed,self.target)
        bullet=TrapBullet(self.model.getPos()+(0,0,defaultMechanicalSpiderFlyAttackZ), time.time(),defaultMechanicalSpiderFlyAttackPower, defaultMechanicalSpiderFlyAttackRange, DefaultHeroMaskVal,defaultMechanicalSpiderFlyAttackTime)
        base.messenger.send("bullet-create", [bullet])

    def shoot(self):
        if self.state!="alive":
            return
        self.invincible=True
        self.model.loop("Prepare")
        AISetting.stop(self)
        pos=self.target.getPos()
        taskMgr.doMethodLater(defaultMechanicalSpiderToShootTime, self.shoot2,"name",[])
    def shoot2(self):
        if self.state!="alive":
            return
        self.skillAI="shoot"
        taskMgr.doMethodLater(defaultMechanicalSpiderShootLastTime, self.shoot3,"name",[])
    def shoot3(self):
        if self.state!="alive":
            return
        self.model.loop("Walk")
        self.skillAI="none"
        self.invincible=False
        AISetting.pursue(self,defaultMechanicalSpiderPursueSpeed,self.target)

    def recovery(self):
        if self.state!="alive":
            return
        self.invincible=True
        self.model.loop("Prepare")
        AISetting.stop(self)
        pos=self.target.getPos()
        taskMgr.doMethodLater(defaultMechanicalSpiderToRecoveryTime, self.recovery2,"name",[])
    def recovery2(self):
        if self.state!="alive":
            return
        self.skillAI="recovery"
        self.model.loop("Recovery")
        r=defaultMechanicalSpiderRecoveryWeakPointRadius

        angle=random.randint(1,360)
        angle=1.0*angle/180*math.pi
        pos=self.model.getPos()+(math.sin(angle)*r,math.cos(angle)*r,0)
        self.weakpoint1=WeakPoint(pos,self.target)

        angle=random.randint(1,360)
        angle=1.0*angle/180*math.pi
        pos=self.model.getPos()+(math.sin(angle)*r,math.cos(angle)*r,0)
        self.weakpoint2=WeakPoint(pos,self.target)

        angle=random.randint(1,360)
        angle=1.0*angle/180*math.pi
        pos=self.model.getPos()+(math.sin(angle)*r,math.cos(angle)*r,0)
        self.weakpoint3=WeakPoint(pos,self.target)

        base.messenger.send("monster-create",[[self.weakpoint1,self.weakpoint2,self.weakpoint3]])

        newPos=self.model.getPos()
        monsterStrs=['Robot','BigRobot','FlyingRobot','MechanicalHead','Train','DrillRobot']


        monster1=MonsterFactory.create(monsterStrs[random.randint(0,len(monsterStrs)-1)],newPos+(defaultMinotaurSummonRange,0,0),self.target)
        monster2=MonsterFactory.create(monsterStrs[random.randint(0,len(monsterStrs)-1)],newPos+(-defaultMinotaurSummonRange,0,0),self.target)
        monster3=MonsterFactory.create(monsterStrs[random.randint(0,len(monsterStrs)-1)],newPos+(0,defaultMinotaurSummonRange,0),self.target)


        base.messenger.send("monster-create",[[monster1,monster2,monster3]])

    def recovery3(self):
        if self.state!="alive":
            return
        self.model.loop("Walk")
        self.invincible=False
        AISetting.pursue(self,defaultMechanicalSpiderPursueSpeed,self.target)
        self.skillAI="none"


    def detachSound(self):
        base.audio3d.detachSound(self.sounds["Hit"])
        base.audio3d.detachSound(self.sounds["Prepare"])
    def removeCollider(self):
        if not self.colliderNodePath.isEmpty():
            self.colliderNodePath.removeNode()

    def removeAI(self):
        self.AIworld.removeAiChar(self.AIName)
class WeakPoint(Monster):
    def __init__(self,pos,target):
        Monster.__init__(self,pos)
        self.MaxHP = 100
        self._HP = 100
        self.attackPower = 0

        #加载模型
        self.typeStr = 'WeakPoint'
        self.model = Actor(
            MonsterModelPath + "model_weakpoint"
            # {
            #     "Walk": MonsterModelPath + "slime_walk",
            #     "Attack": MonsterModelPath + "slime_attack",
            #     "Hit": MonsterModelPath + "slime_hit",
            #     "Die": MonsterModelPath + "slime_die"
            # }
        )
        self.model.reparentTo( base.render)
        self.model.setPos(self.position+(0,0,defaultWeakPointModelZ))
        self.model.setScale(defaultWeakPointScale)
        self.lastPos=self.model.getPos()
        #主碰撞体
        self.colliderName = 'monster'
        characterColNode = CollisionNode("monster")
        characterColNode.addSolid(CollisionSphere(0,0,defaultWeakPointColliderZ,defaultWeakPointColliderRadius))
        characterColNode.setFromCollideMask( CollideMask.bit(DefaultMonsterMaskVal) )#0
        characterColNode.setIntoCollideMask(CollideMask.bit(defaultHeroInMonsterMaskVal))#2
        Monster.setMonster(characterColNode,self)
        self.colliderNodePath = self.model.attachNewNode(characterColNode)
        self.colliderNodePath.setPythonTag("Monster",self)
        # self.colliderNodePath.show()
        base.cTrav.addCollider(self.colliderNodePath,base.cHandler)

        #音效
        self.sounds["Hit"] = base.audio3d.loadSfx(MonsterSoundPath + "WeakPointGotHit.mp3")

        if not self.sounds["Hit"] is None:
            base.audio3d.attachSoundToObject(self.sounds["Hit"], self.model)

        #AI
        self.initAI(base.AIworld,target)
    def initAI(self,AIworld,target):
        self.AIworld=AIworld
        self.target=target

    def underAttack(self,val):
        self.model.play("Hit")
        if not self.sounds["Hit"] is None:
            self.sounds["Hit"].play()
        self.decreaseHP(100000)
    def die(self):

        self.state="todie"
        self.ignoreAll()

        taskMgr.doMethodLater(0, self.setDie,"name",[])

    def updateAI(self):
        pass
    def detachSound(self):
        base.audio3d.detachSound(self.sounds["Hit"])
    def removeCollider(self):
        if not self.colliderNodePath.isEmpty():
            self.colliderNodePath.removeNode()

    def removeAI(self):
        pass

class AISetting (object):
    @staticmethod
    def wander(monster,speed,rang,act=5,flag=True):#闲逛：怪物，速度，范围
        if monster.AI=="wander" and flag:
            return
        if not monster.AIName is None:
            monster.removeAI()
        monster.AI="wander"
        monster.AIName='%d'%Monster.AINum
        Monster.AINum=Monster.AINum+1
        monster.AIchar = AICharacter(monster.AIName,monster.model, 100, 0.05, speed)
        monster.AIworld.addAiChar(monster.AIchar)
        monster.AIbehaviors = monster.AIchar.getAiBehaviors()
        monster.AIbehaviors.wander(act, 0, rang, 1.0)
    @staticmethod
    def pursue(monster,speed,target,flag=True):#追逐：怪物，速度，目标
        if monster.AI=="pursue" and flag:
            return
        if not monster.AIName is None:
            monster.removeAI()
        monster.AI="pursue"
        monster.AIName='%d'%Monster.AINum
        Monster.AINum=Monster.AINum+1
        monster.AIchar = AICharacter(monster.AIName,monster.model, 100, 0.05, speed)
        monster.AIworld.addAiChar(monster.AIchar)
        monster.AIbehaviors = monster.AIchar.getAiBehaviors()
        monster.AIbehaviors.pursue(target)
    @staticmethod
    def flee(monster,speed,target,panicDis,relaxDis,flag=True):#追逐：怪物，速度，目标,恐慌距离，脱离距离
        if monster.AI=="flee" and flag:
            return
        if not monster.AIName is None:
            monster.removeAI()
        monster.AI="flee"
        monster.AIName='%d'%Monster.AINum
        Monster.AINum=Monster.AINum+1
        monster.AIchar = AICharacter(monster.AIName,monster.model, 100, 0.05, speed)
        monster.AIworld.addAiChar(monster.AIchar)
        monster.AIbehaviors = monster.AIchar.getAiBehaviors()
        monster.AIbehaviors.flee(target,panicDis,relaxDis)
    @staticmethod
    def stop(monster):#移除AI
        if monster.AI=="stop":
            return
        if not monster.AIName is None:
            monster.removeAI()
        monster.AI="stop"

def getDistance(pos1,pos2):
    if abs(pos1.getZ()-pos2.getZ())>15:
        return 100000
    a=math.pow(pos1.getX()-pos2.getX(),2)
    b=math.pow(pos1.getY()-pos2.getY(),2)
    c=math.sqrt(a+b)
    return c