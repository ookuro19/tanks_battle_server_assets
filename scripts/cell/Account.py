# -*- coding: utf-8 -*-
import KBEngine
from KBEDebug import *
from interfaces.EntityCommon import EntityCommon
import GameConfigs

TIMER_TYPE_ADD_TRAP = 1


class Account(KBEngine.Entity, EntityCommon):
    def __init__(self):
        KBEngine.Entity.__init__(self)
        EntityCommon.__init__(self)
        self.progress = 0
        self.getCurRoom().onEnter(self)
        self.curProp = None

    # region Matching
    def regProgress(self, tprogress):
        """
        regLoadingProgress
        客户端加载进度
        """
        if self.progress < tprogress:
            self.progress = tprogressf
            INFO_MSG("cell::account[%i] reg progress. entityCall:%s, progress:%s" %
                     (self.id, self.client, tprogress))
            if self.progress == GameConfigs.LOADING_FINISH_PROGRESS:
                self.getCurRoom().AccountloadingFinish(self.id)
    # endregion

    # region Props
    def regGetProps(self, prop_key, prop_type):
        """
        当前玩家获得道具
        :param prop_key: 道具的key
        :param prop_type: 所获得的道具类型
        """
        DEBUG_MSG("Account id: %i, get props: %i." % (self.id, prop_type))
        # 传递给服务器，由服务器判断是否吃到道具
        self.getCurRoom().regCheckPropsAvailable(prop_key, prop_type)

    def onGetProps(self, if_available, prop_key, prop_type):
        """
        on get props
        获得道具回调
        :param if_available: 道具是否可获得
        :param prop_key: 道具的key
        :param prop_type: 所获得的道具类型
        """
        if if_available:
            self.curProp = prop_key
            # 通知所有客户端该玩家获得道具
            self.allClients.onGetProps(prop_key, prop_type)

    def regUseProp(self, target_id, skill_type):
        """
        use skill
        使用道具
        :param target_id: 目标玩家的id
        :param skill_type: 道具/技能类型
        """
        if skill_type == self.curProp:
            self.curProp = None
            self.allClients.onUseProp(self.id, target_id, skill_type)

    def regPropResult(self, target_id, suc):
        self.allClients.onPropResult(self.id, target_id, suc)

    def onPropResult(self, target_id, prop_type, suc):
        self.allClients.onPropResult(self.id, target_id, prop_type, suc)
    # endregion Props

    # region Destination
    def regReachDestination(self):
        """
        reach destination
        当前玩家到达终点
        """
        INFO_MSG("cell::account[%i] reach destination. entityCall:%s" %
                 (self.id, self.client))

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

        if TIMER_TYPE_ADD_TRAP == user_arg:
            self.addProximity(self.modelRadius, 0, 0)

    def onUpgrade(self):
        pass

    def onDestroy(self):
        """
        KBEngine method.
        entity销毁
        """
        DEBUG_MSG("Account::onDestroy: %i." % self.id)
        room = self.getCurRoom()

        if room:
            room.onLeave(self.id)
    # endregion
