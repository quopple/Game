#!/usr/bin/python
#coding:utf-8

# Python imports
import os
import logging
import sys
import traceback
import time
import threading
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

#
# PATHS AND CONFIGS
#
# set the application Name
companyName = "MIAO"
appName = "Arrival"
versionstring = "1.0"
home = os.path.expanduser(sys.path[0])
basedir = os.path.join(
    home,
    companyName,
    appName)
if not os.path.exists(basedir):
    os.makedirs(basedir)
prcFile = os.path.join(basedir, "{}.prc".format(appName))
if os.path.exists(prcFile):
    mainConfig = loadPrcFile(Filename.fromOsSpecific(prcFile))
loadPrcFileData("",
"""
    window-title {}
    cursor-hidden 0
    notify-timestamp 1
    #show-frame-rate-meter 1
    model-path $MAIN_DIR/assets/
    framebuffer-multisample 1
    multisamples 8
    texture-anisotropic-degree 0
    textures-auto-power-2 1
""".format(appName))
#
# PATHS AND CONFIGS END
#

#
# LOGGING
#
# setup Logging
logging.basicConfig(
    level=logging.DEBUG,
    format='%(asctime)s %(filename)s[line:%(lineno)d] %(levelname)s %(message)s',
    filename=os.path.join(basedir, "game.log"),
    datefmt="%d-%m-%Y %H:%M:%S",
    filemode="w")

# First log entry, the program version
logging.info("Version {}".format(versionstring))

# redirect the notify output to a log file
nout = MultiplexStream()
Notify.ptr().setOstreamPtr(nout, 0)
nout.addFile(Filename(os.path.join(basedir, "game_p3d.log")))

#
# LOGGING END
#

class Main(ShowBase, FSM):
    """Main function of the application
    initialise the engine (ShowBase)"""

    def __init__(self):
        """initialise the engine"""
        ShowBase.__init__(self)
        FSM.__init__(self, "FSM-Game")

        #
        # BASIC APPLICATION CONFIGURATIONS
        #
        # disable pandas default camera driver
        self.disableMouse()
        # set background color to black
        self.setBackgroundColor(0, 0, 0)
        # set antialias for the complete sceen to automatic
        self.render.setAntialias(AntialiasAttrib.MAuto)
        # shader generator
        render.setShaderAuto()
        # Enhance font readability
        DGG.getDefaultFont().setPixelsPerUnit(100)

        #
        # CONFIGURATION LOADING
        #
        # load given variables or set defaults
        # check if audio should be muted
        mute = ConfigVariableBool("audio-mute", False).getValue()
        if mute:
            self.disableAllAudio()
        else:
            self.enableAllAudio()
        # check if particles should be enabled
        particles = ConfigVariableBool("particles-enabled", True).getValue()
        if particles:
            self.enableParticles()

        base.width = self.pipe.getDisplayWidth()
        base.height = self.pipe.getDisplayHeight()

        # check if the config file hasn't been created
        if not os.path.exists(prcFile):
            # get the displays width and height
            w = self.pipe.getDisplayWidth()
            h = self.pipe.getDisplayHeight()
            # set window properties
            # clear all properties not previously set
            base.win.clearRejectedProperties()
            # # setup new window properties
            props = WindowProperties()
            # # # Fullscreen
            props.setFullscreen(True)
            # # # set the window size to the screen resolution
            props.setSize(w, h)
            # # request the new properties
            base.win.requestProperties(props)
            pass
        elif base.appRunner:
            # As when the application is started as appRunner instance
            # it doesn't respect our loadPrcFile configurations specific
            # to the window, hence we need to manually set them here.
            for dec in range(mainConfig.getNumDeclarations()):
                #TODO: Check for all window specific variables like
                #      fullscreen, screen size, title and window
                #      decoration that you have in your configuration
                #      and set them by your own.
                if mainConfig.getVariableName(dec) == "fullscreen":
                    if not mainConfig.getDeclaration(dec).getBoolWord(0): break
                    # get the displays width and height
                    w = self.pipe.getDisplayWidth()
                    h = self.pipe.getDisplayHeight()
                    # set window properties
                    # clear all properties not previously set
                    base.win.clearRejectedProperties()
                    # setup new window properties
                    props = WindowProperties()
                    # Fullscreen
                    props.setFullscreen(True)
                    # set the window size to the screen resolution
                    props.setSize(w, h)
                    # request the new properties
                    base.win.requestProperties(props)
                    break
                pass

        # automatically safe configuration at application exit
        base.exitFunc = self.__writeConfig
        # due to the delayed window resizing and switch to fullscreen
        # we wait some time until everything is set so we can savely
        # proceed with other setups like the menus
        if base.appRunner:
            # this behaviour only happens if run from p3d files and
            # hence the appRunner is enabled
            taskMgr.doMethodLater(0.5, self.postInit,
                "post initialization", extraArgs=[])
        else:
            self.postInit()

    def postInit(self):
        #
        # initialize game content
        #
        # camera
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
        # manager
        self.archiveManager = ArchiveManager()
        self.mapManager = MapManager()
        self.initHeroInfo = None
        # Lock
        self.lock = threading.Lock()
        self.gameThread = None

        self.filters = CommonFilters(base.win,base.cam)
        # UI
        self.menu = Menu()
        self.option = Option()
        self.archive = Archive()
        self.death = Death()
        # self.oobe()
        #self.Archive_status = 0
        # self.menuMusic = loader.loadMusic("assets/audio/menuMusic.ogg")
        # self.menuMusic.setLoop(True)
        # self.fightMusic = loader.loadMusic("assets/audio/fightMusic.ogg")
        # self.fightMusic.setLoop(True)
        # base.audio3d = Audio3DManager(base.sfxManagerList[0], camera)

        self.titleVideo,self.titleCard = loadVideo('title.mp4')
         
        self.isInited = False
        self.isSkip = False
        self.isRenew = False
        #
        # Event handling
        #
        self.accept("escape", self.__escape)

        #
        # Start with the menu
        #
        self.request("Menu")

    #
    # FSM PART
    #
    def enterMenu(self):
        show_cursor()
        self.accept("Menu-Game", self.request, ["Archive"])
        self.accept("Menu-Option", self.request, ["Option"])
        self.accept("Menu-Quit", self.quit)
        self.menu.show()

    def exitMenu(self):
        self.ignore("Menu-Game")
        self.ignore("Menu-Option")
        self.ignore("Menu-Quit")
        self.menu.hide()

    def enterOption(self):
        show_cursor()
        self.accept("ChangeVolume", self.ChangeMusic)
        self.accept("ChangeSound", self.ChangeSound)
        self.option.show()

    def exitOption(self):
        self.ignore("ChangeVolume")
        self.ignore("ChangeSound")
        self.option.hide()

    def enterArchive(self):
        show_cursor()
        self.accept("LoadArchive", self.LoadArchive)
        self.accept("DeleteArchive", self.DeleteArchive)
        self.accept("UpdateArchive",self.UpdateArchive)
        self.accept("NewGame",self.NewGame)
        self.UpdateArchive()

    def exitArchive(self):
        self.archive.hide()
        self.ignore("LoadArchive")
        self.ignore("DeleteArchive")
        self.ignore("UpdateArchive")
        self.ignore("NewGame")
        

    def enterPause(self):
        # self.accept("Pause-Newgame")
        # self.accept("Pause-Option")
        # self.accept("Pause-Back")
        show_cursor()


    def exitPause(self):
        self.ignore("Pause-Newgame")
        self.ignore("Pause-Option")
        self.ignore("Pause-Back")

    
    def enterInitGame(self):
        if Nodebug:
            self.titleCard.show()
            self.titleVideo.play()

    def exitInitGame(self):
        if Nodebug:
            self.titleCard.hide()
            self.titleVideo.stop()

    
    def enterGame(self):
        self.accept("hero-death", self.request, ["Death"])
        self.accept('game-end',self.request,['Menu'])
        base.messenger.send('game-start',[self.isRenew])
    
    def exitGame(self):
        self.ignore('hero-death')
        #self.archiveManager.SaveArchive(self.archiveID,MapManager.ToDict(self.mapManager))
        pass

    def enterDeath(self):
        self.mapManager.index=0 # renew
        self.accept("Death-Game", self.NewGame)
        self.accept("Death-Menu", self.request, ["Menu"])
        self.accept("Death-Quit", self.quit)
        self.death.show()
        show_cursor()

    def exitDeath(self):
        self.ignore("Death-Menu")
        self.ignore("Death-Quit")
        self.death.hide()
    #
    # FSM PART END
    #
    
    @print_func_time
    def NewGame(self):
        delayTime = self.titleVideo.length()
        archiveDir = self.archiveManager.basedir
        self.isInited=False
        self.request('InitGame')
        delayTime = self.titleVideo.length()
        if not self.isSkip:
            self.timer = threading.Timer(delayTime,self._accept_skip)
            self.timer.start()
        self.isInited=False
        checkThread = threading.Thread(target=self._thread_check,name='check')
        checkThread.start()
        self.gameThread = threading.Thread(target=self._initGame,args=(None,archiveDir),name='newgame')
        self.gameThread.start()

    def _thread_check(self):
        while(not self.isInited or not self.isSkip):
            pass
        self.isInited = False
        self.request('Game')

    @print_func_time
    def _accept_skip(self):
        self.lock.acquire()
        try:
            self.isSkip=True
        finally:
            self.lock.release()

    def _initGame(self,archive,archivePath):
        sTime = time.time()
        self.isInited = False
        self.mapManager.archivePath = archivePath
        #self.filters.setBloom()
        if self.mapManager.hero==None:
            self.mapManager.loadResource()
            self.initHeroInfo = Hero.ToDict(self.mapManager.hero)
        self.mapManager.hero.reInit(self.initHeroInfo)
        
        if archive ==None:
            self.mapManager.genMap()
            self.isRenew=True
            if not self.isSkip:
                self.acceptOnce('enter',self._accept_skip)
        else:
            self.mapManager.reInit(archive)
            self.isRenew=False
            if not self.isSkip:
                self.acceptOnce('enter',self._accept_skip)
        
        self.isInited = True
        

    @print_func_time
    def LoadGame(self):
        self.Archive_status = 1
        self.request("Archive")

    def ChangeMusic(self):
        print self.option.slider_volume['value']

    def ChangeMusic(self):
        base.musicManager.setVolume(self.option.slider_volume['value']/100)

    def ChangeSound(self):
        base.sfxManagerList[0].setVolume(self.option.slider_sound['value']/100)

    def DeleteArchive (self):
        self.archiveManager.DeleteArchive(self.archive.v[0])
        self.UpdateArchive()

    
    def LoadArchive (self):
        self.archiveID = self.archive.v[0]
        archive = self.archiveManager.ReadArchive(self.archiveID)
        archiveDir = self.archiveManager.basedir
        delayTime = self.titleVideo.length()
        self.request('InitGame')
        if not self.isSkip:
            self.timer = threading.Timer(delayTime,self._accept_skip)
            self.timer.start()
        self.isInited=False
        checkThread = threading.Thread(target=self._thread_check,name='check')
        checkThread.start()
        self.gameThread = threading.Thread(target=self._initGame,args=(archive,archiveDir),name='newgame')
        self.gameThread.start()

    def UpdateArchive(self):
        msg = self.archiveManager.GetArchiveListShortMsg()
        self.archive.show(msg)
    #
    # BASIC FUNCTIONS
    #

    def __escape(self):
        if self.state == "Menu":
            self.gameThread=None
            self.quit()
        elif self.state == "Game":
            archive = MapManager.ToDict(self.mapManager)
            self.archiveManager.SaveArchive(self.archive.v[0], archive)
            self.mapManager.room.request("Idle")
            base.musicManager.stopAllSounds()
            base.sfxManagerList[0].stopAllSounds()

            self.request("Menu")
        else:
            self.request("Menu")

    def quit(self):
        """This function will stop the application"""
        self.userExit()

    def __writeConfig(self):
        """Save current config in the prc file or if no prc file exists
        create one. The prc file is set in the prcFile variable"""
        page = None

        # These TODO tags are as a reminder for to add any new config
        # variables that may occur in the future
        #TODO: get values of configurations here
        particles = "#f" if not base.particleMgrEnabled else "#t"
        volume = str(round(base.musicManager.getVolume(), 2))
        mute = "#f" if base.AppHasAudioFocus else "#t"
        #TODO: add any configuration variable name that you have added
        customConfigVariables = [
            "", "particles-enabled", "audio-mute", "audio-volume"]
        if os.path.exists(prcFile):
            # open the config file and change values according to current
            # application settings
            page = loadPrcFile(Filename.fromOsSpecific(prcFile))
            removeDecls = []
            for dec in range(page.getNumDeclarations()):
                # Check if our variables are given.
                # NOTE: This check has to be done to not loose our base or other
                #       manual config changes by the user
                if page.getVariableName(dec) in customConfigVariables:
                    decl = page.modifyDeclaration(dec)
                    removeDecls.append(decl)
            for dec in removeDecls:
                page.deleteDeclaration(dec)
            # NOTE: particles-enabled and audio-mute are custom variables and
            #       have to be loaded by hand at startup
            # Particles
            page.makeDeclaration("particles-enabled", particles)
            # audio
            page.makeDeclaration("audio-volume", volume)
            page.makeDeclaration("audio-mute", mute)
        else:
            # Create a config file and set default values
            cpMgr = ConfigPageManager.getGlobalPtr()
            page = cpMgr.makeExplicitPage("{} Pandaconfig".format(appName))
            # set OpenGL to be the default
            page.makeDeclaration("load-display", "pandagl")
            # get the displays width and height
            w = self.pipe.getDisplayWidth()
            h = self.pipe.getDisplayHeight()
            # set the window size in the config file
            page.makeDeclaration("win-size", "{} {}".format(w, h))
            # set the default to fullscreen in the config file
            page.makeDeclaration("fullscreen", "1")
            # particles
            page.makeDeclaration("particles-enabled", "#t")
            # audio
            page.makeDeclaration("audio-volume", volume)
            page.makeDeclaration("audio-mute", "#f")
        # create a stream to the specified config file
        configfile = OFileStream(prcFile)
        # and now write it out
        page.write(configfile)
        # close the stream
        configfile.close()

    #
    # BASIC END
    #
# CLASS Main END

Game = Main()
try:
    Game.run()
except BaseException as e:
    logging.debug("game error: {}".format(traceback.format_exc()))



