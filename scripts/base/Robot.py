# -*- coding: utf-8 -*-
import KBEngine
from KBEDebug import *
import GameConfigs
import random

TIMER_TYPE_Robot_Controlled = 1


class Robot(KBEngine.Proxy):
    def __init__(self):
        KBEngine.Proxy.__init__(self)

        self.cellData["nameS"] = "I, Robot"

        self.curRoomBase = None

        self._destroyTimer = 0

        KBEngine.globalData["Halls"].enterRoom(
            entityCall=self, modeNum=-1, mapNum=-1, matchCode=-1, roomKey=self.roomKey)

    def createCell(self, space, roomKey, roomNo):
        """
        defined method.lo
        创建cell实体
        """
        self.cellData["roomNo"] = roomNo
        self.curRoomBase = space.base
        self.createCellEntity(space)

    def onMatchingFinish(self, suc):
        """
        matching finish
        匹配结束，通知客户端可以开始加载地图
        """
        if suc == 0:
            pass
        else:
            # 必须先销毁cell实体，才能销毁base
            if self.cell is not None:
                self.destroyCellEntity()
                return
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
        if TIMER_TYPE_Robot_Controlled == userArg:
            DEBUG_MSG("Robot_Cell::TIMER_TYPE_Robot_Controlled")
            self.curRoomBase.getController(self)

    def onGetCell(self):
        """
        KBEngine method.
        entity的cell部分实体被创建成功
        """
        DEBUG_MSG('Robot::onGetCell: %s' % self.cell)
        self.addTimer(1, 0, TIMER_TYPE_Robot_Controlled)

    def onLoseCell(self):
        """
        KBEngine method.
        entity的cell部分实体丢失
        """
        DEBUG_MSG("%s::onLoseCell: %i" % (self.className, self.id))
        self.destroy()

    def onRestore(self):
        """
        KBEngine method.
        entity的cell部分实体被恢复成功
        """
        DEBUG_MSG("%s::onRestore: %s" % (self.getScriptName(), self.cell))