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
        self.lastNewRoomKey = 0

    def findRoom(self, modeNum=-1, mapNum=-1, matchCode=-1, roomKey=-1, notFoundCreate=False):
        """
        查找一个指定房间，如果找不到允许创建一个新的
        """
        if matchCode > 0:
            roomDatas = self.matching_rooms.get(matchCode)

        else:
            roomDatas = self.rooms.get(roomKey)

            # 如果房间没有创建，则将其创建
            if not roomDatas:
                if not notFoundCreate:
                    return FIND_ROOM_NOT_FOUND

                # 如果最后创建的房间没有满员，则使用最后创建的房间key，否则产生一个新的房间唯一Key
                roomDatas = self.rooms.get(self.lastNewRoomKey)
                if roomDatas is not None and roomDatas["PlayerCount"] < GameConfigs.ROOM_MAX_PLAYER:
                    return roomDatas

                self.lastNewRoomKey = KBEngine.genUUID64()

                # 将房间base实体创建在任意baseapp上
                # 此处的字典参数中可以对实体进行提前def属性赋值
                KBEngine.createEntityAnywhere("Room",
                                              {
                                                  "roomKey": self.lastNewRoomKey,
                                              },
                                              Functor.Functor(self.onRoomCreatedCB, self.lastNewRoomKey))

                roomDatas = {"roomEntityCall": None, "PlayerCount": 0,
                             "enterRoomReqs": [], "roomKey": self.lastNewRoomKey}
                self.rooms[self.lastNewRoomKey] = roomDatas
                return roomDatas
            else:
                if roomDatas["PlayerCount"] < GameConfigs.ROOM_MAX_PLAYER:
                    return roomDatas
                else:
                    return FIND_ROOM_NOT_FOUND

    def enterRoom(self, entityCall, modeNum, mapNum, matchCode, roomKey = -1):
        """
        defined method.
        请求进入某个Room中
        """
        if roomKey < 0:
            # 玩家非制定进入房间，可以新建
            roomDatas = self.findRoom(
                modeNum, mapNum, matchCode, roomKey, True)
        else:
            # 制定房间号，可能是机器人或玩家，不需要创建房间
            roomDatas = self.findRoom(
                modeNum, mapNum, matchCode, roomKey, False)

        if type(roomDatas) is dict:
            roomDatas["PlayerCount"] += 1

            roomEntityCall = roomDatas["roomEntityCall"]
            if roomEntityCall is not None:
                roomEntityCall.enterRoom(entityCall)
            else:
                DEBUG_MSG("Halls::enterRoom: space %i creating..., enter entityID=%i" % (
                    roomDatas["roomKey"], entityCall.id))
                roomDatas["enterRoomReqs"].append(
                    (entityCall))
        else:
            # 此时可能是房间满员，则会使玩家重连失败，或者机器人没有必要在进入相应房间
            if roomDatas == FIND_ROOM_CREATING:
                entityCall.onMatchingFinish(-1)

    def leaveRoom(self, avatarID, roomKey):
        """
        defined method.
        某个玩家请求登出服务器并退出这个space
        """
        roomDatas = self.findRoom(notFoundCreate=False, roomKey=roomKey)

        if type(roomDatas) is dict:
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
