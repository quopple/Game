#coding:utf-8
from panda3d.core import *
from direct.particles.ParticleEffect import ParticleEffect
import math
import time
from DefaultConfigVal import*
from MovableObject import MovableObject
from VideoHelper import *

bulletModelPath = 'Model/Bullet/'

class BulletFactory(object):
    @staticmethod
    def getBullet(dict,hero):
        if dict['class'] == "SphereBullet":
            if hero.attackMode == "Shotgun":
                hero.sounds["Attack"] = loader.loadSfx("Audio/shotgun.wav")
                # 用于替换的攻击函数
                def attack(taskTime):
                    # 是否过了攻击冷却期
                    currTime = time.time()
                    split = currTime - hero.lastAttackTime
                    if standarHitRate * 1.0 / hero.attackSpeed > split:
                        return

                    hero.lastAttackTime = currTime

                    # 播放攻击动画
                    hero.model.play("Attack")
                    # 播放攻击音效
                    hero.sounds["Attack"].play()

                    angle = hero.angle
                    # 子弹位置
                    pos = hero.model.getPos()
                    bullet1 = hero.bullet.copy()
                    bullet1.model.reparentTo(render)
                    bullet1.setPos(pos)
                    bullet1.setZ(2)  # bullet.getZ() +
                    # 子弹生命周期（消亡的时间）
                    bullet1.setExpires(currTime + bullet1.bulletLife)  # bullet.bulletLife
                    # 子弹飞行方向
                    angle1 = angle * math.pi / 180.0
                    bullet1.setAngle(angle1)
                    # 子弹伤害值 （ 子弹本身伤害值 + 英雄攻击力 ）
                    bullet1.damage += hero.attackPower
                    bullet1.model.show()
                    # 注册子弹
                    base.messenger.send("bullet-create", [bullet1])

                    bullet2 = bullet1.copy()
                    bullet2.model.reparentTo(render)
                    angle2 = (angle + defaultFlection) * math.pi / 180.0
                    bullet2.setAngle(angle2)
                    bullet2.model.show()
                    base.messenger.send("bullet-create", [bullet2])

                    bullet3 = bullet1.copy()
                    angle3 = (angle - defaultFlection) * math.pi / 180.0
                    bullet3.setAngle(angle3)
                    bullet3.model.reparentTo(base.render)
                    bullet3.model.show()
                    base.messenger.send("bullet-create", [bullet3])

                # 更改英雄的攻击方式
                hero.attack = attack
            return SphereBullet.ToBullet(dict)
        elif dict['class'] == "TubeSingleBullet":
            return TubeSingleBullet.ToBullet(dict,hero)
        elif dict['class'] == "TrapBullet":
            return TrapBullet.ToBullet(dict)
        elif dict['class'] == "TrapDurativeBullet":
            return TrapDurativeBullet.ToBullet(dict)
        elif dict['class'] == "AroundDurativeBullet":
            return AroundDurativeBullet.ToBullet(dict)

class Bullet(MovableObject):
    @staticmethod
    def setBullet(nodepath,bullet):
        nodepath.setPythonTag("bullet",bullet)
    @staticmethod
    def getBulltet(nodepath):
        return nodepath.getPythonTag("bullet")

    @staticmethod
    def getHero(nodepath):
        return nodepath.getPythonTag("Hero")
    @staticmethod
    def getMonster(nodepath):
        return nodepath.getPythonTag("Monster")

    @staticmethod
    def onCollision(entry):
        nodepath=entry.getIntoNodePath()
        bullet=Bullet.getBulltet(nodepath)
        bullet.action(entry)

    @staticmethod
    def ToDict(bullet):
        dict = {}
        dict["intoMask"] = bullet.intoMask
        dict["damage"] = bullet.damage
        dict["range"] = bullet.range
        dict["volume"] = bullet.volume
        dict["bulletLife"] = bullet.bulletLife

        return dict

    @staticmethod
    def ToBullet(obj,dict):
        obj.model.hide()
        obj.setIntoMask(dict["intoMask"])
        obj.damage = dict["damage"]
        obj.range = dict["range"]
        obj.setVolume(dict["volume"] )
        obj.bulletLife = dict["bulletLife"]



    def __init__(self):
        super(Bullet,self).__init__()
        self.intoMask = 0
        self.damage = 1
        self.model = None
        self.range = 1
        self.volume = 1
        self.bulletLife = 1
        self.sounds["hit"] = loader.loadSfx("Audio/gotHit.wav")

    def copy(self,obj):
         obj.intoMask = self.intoMask
         obj.damage =   self.damage
         obj.range  =   self.range
         obj.setVolume (self.volume)
         obj.bulletLift = self.bulletLife

    def update(self):
        return

    def remove(self):
        if not self.model.isEmpty():
            self.model.removeNode()

    def action(self, entry):

        return

    def setPos(self, pos):
        self.position = pos
        self.model.setPos(pos)

    def setZ(self, z):
        self.position[2] = z
        self.model.setZ(z)

    def setExpires(self, t):
        self.expires = t

    def setAngle(self, angle):
        self.model.setH(angle+180)
        angle = angle*math.pi/180.0
        self.angle = angle

    def setVolume(self, volume):
        self.volume = volume
        if self.model:
          self.model.setScale(volume)

    def setIntoMask(self,mask):
        pass
        #self.intoMask = mask
        #self.colliderNodePath = NodePath()
        #self.colliderNodePath.setIntoCollideMask(CollideMask.bit(mask) )
    def setRange(self,range):
        self.range = range
        pass

class SphereBullet(Bullet):
    @staticmethod
    def ToDict(bullet):
        dict = Bullet.ToDict(bullet)
        dict["class"] = "SphereBullet"
        dict["angle"] = bullet.angle
        dict["speed"] = bullet.speed

        return dict

    @staticmethod
    def ToBullet(dict):
        obj = SphereBullet()
        Bullet.ToBullet(obj,dict)
        obj.angle = dict["angle"]
        obj.speed = dict["speed"]

        return obj

    def copy(self):
        obj = SphereBullet( pos = self.position,angle = self.angle,intoMask = self.intoMask,speed = self.speed)
        super(SphereBullet,self).copy(obj)
        obj.expires = self.expires

        return obj

    def __init__(self,pos = LVecBase3f(0,0,-40), time=0, angle=DefaultAngleVal,intoMask=DefaultMonsterMaskVal, damage=DefaultDamageVal,  size=DefaultSizeVal, speed=DefaultSpeedVal, range=DefaultRangeVal,modelPath="SphereBullet"):
        Bullet.__init__(self)
        angle=angle*math.pi/180
        self.intoMask=intoMask
        self.damage=damage
        self.angle=angle
        self.volume=size
        self.speed=speed
        self.range=range
        self.bulletLife = range / speed
        self.expires=time+self.bulletLife
        self.position = pos

        nodepath=render.attachNewNode("bullet")
        self.model=nodepath
        nodepath.setPos(pos)
        # nodepath.setZ(nodepath,0.5)
        model=loader.loadModel(bulletModelPath+modelPath)
        model.setScale(self.volume)
        model.reparentTo(nodepath)
        col=CollisionNode("bullet")
        self.colliderNodePath = self.colliderNodePath = nodepath.attachNewNode(col)
        col.addSolid(CollisionSphere(0,0,0,self.volume))
        col.setIntoCollideMask(CollideMask.bit(self.intoMask))

        Bullet.setBullet(col,self)

    def update(self,time):
        if self.model is None:
            return
        if self.expires<=time:
            self.expires = -1
            self.remove()
            return
        self.model.setX(self.model.getX()+self.speed*math.sin(self.angle))
        self.model.setY(self.model.getY()+(-self.speed)*math.cos(self.angle))

    def action(self,entry):
        if self.model is None:
            return
        self.expires=-1
        nodepath=entry.getFromNodePath()
        obj=self.getMonster(nodepath)
        if obj is None:
            obj=self.getHero(nodepath)
        if obj is None:
            return
        obj.underAttack(self.damage)

        self.particle = ParticleEffect()
        self.particle.loadConfig( "assets/particles/BloodSplat.ptf")
        self.particle.start(render)
        self.particle.setPos(obj.model.getPos())
        self.particle.setH(self.angle*180/math.pi+180)
        base.taskMgr.doMethodLater(0.5, self.particle.cleanup,
                              "stop Particle", extraArgs=[])

        self.remove()

class LeapBullet(Bullet):

    def __init__(self,pos = LVecBase3f(0,0,-40),intoMask=DefaultMonsterMaskVal,  size=DefaultSizeVal, speed=DefaultSpeedVal,modelPath="SphereBullet"):
        Bullet.__init__(self)
        self.intoMask=intoMask
        self.volume=size
        self.speed=speed
        self.expires=time.time()+5
        self.position = pos

        nodepath=render.attachNewNode("bullet")
        self.model=nodepath
        nodepath.setPos(pos)
        # nodepath.setZ(nodepath,0.5)
        model=loader.loadModel(bulletModelPath+modelPath)
        model.setScale(self.volume)
        model.reparentTo(nodepath)
        col=CollisionNode("bullet")
        self.colliderNodePath = self.colliderNodePath = nodepath.attachNewNode(col)
        col.addSolid(CollisionSphere(0,0,0,self.volume))
        col.setIntoCollideMask(CollideMask.bit(self.intoMask))

        Bullet.setBullet(col,self)

    def update(self,time):

        if self.model is None:
            return
        if self.expires<=time:
            self.expires = -1
            self.remove()
            return
        self.model.setZ(self.model.getZ()-self.speed)
        self.model.setP(-90)

    def action(self,entry):
        if self.model is None:
            return
        self.expires=-1
        nodepath=entry.getFromNodePath()
        obj=self.getMonster(nodepath)
        if obj is None:
            obj=self.getHero(nodepath)
        if obj is None:
            return
        obj.underAttack(100000)
        self.remove()


class TubeSingleBullet(Bullet):
    @staticmethod
    def ToDict(bullet):
        dict = Bullet.ToDict(bullet)
        dict["class"] = "TubeSingleBullet"
        dict["radius"] = bullet.radius

        return dict

    @staticmethod
    def ToBullet(dict,hero):
        obj = TubeSingleBullet(hero)
        Bullet.ToBullet(obj, dict)
        obj.radius = dict["radius"]

        hero.bullet = obj
        hero.bullet.model.detachNode()
        hero.sounds["Attack"] = loader.loadSfx("Audio/ray.mp3")

        def attack(taskTime):
            '''
            taskTime 无效参数，可以重新赋值
            '''
            angle = hero.angle
            # 是否过了攻击冷却期
            currTime = time.time()
            split = currTime - hero.lastAttackTime
            if standarHitRate * 1.0 / hero.attackSpeed > split:
                return

            #是否过了激光冷却期
            if hero.bullet.expires > currTime:
                return

            # 更新上一次攻击的时间
            hero.lastAttackTime = currTime

            # 播放攻击动画
            hero.model.play("Attack")
            # 播放攻击音效
            hero.sounds["Attack"].play()

            # 子弹位置
            pos = hero.model.getPos()
            bullet =  TubeSingleBullet(hero,radius=bulletModelScaleVal)

            # 子弹生命周期（消亡的时间）
            bullet.setExpires(currTime + bullet.bulletLife)  # bullet.bulletLife
            # # 子弹飞行方向
            # angle = angle * math.pi / 180.0
            # bullet.setAngle(angle)
            # 子弹伤害值 （ 子弹本身伤害值 + 英雄攻击力 ）
            bullet.damage += hero.attackPower
            # 注册子弹
            base.messenger.send("bullet-create", [bullet])

        hero.attack = attack

        return obj

    def copy(self):
        obj = TubeSingleBullet(hero = self.heroPtr, radius = self.radius,intoMask = self.intoMask)
        super(TubeSingleBullet,self).copy(obj)
        return obj

    def __init__(self, hero,time=0,damage=DefaultDamageVal, rang=DefaultTubeRangeVal, radius=DefaultRadiusVal, intoMask=DefaultMonsterMaskVal,lasttime=DefaultRayLastTimeVal):
        Bullet.__init__(self)
        self.intoMask=intoMask
        self.damage=damage
        self.range=rang
        self.radius=radius
        self.hurtlist=[]
        self.bulletLife = lasttime
        self.expires=time+lasttime
        self.heroPtr = hero
        nodepath=hero.model.attachNewNode("bullet")
        self.model=nodepath
        nodepath.setPos(0,0,0)
        model=loader.loadModel(bulletModelPath+"TubeBullet")
        model.setScale(radius)
        model.reparentTo(nodepath)
        col=CollisionNode("bullet")
        self.colliderNodePath = col
        nodepath.attachNewNode(col).show()
        col.addSolid(CollisionTube(0,0,2,0,-rang,2,self.radius))
        col.setIntoCollideMask(CollideMask.bit(self.intoMask))

        Bullet.setBullet(col,self)

    def update(self,time):
        if self.model is None:
            return
        if self.expires<=time:
            self.expires = -1
            self.remove()

    def action(self,entry):
        if self.model is None:
            return
        self.sounds["hit"].play()
        nodepath=entry.getFromNodePath()
        obj=self.getMonster(nodepath)
        if obj is None:
            obj=self.getHero(nodepath)
        if obj is None:
            return

        for o in self.hurtlist:
            if o is obj:
                return
        obj.underAttack(self.damage)
        self.hurtlist.append(obj)

class TrapBullet(Bullet):
    @staticmethod
    def ToDict(bullet):
        dict = Bullet.ToDict(bullet)
        dict["class"] = "TrapBullet"
        dict["radius"] = bullet.radius

        return dict

    @staticmethod
    def ToBullet(dict):
        obj = TrapBullet()
        Bullet.ToBullet(obj, dict)
        obj.radius = dict["radius"]

        return obj

    def copy(self):
        obj = TrapBullet(radius = self.radius,intoMask = self.intoMask)
        super(TrapBullet,self).copy(obj)
        return obj

    def __init__(self,pos =LVecBase3f(0,0,0), time=0, damage=DefaultDamageVal, radius=DefaultRadiusVal, intoMask=DefaultMonsterMaskVal,lasttime=DefaultLastTimeVal,modelPath="TrapBullet"):
        Bullet.__init__(self)
        self.intoMask=intoMask
        self.damage=damage
        self.radius=radius
        self.bulletLife = lasttime
        self.expires=time+lasttime
        nodepath=render.attachNewNode("bullet")
        self.model=nodepath
        nodepath.setPos(pos)
        model=loader.loadModel(bulletModelPath+modelPath)
        model.setScale(radius)
        model.reparentTo(nodepath)
        col=CollisionNode("bullet")
        self.colliderNodePath = col
        nodepath.attachNewNode(col)
        col.addSolid(CollisionSphere(0,0,0,self.radius))
        col.setIntoCollideMask(CollideMask.bit(self.intoMask))
        Bullet.setBullet(col,self)
    def update(self,time):
        if self.model is None:
            return
        if self.expires<=time:
            self.remove()
            self.expires = -1
    def action(self,entry):
        if self.model is None:
            return
        self.expires = -1
        nodepath=entry.getFromNodePath()
        obj=self.getMonster(nodepath)
        if obj is None:
            obj=self.getHero(nodepath)
        if obj is None:
            return
        obj.underAttack(self.damage)
        self.sounds["hit"].play()
        self.remove()

class TrapDurativeBullet (Bullet):
    @staticmethod
    def ToDict(bullet):
        dict = Bullet.ToDict(bullet)
        dict["class"] = "TrapDurativeBullet"
        dict["radius"] = bullet.radius

        return dict

    @staticmethod
    def ToBullet(dict):
        obj = TrapDurativeBullet()
        Bullet.ToBullet(obj, dict)
        obj.radius = dict["radius"]

        return obj

    def copy(self):
        obj = TrapDurativeBullet(radius = self.radius,intoMask = self.intoMask)
        super(TrapDurativeBullet,self).copy(obj)
        return obj

    def __init__(self,pos =LVecBase3f(0,0,0), time=0, damage=DefaultDamageVal, radius=DefaultRadiusVal, intoMask=DefaultMonsterMaskVal,lasttime=DefaultLastTimeVal,modelPath="TrapDurativeBullet"):
        Bullet.__init__(self)
        self.intoMask=intoMask
        self.damage=damage
        self.radius=radius
        self.bulletLife = lasttime
        self.expires=time+lasttime
        nodepath=render.attachNewNode("bullet")
        self.model=nodepath
        nodepath.setPos(pos)
        model=loader.loadModel(bulletModelPath+modelPath)
        model.setScale(radius)
        model.reparentTo(nodepath)
        col=CollisionNode("bullet")
        self.colliderNodePath = col
        nodepath.attachNewNode(col)
        col.addSolid(CollisionSphere(0,0,0,self.radius))
        col.setIntoCollideMask(CollideMask.bit(self.intoMask))
        Bullet.setBullet(col,self)
    def update(self,time):
        if self.model is None:
            return
        if self.expires<=time:
            self.remove()
            self.expires = -1
    def action(self,entry):
        if self.model is None:
            return
        nodepath=entry.getFromNodePath()
        obj=self.getMonster(nodepath)
        if obj is None:
            obj=self.getHero(nodepath)
        if obj is None:
            return
        self.sounds["hit"].play()
        obj.underAttack(self.damage)

class AroundDurativeBullet (Bullet):
    @staticmethod
    def ToDict(bullet):
        dict = Bullet.ToDict(bullet)
        dict["class"] = "AroundDurativeBullet"
        dict["radius"] = bullet.radius
        dict["angleSpeed"] = bullet.angleSpeed
        dict["center"] = bullet.center
        dict["angle"] = bullet.angle
        return dict

    @staticmethod
    def ToBullet(dict):
        obj = AroundDurativeBullet(dict["center"])
        Bullet.ToBullet(obj, dict)
        obj.radius = dict["radius"]
        obj.angleSpeed = dict["angleSpeed"]
        obj.angle = dict["angle"]

        return obj

    def copy(self):
        obj = TrapDurativeBullet(center = self.center,radius = self.radius,angleSpeed = self.angleSpeed,intoMask = self.intoMask)
        super(TrapDurativeBullet,self).copy(obj)
        return obj

    def __init__(self, center,time=0,damage=DefaultDamageVal, angleSpeed=DefaultAngleSpeedVal , size=DefaultSizeVal ,radius=DefaultRadiusVal,  intoMask=DefaultMonsterMaskVal,lasttime=DefaultLastTimeVal):
        Bullet.__init__(self)
        self.intoMask=intoMask
        self.damage=damage
        self.angleSpeed=angleSpeed
        self.center=center
        self.volume=size
        self.radius=radius
        self.angle=0
        self.bulletLife = lasttime
        self.expires=time+lasttime

        nodepath=render.attachNewNode("bullet")
        self.model=nodepath
        nodepath.setPos(center+(radius,0,0.5))

        model=loader.loadModel(bulletModelPath+"AroundDurativeBullet")
        model.setScale(size)
        model.reparentTo(nodepath)
        col=CollisionNode("bullet")
        self.colliderNodePath = col
        nodepath.attachNewNode(col)
        col.addSolid(CollisionSphere(0,0,0,size))
        col.setIntoCollideMask(CollideMask.bit(self.intoMask))
        Bullet.setBullet(col,self)

    def update(self,time):
        if self.model is None:
            return
        if self.expires<=time:
            self.remove()
            self.expires = -1
            return
        self.angle=self.angle+self.angleSpeed
        if self.angle>360:
            self.angle=self.angle-360
        angle=self.angle*math.pi/180
        self.model.setPos(self.center+(self.radius*math.sin(angle),-self.radius*math.cos(angle),0.5))


    def action(self,entry):
        if self.model is None:
            return
        nodepath=entry.getFromNodePath()
        obj=self.getMonster(nodepath)
        if obj is None:
            obj=self.getHero(nodepath)
        if obj is None:
            return
        self.sounds["hit"].play()
        obj.underAttack(self.damage)

class AroundPermanentBullet (Bullet):

    def __init__(self, target,angle=0,damage=DefaultDamageVal, angleSpeed=DefaultAngleSpeedVal , size=DefaultSizeVal ,radius=DefaultRadiusVal,  intoMask=DefaultMonsterMaskVal,modelPath="AroundBullet"):
        Bullet.__init__(self)
        self.intoMask=intoMask
        self.damage=damage
        self.angleSpeed=angleSpeed
        self.target=target
        self.volume=size
        self.radius=radius
        self.angle=angle
        self.expires=2

        nodepath=self.target.model.attachNewNode("bullet")
        self.model=nodepath
        nodepath.setPos(radius,0,0.5)

        model=loader.loadModel(bulletModelPath+"AroundPermanentBullet")
        model.setScale(size)
        model.reparentTo(nodepath)
        col=CollisionNode("bullet")
        self.colliderNodePath = col
        nodepath.attachNewNode(col).show()
        col.addSolid(CollisionSphere(0,0,0,size))
        col.setIntoCollideMask(CollideMask.bit(self.intoMask))
        Bullet.setBullet(col,self)

    def update(self,time):
        if self.model is None:
            return
        self.angle=self.angle+self.angleSpeed
        if self.angle>360:
            self.angle=self.angle-360
        angle=self.angle*math.pi/180
        self.model.setPos(self.radius*math.sin(angle),-self.radius*math.cos(angle),2)


    def action(self,entry):
        if self.model is None:
            return
        nodepath=entry.getFromNodePath()
        obj=self.getMonster(nodepath)
        if obj is None:
            obj=self.getHero(nodepath)
        if obj is None:
            return
        self.sounds["hit"].play()
        obj.underAttack(self.damage)

class SectorBullet(Bullet):

    def __init__(self, chara,time=0,damage=DefaultDamageVal, rang=DefaultTubeRangeVal, size=3, intoMask=DefaultMonsterMaskVal,lasttime=DefaultLastTimeVal):
        Bullet.__init__(self)
        self.intoMask=intoMask
        self.damage=damage
        self.range=rang
        self.size=size
        self.hurtlist=[]
        self.bulletLife = lasttime
        self.expires=time+lasttime
        nodepath=chara.model.attachNewNode("bullet")
        self.model=nodepath
        nodepath.setPos(0,0,-2)
        model=loader.loadModel(bulletModelPath+"TubeBullet")
        
        model.reparentTo(nodepath)
        col=CollisionNode("bullet")
        self.colliderNodePath = col
        nodepath.attachNewNode(col)#.show()

        col.addSolid(CollisionTube(0,0,2,0,-rang,2,0.5))
        for x in xrange(1,size+1):
            angle=1.0*x*5/180*math.pi
            col.addSolid(CollisionTube(0,0,2,-rang*math.sin(angle),-rang*math.cos(angle),2,0.5))
            angle=-1.0*x*5/180*math.pi
            col.addSolid(CollisionTube(0,0,2,-rang*math.sin(angle),-rang*math.cos(angle),2,0.5))

        col.setIntoCollideMask(CollideMask.bit(self.intoMask))
        Bullet.setBullet(col,self)

    def update(self,time):
        if self.model is None:
            return
        if self.expires<=time:
            self.expires = -1
            self.remove()

    def action(self,entry):
        if self.model is None:
            return
        self.sounds["hit"].play()
        nodepath=entry.getFromNodePath()
        obj=self.getMonster(nodepath)
        if obj is None:
            obj=self.getHero(nodepath)
        if obj is None:
            return
        obj.underAttack(self.damage)
