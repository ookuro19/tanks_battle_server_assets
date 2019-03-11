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
        # 随便取个名字吧
        self.cellData["name"] = self.__ACCOUNT_NAME__
        self.cellData["progress"] = 0
        self._destroyTimer = 0
        self.roomBaseEntityCall = None

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

    def createCell(self, space, roomKey, roomNo):
        """
        defined method.
        创建cell实体
        """
        self.roomKey = roomKey
        self.cellData["roomNo"] = roomNo
        self.createCellEntity(space)
        self.roomBaseEntityCall = space.base

    def destroySelf(self):
        """
        """
        if self.client is not None:
            return

        # 必须先销毁cell实体，才能销毁base
        if self.cell is not None:
            self.destroyCellEntity()
            return

        # 销毁base
        self.destroy()
        self._destroyTimer = 0

    def matchingFinish(self):
        """
        matching finish
        匹配结束，通知客户端可以开始加载地图
        """
        self.client.onMatchingFinish(0)

    def regLoadingProgress(self, progress):
        """
        regLoadingProgress
        客户端加载进度
        """
        # self.cellData["progress"] = progress
        if not self.isLoadingFinish:
            INFO_MSG("account[%i] regLoadingProgress. entityCall:%s" %
                     (self.id, self.client))
            if progress == 100:
                self.isLoadingFinish = True
                if self.roomBaseEntityCall is not None:
                    self.roomBaseEntityCall.loadingFinish(self.id)

    def loadingFinish(self):
        """
        loading finish
        所有玩家完成地图加载，通知客户端可以开始比赛
        """
        self.client.onLoadingFinish(0)

    # --------------------------------------------------------------------------------------------
    #                              Callbacks
    # --------------------------------------------------------------------------------------------

    def onClientEnabled(self):
        """
        KBEngine method.
        该entity被正式激活为可使用， 此时entity已经建立了client对应实体， 可以在此创建它的
        cell部分。
        """
        INFO_MSG("account[%i] entities enable. entityCall:%s" %
                 (self.id, self.client))

    def onClientDeath(self, entityCall, position, direction):
        """
        KBEngine method.
        客户端对应实体已经销毁
        """
        DEBUG_MSG("Avatar[%i].onClientDeath:" % self.id)
        self.destroy()
