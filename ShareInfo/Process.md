
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
avatar -> room : AccountloadingFinish
room -> room : check players' progress
room -> avatar : loadingFinish
avatar -> sdk : loadingFinish

# 游戏阶段
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

# 获得道具判断方法有待改进
Note left of sdk : getProps
sdk -> avatar : getProps
avatar -> sdk : onGetProps

# 使用技能
Note left of sdk : useSkill
sdk -> avatar : use skill
avatar -> avatar : check skill available
avatar -> avatar : use skill to other
avatar -> sdk : A fires at B

# 比赛结束
Note left of sdk : game over
room -> room : gameover
room -> avatar : exit room
avatar -> sdk : on exit room
```