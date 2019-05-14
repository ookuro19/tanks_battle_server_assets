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

## 4. 获得道具判断方法有待改进

```sequence {theme="simple"}
Note left of sdk : getProps
sdk -> avatar : regGetProps
avatar -> Room : regCheckPropsAvailable
Room -> avatar : onGetProps
avatar -> sdk : onGetProps
```

## 5. 使用道具

```sequence {theme="simple"}
Note left of sdk : useProp
sdk -> avatar : regUseProp
avatar -> avatar : check skill available
avatar -> sdk : onUseProp
sdk -> sdk : regPropResult

```

## 6. 比赛结束

```sequence {theme="simple"}
Note left of sdk : game over
room -> room : gameover
room -> avatar : exit room
avatar -> sdk : on exit room
```