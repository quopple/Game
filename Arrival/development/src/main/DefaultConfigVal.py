from DefaultMonsterVal import *
from panda3d.core import LVecBase2
# hero setting
defaultHeroHP = 2000
defaultHeroMaxHPMax = defaultHeroHP*3
defaultHeroAttackPower = 20
defaultHeroAttackPowerMax = defaultHeroAttackPower*3
defaultHeroAttackSpeed = 2
defaultHeroAttackSpeedMax = defaultHeroAttackSpeed*3
defaultHeroMoveSpeed = 10
defaultHeroMoveSpeedMax = defaultHeroMoveSpeed*1.5
defaultHeroHitByMonsterDamageVal = 10
defaultHeroHitByMonsterDamageValMax = defaultHeroHitByMonsterDamageVal*3

# item setting
standarHitRate = 1
defaultDamageVal = 50
defaultFlection = 30
defaultScopeDamageVal = 50
defaultIncreaseHP = 200
defaultIncreaseMoveSpeed = defaultHeroMoveSpeed/4.0
defaultIncreaseAttackSpeed = 1.2
defaultIncreaseBulletSpeed = 1.2
defaultIncreaseBulletRange = 50
defaultIncreaseBulletSize = 1.5

# Bullet setting
DefaultDamageVal=20
DefaultAngleVal=0
DefaultSizeVal=0.5
DefaultSpeedVal=0.8
DefaultRangeVal=0.5
DefaultRadiusVal=0.5
DefaultLastTimeVal=2
DefaultRayLastTimeVal=0.1
DefaultTubeRangeVal=30
DefaultAngleSpeedVal=5

bulletModelScaleVal = 0.1

# Map setting
DefaultMasterRoomNum=9
DefaultBranchRoomNum=3
# 每个难度等级对应的怪物数量,最大为16
levels = [LVecBase2(4,5),LVecBase2(5,7),LVecBase2(6,10)]
DefaultMonsterDistributions=[0.8,0.7,0.6,
                            0.7,0.6,0.6,
                            0.6,0.5,0.4
                            ]

# leap
LEAPMOTION_ROOM = False
MonsterNums=[0,2,4,6,0]
# Room settting
DefaultRoomX = 50
DefaultRoomY = 40
bossRoomModelName = 'model_room_firstChapter_firstBoss'
InitRoomMinTime = 2

# Light setting
aa=0.5
alightColor = (aa,aa,aa,1)
Sa =1
SlightColor = (Sa,Sa,Sa,1)

#Mask setting
DefaultMonsterMaskVal=0
DefaultHeroMaskVal=1
defaultHeroInMonsterMaskVal=2
defaultMonsterInWallMaskVal=8
uselessMaskVal=10

# particle
PARTICLE = True
defaultParticleZ = 2
defaultParticleScale = 5
defaultParticleAngle = 90
defaultParticleInterTime = 0.5

# debug
Debug = False
Nodebug = not Debug
NeedRoomInitVideo = True

if Debug:
	defaultHeroAttackPower = 10000
	MonsterNums=[0,1,1,1,0]