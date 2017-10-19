#coding:utf-8

from panda3d.core import TextNode
from direct.gui.DirectGui import (
    DirectFrame,
    DirectLabel,
    DirectButton)



class Menu:
    def __init__(self):
        self.frameMain = DirectFrame(
            image = "gui/BackGround.png",
            image_scale = (1.7778, 1, 1),
            frameSize = (base.a2dLeft, base.a2dRight,
                         base.a2dBottom, base.a2dTop),
            frameColor = (0, 0, 0, 0))
        self.frameMain.setTransparency(1)

        # self.title = DirectLabel(
        #     scale = 0.3,
        #     text_align = TextNode.ALeft,
        #     pos = (-0.2, 0, 0.4),
        #     frameColor = (0, 0, 0, 0),
        #     text = "Arrival",
        #     text_fg = (1,0,0,1))
        # self.title.setTransparency(1)
        # self.title.reparentTo(self.frameMain)

        self.btn_newgame = self.createButton(
            "Start",
            -.10,
            ["Menu-Game"])

        self.btn_option = self.createButton(
            "Option",
            -.25,
            ["Menu-Option"])

        self.btnExit = self.createButton(
            "Quit",
            -.40,
            ["Menu-Quit"])

        self.hide()

    def createButton(self, text, verticalPos, eventArgs):
        maps = loader.loadModel("gui/button_map")
        btnGeom = (maps.find("**/btn_ready"),
                    maps.find("**/btn_click"),
                    maps.find("**/btn_rollover"),
                    maps.find("**/btn_disabled"))
        sound = loader.loadSfx("Audio/click.wav")
        btn = DirectButton(
            text = text,
            text_fg = (1,1,1,1),
            text_scale = 0.05,
            text_pos = (0.25, -0.013),
            text_align = TextNode.ACenter,
            #text_font = loader.loadFont('DreamerOne Bold.ttf'),
            scale = 2,
            pos = (base.a2dLeft + 1.8, 0, verticalPos),
            geom = btnGeom,
            relief = 0,
            frameColor = (0,0,0,0),
            command = base.messenger.send,
            extraArgs = eventArgs,
            pressEffect = True,
            rolloverSound = None,
            clickSound = sound)
        btn.reparentTo(self.frameMain)
    def show(self):
        self.frameMain.show()

    def hide(self):
        self.frameMain.hide()
