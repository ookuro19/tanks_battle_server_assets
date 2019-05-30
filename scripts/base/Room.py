# -*- coding: utf-8 -*-
import KBEngine
from KBEDebug import *
import GameConfigs

TIMER_TYPE_Matching = 1
TIMER_TYPE_Robot_Refresh = 2


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

        self.accounts = {}
        self.robots = {}
        self.hostEntity = None
        self.palyerNum = 0
        self.mapNo = 0
        self.modeNo = 0

        # self.addTimer(GameConfigs.ROOM_MATCHING_TIME, 0, TIMER_TYPE_Matching)

        DEBUG_MSG("Room::__init__: %i" % self.id)

    # region enter&leave
    def enterRoom(self, entityCall):
        """
        defined method.
        请求进入某个space中
        """
        if len(self.accounts) == 0:
            self.hostEntity = entityCall
            self.mapNo = entityCall.mapNum
            self.modeNo = entityCall.modeNum

        self.palyerNum += 1
        entityCall.createCell(self.cell, self.roomKey, self.palyerNum)

        self.onEnter(entityCall)
        DEBUG_MSG("Room::enterRoom: %i, mapNo: %i, modeNo: %i"
                  % (self.id, self.mapNo, self.modeNo))

    def onEnter(self, entityCall):
        """
        defined method.
        进入场景
        """
        if entityCall.className == "Account":
            # 如果是玩家，则需要通知更换地图
            entityCall.onMapModeChanged(self.mapNo, self.modeNo)
            self.accounts[entityCall.id] = entityCall
        else:
            self.robots[entityCall.id] = entityCall

        if (len(self.accounts) + len(self.robots)) == GameConfigs.ROOM_MAX_PLAYER:
            # 当人数足够时，即可开始游戏
            for info in self.accounts.values():
                info.onMatchingFinish(0)
            DEBUG_MSG("Room::matchingFinish: %i" % self.roomKey)

    def leaveRoom(self, entityID):
        """
        defined method.
        某个玩家请求退出这个space
        """
        self.onLeave(entityID)

    def onLeave(self, entityID):
        """
        defined method.
        离开场景
        """
        if entityID in self.accounts:
            del self.accounts[entityID]
    # endregion enter&leave

    # region matching
    def getController(self, robot):
        """

        给机器人添加控制
        """
        robot.cell.onControlledBy(self.hostEntity)
    # endregion matching

    # region loading

    def onAllPlayerLoadingFinish(self):
        """
        on all player loading finish.
        通知所有玩家加载结束
        """
        DEBUG_MSG('Room::onAllPlayerLoadingFinish roomID = %i.' % self.roomKey)
        for info in self.accounts.values():
            info.onLoadingFinish(0)
    # endregion loading

    # region props
    def onResetProps(self, prop_list):
        """
        on all player loading finish.
        通知所有玩家加载结束
        """
        DEBUG_MSG('Room::onResetProps prop_list = %s.' % ('.'.join(prop_list)))
        for info in self.accounts.values():
            info.client.onResetPropClient(prop_list)
    # endregion props

    # region destination
    def onPlayerReachDestination(self, eid, time):
        """
        player reach destination
        玩家到达终点
        """
        for info in self.accounts.values():
            info.onReachDestination(eid, time)

    def onTimerChanged(self, timer):
        """
        通知客户端倒计时
        """
        for info in self.accounts.values():
            info.onTimerChanged(timer)
    # endregion destination

    # --------------------------------------------------------------------------------------------
    #                              Callbacks
    # --------------------------------------------------------------------------------------------

    def onTimer(self, id, userArg):
        """
        KBEngine method.
        使用addTimer后， 当时间到达则该接口被调用
        @param id		: addTimer 的返回值ID
        @param userArg	: addTimer 最后一个参数所给入的数据
        """
        if TIMER_TYPE_Matching == userArg:
            DEBUG_MSG("Room_Base::TIMER_TYPE_Matching")
            if (len(self.accounts) + len(self.robots)) < GameConfigs.ROOM_MAX_PLAYER:
                DEBUG_MSG("create a robot")
                # 生成机器人
                KBEngine.createEntity(
                    "Robot", {"progress": 100, "roomKey": self.roomKey})
                self.addTimer(GameConfigs.ROOM_MATCHING_TIME,
                              0, TIMER_TYPE_Matching)

    def onLoseCell(self):
        """
        KBEngine method.
        entity的cell部分实体丢失
        """
        KBEngine.globalData["Halls"].onRoomLoseCell(self.roomKey)

        self.accounts = {}
        self.destroy()

    def onGetCell(self):
        """
        KBEngine method.
        entity的cell部分实体被创建成功
        """
        DEBUG_MSG("Room::onGetCell: %i" % self.id)
        KBEngine.globalData["Halls"].onRoomGetCell(self, self.roomKey)
