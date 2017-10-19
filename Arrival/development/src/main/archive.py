#coding:utf-8
from panda3d.core import TextNode
from direct.gui.DirectGui import (
    DirectFrame,
    DirectLabel,
    DirectButton,
    DirectScrolledList,
    DirectRadioButton)
from direct.gui.OnscreenText import OnscreenText

class Archive:
    """docstring for Archive"""
    def __init__(self):
        self.archivesShotMsg = []
        self.frameArchive = DirectFrame(
            image = "gui/BackGround_a.png",
            image_scale = (1.7778, 1, 1),
            frameSize = (base.a2dLeft, base.a2dRight,
                         base.a2dBottom, base.a2dTop),
            frameColor = (0, 0, 0, 0))
        self.frameArchive.setTransparency(1)

        ArchiveFrameTexture = loader.loadTexture("gui/ArchiveFrameBG.png")
        self.frameArchive1 = DirectFrame(
            frameTexture = ArchiveFrameTexture,
            frameSize = (-1.4,-0.6,
                         base.a2dBottom+0.5,base.a2dTop-0.4),
            frameColor = (1,1,1,0.5),

        )

        self.frameArchive1.reparentTo(self.frameArchive)

        self.frameArchive2 = DirectFrame(
            frameSize = (-0.4,0.4,
                         base.a2dBottom+0.5,base.a2dTop-0.4),
            frameColor = (1,1,1,0.5),
            frameTexture=ArchiveFrameTexture
        )
        self.frameArchive2.reparentTo(self.frameArchive)

        self.frameArchive3 = DirectFrame(
            frameSize = (0.6,1.4,
                         base.a2dBottom+0.5,base.a2dTop-0.4),
            frameColor = (1,1,1,0.5),
            frameTexture=ArchiveFrameTexture
        )
        self.frameArchive3.reparentTo(self.frameArchive)

        self.v=[0]

        self.archiveImg = loader.loadTexture("gui/ArchiveImg.png")
        self.questionMark = loader.loadTexture("gui/QuestionMark.jpg")
        self.pictures = [
            DirectFrame(frameSize=(-1.3, -0.7,base.a2dBottom + 0.9, base.a2dTop - 0.5),frameColor=(1, 1, 1, 1),frameTexture = self.questionMark),
            DirectFrame(frameSize=(-0.3, 0.3, base.a2dBottom + 0.9, base.a2dTop - 0.5), frameColor=(1, 1, 1, 1),frameTexture = self.questionMark),
            DirectFrame(frameSize=(0.7,1.3, base.a2dBottom + 0.9, base.a2dTop - 0.5), frameColor=(1, 1, 1, 1),frameTexture = self.questionMark)
        ]
        self.pictures[0].reparentTo(self.frameArchive1)
        self.pictures[1].reparentTo(self.frameArchive2)
        self.pictures[2].reparentTo(self.frameArchive3)

        self.buttons = [
            DirectRadioButton(variable=self.v, value=[0], scale=0.05, pos=(-0.98, 0, base.a2dTop-1.4),command = self.updateUI),
            DirectRadioButton(variable=self.v, value=[1], scale=0.05, pos=(0.02, 0, base.a2dTop-1.4),command = self.updateUI),
            DirectRadioButton(variable=self.v, value=[2], scale=0.05, pos=(1.02, 0, base.a2dTop-1.4),command = self.updateUI)
        ]
        self.buttons[0].reparentTo(self.frameArchive1)
        self.buttons[1].reparentTo(self.frameArchive2)
        self.buttons[2].reparentTo(self.frameArchive3)
        for button in self.buttons:
            button.setOthers(self.buttons)

        titles0 = [
            OnscreenText(scale = .05, align = TextNode.ACenter, pos=(-1.0, base.a2dBottom+0.85), text="time", fg = (0,0,0,1)),
            OnscreenText(scale = .05, align = TextNode.ACenter, pos=(-1.0, base.a2dBottom+0.8), text="room", fg = (0,0,0,1)),
            #    DirectLabel(frameColor = (0, 0, 0, 0),scale = .05, align = TextNode.ALeft, pos=(-1.1, 0, base.a2dBottom+0.75), text="attribute", fg = (0,0,0,1))
        ]
        titles0[0].hide()
        titles0[1].hide()
        # titles0[0].reparentTo(self.frameArchive1)
        # titles0[1].reparentTo(self.frameArchive1)
        #  titles0[2].reparentTo(self.frameArchive1)

        titles1 = [
            OnscreenText(scale = .05, align = TextNode.ACenter, pos=(-0.0, base.a2dBottom+0.85), text="time", fg = (0,0,0,1)),
            OnscreenText(scale = .05, align = TextNode.ACenter, pos=(-0.0, base.a2dBottom+0.8), text="room", fg = (0,0,0,1)),
            #     DirectLabel(frameColor = (0, 0, 0, 0),scale = .05, align = TextNode.ALeft, pos=(-0.1, 0, base.a2dBottom+0.75), text="attribute", fg = (0,0,0,1))
        ]
        titles1[0].hide()
        titles1[1].hide()
        # titles1[0].reparentTo(self.frameArchive2)
        # titles1[1].reparentTo(self.frameArchive2)
        #  titles1[2].reparentTo(self.frameArchive2)

        titles2 = [
            OnscreenText(scale = .05, align = TextNode.ACenter, pos=(1, base.a2dBottom+0.85), text="time", fg = (0,0,0,1)),
            OnscreenText(scale = .05, align = TextNode.ACenter, pos=(1, base.a2dBottom+0.8), text="room", fg = (0,0,0,1)),
            #     DirectLabel(frameColor = (0, 0, 0, 0),scale = .05, align = TextNode.ALeft, pos=(0.9, 0, base.a2dBottom+0.75), text="attribute", fg = (0,0,0,1))
        ]
        titles2[0].hide()
        titles2[1].hide()
        # titles2[0].reparentTo(self.frameArchive3)
        # titles2[1].reparentTo(self.frameArchive3)
        #  titles2[2].reparentTo(self.frameArchive3)
        self.title = [ titles0,titles1,titles2 ]

        self.btn_load = self.createButton(
            "Load",
            -0.6,
            ["LoadArchive"])
        self.btn_delete = self.createButton(
            "Delete",
            -0.8,
            ["DeleteArchive"])
        self.btn_newgame = self.createButton(
            "NewGame",
            -0.7,
            ["NewGame"])

        self.hide()


    def createButton(self, text, horizontalPos, eventArgs):
        sound = loader.loadSfx("Audio/click.wav")
        maps = loader.loadModel("gui/button_map")
        btnGeom = (maps.find("**/btn_ready"),
                    maps.find("**/btn_click"),
                    maps.find("**/btn_rollover"),
                    maps.find("**/btn_disabled"))
        btn = DirectButton(
            text = text,
            text_fg = (1,1,1,1),
            text_scale = 0.05,
            text_pos = (0.125, -0.013),
            text_align = TextNode.ALeft,
            scale = 2,
            geom = btnGeom,
            pos = (base.a2dRight - 0.6, 0, horizontalPos),
           # pos = (horizontalPos, 0, -.7),
            relief = 0,
            frameColor = (0,0,0,0),
            command = base.messenger.send,
            extraArgs = eventArgs,
            pressEffect = True,
            rolloverSound = None,
            clickSound = sound)
        btn.reparentTo(self.frameArchive)
        return btn

    def updateUI(self):
        if len(self.archivesShotMsg) == 0:
            base.messenger.send("UpdateArchive")
        else:
            if len(self.archivesShotMsg[self.v[0]]) == 0:
                self.btn_delete.hide()
                self.btn_load.hide()
                self.btn_newgame.show()
            else:
                self.btn_delete.show()
                self.btn_load.show()
                self.btn_newgame.hide()

    def show(self,archiveListShortMsg):
        self.archivesShotMsg = archiveListShortMsg

        for index in range(3):
            self.title[index][0].show()
            self.title[index][1].show()
            if len(self.archivesShotMsg[index]) == 0:
                self.pictures[index]["frameTexture"] = self.questionMark
                self.title[index][0].setText("?")
                self.title[index][1].setText("?")
            else:
                self.pictures[index]["frameTexture"]= self.archiveImg
                self.title[index][0].setText( "createTime : " + str( archiveListShortMsg[index]["timestamp"]))
                self.title[index][1].setText("currRoom : "+str(archiveListShortMsg[index]["currRoom"]))

        self.updateUI()
        self.frameArchive.show()

    def hide(self):
        for index in range(3):
            self.title[index][0].hide()
            self.title[index][1].hide()
        self.frameArchive.hide()