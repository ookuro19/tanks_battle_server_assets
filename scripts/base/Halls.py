import KBEngine
import Functor
import GameConfigs
from KBEDebug import *

FIND_ROOM_NOT_FOUND = 0
FIND_ROOM_CREATING = 1


class Halls(KBEngine.Entity):
    """
    这是一个脚本层封装的房间管理器
    """

    def __init__(self):
        KBEngine.Entity.__init__(self)

        # 向全局共享数据中注册这个管理器的entityCall以便在所有逻辑进程中可以方便的访问
        KBEngine.globalData["Halls"] = self

        # 所有房间，是个字典结构，包含 {"roomEntityCall", "PlayerCount", "enterRoomReqs"}
        # enterRoomReqs, 在房间未创建完成前， 请求进入房间和登陆到房间的请求记录在此，等房间建立完毕将他们扔到space中
        self.rooms = {}
        self.matching_rooms = {}
        self.last_new_room_keys = {}

    def findRoom(self, modeNum=-1, mapNum=-1, matchCode=-1, roomKey=-1):
        """
        查找一个指定房间，如果找不到允许创建一个新的
        """
        tRoomDatas = None
        if matchCode > 0:
            tRoomDatas = self.matching_rooms.get(matchCode)
        else:
            if roomKey >= 0:
                # 新进入的玩家是不可能存在需要匹配的房间的
                tRoomDatas = self.rooms.get(roomKey)
            else:
                lastNewRoomKey = None
                # 按照地图，模式匹配
                if mapNum == -1 or modeNum == -1:
                    # 玩家为快速匹配时，查找已有房间中人数最多的房间
                    temp_player_count = 0
                    for map_mode_key, child_room_key in self.last_new_room_keys.items():
                        # for (map, mode), child_room_key in self.last_new_room_keys.items(): 也可以，但可能有效率问题(?)
                        # 检查是否存在已有房间
                        temp_room_datas = self.rooms.get(child_room_key)
                        if temp_room_datas is not None:
                            # 检查roomdata是否存在
                            if temp_room_datas["PlayerCount"] < GameConfigs.ROOM_MAX_PLAYER and temp_room_datas["PlayerCount"] >= temp_player_count:
                                # 检查是否满员且人数最多
                                (mapNum, modeNum) = map_mode_key
                                DEBUG_MSG("Halls::findroom quikly matching room key %s, player count is %i" %
                                          child_room_key, temp_room_datas["PlayerCount"])

                if mapNum == -1 or modeNum == -1:
                    # 如果上一步未能修改，则随机生成mapNum和modeNum
                    mapNum = random.randint(
                        0, GameConfigs.MAP_NUM_LIMIT)  # 包含上下界
                    modeNum = random.randint(
                        0, GameConfigs.MODE_NUM_LIMIT)

                lastNewRoomKey = self.last_new_room_keys.get(
                    (mapNum, modeNum))

                if lastNewRoomKey is not None:
                    DEBUG_MSG("Halls::findroom mode = %i,map = %i,matchCode = %i, lastNewRoomKey exit = %i" %
                              (modeNum, mapNum, matchCode, lastNewRoomKey == None))
                    # 房间可能被删除
                    tRoomDatas = self.rooms.get(lastNewRoomKey)

        if tRoomDatas is None:
            return (FIND_ROOM_NOT_FOUND, mapNum, modeNum)
        else:
            return (tRoomDatas, mapNum, modeNum)

    def createRoom(self, modeNum=-1, mapNum=-1, matchCode=-1):
        """
        create room
        根据匹配码，地图、模式等创建房间，并不需要用房间号，因为不可能根据房间号创建地图
        """
        tempRoomKey = KBEngine.genUUID64()

        # 将房间base实体创建在任意baseapp上
        # 此处的字典参数中可以对实体进行提前def属性赋值
        KBEngine.createEntityAnywhere("Room",
                                      {
                                          "roomKey": tempRoomKey,
                                          "modeNum": modeNum,
                                          "mapNum": mapNum
                                      },
                                      Functor.Functor(self.onRoomCreatedCB, tempRoomKey))

        cRoomDatas = {"roomEntityCall": None, "PlayerCount": 0,
                      "enterRoomReqs": [], "roomKey": tempRoomKey}
        self.rooms[tempRoomKey] = cRoomDatas

        if matchCode > 0:
            pass
        else:
            self.last_new_room_keys[(mapNum, modeNum)] = tempRoomKey

        DEBUG_MSG("Halls::createRoom mode=%i,map=%i,matchCode=%i, room is: %i" %
                  (modeNum, mapNum, matchCode, self.last_new_room_keys[(mapNum, modeNum)]))

        return cRoomDatas

    def enterRoom(self, entityCall, modeNum, mapNum, matchCode, roomKey=-1):
        """
        defined method.
        请求进入某个Room中
        """
        DEBUG_MSG("Halls::enterRoom: enter entityID=%i, mode=%i,map=%i,matchCode=%i" %
                  (entityCall.id, modeNum, mapNum, matchCode))
        (roomDatas, mapNum, modeNum) = self.findRoom(
            modeNum, mapNum, matchCode, roomKey)

        if type(roomDatas) is not dict or roomDatas["PlayerCount"] >= GameConfigs.ROOM_MAX_PLAYER:
            # 如果不是房间或房间已满员
            if entityCall.className == "Account":
                # 如果是玩家就创建房间
                roomDatas = self.createRoom(modeNum, mapNum, matchCode)

        # 重新检查，避免新建房间出错
        if type(roomDatas) is dict and roomDatas["PlayerCount"] < GameConfigs.ROOM_MAX_PLAYER:
            roomDatas["PlayerCount"] += 1
            roomEntityCall = roomDatas["roomEntityCall"]
            if roomEntityCall is not None:
                # 将来采用对象池的方式时需要调用
                # roomEntityCall.setModeMap(modeNum, mapNum)
                roomEntityCall.enterRoom(entityCall)
            else:
                DEBUG_MSG("Halls::enterRoom: space %i creating..., enter entityID=%i" % (
                    roomDatas["roomKey"], entityCall.id))
                roomDatas["enterRoomReqs"].append(
                    (entityCall))
        else:
            # 满员时机器人无需进入
            # 正常情况，玩家这里应该时不会被执行的
            DEBUG_MSG("Halls::enterRoom can't enter room %i",
                      entityCall.className)
            entityCall.onMatchingFinish(-1)

    def leaveRoom(self, avatarID, roomKey):
        """
        defined method.
        某个玩家请求登出服务器并退出这个space
        """
        roomDatas = self.findRoom(roomKey=roomKey)

        if roomDatas is not None and type(roomDatas) is dict:
            roomEntityCall = roomDatas["roomEntityCall"]
            if roomEntityCall:
                roomEntityCall.leaveRoom(avatarID)
        else:
            # 由于玩家即使是掉线都会缓存至少一局游戏， 因此应该不存在退出房间期间地图正常创建中
            if roomDatas == FIND_ROOM_CREATING:
                raise Exception("FIND_ROOM_CREATING")

    # --------------------------------------------------------------------------------------------
    #                              Callbacks
    # --------------------------------------------------------------------------------------------
    def onRoomCreatedCB(self, roomKey, roomEntityCall):
        """
        一个space创建好后的回调
        """
        DEBUG_MSG("Halls::onRoomCreatedCB: space %i. entityID=%i" %
                  (roomKey, roomEntityCall.id))

    def onRoomLoseCell(self, roomKey):
        """
        defined method.
        Room的cell销毁了
        """
        DEBUG_MSG("Halls::onRoomLoseCell: space %i." % (roomKey))
        del self.rooms[roomKey]

    def onRoomGetCell(self, roomEntityCall, roomKey):
        """
        defined method.
        Room的cell创建好了
        """
        self.rooms[roomKey]["roomEntityCall"] = roomEntityCall

        # space已经创建好了， 现在可以将之前请求进入的玩家全部丢到cell地图中
        for infos in self.rooms[roomKey]["enterRoomReqs"]:
            entityCall = infos
            roomEntityCall.enterRoom(entityCall)
        self.rooms[roomKey]["enterRoomReqs"] = []
