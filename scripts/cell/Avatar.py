# -*- coding: utf-8 -*-
import KBEngine
from KBEDebug import *

TIMER_TYPE_ADD_TRAP = 1


class Avatar(KBEngine.Entity):
    def __init__(self):
        KBEngine.Entity.__init__(self)

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
