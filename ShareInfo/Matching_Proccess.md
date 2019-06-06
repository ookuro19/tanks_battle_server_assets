# 游戏匹配规则

游戏匹配主要是依据匹配码，所选地图和模式进行。

大致流程描述：

## 0. 通用流程

通用流是指从查找房间到进入房间的这一段过程

```flow
e=>end: 结束
sr_find_and_enter=>subroutine: 查找并进入房间
cond_has_room=>condition: 是否有相
应房间?
op_enter_room=>operation: 进入相应房间
op_create_room=>operation: 创建相应房间
sr_room_key=>subroutine: 房间号匹配

sr_find_and_enter->cond_has_room
cond_has_room(yes)->op_enter_room
cond_has_room(no)->op_create_room->op_enter_room->e
```
## 1. 匹配码

判断有无匹配码，若匹配码不为零，则按照相应逻辑进入地图，流程图如下图所示。

```flow
st=>start: 开始匹配
e=>end: 结束
input_match_code=>inputoutput: 输入匹配码
cond_match_code=>condition: 是否有
匹配码?
cond_has_room=>condition: 是否有相
应房间?
op_enter_room=>operation: 进入相应房间
op_create_room=>operation: 创建相应房间
sr_room_key=>subroutine: 房间号匹配
sr_find_and_enter=>subroutine: 查找并进入房间

st->input_match_code->cond_match_code
cond_match_code(no)->sr_room_key
cond_match_code(yes,right)->sr_find_and_enter
op_enter_room->e
```

## 2. 根据房间号匹配(暂未开通)

**注意**：

1. 玩家匹配时房间号这一属性并不填写，所以默认为-1；机器人由于需要进入相应房间，所以必有房间号。
2. 对玩家而言，匹配时不存在房间号相关操作，故不需要创建房间；离开房间时才会有操作，但也不需要创建房间。
3. 对于机器人，进入和离开都会有房间号，但都不需要创建房间。

综上，基于房间号的匹配不应该创建房间。所以流程如下：

```flow
e=>end: 结束
sr_room_key=>subroutine: 普通匹配
input_room_key=>inputoutput: 输入房间号
cond_room_key=>condition: 是否有
房间号?
cond_has_room=>condition: 是否有相
应房间?
cond_player_full=>condition: 房间是
否人满?
op_enter_room=>operation: 进入相应房间
sr_normal_match=>subroutine: 地图和模式匹配

sr_room_key->input_room_key->cond_room_key
cond_room_key(yes,right)->cond_has_room
cond_has_room(yes,right)->cond_player_full
cond_has_room(no)->e
cond_player_full(no)->op_enter_room->e
cond_room_key(no)->sr_normal_match
```

## 3. 根据地图和模式匹配

```flow
cond_has_room=>condition: 是否有相
应房间?
cond_player_full=>condition: 房间是
否人满?
op_create_room=>operation: 创建相应房间
op_enter_room=>operation: 进入相应房间

sr_normal_match=>subroutine: 地图和模式匹配
input_map_and_mode=>inputoutput: 输入地图，模式
cond_match_mode=>condition: 是否均为-1?
sr_quick_game=>subroutine: 快速比赛
sr_custom_game=>subroutine: 自定义比赛

cond_exited_room=>condition: 是否已有房间
cond_maxplayer_room=>condition: 是否存在人数最多
但未满员的房间
op_set_player_mode=>operation: 设置玩家模式和地图
op_rand_mode=>operation: 随机生成模式地图参数
op_mark_mode=>operation: 记录相应模式地图参数
sr_find_and_enter=>subroutine: 查找并进入房间

sr_normal_match->input_map_and_mode->cond_match_mode
cond_match_mode(no)->sr_custom_game
cond_match_mode(yes)->sr_quick_game
sr_quick_game->cond_exited_room
cond_exited_room(yes)->cond_maxplayer_room
cond_exited_room(no)->op_rand_mode->op_set_player_mode
cond_maxplayer_room(yes)->op_mark_mode->op_set_player_mode
cond_maxplayer_room(no)->op_rand_mode->op_set_player_mode

op_set_player_mode->cond_has_room
sr_custom_game->cond_has_room

cond_has_room(yes)->sr_find_and_enter
```

在find room时直接设置（-1，-1）玩家的mode和map，以上流程只是相当于给快速匹配的玩家，从匹配随机生成(mode, map)，变成先查找后在判定是否随机生成(mode, map)
