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
