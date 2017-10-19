import time
import logging

from panda3d.core import (
        MovieTexture,
        CardMaker
        )

def loadVideo(videoFileName,loop=False):
        videoPathStr = 'Video/{}'
        videoPathStr = videoPathStr.format(videoFileName)

        
        try:
            tex = MovieTexture(videoFileName)
            success = tex.read(videoPathStr)
            assert success, "Failed to load video!"

            # Set up a fullscreen card to set the video texture on.
            cm = CardMaker("My Fullscreen Card")
            cm.setFrameFullscreenQuad()
            # Tell the CardMaker to create texture coordinates that take into
            # account the padding region of the texture.
            cm.setUvRange(tex)
            # Now place the card in the scene graph and apply the texture to it.
            card = render2d.attachNewNode(cm.generate())
            card.setTexture(tex)
            card.hide()
            sound = loader.loadMusic(videoPathStr)
            # set loop false
            sound.setLoop(loop)
            # Synchronize the video to the sound.
            tex.synchronizeTo(sound)

            return sound,card
        except Exception as e:
            #logging.debug("loadvideo: {}".format(traceback.format_exc()))
            pass
        return sound,card
        

def print_func_time(func):
    def wrapper(*args,**argv):
        logging.info('[funcName:{}] enter time[{}]'.format(func.__name__,time.time()))
        #print func.__name__
        func(*args,**argv)
        logging.info('[funcName:{}] exit time[{}]'.format(func.__name__,time.time()))
    return wrapper  