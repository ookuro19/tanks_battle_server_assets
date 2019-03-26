# 各部分可参考时序图
主要参考kbengine ball demo

## 登录相关可参考
```sequence {theme="simple"}

client -> client : login, load world scene
client -> sdk : firein(login)
sdk -> client : login success
sdk -> client : onAvataEnterWorld
client -> client : create game entity
```

## 道具相关可参考
```sequence {theme="simple"}

Note over room : CELL
room -> room : addTimer
room -> room : onDestroyTimer()
# 请求销毁引擎中创建的真实空间，在空间销毁后，所有该空间上的实体都被销毁
room -> room : destroySpace()

food -> room : onFoodDestroy
smash -> room : onFoodSmash

```