# -*- coding: utf-8 -*-
import KBEngine
from KBEDebug import *
import GameConfigs
import random
import ShopItemData
import time
import datetime

TIMER_TYPE_DESTROY = 1


class Account(KBEngine.Proxy):
    def __init__(self):
        KBEngine.Proxy.__init__(self)

        self.cellData["dbid"] = self.databaseID
        self.cellData["nameS"] = self.__ACCOUNT_NAME__
        self.cellData["progress"] = 0
        self.loginTime = time.time()
        self._destroyTimer = 0

        self.checkDefaultEquipment()
        self.loginCheckData()

    # region play record

    def loginCheckData(self):
        """
        检查登录时间，更新游戏记录
        """
        self.loginTimeSpan = time.time()
        self.totalLoginTimes += 1
        dateToday = datetime.datetime.now().day

        if self.lastLoginDate != dateToday:
            self.lastLoginDate = dateToday
            self.lastLoginDayLoginTimes = 1
            self.lastLoginDayPlayTime = 0
        else:
            self.lastLoginDayLoginTimes += 1

    def logoutCheckData(self):
        """
        登出时更新游戏记录
        """
        curPlayTime = int(time.time() - self.loginTimeSpan)
        self.totalPlayTime += curPlayTime
        self.lastLoginDayPlayTime += curPlayTime
    # endregion play record

    # region Matching

    def regStartMatching(self, modeNum, mapNum, matchCode):
        """
        start matching
        根据玩家提交的地图和模式开始进行匹配
        """

        INFO_MSG("account[%i] start matching. entityCall:%s, mapNum:%s, modeNum:%s, roomKey is :%s" %
                 (self.id, self.client, mapNum, modeNum, self.roomKey))
        # 如果玩家存在cell， 说明已经在地图中了， 因此不需要再次进入地图
        if self.cell is None:
            self.modeNum = modeNum
            self.mapNum = mapNum
            self.matchCode = matchCode
            # 玩家上线了或者重登陆了， 此处告诉大厅，玩家请求登陆到游戏地图中
            KBEngine.globalData["Halls"].enterRoom(
                self, modeNum, mapNum, matchCode)
        else:
            INFO_MSG("account[%i] has its cell. roomKey:%s" %
                     (self.id, self.roomKey))

    def createCell(self, space, roomKey, roomNo):
        """
        defined method.lo
        创建cell实体
        """
        self.roomKey = roomKey
        self.cellData["roomNo"] = roomNo
        self.createCellEntity(space)

    def onMapModeChanged(self, mapNum, modeNum):
        """
        set game mode and map
        通知玩家房间的游戏地图和模式
        """
        self.mapNum = mapNum
        self.modeNum = modeNum
        self.client.onMapModeChanged(self.mapNum, self.modeNum)

    def onMatchingFinish(self, suc):
        """
        matching finish
        匹配结束
        0-匹配成功; -1-匹配失败
        """
        if suc == 0:
            self.loginState = 1
        self.client.onMatchingFinish(suc)
    # endregion Matching

    # region equipment
    def regBuyEquip(self, item_id):
        """
        reg buy equip
        购买装备
        :param time: 装备id
        """
        if item_id in self.bagItemList:
            # 已拥有, 无需购买
            self.client.onBuyEquip(item_id, 1)
        else:
            if item_id in ShopItemData.EquipmentData:
                if self.gold >= ShopItemData.EquipmentData[item_id]:
                    # 购买成功
                    self.gold -= ShopItemData.EquipmentData[item_id]
                    self.bagItemList.append(item_id)
                    # !!!此处需测试与客户端的同步问题, 果然同步不了，，，
                    self.onChangeEquipBase(item_id)
                    # 这一步与客户端进行同步
                    self.bagItemList = self.bagItemList
                    self.currentItemDict = self.currentItemDict
                    self.client.onBuyEquip(item_id, 0)
                else:
                    # 金币不足
                    self.client.onBuyEquip(item_id, 2)
            else:
                # 道具不存在
                self.client.onBuyEquip(item_id, 3)

    def regChangeEquip(self, item_id):
        """
        reg change equip
        更换装备
        :param time: 装备id
        """
        if item_id in self.bagItemList:
            self.onChangeEquipBase(item_id)
            # 与客户端进行同步currentItemDict
            self.currentItemDict = self.currentItemDict
            self.client.onChangeEquip(item_id, 0)
        else:
            # 玩家尚未拥有此装备
            self.client.onChangeEquip(item_id, 1)

    def onChangeEquipBase(self, item_id):
        """
        on change equip
        服务器端更换装备
        :param time: 装备id
        """
        keyValue = int(item_id / 100)
        if keyValue == 0:
            self.currentItemDict['head'] = item_id
        elif keyValue == 1:
            self.currentItemDict['clothes'] = item_id
        elif keyValue == 2:
            self.currentItemDict['hand'] = item_id
        elif keyValue == 3:
            self.currentItemDict['shoe'] = item_id
        elif keyValue == 4:
            self.currentItemDict['bag'] = item_id

    def checkDefaultEquipment(self):
        if 100 not in self.bagItemList:
            self.bagItemList = [0, 100, 200, 300, 400]
            self.bagItemList = self.bagItemList
            self.currentItemDict['head'] = 0
            self.currentItemDict['clothes'] = 100
            self.currentItemDict['hand'] = 200
            self.currentItemDict['shoe'] = 300
            self.currentItemDict['bag'] = 400
            self.currentItemDict = self.currentItemDict

    # endregion equipment

    def regGetGold(self, gold_num):
        """
        reg get gold
        获得金币
        """
        self.gold += gold_num
        self.client.onGetGold(gold_num)

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
        # 如果销毁玩家计时器已经开启了，此处玩家又上线了那么应该取消计时器
        if self._destroyTimer > 0:
            self.delTimer(self._destroyTimer)
            self._destroyTimer = 0

        # 0-当前玩家未匹配
        # 1-当前玩家匹配未比赛
        # 2-当前玩家是比赛中掉线的
        self.client.onLoginState(self.loginState)

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
        DEBUG_MSG('Account::onGetCell: %s' % self.cell)

    def onLoseCell(self):
        """
        KBEngine method.
        entity的cell部分实体丢失
        """
        DEBUG_MSG("%s::onLoseCell: %i" % (self.className, self.id))

        self.loginState = 0

        # 如果self._destroyTimer大于0说明之前已经由base请求销毁，通常是客户端断线了
        if self._destroyTimer > 0:
            self.delTimer(self._destroyTimer)
            self.destroySelf()

        # 否则由cell发起销毁， 那么说明游戏结束了
        if(self.client != None):
            self.client.onExitRoom(0)

    def onClientDeath(self):
        """
        KBEngine method.
        客户端对应实体已经销毁
        """
        DEBUG_MSG("Account[%i].onClientDeath:" % self.id)

        self.logoutCheckData()

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
        DEBUG_MSG("Account::onDestroyTimer: %i" % (self.id))
        self.destroySelf()
