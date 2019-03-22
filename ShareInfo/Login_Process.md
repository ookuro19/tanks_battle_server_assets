# 登录及重连时可能发生的情况
玩家正常登录之后，仍然可能存在掉线的情况，因此有必要对各个情况进行分析：

1. 正常登录
1. 未匹配前掉线
1. 匹配时掉线
1. 匹配后、比赛前掉线
1. 比赛时掉线
1. 比赛结束时掉线

```sequence {theme="simple"}
Note left of sdk : login
sdk -> loginapp : firein(login)
loginapp -> sdk : login result

Note left of sdk : before matching
sdk -> loginapp : firein(login)
loginapp -> avatar : 
```