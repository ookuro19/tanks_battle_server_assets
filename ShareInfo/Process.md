# 滑雪3.0服务器各部分逻辑流程

## 1. 登录

```sequence {theme="simple"}

Note left of sdk : login
sdk -> avatar : login
avatar -> sdk : onLoginSucessfully
```

## 2. 匹配

```sequence {theme="simple"}
# 开始匹配
Note left of sdk : matching
sdk -> avatar : start matching
avatar -> halls : enter room
halls -> room : init, onGetCell
room -> halls : onroomGetCell
halls -> room : enter room, on enter
room -> avatar : create cell, createCellEntity
avatar -> sdk : onAccountEnterWorld
room -> room : check player count
avatar -> sdk : matching finish

# 更新加载进度
Note left of sdk : progress
sdk -> avatar : regProgress
avatar -> room : AccountloadingFinish
room -> room : check players' progress
room -> avatar : loadingFinish
avatar -> sdk : loadingFinish
```

## 3. 坐标

```sequence {theme="simple"}
Note left of sdk : pos
sdk -> avatar : update pos

# 终点判断方法有待改进
Note left of sdk : reach
sdk -> avatar : reach destination
avatar -> room : playerReachDestination
room -> avatar : onReachDestination
avatar -> sdk : onReachDestination
room -> room : addTimer(10)
room -> room : check reach player count
room -> avatar : onTimerChanged
avatar -> sdk : onTimerChanged
```

## 4. 道具相关

### 1.获得道具

```sequence {theme="simple"}
Note left of sdk : getProps
sdk -> avatar : regGetProps(prop_key, prop_type)
avatar -> room : regCheckPropsAvailable(entitycall, prop_key, prop_type)
room -> avatar : onGetPropsBase(avaibility, prop_type)
avatar -> sdk : onGetPropsClient(avaibility, prop_type)
Note left of room : prop reset after 5s
room -> avatar : onPropResetBase(prop_key)
avatar -> sdk : onPropResetClient(prop_key)
```

### 2. 使用道具

```sequence {theme="simple"}
Note left of sdk : useProp
sdk -> avatar : regUseProp(prop_type, target_id)
avatar -> avatar : check skill available
avatar -> sdk : onUseProp
sdk -> avatar : regPropResult
avatar -> room : regCheckPropsResult
room -> avatar : onPropResultBase
avatar -> sdk : onPropResultClient
```

## 6. 比赛结束

```sequence {theme="simple"}
Note left of sdk : game over
room -> room : gameover
room -> avatar : exit room
avatar -> sdk : on exit room
```

## 6. 玩家掉线

```sequence {theme="simple"}
Note left of sdk : lose connect
client -> avatar.base : onClientDeath
avatar.base -> avatar.cell : destroyCellEntity

avatar.cell -> room.cell : onLeave
room.cell -> room.cell : destroySpace
room.cell -> room.base : onLoseCell
room.base -> halls : onRoomLoseCell

avatar.cell -> avatar.base : onLoseCell
avatar.base -> avatar.base : destroySelf
avatar.base -> halls : leaveRoom
halls -> room.base : leaveRoom
```