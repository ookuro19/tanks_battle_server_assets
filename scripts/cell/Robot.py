# -*- coding: utf-8 -*-
import KBEngine
from KBEDebug import *
from interfaces.EntityCommon import EntityCommon
import GameConfigs

class Robot(KBEngine.Entity, EntityCommon):
    def __init__(self):
        self.progress = 100
        self.getCurRoom().onEnter(self)
        self.getCurRoom().AccountloadingFinish(self.id)

    
    # region Destination
    def regReachDestination(self):
        """
        reach destination
        当前玩家到达终点
        """
        INFO_MSG("cell::account[%i] reach destination. entityCall:%s" %
                 (self.id, self.className))
        self.getCurRoom().playerReachDestination(self.id)
    # endregion Destination

    # --------------------------------------------------------------------------------------------
    #                              Callbacks
    # --------------------------------------------------------------------------------------------

    def onTimer(self, tid, user_arg):
        """
        KBEngine method.
        引擎回调timer触发
        """
        # DEBUG_MSG("%s::onTimer: %i, tid:%i, arg:%i" % (self.className, self.id, tid, userArg))
        EntityCommon.onTimer(self, tid, user_arg)

    def onUpgrade(self):
        pass

    def onDestroy(self):
        """
        KBEngine method.
        entity销毁
        """
        DEBUG_MSG("Robot::onDestroy: %i." % self.id)
        room = self.getCurRoom()

        if room:
            room.onLeave(self.id)
    # endregion
