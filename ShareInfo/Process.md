
```sequence {theme="simple"}

# 登录
Note left of sdk : login
sdk -> avatar : login
avatar -> sdk : onLoginSucessfully

Note over avatar: BASE
Note over room: BASE
Note over halls: BASE

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
Note over avatar: CELL
Note over room: CELL
Note over halls: CELL

# 更新加载进度
Note left of sdk : progress
sdk -> avatar : regProgress
avatar -> room : AvatarloadingFinish
room -> room : check players' progress
room -> avatar : loadingFinish
avatar -> sdk : loadingFinish

Note left of sdk : gaming
sdk -> avatar : update pos

# 终点判断方法有待改进
sdk -> avatar : reach destination
avatar -> room : playerReachDestination
room -> avatar : onReachDestination
avatar -> sdk : onReachDestination

# 获得道具判断方法有待改进
sdk -> avatar : getProps
avatar -> sdk : onGetProps

room -> room : addTimer(10)
room -> room : check reach player count
room -> avatar : onTimerChanged
avatar -> sdk : onTimerChanged

# 比赛结束
Note left of sdk : game over
room -> room : gameover
room -> avatar : exit room
avatar -> sdk : on exit room
```