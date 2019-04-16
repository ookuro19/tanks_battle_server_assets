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
        self.progress = 0
        self.getCurRoom().onEnter(self)

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
    # endregion

    # region Props
    def regGetProps(self, prop_type):
        """
        当前玩家获得道具
        :param prop_type: 所获得的道具类型
        """
        DEBUG_MSG("Avatar id: %i, get props: %i." % (self.id, prop_type))
        self.allClients.onGetProps(prop_type)
    # endregion
    
    # region Skill
    def regUseSkill(self, target_id, skill):
        self.allClients.onUseSkill(self.id, target_id, skill)

    def regSkillResult(self, target_id, suc):
        self.allClients.onSkillResult(self.id, target_id, suc)
    # endregion Skill

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
        DEBUG_MSG("Avatar::onDestroy: %i." % self.id)
        room = self.getCurRoom()

        if room:
            room.onLeave(self.id)
    # endregion
