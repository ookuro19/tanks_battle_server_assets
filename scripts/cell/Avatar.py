# -*- coding: utf-8 -*-
import KBEngine
from KBEDebug import *
from interfaces.EntityCommon import EntityCommon
import GameConfigs

TIMER_TYPE_ADD_TRAP = 1


class Avatar(KBEngine.Entity, EntityCommon):
    def __init__(self):
        KBEngine.Entity.__init__(self)
        EntityCommon.__init__(self)

        self.getCurRoom().onEnter(self)

    def onDestroy(self):
        """
        KBEngine method.
        entity销毁
        """
        DEBUG_MSG("Avatar::onDestroy: %i." % self.id)
        room = self.getCurRoom()

        if room:
            room.onLeave(self.id)

    # region Matching
    def regProgress(self, tprogress):
        """
        regLoadingProgress
        客户端加载进度
        """
        if self.progress < tprogress:
            self.progress = tprogress
            INFO_MSG("cell::account[%i] reg progress. entityCall:%s, progress:%s" %
                     (self.id, self.client, tprogress))
            if self.progress == GameConfigs.LOADING_FINISH_PROGRESS:
                self.getCurRoom().AvatarloadingFinish(self.id)

    def loadingFinish(self):
        """
        loading finish
        所有玩家完成地图加载，通知客户端可以开始比赛
        """
        self.client.onLoadingFinish(0)

    # endregion

    # region Props
    def getProps(self, prop_type):
        """
        当前玩家获得道具
        :param prop_type: 所获得的道具类型
        """
        DEBUG_MSG("Avatar id: %i, get props: %i." % (self.id, prop_type))
        self.allClients.onGetProps(prop_type)

    # endregion

    # region Destination
    def reachDestination(self):
        """
        reach destination
        当前玩家到达终点
        """
        INFO_MSG("cell::account[%i] reach destination. entityCall:%s" %
                 (self.id, self.client))
        self.getCurRoom().playerReachDestination(self.id)

    def onReachDestination(self, eid, time):
        """
        on reach destination
        其他玩家到达终点的回调
        """
        INFO_MSG("cell::other account[%i] reach destination. time:%s" %
                 (eid, time))
        self.client.onReachDestination(eid, time)

    def onTimerChanged(self, time):
        """
        on end timer change
        :param time: 倒计时
        """
        self.client.onTimerChanged(time)

    # endregion

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

        if TIMER_TYPE_ADD_TRAP == user_arg:
            self.addProximity(self.modelRadius, 0, 0)

    def onUpgrade(self):
        pass

    def onDestroy(self):
        """
        KBEngine method.
        entity销毁
        """
        DEBUG_MSG("Avatar::onDestroy: %i." % self.id)
        room = self.getCurRoom()

        if room:
            room.onLeave(self.id)
