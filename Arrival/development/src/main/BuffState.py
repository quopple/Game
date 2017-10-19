from direct.gui.DirectButton import  DirectFrame
from direct.showbase.DirectObject import DirectObject
import logging
from Item import *

attackStyleFramePos = -1

class BuffState(DirectObject):
    buff = {}
    num = 0
    defaultWidth = 0.08
    def __init__(self):
        texture = loader.loadTexture("assets/gui/heroPic.png")
        self.heroPic = DirectFrame(frameTexture=texture, frameColor=(1, 1, 1, 1),
                            frameSize=(-1.78, -1.56, base.a2dTop-0.02, base.a2dTop - 0.25))
        self.heroPic.hide()

    def show(self):
        self.heroPic.show()
        for frame in self.buff.itervalues():
            if isinstance( frame,tuple):
                frame[1].show()
            else:
                frame.show()
        
    def hide(self):
        self.heroPic.hide()
        for frame in self.buff.itervalues():
            if isinstance( frame,tuple):
                frame[1].hide()
            else:
                frame.hide()

    def addBuff(self,entry):
        buffItem = entry.getIntoNodePath().getPythonTag("Item")
        self._addBuff( buffItem )

    def _addBuff(self,buffItem):
        item = base.loader.loadModel(ModelPath + "model_" + buffItem.itemName)
        texture = item.findAllTextures()
        if isinstance(buffItem, (RayItem, ShotgunItem)):
            if self.buff.has_key("attackStyleFrame"):
                self.buff["attackStyleFrame"][1].destroy()
            self.buff["attackStyleFrame"] = buffItem.itemName , self.CreateBuffFrame(attackStyleFramePos, texture)
        elif isinstance(buffItem,(LifeItem,AoeDamageItem)):
            return
        elif not self.buff.has_key(buffItem.itemName):
            self.buff[buffItem.itemName] = self.CreateBuffFrame(self.num,texture)
            self.num+=1
        else:
            numStr = self.buff[buffItem.itemName]["text"]
            self.buff[buffItem.itemName]["text"] = str( int( numStr ) + 1 )

    def CreateBuffFrame(self,numTh,texture):
        startX = -1.25 + numTh * (self.defaultWidth+0.02)
        frame = DirectFrame(frameTexture = texture,frameColor = (1,1,1,0.5),frameSize=( startX ,startX + self.defaultWidth ,base.a2dTop - 0.15, base.a2dTop - 0.25),
                            text="1", text_fg=(1, 0, 0, 1),
                            text_pos=(startX + 0.05, 0.73, base.a2dTop), text_scale=(0.03, 0.03),
                            text_align=TextNode.ACenter
                            )
        return frame

    def clear(self):
        if self.buff.has_key("attackStyleFrame"):
            self.buff["attackStyleFrame"][1].destroy()
            self.buff.pop("attackStyleFrame")
        for frame in self.buff.itervalues():
            frame.destroy()
        self.buff.clear()

    @staticmethod
    def ToDict(buffState):
        dict = {}
        buff = {}
        for k,v in buffState.buff.items():
            if k == "attackStyleFrame":
                buff[k] = v[0]
                logging.info(v[0])
            else:
                buff[k] = v["text"]
        dict["buff"] = buff
        return dict

    @staticmethod
    def ToObj(dict):
        buffList = BuffState()
        buff = dict["buff"]
        counter = 0
        for k,v in buff.items():
            if k == "attackStyleFrame":
                item = base.loader.loadModel(ModelPath + "model_" + v)
                texture = item.findAllTextures()
                buffFrame = buffList.CreateBuffFrame(attackStyleFramePos,texture)
                buffList.buff[k] = v,buffFrame
            else:
                item = base.loader.loadModel(ModelPath + "model_" + k)
                texture = item.findAllTextures()
                buffFrame = buffList.CreateBuffFrame(counter, texture)
                buffFrame["text"] = v
                buffList.buff[k] = buffFrame
                counter+=1
        buffList.hide()
        return buffList

    @staticmethod
    def reInit(self,dict):
        if len(self.buff) != 0:
            self.clear()
        buff = dict["buff"]
        counter = 0
        for k,v in buff.items():
            if k == "attackStyleFrame":
                item = base.loader.loadModel(ModelPath + "model_" + v)
                texture = item.findAllTextures()
                buffFrame = self.CreateBuffFrame(attackStyleFramePos,texture)
                self.buff[k] = v,buffFrame
            else:
                item = base.loader.loadModel(ModelPath + "model_" + k)
                texture = item.findAllTextures()
                buffFrame = self.CreateBuffFrame(counter, texture)
                buffFrame["text"] = v
                self.buff[k] = buffFrame
                counter+=1
        self.hide()





