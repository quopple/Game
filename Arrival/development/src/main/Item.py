#!/usr/bin/python
# coding:utf-8

# Game imports
import copy
import time
from Bullet import *
from DefaultConfigVal import *
import random

# Panda3D imports
from direct.actor.Actor import Actor
from direct.showbase.DirectObject import DirectObject
from direct.particles.ParticleEffect import ParticleEffect
from panda3d.core import (
    CollisionNode,
    CollisionSphere,
    CollideMask,
)

from VideoHelper import *
from exceptions import Exception

ModelPath = "Model/Item/"
TexturePath = "Item/Texture/"

DefaultItemScale=2

class ItemFactory(object):
    @staticmethod
    def create(typeStr,pos,target,buffState,parent=None):
        ret = None
        if typeStr=='Damage':
            ret = DamageItem()
        elif typeStr=='Ray':
            ret = RayItem()
        elif typeStr=='Shotgun':
            ret = ShotgunItem()
        elif typeStr=='AoeDamage':
            ret = AoeDamageItem()
        elif typeStr=='Life':
            ret = LifeItem()
        elif typeStr=='MaxLife':
            ret = MaxLifeItem()
        elif typeStr=='MoveSpeed':
            ret = MoveSpeedItem()
        elif typeStr=='AttackSpeed':
            ret = AttackSpeedItem()
        elif typeStr=='BulletSpeed':
            ret = BulletSpeedItem()
        elif typeStr=='BulletSize':
            ret = BulletSizeItem()
        elif typeStr=='BulletRange':
            ret = BulletRangeItem()
        if not ret == None:
            ret.initModel(pos,DefaultItemScale,target,buffState,parent)
        return ret

    @staticmethod
    def isGen(roomCode):
        if roomCode==0:
            return False
        roomMax = (DefaultMasterRoomNum+1)*2
        if random.randint(0,roomMax)<= roomMax/5.0: # 五分之一的几率
            return True
        else:
            return False



class Item(DirectObject,object):
    '''
    道具类的虚基类
    '''

    num = 0  # use to identify item collition node

    def __init__(self, itemName):
        super(Item, self).__init__()
        self.number = Item.num
        self.itemName = itemName
        Item.num += 1

    def initModel(self, pos, scale, player,buffState,parent=None):
        '''
        初始化道具模型和设置碰撞检测
        #pos 道具模型的放置位置 （世界坐标系）
        #scale 模型缩放比例
        #player 英雄实例
        '''

        # 加载并设置模型
        try:
            modelName = ModelPath + "model_"+self.itemName
            self.item = Actor(modelName,
                {'revolve':modelName})
            self.item.loop('revolve')
        except Exception:
            self.item = Actor()
            self.item.setScale(0.3)

        self.item.setPos(pos)
        self.item.setScale(scale)
        if parent==None:
            self.item.reparentTo(base.render)
        else:
            self.item.reparentTo(parent)
        # 设置碰撞检测
        collisionSphere = CollisionSphere(0, 0, 0, 1)
        self.collisionNodeName = "{}CollisionNode{}".format(self.itemName, self.number)
        itemColNode = CollisionNode(self.collisionNodeName)
        itemColNode.addSolid(collisionSphere)
        itemColNode.setIntoCollideMask(CollideMask.bit(DefaultHeroMaskVal))
        itemColNode.setFromCollideMask(CollideMask.allOff())
        self.itemCollision = self.item.attachNewNode(itemColNode)
        self.itemCollision.setPythonTag("Item",self)
        ##显示包围体   用于粗略模拟道具盒
        # self.itemCollision.show()
        base.cTrav.addCollider(self.itemCollision, base.cHandler)

        inEvent = "{}-into-{}".format(player.colliderName, self.collisionNodeName)
        self.accept(inEvent, self.action)
        buffState.accept(inEvent,buffState.addBuff)

    @print_func_time
    def action(self,entry):
        '''
        碰撞处理事件
        将道具效果应用到英雄对象
        不同类型道具有不同实现方式
        '''
        #print self.itemName,self.collisionNodeName
        player = entry.getFromNodePath().getPythonTag("Hero")
        player.sounds["GetItem"].play()

    @print_func_time
    def _destroy(self):
        '''
        道具使用后立即销毁
        '''
        self.ignoreAll()
        if not self.item.isEmpty():
            self.item.cleanup()
            self.item.removeNode()


class DamageItem(Item):
    '''
    增加攻击值的道具
    '''

    def __init__(self, damageVal=defaultDamageVal):
        super(DamageItem, self).__init__('item_DamageItem')
        self.damageVal = damageVal

    def action(self,entry):
        super(DamageItem, self).action(entry)
        player = entry.getFromNodePath().getPythonTag("Hero")
        player.attackPower += self.damageVal
        self._destroy()


class RayItem(Item):
    '''
    将英雄持有的子弹更改为激光
    '''

    def __init__(self):
        super(RayItem, self).__init__('item_RayItem')

    def action(self,entry):
        super(RayItem, self).action(entry)
        player = entry.getFromNodePath().getPythonTag("Hero")
        player.bullet = TubeSingleBullet(player,radius=bulletModelScaleVal)
        player.bullet.model.detachNode()
        player.sounds["Attack"] = loader.loadSfx("Audio/ray.mp3")
        player.attackMode = "Ray"

        def attack(taskTime):
            '''
            taskTime 无效参数，可以重新赋值
            '''
            angle = player.angle
            # 是否过了攻击冷却期
            currTime = time.time()
            split = currTime - player.lastAttackTime
            if standarHitRate * 1.0 / player.attackSpeed > split:
                return

            #是否过了激光冷却期
            if player.bullet.expires > currTime:
                return

            # 更新上一次攻击的时间
            player.lastAttackTime = currTime

            # 播放攻击动画
            player.model.play("Attack")
            # 播放攻击音效
            player.sounds["Attack"].play()

            # 子弹位置
            pos = player.model.getPos()
            bullet =  TubeSingleBullet(player,radius=bulletModelScaleVal)

            # 子弹生命周期（消亡的时间）
            bullet.setExpires(currTime + bullet.bulletLife)  # bullet.bulletLife
            # # 子弹飞行方向
            # angle = angle * math.pi / 180.0
            # bullet.setAngle(angle)
            # 子弹伤害值 （ 子弹本身伤害值 + 英雄攻击力 ）
            bullet.damage += player.attackPower
            # 注册子弹
            base.messenger.send("bullet-create", [bullet])

        player.attack = attack
        # 销毁道具
        self._destroy()


class ShotgunItem(Item):
    '''
    将攻击方式更改为散弹攻击
    '''

    def __init__(self):
        super(ShotgunItem, self).__init__('item_Shotgun')

    def action(self,entry):
        super(ShotgunItem, self).action(entry)
        player = entry.getFromNodePath().getPythonTag("Hero")
        if player.attackMode=='Shotgun':
            # 销毁道具
            self._destroy()
            return
        player.bullet = SphereBullet()
        player.bullet.model.hide()
        player.sounds["Attack"] = loader.loadSfx("Audio/shotgun.wav")
        player.attackMode = "Shotgun"
        # 用于替换的攻击函数
        def attack( taskTime):
            # 是否过了攻击冷却期
            currTime = time.time()
            split = currTime - player.lastAttackTime
            if standarHitRate * 1.0 / player.attackSpeed > split:
                return

            player.lastAttackTime = currTime

            # 播放攻击动画
            player.model.play("Attack")
            # 播放攻击音效
            player.sounds["Attack"].play()

            angle = player.angle
            # 子弹位置
            pos = player.model.getPos()
            bullet1 = player.bullet.copy()
            bullet1.model.reparentTo(render)
            bullet1.setPos(pos)
            bullet1.setZ(2)  # bullet.getZ() +
            # 子弹生命周期（消亡的时间）
            bullet1.setExpires(currTime + bullet1.bulletLife)  # bullet.bulletLife
            # 子弹飞行方向
            bullet1.setAngle(angle)
            # 子弹伤害值 （ 子弹本身伤害值 + 英雄攻击力 ）
            bullet1.damage += player.attackPower
            bullet1.model.show()
            # 注册子弹
            base.messenger.send("bullet-create", [bullet1])

            bullet2 = bullet1.copy()
            bullet2.model.reparentTo(render)

            bullet2.setAngle(angle+defaultFlection)
            bullet2.model.show()
            base.messenger.send("bullet-create", [bullet2])

            bullet3 = bullet1.copy()

            bullet3.setAngle(angle - defaultFlection)
            bullet3.model.reparentTo(base.render)
            bullet3.model.show()
            base.messenger.send("bullet-create", [bullet3])

        # 更改英雄的攻击方式
        player.attack = attack
        # 销毁道具
        self._destroy()

class AoeDamageItem(Item):
    '''
    一次全房间伤害
    '''

    def __init__(self, damageVal=defaultScopeDamageVal):
        super(AoeDamageItem, self).__init__('item_AoeDamage')
        self.damageVal = damageVal

    def cleanup(self):
        self.particle.cleanup()
        self.sound.stop()

    def action(self,entry):
        # 发送事件  事件处理函数将房间内的所有怪物的血量减少damageVal
        super(AoeDamageItem, self).action(entry)
        base.messenger.send("global-damage", [self.damageVal])

        self.sound = loader.loadSfx("Audio/aoe.wav")
        self.sound.play()

        self.particle = ParticleEffect()
        self.particle.loadConfig( "assets/particles/globalBoom.ptf")
        self.particle.setScale(10)
        self.particle.start(render)
        base.taskMgr.doMethodLater(1.2, self.cleanup,"stop Particle",extraArgs = [])

        # 销毁道具
        self._destroy()


class LifeItem(Item):
    '''
    补充英雄的血量
    '''

    def __init__(self, val=defaultIncreaseHP):
        super(LifeItem, self).__init__('item_Life')
        self.val = val

    def action(self,entry):
        super(LifeItem, self).action(entry)
        player = entry.getFromNodePath().getPythonTag("Hero")
        player.increaseHP(self.val)
        self._destroy()


class MaxLifeItem(Item):
    '''
    增加英雄的最大血量
    '''

    def __init__(self, val=defaultIncreaseHP):
        super(MaxLifeItem, self).__init__('item_MaxLife')
        self.val = val

    def action(self,entry):
        super(MaxLifeItem, self).action(entry)
        player = entry.getFromNodePath().getPythonTag("Hero")
        player.increaseHP(self.val)
        player.increaseMaxHP(self.val)
        self._destroy()


class MoveSpeedItem(Item):
    '''
    增加英雄移动速度
    '''

    def __init__(self, moveSpeed=defaultIncreaseMoveSpeed):
        super(MoveSpeedItem, self).__init__('item_MoveSpeed')
        self.moveSpeed = moveSpeed

    def action(self,entry):
        super(MoveSpeedItem, self).action(entry)
        player = entry.getFromNodePath().getPythonTag("Hero")
        player.moveSpeed *= self.moveSpeed
        self._destroy()


class AttackSpeedItem(Item):
    '''
    增加英雄攻击速度
    '''

    def __init__(self, attackSpeed=defaultIncreaseAttackSpeed):
        super(AttackSpeedItem, self).__init__('item_AttackSpeed')
        self.attackSpeed = attackSpeed

    def action(self,entry):
        super(AttackSpeedItem, self).action(entry)
        player = entry.getFromNodePath().getPythonTag("Hero")
        player.attackSpeed *= self.attackSpeed
        self._destroy()


class BulletSpeedItem(Item):
    '''
    加大英雄发射出的子弹的飞行速度
    '''

    def __init__(self, bulletSpeed=defaultIncreaseBulletSpeed):
        super(BulletSpeedItem, self).__init__('item_BulletSpeed')
        self.bulletSpeed = bulletSpeed

    def action(self,entry):
        super(BulletSpeedItem, self).action(entry)
        player = entry.getFromNodePath().getPythonTag("Hero")
        if isinstance(player.bullet, SphereBullet):
            player.bullet.speed *= self.bulletSpeed
        elif isinstance(player.bullet, AroundDurativeBullet):
            player.bullet.angleSpeed *= self.bulletSpeed
        self._destroy()


class BulletRangeItem(Item):
    '''
    加大英雄发射出的子弹的射程
    '''

    def __init__(self, bulletRange=defaultIncreaseBulletRange):
        super(BulletRangeItem, self).__init__('item_BulletRange')
        self.bulletRange = bulletRange

    def action(self,entry):
        super(BulletRangeItem, self).action(entry)
        player = entry.getFromNodePath().getPythonTag("Hero")
        player.bullet.setRange( self.bulletRange*player.bullet.range )
        self._destroy()


class BulletSizeItem(Item):
    '''
    加大英雄发射出的子弹的大小（杀伤范围）
    '''

    def __init__(self, bulletSize=defaultIncreaseBulletSize):
        super(BulletSizeItem, self).__init__('item_BulletSize')
        self.bulletSize = bulletSize

    def action(self,entry):
        super(BulletSizeItem, self).action(entry)
        player = entry.getFromNodePath().getPythonTag("Hero")
        player.bullet.setVolume(self.bulletSize*player.bullet.volume)
        self._destroy()
