# 问题解决方案

## 1. Cell Entitycall

### 1. cell entitycall储存后会由于负载均衡丢失的问题

**解决方案**：

~~(弃用) 将所有原先在cell上储存entitycall的逻辑转移到base上~~
逻辑依旧放在cell上，通知部分则调用base即可

## 2. Progress

### 1. 由于cell entitycall丢失的问题导致的加载完成等问题

**解决方案**：

1. 由于需要通知其他玩家，所以其flag需要在cell上，选择All clients或other clients，故客户端要更新progress依旧只能使用cellcall

2. 由于需要通知所有客户端完成刷新，但cell entitycall储存问题，故加载完成后需要通知base来实现加载完成回调

3. 具体流程为：

```sequence {theme="simple"}
client -> Account_Cell : update progress
Account_Cell -> Account_Cell : check progress == 100
Account_Cell -> Room_Base : AccountLoadingFinish
Room_Base -> Room_Base : check all avatar loading finish
Room_Base -> Account_Base : loading finish
Room_Base -> Room_Cell : start timer
```

### 2. MatchingFinish在玩家enter world之前

**原因分析**：

从函数逻辑上看，room统计出房间内玩家数目为8人时便会发送matching finish，此时最后一个进入的玩家还未创建cell部分，但只有等最后一名玩家创建cell后才执行enter world，故matching finish一定在enter world之前，故发生此问题。

**解决方案**：

1. ~~需要分析cell init，onGetCell，onEnterWorld的执行先后顺序，进而调整~~客户端验证后，发现次序依次为onGetCell，enter world，cell init

2. 根据分析得出的先后顺序将enterroom放在其之后

### 3. Destination

1. 逻辑相应位置
**原因分析**：是否需要将相应机制改为allclients等形式
**解决方案**：否，因为涉及到倒计时等相应机制

2. 计时相应位置
**原因分析**：玩家到达终点时需要通知到达时间
**解决方案**：若倒计时位于cell上，则还需要从cell上取得相应时间

**最终解决方案**： 由于逻辑还在cell上，故此问题不再是问题

## 3. Robot

1. 机器人设置controllerBy
**原因分析**：cell entitycall储存不靠谱
**解决方案**：只能靠机器人本身驱动

具体流程为：
```sequence {theme="simple"}
Robot -> Room_Cell : need controller
Room_Cell -> Room_Base : check progress == 100
Account_Cell -> Room_Base : AccountLoadingFinish
Room_Base -> Room_Base : check all avatar loading finish
Room_Base -> Account_Base : loading finish
Room_Base -> Room_Cell : start timer
```

## 4. Prop

### 1. 道具timer

**原因分析**：道具timer有时会存在叠加行为
**解决方案**：

具体流程为：

### 2. 伤害与防护类道具结算

**解决方案**：

1. 假设时刻t受到伤害
2. 如果防护类道具倒计时Δt大于0，则玩家不会受到伤害，即时刻t1 = t + Δt之前玩家不会受到伤害；反之，如果防护类道具倒计时Δt<=0，则t1 = t + Δt < t，即时刻t1之后，都会受到伤害。
3. 由于道具只可能是在时刻t或其之前使用，同时t1是由使用防护类道具的时刻t0确定的，即t1 = t0 + 5s
4. 综上，根据使用防护累道具的时刻t0确定失效时刻t1，假设被击中时刻为t，如果t < t1，则玩家防护成功，如果t >= t1，则玩家防护失败，判定击中。

## 5. Room

### 1. 记录房间mode和map

**原因分析**：为了防止由于人员变动导致房间本身记录的mode和map失效
**条件约束**：考虑到之后对象池实现方式，房间最好可以修改mode和map
**解决方案**：

1. 方式1:
以字典方式记录在hall中，但房间实体可能无法读取

2. 方式2：
创建时记录为房间属性，但后续可能无法修改

3. 方式3：
检查房间的entity是否存在，如果存在，则调用其函数；不存在时则在创建时设置其属性
