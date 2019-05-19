# -*- coding: utf-8 -*-
from enum import Enum
"""
"""

# ------------------------------------------------------------------------------
# entity state
# ------------------------------------------------------------------------------
ENTITY_STATE_UNKNOW = -1
ENTITY_STATE_SAFE = 0
ENTITY_STATE_FREE = 1
ENTITY_STATE_MAX = 4

# 一个房间最大人数
ROOM_MAX_PLAYER = 3

# 机器人加入间隔
ROOM_MATCHING_TIME = 5

# 加载完成时进度值
LOADING_FINISH_PROGRESS = 100

# 终点倒计时（秒）
GAME_End_TIME = 10

# 一局比赛预计用时
GAME_ROUND_TIME = 100


class EProp(Enum):
    Shell = 0
    Bullet = 1
