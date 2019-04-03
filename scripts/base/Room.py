# -*- coding: utf-8 -*-
import KBEngine
from KBEDebug import *
import GameConfigs


class Room(KBEngine.Entity):
    """
    一个可操控cellapp上真正space的实体
    注意：它是一个实体，并不是真正的space，真正的space存在于cellapp的内存中，通过这个实体与之关联并操控space。
    """

    def __init__(self):
        KBEngine.Entity.__init__(self)

        self.cellData["roomKeyC"] = self.roomKey

        # 请求在cellapp上创建cell空间
        self.createCellEntityInNewSpace(None)

        self.avatars = {}
        DEBUG_MSG("Room::__init__: %i" % self.id)

    # region enter or leave
    def enterRoom(self, entityCall):
        """
        defined method.
        请求进入某个space中
        """
        entityCall.createCell(self.cell, self.roomKey, len(self.avatars))
        entityCall.onMapModeChanged(0, 0)
        self.onEnter(entityCall)

    def leaveRoom(self, entityID):
        """
        defined method.
        某个玩家请求退出这个space
        """
        self.onLeave(entityID)

    def onEnter(self, entityCall):
        """
        defined method.
        进入场景
        """
        self.avatars[entityCall.id] = entityCall
        if len(self.avatars) == GameConfigs.ROOM_MAX_PLAYER:
            for info in self.avatars.values():
                info.onMatchingFinish(0)
                DEBUG_MSG("Room::matchingFinish: %i" % self.roomKey)

    def onLeave(self, entityID):
        """
        defined method.
        离开场景
        """
        if entityID in self.avatars:
            del self.avatars[entityID]
    # endregion enter or leave

    # region loading
    def onAllPlayerLoadingFinish(self):
        """
        on all player loading finish.
        通知所有玩家加载结束
        """
        DEBUG_MSG('Room::onAllPlayerLoadingFinish roomID = %i.' % self.roomKey)
        for info in self.avatars.values():
            info.onLoadingFinish(0)
    # endregion loading

    # region destination
    def onPlayerReachDestination(self, eid, time):
        """
        player reach destination
        玩家到达终点
        """
        for info in self.avatars.values():
            info.onReachDestination(eid, time)

    def onTimerChanged(self, timer):
        """
        通知客户端倒计时
        """
        for info in self.avatars.values():
            info.onTimerChanged(timer)
    # endregion destination

    # --------------------------------------------------------------------------------------------
    #                              Callbacks
    # --------------------------------------------------------------------------------------------

    def onLoseCell(self):
        """
        KBEngine method.
        entity的cell部分实体丢失
        """
        KBEngine.globalData["Halls"].onRoomLoseCell(self.roomKey)

        self.avatars = {}
        self.destroy()

    def onGetCell(self):
        """
        KBEngine method.
        entity的cell部分实体被创建成功
        """
        DEBUG_MSG("Room::onGetCell: %i" % self.id)
        KBEngine.globalData["Halls"].onRoomGetCell(self, self.roomKey)
