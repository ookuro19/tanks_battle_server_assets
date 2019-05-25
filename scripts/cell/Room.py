# -*- coding: utf-8 -*-
import KBEngine
from KBEDebug import *
import GameConfigs
import random
import PropsData

TIMER_TYPE_TOTAL_TIME = 1
TIMER_TYPE_START = 2
TIMER_TYPE_END = 3
TIMER_TYPE_DESTROY = 4


class Room(KBEngine.Entity):
    """
    游戏场景
    """

    def __init__(self):
        KBEngine.Entity.__init__(self)
        # 这个房间中所有的玩家
        self.avatars = {}

        # 让baseapp和cellapp都能够方便的访问到这个房间的entityCall
        KBEngine.globalData["Room_%i" % self.spaceID] = self.base

        # 加载完成人数
        self.loadingFinishCount = 0

        # 比赛总计用时
        self.totalTime = 0

        # 比赛终点倒计时
        self.endTimer = 0

        # 到达终点人数总计
        self.reachCount = 0

        # 房主实体
        self.hostEntity = None

        # 已使用的道具, key: prop_key, value: 要恢复的时刻
        self.prop_used_dict = {}
        # 已使用道具相应计时, key: 要恢复的时刻， value: dict{prop_key}
        self.prop_timer_dict = {}

        # 防御类道具失效时刻, key: entity_id, value: 失效时刻
        self.shell_timer_dict = {}

    # region enter or leave

    def onEnter(self, entityCall):
        """
        defined method.
        进入场景
        """
        DEBUG_MSG('Room::onEnter space[%d] entityID = %i.' %
                  (self.spaceID, entityCall.id))
        self.avatars[entityCall.id] = entityCall
        # 失效时间置为0
        self.shell_timer_dict[entityCall.id] = 0

    def onLeave(self, entityID):
        """
        defined method.
        离开场景
        """
        DEBUG_MSG('Room::onLeave space[%d] entityID = %i.' % (
            self.spaceID, entityID))

        if entityID in self.avatars:
            del self.avatars[entityID]
    # endregion enter or leave

    # region loading
    def AccountloadingFinish(self, entityID):
        """
        loading finish.
        加载结束
        """
        DEBUG_MSG('Room::loadingFinish entityID = %i.' % entityID)
        if entityID in self.avatars:
            self.loadingFinishCount += 1
            if self.loadingFinishCount == GameConfigs.ROOM_MAX_PLAYER:
                self._startTimer = self.addTimer(3, 0, TIMER_TYPE_START)
                self.base.onAllPlayerLoadingFinish()
    # endregion loading

    # region playing
    def regCheckPropsAvailable(self, entityCall, prop_key, prop_type):
        """
        检查是否获得相应道具
        """
        tPropTimer = self.prop_used_dict.get(prop_key)
        # tProp['timer'] > 0 相当于 tProp['endtime'] - curTime > 0
        # 即tProp['endtime'] > curTime
        if tPropTimer is not None and tPropTimer > self.totalTime:
            # 此时道具还未被使用或已被使用但还未被重置
            DEBUG_MSG("Prop %s is not available" % prop_key)
            entityCall.onGetPropsBase(1, prop_key, prop_type)
        else:
            tProp = PropsData.datas.get(prop_key)
            if tProp is None:
                DEBUG_MSG("Prop %s is not exist" % prop_key)
                entityCall.onGetPropsBase(1, prop_key, prop_type)
            else:
                DEBUG_MSG("Prop %s is existed, PosX is %i" %
                          (prop_key, tProp['posx']))
                entityCall.onGetPropsBase(0, prop_key, prop_type)
                self.GetProp(prop_key)

    def regCheckPropsResult(self, entityCall, origin_id, target_id, prop_type, suc):
        """
        检查道具使用结果
        """
        if prop_type == GameConfigs.E_Prop_Shell:
            if origin_id in self.shell_timer_dict:
                self.shell_timer_dict[origin_id] = self.totalTime + 5
            else:
                entityCall.onPropResultBase(origin_id, target_id, prop_type, 1)
        elif prop_type == GameConfigs.E_Prop_Bullet:
            if target_id in self.shell_timer_dict:
                if self.shell_timer_dict[target_id] <= self.totalTime:
                    # 此时护盾效果失效, 判定命中
                    entityCall.onPropResultBase(
                        origin_id, target_id, prop_type, 0)
                else:
                    # 此时还在护盾效果内, 判定未命中, 并刷新护盾结束时间
                    entityCall.onPropResultBase(
                        origin_id, target_id, prop_type, 1)
                    self.shell_timer_dict[target_id] = self.totalTime
            else:
                entityCall.onPropResultBase(origin_id, target_id, prop_type, 1)
        else:
            entityCall.onPropResultBase(origin_id, target_id, prop_type, 1)

    def playerReachDestination(self, entityID):
        """
        player reach destition
        玩家到达终点
        """
        DEBUG_MSG('Room::player reach destination entityID = %i.' % entityID)
        if entityID in self.avatars:
            self.base.onPlayerReachDestination(entityID, self.totalTime)
            self.reachCount += 1
            if self.reachCount == 1:
                self.endTimer = -1
                self._endTimer = self.addTimer(0, 1, TIMER_TYPE_END)
            elif self.reachCount == len(self.avatars):
                if self.totalTime > 0:
                    self.gameOver()

    def GetProp(self, prop_key):
        """
        on get prop
        有玩家获得道具
        """
        tempTime = self.totalTime + 5
        self.prop_used_dict[prop_key] = tempTime
        if tempTime not in self.prop_timer_dict:
            self.prop_timer_dict[tempTime] = {}
        self.prop_timer_dict[tempTime][prop_key] = None

    def releaseProp(self, time):
        """
        release and reset prop
        释放并重置道具
        """
        tempDict = {}
        if time in self.prop_timer_dict:
            tempDict = self.prop_timer_dict.pop(time)
            # 该时刻对应字典的道具恢复
            for prop_key in tempDict.keys():
                if prop_key in self.prop_used_dict:
                    self.prop_used_dict.pop(prop_key)
            self.base.onResetProps(list(tempDict.keys()))

    # endregion playing

    # region gameover
    def gameOver(self):
        if self.endTimer > 0:
            self.delTimer(self._endTimer)
        if self.totalTime > 0:
            self.delTimer(self._totalTimer)
        self.base.onTimerChanged(0)
        self._destroyTimer = self.addTimer(1, 0, TIMER_TYPE_DESTROY)

    def onDestroyTimer(self):
        DEBUG_MSG("Room::onDestroyTimer: %i" % (self.id))
        # 请求销毁引擎中创建的真实空间，在空间销毁后，所有该空间上的实体都被销毁
        self.destroySpace()
    # endregion gameover

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
        if TIMER_TYPE_START == userArg:
            DEBUG_MSG("Room::TIMER_TYPE_START")
            self.delTimer(self._startTimer)
            self.totalTime = 0
            # 开始计时总时间
            self._totalTimer = self.addTimer(1, 1, TIMER_TYPE_TOTAL_TIME)

        elif TIMER_TYPE_TOTAL_TIME == userArg:
            self.totalTime += 1
            self.releaseProp(self.totalTime)
            # DEBUG_MSG("Room::TIMER_TYPE_TOTAL_TIME: %i" % (self.totalTime))

        elif TIMER_TYPE_END == userArg:
            self.endTimer += 1
            DEBUG_MSG("Room::TIMER_TYPE_END: %i" % (self.endTimer))
            if self.endTimer == 10:
                self.gameOver()
            else:
                self.base.onTimerChanged(10 - self.endTimer)
        elif TIMER_TYPE_DESTROY == userArg:
            self.onDestroyTimer()

    def onDestroy(self):
        """
        KBEngine method.
        """
        DEBUG_MSG("Room::onDestroy: %i" % (self.id))
        del KBEngine.globalData["Room_%i" % self.spaceID]
