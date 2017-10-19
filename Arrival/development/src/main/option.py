#coding:utf-8
from panda3d.core import TextNode
from direct.gui.DirectGui import (
    DirectFrame,
    DirectLabel,
    DirectButton,
    DirectSlider,
    DirectCheckButton)

class Option:
    """docstring for Option"""
    def __init__(self):
        self.testMusic = loader.loadMusic("Audio/click.wav")
        self.testSfx = loader.loadSfx("Audio/click.wav")
        self.frameOption = DirectFrame(
            image = "gui/BackGround_o.png",
            image_scale = (1.7778, 1, 1),
            frameSize = (base.a2dLeft, base.a2dRight,
                         base.a2dBottom, base.a2dTop),
            frameColor = (0, 0, 0, 0))
        self.frameOption.setTransparency(1)

        self.title = DirectLabel(
            scale = 0.15,
            text_align = TextNode.ALeft,
            pos = (-0.3, 0, 0.5),
            frameColor = (0, 0, 0, 0),
            text = "",
            text_fg = (1,1,1,1))
        self.title.setTransparency(1)
        self.title.reparentTo(self.frameOption)

        self.title_volume = DirectLabel(
            scale = 0.1,
            text_align = TextNode.ALeft,
            pos = (base.a2dLeft + 1.3 , 0, -0.2),
            frameColor = (0, 0, 0, 0),
            text = "Music",
            text_fg = (1,1,1,1))
        self.title_volume.setTransparency(1)
        self.title_volume.reparentTo(self.frameOption)

        self.slider_volume = DirectSlider(
            pos = (base.a2dLeft + 2.2, 0, -0.2),
            value = 50,
            range = (0,100),
            pageSize = 5,
            scale = 0.5,
            command = base.messenger.send,
            extraArgs = ["ChangeVolume"]
        )
        self.slider_volume.reparentTo(self.frameOption)

        self.testMusicBtn = self.createButton(-0.2,self.testMusic)

        self.title_sound = DirectLabel(
            scale = 0.1,
            text_align = TextNode.ALeft,
            pos = (base.a2dLeft + 1.3 , 0, -0.4),
            frameColor = (0, 0, 0, 0),
            text = "Sfx",
            text_fg = (1,1,1,1))
        self.title_sound.setTransparency(1)
        self.title_sound.reparentTo(self.frameOption)
        self.slider_sound = DirectSlider(
            pos = (base.a2dLeft + 2.2, 0, -0.4),
            value = 50,
            range = (0,100),
            pageSize = 5,
            #frameSize = (1,1,1,1)
            scale = 0.5,
            command = base.messenger.send,
            extraArgs = ["ChangeSound"]
        )
        self.slider_sound.reparentTo(self.frameOption)
        self.testSfxBtn = self.createButton(-0.4, self.testSfx)
        # self.title_leapmotion = DirectLabel(
        #   scale = 0.1,
        #   text_align = TextNode.ALeft,
        #   pos = (base.a2dLeft + 0.6 , 0, -0.6),
        #   frameColor = (0, 0, 0, 0),
        #   text = "Leapmotion",
        #   text_fg = (1,1,1,1))
        # self.title_leapmotion.reparentTo(self.frameOption)
        # self.cbtn_leapmotion = DirectCheckButton(
        #   text = "needed",text_fg=(1,1,1,1),
        #   scale = .1,
        #   pos = (base.a2dLeft + 1.5 , 0, -0.6),
        #   command = base.messenger.send,
        #   extraArgs = ["ChangeLeapmotion"])
        # self.cbtn_leapmotion.reparentTo(self.frameOption)


        self.hide()

    def createButton(self, verticalPos, eventArgs):
        maps = loader.loadModel("gui/button_map")
        btnGeom = (maps.find("**/btn_ready"),
                    maps.find("**/btn_click"),
                    maps.find("**/btn_rollover"),
                    maps.find("**/btn_disabled"))
        btn = DirectButton(
            text="apply",
            text_fg=(1, 1, 1, 1),
            text_scale=0.05,
            text_pos=(0.15, -0.013),
            text_align=TextNode.ALeft,
            scale = 2,
            geom = btnGeom,
            pos = (base.a2dRight - 0.7, 0, verticalPos),
            relief = 0,
            frameColor = (1,1,1,1),
            command = self.testPlay,
            extraArgs = [eventArgs,],
            pressEffect = True,
            rolloverSound = None)
        btn.reparentTo(self.frameOption)
        btn.setTransparency(1)
        return btn

    def testPlay(self,sound):
        sound.play()

    def show(self):
        self.frameOption.show()


    def hide(self):
        self.frameOption.hide()