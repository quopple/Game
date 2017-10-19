class MovableObject(object):
    def __init__(self):
        self.model = None
        self.speed = 0
        self.direction = [0,0,0]
        self.position = None
        self.colliderNodePath = None
        self.colliderName = ''
        self.sounds = {}