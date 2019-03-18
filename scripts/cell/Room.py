# -*- coding: utf-8 -*-
import KBEngine
from KBEDebug import *
import GameConfigs
import random

TIMER_TYPE_TOTAL_TIME = 1
TIMER_TYPE_START = 2
TIMER_TYPE_END = 3


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

        # 比赛总计用时
        self.totalTimer = 0

        # 比赛终点倒计时
        self.endTimer = 0

        # 到达终点人数总计
        self.reachCount = 0

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

    def AvatarloadingFinish(self, entityID):
        """
        loading finish.
        加载结束
        """
        DEBUG_MSG('Room::loadingFinish entityID = %i.' % entityID)
        if entityID in self.avatars:
            loadingFinishCount = 0
            for info in self.avatars.values():
                if info.progress == GameConfigs.LOADING_FINISH_PROGRESS:
                    loadingFinishCount += 1
            if loadingFinishCount == GameConfigs.ROOM_MAX_PLAYER:
                for info in self.avatars.values():
                    info.loadingFinish()
                # 所有玩家加载完成后，开局倒计时3s
                self._startTimer = self.addTimer(3, 0, TIMER_TYPE_START)

    def playerReachDestination(self, entityID):
        """
        player reach destition
        玩家到达终点
        """
        DEBUG_MSG('Room::player reach destination entityID = %i.' % entityID)
        if entityID in self.avatars:
            for info in self.avatars.values():
                info.onReachDestination(entityID, self.totalTimer)
            self.reachCount += 1
            if self.reachCount == 1:
                self.endTimer = -1
                self._endTimer = self.addTimer(0, 1, TIMER_TYPE_END)
            elif self.reachCount == len(self.avatars):
                if self.totalTimer > 0:
                    self.gameOver()

    def gameOver(self):
        if self.endTimer > 0:
            self.delTimer(self._endTimer)
        if self.totalTimer > 0:
            self.delTimer(self._totalTimer)
        for info in self.avatars.values():
            info.onTimerChanged(0)

    def onDestroy(self):
        """
        KBEngine method.
        """
        DEBUG_MSG("Room::onDestroy: %i" % (self.id))
        del KBEngine.globalData["Room_%i" % self.spaceID]

    # --------------------------------------------------------------------------------------------
    #                              Callbacks
    # --------------------------------------------------------------------------------------------

    def onTimer(self, id, userArg):
        """
        KBEngine method.
        使用addTimer后， 当时间到达则该接口被调用
        @param id		: addTimer 的返回值ID
        @param userArg	: addTimer 最后一个参数所给入的数据
        """
        if TIMER_TYPE_START == userArg:
            DEBUG_MSG("Room::TIMER_TYPE_START")
            self.delTimer(self._startTimer)
            self.totalTimer = 0
            # 开始计时总时间
            self._totalTimer = self.addTimer(1, 1, TIMER_TYPE_TOTAL_TIME)

        elif TIMER_TYPE_TOTAL_TIME == userArg:
            self.totalTimer += 1
            DEBUG_MSG("Room::TIMER_TYPE_TOTAL_TIME: %i" % (self.totalTimer))

        elif TIMER_TYPE_END == userArg:
            self.endTimer += 1
            DEBUG_MSG("Room::TIMER_TYPE_END: %i" % (self.endTimer))
            if self.endTimer == 10:
                self.gameOver()
            else:
                for info in self.avatars.values():
                    info.onTimerChanged(10 - self.endTimer)
