```sequence {theme="simple"}

Note over room : CELL
room -> room : addTimer
room -> room : onDestroyTimer()
# 请求销毁引擎中创建的真实空间，在空间销毁后，所有该空间上的实体都被销毁
room -> room : destroySpace()

food -> room : onFoodDestroy
smash -> room : onFoodSmash

```