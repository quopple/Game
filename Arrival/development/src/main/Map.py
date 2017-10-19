#coding:utf-8
from panda3d.core import TextNode, TexturePool
from direct.gui.DirectGui import (
    DirectFrame,
    DirectLabel,
    DirectButton)
from pandac.PandaModules import Filename

import os


class Map:
  def __init__(self,path):
    self.path = path
    self.tex = loader.loadTexture( "map.png")
    self.frameMap = DirectFrame(
        # image = "map.png",
        # image_scale = (0.25, 1,0.25),
        frameTexture = self.tex,
        #frameSize=(1, 1.7, base.a2dBottom+0.05 , base.a2dTop - 1.5), frameColor=(1, 1, 1, 0.3)
        frameSize=(1, 1.7, base.a2dBottom+1.5 , base.a2dTop - 0.05), frameColor=(1, 1, 1, 0.3)
        # pos = (base.a2dRight,0,base.a2dTop-0.25)
        )
    self.frameMap.setTransparency(1)

    self.hide()
  def changeMap(self , newMap = "map.png"):
    # self.frameMap["image"] = newMap
    # self.frameMap.setImage()
    self.frameMap.clearTexture()
    TexturePool.releaseTexture(self.tex)
    self.tex = loader.loadTexture( Filename.fromOsSpecific( os.path.join(self.path , newMap)))
    self.frameMap["frameTexture"] = self.tex


  def show(self):
      self.frameMap.show()

  def hide(self):
      self.frameMap.hide()
