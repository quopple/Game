# coding=UTF-8
from PIL import Image,ImageDraw
import os

class MiniMap:
    def __init__(self, drawList = [0,0,0,0,0,0,0,0,0], path = ""):
        self.mapW=310
        self.mapH=310

        self.bg=(0,0,0)
        self.lineBG=(255,0,0)


        self.ToVisitBG=(0,255,0)
        self.BossBG=(0,0,255)
        self.LeapBG=(0,255,255)
        self.RoomBG=(255,255,255)
        self.BGs = {1:self.RoomBG,4:self.ToVisitBG,2:self.BossBG,3:self.LeapBG}

        self.LineList=[(100,0,105,310),(205,0,210,310),(0,100,310,105),(0,205,310,210)]
        self.MapList = [(0,0,100,100),(105,0,205,100),(210,0,310,100),
                        (0,105,100,205),(105,105,205,205),(210,105,310,205),
                        (0,210,100,310),(105,210,205,310),(210,210,310,310)]

        self.DrawList = drawList

        self.Path = path

        if not os.path.exists( os.path.join(self.Path , "map.png")):
            open(self.Path + "map.png", "w").close()
    '''
    画图
    '''
    def drawMap(self, drawList = (0,0,0,0,1,0,0,0,0)):
        # print "drawList",drawList
        blank=Image.new('RGB',(self.mapW,self.mapH),self.bg)
        DrawObject=ImageDraw.Draw(blank)
        for line in self.LineList:
            DrawObject.rectangle(line,self.lineBG)
        for i in range(0,len(drawList)):
            if not (drawList[i] == 0):
                DrawObject.rectangle(self.MapList[i],self.BGs[drawList[i]])
        blank.save(os.path.join(self.Path , "map.png"))
        return blank
