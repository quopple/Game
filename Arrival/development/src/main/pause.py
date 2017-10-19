#coding:utf-8

from panda3d.core import TextNode
from direct.gui.DirectGui import (
    DirectFrame,
    DirectLabel,
    DirectButton)

class Pause:
  def __init__(self):
    self.framePause = DirectFrame(
        image = "gui/BackGround.png",
        image_scale = (1.7778, 1, 1),
        frameSize = (base.a2dLeft, base.a2dRight,
                     base.a2dBottom, base.a2dTop),
        frameColor = (0, 0, 0, 0))
    self.framePause.setTransparency(1)

    self.title = DirectLabel(
        scale = 0.15,
        text_align = TextNode.ALeft,
        pos = (-0.2, 0, 0.5),
        frameColor = (0, 0, 0, 0),
        text = "Pause",
        text_fg = (1,1,1,1))
    self.title.setTransparency(1)
    self.title.reparentTo(self.framePause)

    self.btn_continue = self.createButton(
        "Continue",
        -.25,
        ["Pause-Continue"])

    self.btn_option = self.createButton(
        "Option",
        -.40,
        ["Pause-Option"])

    self.btnExit = self.createButton(
       "Back",
        -.55,
        ["Pause-Back"])

    self.hide()

  def createButton(self, text, verticalPos, eventArgs):
        maps = loader.loadModel("gui/button_map")
        btnGeom = (maps.find("**/btn_ready"),
                    maps.find("**/btn_click"),
                    maps.find("**/btn_rollover"),
                    maps.find("**/btn_disabled"))
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
            pressEffect = False,
            rolloverSound = None,
            clickSound = None)
        btn.reparentTo(self.framePause)

  def show(self):
      self.framePause.show()

  def hide(self):
      self.framePause.hide()
