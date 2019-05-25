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
            self.progress = tprogress
            INFO_MSG("cell::account[%i] reg progress. entityCall:%s, progress:%s" %
                     (self.id, self.client, tprogress))
            if self.progress == GameConfigs.LOADING_FINISH_PROGRESS:
                self.getCurRoom().AccountloadingFinish(self.id)
    # endregion

    # region GetProps
    def regGetProps(self, prop_key, prop_type):
        """
        当前玩家获得道具
        :param prop_key: 道具的key
        :param prop_type: 所获得的道具类型
        """
        DEBUG_MSG("Account id: %i, get props: %i." % (self.id, prop_type))
        # 传递给服务器，由服务器判断是否吃到道具
        self.getCurRoom().regCheckPropsAvailable(self, prop_key, prop_type)

    def onGetPropsBase(self, suc, prop_key, prop_type):
        """
        on get props
        获得道具回调
        :param suc: 道具是否可获得
        :param prop_key: 道具的key
        :param prop_type: 所获得的道具类型
        """
        if suc == 0:
            self.curProp = prop_key
            # 通知所有客户端该玩家获得道具
            # self.allClients.onGetPropsClient(prop_key, prop_type)
            # 只是获得道具的话只需要自己知道
            self.allClients.onGetPropsClient(self.id, prop_key, prop_type)
    # endregion GetProps

    # region UseProps
    def regUseProp(self, target_id, prop_type):
        """
        use prop
        使用道具, 判断拥有道具后直接使用
        :param target_id: 目标玩家的id
        :param prop_type: 道具类型
        """
        if prop_type == self.curProp:
            self.curProp = None
            # 至于个人是否拥有相关，不需要房间总体判断
            self.allClients.onUseProp(
                self.id, target_id, prop_type, Math.Vector3(self.position))
            
    def regPropResult(self, origin_id, target_id, prop_type, suc):
        # 传递给服务器，由服务器结算
        self.getCurRoom().regCheckPropsResult(self, origin_id, target_id, prop_type, suc)

    def onPropResultBase(self, origin_id, target_id, prop_type, suc):
        self.allClients.onPropResultClient(origin_id, target_id, prop_type, suc)
    # endregion UseProps

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
