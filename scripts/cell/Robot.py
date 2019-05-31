# -*- coding: utf-8 -*-
import KBEngine
from KBEDebug import *
from interfaces.EntityCommon import EntityCommon
import GameConfigs


class Robot(KBEngine.Entity, EntityCommon):
    def __init__(self):
        KBEngine.Entity.__init__(self)
        EntityCommon.__init__(self)

        self.progress = 100
        self.getCurRoom().onEnter(self)
        self.getCurRoom().AccountloadingFinish(self.id)

    def onControlledBy(self, controllerEntity):
        """
        on controlled by
        设置控制机器人的实体
        """
        self.controlledBy = controllerEntity

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
        @param id		: addTimer 的返回值ID
        @param user_arg	: addTimer 最后一个参数所给入的数据
        """
        # DEBUG_MSG("%s::onTimer: %i, tid:%i, arg:%i" % (self.className, self.id, tid, userArg))
        EntityCommon.onTimer(self, tid, user_arg)

    def onLoseControlledBy(self, id):
        DEBUG_MSG("%s::onLoseControlledBy: %i, owner %i" %
                  (self.className, self.id, id))

    def onUpgrade(self):
        pass

    def onDestroy(self):
        """
        KBEngine method.
        entity销毁
        """
        DEBUG_MSG("Robot::onDestroy: %i." % self.id)
        # room = self.getCurRoom()

        # if room:
        #     room.onLeave(self.id)
    # endregion
