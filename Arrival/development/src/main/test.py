#!/usr/bin/python
#coding:utf-8

# Python imports
import os
import logging
import sys
import traceback
# Panda3D imoprts
from direct.interval.IntervalGlobal import *
from direct.showbase.ShowBase import ShowBase
from direct.fsm.FSM import FSM
from direct.filter.CommonFilters import CommonFilters
from panda3d.ai import *
from panda3d.core import (
    CollisionTraverser,
    CollisionHandlerPusher,
    CollisionHandlerEvent,
    CollisionHandlerQueue,
    ClockObject,
    AntialiasAttrib,
    ConfigPageManager,
    ConfigVariableBool,
    OFileStream,
    WindowProperties,
    loadPrcFileData,
    loadPrcFile,
    MultiplexStream,
    Notify,
    Filename,
    LPoint3,
    AudioSound)
from direct.gui.DirectGui import DGG
from direct.showbase.Audio3DManager import Audio3DManager

# Game imports
# UI
from menu import Menu
from option import Option
from archive import Archive
from death import Death
from helper import hide_cursor, show_cursor
#
from Room import Room,RoomInformation
from MapManager import MapManager
from archiveManager import ArchiveManager
from VideoHelper import *
from Hero import Hero
from DefaultConfigVal import *
LEAPMOTION = True
try:
    from LeapMotion import *
except Exception as e:
    LEAPMOTION = False
from Monster import *

class Main(ShowBase, FSM):
    """Main function of the application
    initialise the engine (ShowBase)"""

    def __init__(self):
        """initialise the engine"""
        ShowBase.__init__(self)
        base.camLens.setNearFar(1.0, 10000)
        base.camLens.setFov(75)
        
        a = 33
        base.camera.setPos(0,-a,a+3)#80)
        # collision
        base.cTrav = CollisionTraverser("base collision traverser")
        base.cHandler = CollisionHandlerEvent()
        base.cPusher = CollisionHandlerPusher()
        base.cQueue = CollisionHandlerQueue()
        base.globalClock=ClockObject.getGlobalClock()
        base.cHandler.addInPattern('%fn-into-%in')
        base.cHandler.addOutPattern('%fn-out-%in')
        base.cHandler.addAgainPattern('%fn-again-%in')
        # ai init
        base.AIworld = AIWorld(render)
        # 3d manager
        base.audio3d = Audio3DManager(base.sfxManagerList[0], camera)
        self.monsters = []
        self.accept('c',self._create)

        base.enableParticles()
    def _create(self):
        for monster in self.monsters:
            print 'remove'
            monster.detachSound()
            monster.model.cleanup()
            monster.model.removeNode()
        self.monsters=[]
        for i in range(0,1):
            print i
            monster = MonsterFactory.create('Minotaur',LPoint3(0,i*50,0),render)
            if isinstance(monster,Monster):
                self.monsters.append(monster)
                # 火焰
                monster.fire2()
                # particle_fire2 = ParticleEffect()
                # particle_fire2.loadConfig('assets/particles/fireish.ptf')
                # particle_fire2.setPos(monster.model.getPos())
                # particle_fire2.setZ(4)
                # particle_fire2.setH(monster.model.getH()-90)
                # particle_fire2.setP(90)
                # particle_fire2.setScale(defaultParticleScale*2,defaultParticleScale,defaultParticleScale*3)
                # Sequence(
                #     Func(particle_fire2.start,render),
                #     Wait(defaultMinotaurFireTime+5),
                #     Func(particle_fire2.cleanup),
                # ).start()
Game = Main()
try:
    Game.run()
except BaseException as e:
    logging.debug("game error: {}".format(traceback.format_exc()))



