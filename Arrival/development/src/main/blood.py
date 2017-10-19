# Panda3D imoprts
from direct.showbase.DirectObject import DirectObject
from direct.gui.DirectGui import DirectWaitBar, DGG
from panda3d.core import TextNode

class HeroBlood(DirectObject):
    """docstring for Blood"""
    def __init__(self):
        self.value = 100
        self.maxVal = 100
        #text text_pos value frameSize pos
        frameTex = loader.loadTexture("assets/gui/blood.jpg")
        barTex = loader.loadTexture("assets/gui/btn_click.png")
        self.lifeBar = DirectWaitBar(
            text = str(self.value),
            text_fg = (1,1,1,0.6),
            text_pos = (0.8, 1.92, 0),
            text_align = TextNode.ALeft,
            value = self.value,
            barColor = (0, 0.95, 0.25, 1),
            frameTexture = frameTex,
            barTexture = barTex,
            barRelief = DGG.RIDGE,
            barBorderWidth = (0.01, 0.01),
            borderWidth = (0.01, 0.01),
            relief = DGG.SUNKEN,
            frameSize = (0.25, 0.8, 1.92, 1.97),
            pos = (base.a2dLeft,0,base.a2dBottom)
        )
        self.lifeBar.setTransparency(1)
        self.hide()

    def show(self):
        self.lifeBar.show()

    def hide(self):
        self.lifeBar.hide()

    def setLifeBarValue(self, newValue,name='Player'):
        self.value = newValue
        self.lifeBar["text"] = str(self.value)+"/"+ str(self.maxVal)+' '+name
        self.lifeBar["value"] = self.value*100/self.maxVal

    def setLifeBarMaxValue(self,newValue,name='Player'):
        self.maxVal = newValue
        self.lifeBar["text"] =  str(self.value)+"/"+ str(self.maxVal)+' '+name
        self.lifeBar["value"] =  self.value*100/self.maxVal


class BossBlood(DirectObject):
    def __init__(self):
        self.value = 100
        frameTex = loader.loadTexture("assets/gui/blood.jpg")
        barTex = loader.loadTexture("assets/gui/btn_click.png")
        self.lifeBar = DirectWaitBar(
            text = "Boss",
            text_fg = (1,1,1,1),
            text_pos=(1.0, 0.07, 0),
            text_align = TextNode.ARight,
            value = self.value,
            #0, 1, 0.25, 1   0.8,0.05,0.10,1
            #barTexture = "assets/gui/btn_click.png",
            barColor = (0.8,0.05,0.10,1),
            frameTexture = frameTex,
            barTexture = barTex,
            barRelief = DGG.RIDGE,
            barBorderWidth = (0.01, 0.01),
            borderWidth = (0.01, 0.01),
            relief = DGG.SUNKEN,
            frameSize = (0, 3.2, 0, 0.05),
            pos = (base.a2dLeft,0,base.a2dBottom))
        self.lifeBar.setTransparency(1)
        self.hide()

    def show(self):
        self.lifeBar["value"] = self.value
        self.lifeBar.show()

    def hide(self):
        self.lifeBar.hide()

    def setLifeBarValue(self, newValue,name='BOSS'):
        self.value = newValue
        self.lifeBar["value"] =  self.value*100/self.maxVal
        self.lifeBar["text"] = str(self.value)+"/"+ str(self.maxVal)+' BOSS'
    def setLifeBarMaxValue(self,newValue,name='BOSS'):
        self.maxVal = newValue
        self.lifeBar["text"] =  str(self.value)+"/"+ str(self.maxVal)+' BOSS'
        self.lifeBar["value"] =  self.value*100/self.maxVal

class MonsterBlood(DirectObject):
    def __init__(self):
        self.value = 100
        self.lifeBar = DirectWaitBar(
            text = "Monster",
            text_fg = (1,1,1,1),
            text_pos = (1.2, -0.18, 0),
            text_align = TextNode.ARight,
            value = self.value,
            barColor = (0, 1, 0.25, 1),
            barRelief = DGG.RAISED,
            barBorderWidth = (0.03, 0.03),
            borderWidth = (0.01, 0.01),
            relief = DGG.RIDGE,
            frameColor = (0.8,0.05,0.10,1),
            frameSize = (0, 1.2, 0, -0.1),
            pos = (0.2,0,base.a2dTop-0.15))
        self.lifeBar.setTransparency(1)
        self.hide()

    def show(self):
        self.lifeBar["value"] = self.value
        self.lifeBar.show()

    def hide(self):
        self.lifeBar.hide()

    def setLifeBarValue(self, newValue):
        self.lifeBar["value"] = newValue
