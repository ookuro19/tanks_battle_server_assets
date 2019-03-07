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

    def enterRoom(self, entityCall):
        """
        defined method.
        请求进入某个space中
        """
        entityCall.createCell(self.cell, self.roomKey)
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
                info.matchingFinish()
                DEBUG_MSG("Room::matchingFinish: %i" % self.roomKey)

    def onLeave(self, entityID):
        """
        defined method.
        离开场景
        """
        if entityID in self.avatars:
            del self.avatars[entityID]

    def loadingFinish(self, entityID):
        """
        loading finish.
        加载结束
        """
        DEBUG_MSG('Room::loadingFinish space[%d] entityID = %i.' % (
            self.spaceID, entityID))
        if entityID in self.avatars:
            count = 0
            for key, ec in self.avatars.items():
                if ec.cellData["progress"] != 1:
                    break
                else:
                    count += 1
            if count == len(self.avatars):
                for info in self.avatars.values():
                    info.loadingFinish()

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
