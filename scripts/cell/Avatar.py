# -*- coding: utf-8 -*-
import KBEngine
from KBEDebug import *
from interfaces.EntityCommon import EntityCommon

TIMER_TYPE_ADD_TRAP = 1


class Avatar(KBEngine.Entity, EntityCommon):
    def __init__(self):
        KBEngine.Entity.__init__(self)
        EntityCommon.__init__(self)

        self.getCurrRoom().onEnter(self)

    def onDestroy(self):
        """
        KBEngine method.
        entity销毁
        """
        DEBUG_MSG("Avatar::onDestroy: %i." % self.id)
        room = self.getCurrRoom()

        if room:
            room.onLeave(self.id)

    def regProgress(self, tprogress):
        """
        regLoadingProgress
        客户端加载进度
        """
        if self.progress < tprogress:
            self.progress = tprogress
            INFO_MSG("cell::account[%i] reg progress. entityCall:%s, progress:%s" %
                     (self.id, self.client, tprogress))
            if self.progress == 100:
                self.getCurrRoom().AvatarloadingFinish(self.id)

    def loadingFinish(self):
        """
        loading finish
        所有玩家完成地图加载，通知客户端可以开始比赛
        """
        self.client.onLoadingFinish(0)
    # --------------------------------------------------------------------------------------------
    #                              Callbacks
    # --------------------------------------------------------------------------------------------

    def onTimer(self, tid, userArg):
        """
            KBEngine method.
            引擎回调timer触发
            """
        #DEBUG_MSG("%s::onTimer: %i, tid:%i, arg:%i" % (self.className, self.id, tid, userArg))
        EntityCommon.onTimer(self, tid, userArg)

        if TIMER_TYPE_ADD_TRAP == userArg:
            self.addProximity(self.modelRadius, 0, 0)

    def onUpgrade(self):
        pass

    def onDestroy(self):
        """
        KBEngine method.
        entity销毁
        """
        DEBUG_MSG("Avatar::onDestroy: %i." % self.id)
        room = self.getCurrRoom()

        if room:
            room.onLeave(self.id)
