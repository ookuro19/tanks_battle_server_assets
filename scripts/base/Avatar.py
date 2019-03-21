# -*- coding: utf-8 -*-
import KBEngine
from KBEDebug import *
import GameConfigs
import random

TIMER_TYPE_DESTROY = 1


class Avatar(KBEngine.Proxy):
    def __init__(self):
        KBEngine.Proxy.__init__(self)

        self.cellData["dbid"] = self.databaseID

        self.cellData["name"] = self.__ACCOUNT_NAME__

        self.cellData["progress"] = 0

        self._destroyTimer = 0

    def createCell(self, space, roomKey, roomNo):
        """
        defined method.lo
        创建cell实体
        """
        self.roomKey = roomKey
        self.cellData["roomNo"] = roomNo
        self.createCellEntity(space)

    def destroySelf(self):
        """

        """
        if self.client is not None:
            return

        # 必须先销毁cell实体，才能销毁base
        if self.cell is not None:
            self.destroyCellEntity()
            return

        KBEngine.globalData["Halls"].leaveRoom(self.id, self.roomKey)

        # 销毁base
        self.destroy()
        self._destroyTimer = 0

    # region Matching

    def startMatching(self, mapNum, modeNum):
        """
        start matching
        根据玩家提交的地图和模式开始进行匹配
        """
        INFO_MSG("account[%i] start matching. entityCall:%s, mapNum:%s, modeNum:%s" %
                 (self.id, self.client, mapNum, modeNum))
        self.isLoadingFinish = False
        # 如果玩家存在cell， 说明已经在地图中了， 因此不需要再次进入地图
        if self.cell is None:
            # 玩家上线了或者重登陆了， 此处告诉大厅，玩家请求登陆到游戏地图中
            KBEngine.globalData["Halls"].enterRoom(
                self, self.roomKey)

    def matchingFinish(self):
        """
        matching finish
        匹配结束，通知客户端可以开始加载地图
        """
        self.client.onMatchingFinish(0)
    # endregion Matching

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
        if TIMER_TYPE_DESTROY == userArg:
            self.onDestroyTimer()

    def onClientEnabled(self):
        """
        KBEngine method.
        该entity被正式激活为可使用， 此时entity已经建立了client对应实体， 可以在此创建它的
        cell部分。
        """
        INFO_MSG("account[%i] entities enable. entityCall:%s" %
                 (self.id, self.client))

    def onLogOnAttempt(self, ip, port, password):
        """
        KBEngine method.
        客户端登陆失败时会回调到这里
        """
        INFO_MSG(ip, port, password)
        return KBEngine.LOG_ON_ACCEPT

    def onGetCell(self):
        """
        KBEngine method.
        entity的cell部分实体被创建成功
        """
        DEBUG_MSG('Avatar::onGetCell: %s' % self.cell)

    def onLoseCell(self):
        """
        KBEngine method.
        entity的cell部分实体丢失
        """
        DEBUG_MSG("%s::onLoseCell: %i" % (self.className, self.id))

        # 如果self._destroyTimer大于0说明之前已经由base请求销毁，通常是客户端断线了
        if self._destroyTimer > 0:
            self.destroySelf()

        # 否则由cell发起销毁， 那么说明游戏结束了

    def onClientDeath(self):
        """
        KBEngine method.
        客户端对应实体已经销毁
        """
        DEBUG_MSG("Avatar[%i].onClientDeath:" % self.id)

        # 如果玩家没有cell, 直接退出？
        if self.cell is None:
            self.destroySelf()
        else:
            # 防止正在请求创建cell的同时客户端断开了， 我们延时一段时间来执行销毁cell直到销毁base
            # 这段时间内客户端短连接登录则会激活entity
            # 延时GAME_ROUND_TIME秒的原因是， 我们确保玩家掉线后， 他的服务端实体能够完整参与一场游戏
            self._destroyTimer = self.addTimer(
                GameConfigs.GAME_ROUND_TIME + 15, 0, TIMER_TYPE_DESTROY)

    def onRestore(self):
        """
        KBEngine method.
        entity的cell部分实体被恢复成功
        """
        DEBUG_MSG("%s::onRestore: %s" % (self.getScriptName(), self.cell))

    def onDestroyTimer(self):
        DEBUG_MSG("Avatar::onDestroyTimer: %i" % (self.id))
        self.destroySelf()
