#coding:utf-8
import sys
import os
import time
import json

class ArchiveManager:
    """docstring for ArchiveManager"""
    def __init__(self):
        self.basedir = os.path.join(sys.path[0],"ArchiveFiles")
        if not os.path.exists(self.basedir):
            os.makedirs(self.basedir)
        self.files = [os.path.join(self.basedir, "Archive1.txt"),
                      os.path.join(self.basedir, "Archive2.txt"),
                      os.path.join(self.basedir, "Archive3.txt")]

        if os.path.exists(self.files[0]):
            fd = os.open(self.files[0],os.O_RDWR)
            ret = os.read(fd,100)
            os.close(fd)
        else:
            open(self.files[0],"w").close()

        if os.path.exists(self.files[1]):
            fd = os.open(self.files[1],os.O_RDWR)
            ret = os.read(fd,100)
            os.close(fd)
        else:
            open(self.files[1],"w").close()

        if os.path.exists(self.files[2]):
            fd = os.open(self.files[2],os.O_RDWR)
            ret = os.read(fd,100)
            os.close(fd)
        else:
            open(self.files[2],"w").close()
    #保存内容到指定文件
    def SaveArchive(self, ArchiveID, archive):
        fd = open(self.files[ArchiveID],"w")
        head = {}
        head["currRoom"] = archive["preRoomCode"]
        head["timestamp"] = time.strftime("%Y-%m-%d %H:%M:%S", time.localtime())
        fd.writelines( json.dumps(head) )
        fd.write('\n')
        content = json.dumps(archive)
        fd.writelines(content)
        fd.close()
    #返回指定文件的内容
    def ReadArchive(self,ArchiveID):
        fd = open(self.files[ArchiveID],'r')
        head = fd.readline()
        content = fd.readline()
        fd.close()
        if content=='':
            return None
        else:
            return json.loads(content.encode('utf-8'),encoding='utf-8')
    #删除指定文件的内容
    def DeleteArchive(self, ArchiveID):
        f = open(self.files[ArchiveID], "w")
        f.write("")
        f.close()

    def GetArchiveListShortMsg(self):
        shortMsg = []
        for index in range(3):
            fd = open(self.files[index],'r')
            head = fd.readline()
            if len(head) == 0:
                shortMsg.append({})
            else:
                shortMsg.append( json.loads(head) )
            fd.close()
        return shortMsg



