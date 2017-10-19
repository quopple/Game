#coding:utf-8

from panda3d.core import TextNode
from direct.gui.DirectGui import (
    DirectFrame,
    DirectLabel,
    DirectButton)

class Death:
    def __init__(self):
        self.frameDeath = DirectFrame(
        image = "assets/gui/BackGround_d.jpg",
        image_scale = (1.7778, 1, 1),
        frameSize = (base.a2dLeft, base.a2dRight,
        base.a2dBottom, base.a2dTop),
        frameColor = (0, 0, 0, 0))
        self.frameDeath.setTransparency(1)

        self.title = DirectLabel(
        scale = 0.15,
        text_align = TextNode.ACenter,
        pos = (0, 0, 0.4),
        frameColor = (0, 0, 0, 0),
        text = "You Dead",
        text_fg = (1,1,1,1))
        self.title.setTransparency(1)
        self.title.reparentTo(self.frameDeath)

        self.btn_newgame = self.createButton(
        "Restart",
        -.10,
        ["Death-Game"])

        self.btn_option = self.createButton(
        "Back",
        -.25,
        ["Death-Menu"])

        self.btnExit = self.createButton(
        "Quit",
        -.40,
        ["Death-Quit"])

        self.hide()

    def createButton(self, text, verticalPos, eventArgs):
        maps = loader.loadModel("gui/button_map")
        btnGeom = (maps.find("**/btn_ready"),
        maps.find("**/btn_click"),
        maps.find("**/btn_rollover"),
        maps.find("**/btn_disabled"))
        sound = loader.loadSfx("Audio/click.wav")
        sound.setVolume(0.1)
        btn = DirectButton(
        text = text,
        text_fg = (1,1,1,1),
        text_scale = 0.05,
        text_pos = (0.02, -0.013),
        text_align = TextNode.ACenter,
        scale = 2,
        pos = (0, 0, verticalPos),
        #geom = btnGeom,
        relief = 0,
        frameColor = (0,0,0,0),
        command = base.messenger.send,
        extraArgs = eventArgs,
        pressEffect = True,
        rolloverSound = None,
        clickSound = sound)
        btn.reparentTo(self.frameDeath)

    def show(self):
        self.frameDeath.show()

    def hide(self):
        self.frameDeath.hide()
