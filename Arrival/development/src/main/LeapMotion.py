
# coding=UTF-8
import os
import sys
import inspect
import thread
import time
import traceback
import math 
from panda3d.core import LPoint3
src_dir = os.path.dirname(inspect.getfile(inspect.currentframe()))
lib_dir = os.path.abspath(os.path.join(src_dir, './lib'))
sys.path.insert(1000, lib_dir)

arch_dir = './lib/x64' if sys.maxsize > 2**32 else './lib/x86'
sys.path.insert(1000, os.path.abspath(os.path.join(src_dir, arch_dir)))

import Leap


from direct.showbase.DirectObject import DirectObject

class LeapListener(Leap.Listener,DirectObject):
    def __init__(self):
        Leap.Listener.__init__(self)
        DirectObject.__init__(self)
        self.controller = Leap.Controller()
        self.controller.add_listener(self)
        self.enable = False
    def release(self):
        print "release"
        self.controller.remove_listener(self)

    def on_init(self, controller):
        ###leapmotion程序启动时需要完成的动作的代码
        print "init"
        self.LastHand = [0,0,0]
        self.LastIndexFinger =[ 0,0,0 ]
        self.origin = (-140,320)

        ###调节手势捕捉的灵敏度，即运动多少距离判断为触发了手势
        self.HANDSENSITIVITY = 3
        self.FINGERSENSITIVITY = 15
        self.FINGER_HAND_SENSETIVITY = 5

        self.lastClick = 0
        self.preTime = 0
        self.isConnected = False
        self.lastGrab = 0.0


    def on_connect(self, controller):
        ####这里写当设备初始化完成时的代码
        print 'connect'
        self.isConnected = True

    def on_disconnect(self, controller):
        ### 设备移除时需要做的动作的代码
        print 'disconnect'
        self.isConnected = False

    def on_exit(self, controller):
        ###当leapmotion程序退出时需要做的动作的代码
        print "Exited"
        pass

    def on_frame(self, controller):
        ### Get the most recent frame and report some basic information

        # print '手的方向向量的x坐标',hand.direction.x                           ## 获取手的方向向量 【x,y,z】
        # print '手的法向量的x坐标',        hand.palm_normal.x                  ##获取当前手的法向量 【x,y,z】
        # print '手的握紧程度',               hand.grab_strength                      ## 获取手的抓取强度，在0-1之间，当手完全张开时强度为0，当手握成拳头时为1
        # print '手的位置的x坐标',     hand.stabilized_palm_position.x                 ## 获取手的当前坐标位置 【x,y,z】
        # print "手的ID是：",               hand.id                                     ## 获取手的ID，在连贯捕捉的帧中这个ＩＤ是相同的，但是中间断开时会改变
        # print '这是左手吗？ ',          hand.is_left                                    ## 判断当前手是否为左手
        # print '这是右手吗?  ',             hand.is_right                               ## 判断当前手是否为右手
        # print '当前手对象有效吗？ ',   hand.is_valid                               ## 判断当前手对象是否有效
        # print '手的移动速度的x坐标',   hand.palm_velocity.x                    ## 获取当前手的移动速度 ms/s 【x,y,z】
        # print '手的稳定位置的x坐标', hand.stabilized_palm_position.x   ## 获取当前手掌的稳定位置，这个位置的变化会更平滑稳定，利于2D交互
        # print '当前手被捕获的时间',    hand.time_visible                           ## 当前手已经被leapmotion捕获的时间    
        if not self.enable:
            return
        frame = controller.frame()
        for hand in frame.hands:
            if not hand.is_valid:
                continue
            if hand.is_left:
                # if hand.time_visible - self.preTime < 0.005:
                #     print hand.time_visible,' ',self.preTime
                #     return
                # self.preTime = hand.time_visible
                    
                newPos = [0, 0,0]
                iBox = frame.interaction_box
                leapPoint = hand.palm_position
                pos = iBox.normalize_point(leapPoint,False)
                pos = LPoint3(pos[0],pos[1],pos[2])
                pos[0] = pos[0] if pos[0] > 0 else 0
                pos[0] = pos[0] if pos[0] < 1 else 1
                pos[1] = pos[1] if pos[1] > 0 else 0
                pos[1] = pos[1] if pos[1] < 1 else 1

                for i in range(0,2):
                    if abs(self.LastHand[i]-pos[i]) < 0.001:# or abs(self.LastHand[i]-pos[i]) > 0.2:
                        pos[i] = self.LastHand[i]
                    else:
                        self.LastHand[i] = pos[i] 
                base.messenger.send('new-pos',[pos])
            if hand.is_right:
                #print "hand.sphere_radius",hand.sphere_radius
                if hand.sphere_radius < 45:
                    base.messenger.send('fire')
                    #print 'fire'
                
                #print hand.palm_normal
                if hand.palm_normal[1] > 0.45:
                    base.messenger.send('pick')
                    # print 'pick'

if __name__ == '__main__':
    listener = LeapListener()
    controller = Leap.Controller()

    controller.add_listener(listener)

    print "press Enter to quit..."

    try:
        sys.stdin.readline()
    except KeyboardInterrupt:
        pass
    finally:
        controller.remove_listener(listener)
