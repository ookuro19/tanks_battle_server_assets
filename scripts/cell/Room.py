# -*- coding: utf-8 -*-
import KBEngine
from KBEDebug import *
import GameConfigs
import random

TIMER_TYPE_DESTROY = 1
TIMER_TYPE_BALANCE_MASS = 2


class Room(KBEngine.Entity):
    """
    游戏场景
    """

    def __init__(self):
        KBEngine.Entity.__init__(self)
        # 这个房间中所有的玩家
        self.avatars = {}

        # 让baseapp和cellapp都能够方便的访问到这个房间的entityCall
        KBEngine.globalData["Room_%i" % self.spaceID] = self.base

    def onEnter(self, entityCall):
        """
        defined method.
        进入场景
        """
        DEBUG_MSG('Room::onEnter space[%d] entityID = %i.' %
                  (self.spaceID, entityCall.id))
        self.avatars[entityCall.id] = entityCall

    def onLeave(self, entityID):
        """
        defined method.
        离开场景
        """
        DEBUG_MSG('Room::onLeave space[%d] entityID = %i.' % (
            self.spaceID, entityID))

        if entityID in self.avatars:
            del self.avatars[entityID]

    def enterGameWorld(self, entityCall, position, direction):
        """
        defined method.
        设置初始位置
        """
        DEBUG_MSG('Room::enterGameWorld space[%d] entityID = %i. pos: %i' % (
            self.spaceID, entityCall.id, position))

        if entityCall.id in self.avatars:
            entityCall.position = position
            entityCall.direction = direction
