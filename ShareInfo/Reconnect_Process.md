# 登录及重连时可能发生的情况
玩家正常登录之后，仍然可能存在掉线的情况，因此有必要对各个情况进行分析：

1. 登录——无base
    登录失败则会自动调用onLoginFailed，因此在登录过程中不存在掉线问题

    ```sequence {theme="simple"}
    Note left of sdk : login
    loginapp --> sdk : 未登录
    ```

2. 未匹配前掉线——无cell
    登录成功则有base，未匹配则无cell，因此此时掉线只需重新登陆即可

    ```sequence {theme="simple"}
    Note left of sdk : 未匹配前掉线
    base --> loginapp : lost connection
    loginapp --> sdk : 已登录但没有cell
    ```

3. **匹配时掉线——cell创建中**

    ```sequence {theme="simple"}

    Note left of sdk : 未匹配前掉线
    base --> loginapp : lost connection
    loginapp --> sdk : 已登录但没有cell

    Note left of sdk : 匹配时掉线

    Note left of sdk : 匹配后、比赛前掉线

    Note left of sdk : 比赛时掉线

    Note left of sdk : 比赛结束时掉线
    ```

4. 匹配后、比赛前掉线

    ```sequence {theme="simple"}
    Note left of sdk : login
    loginapp --> sdk : 未登录

    Note left of sdk : 未匹配前掉线
    base --> loginapp : lost connection
    loginapp --> sdk : 已登录但没有cell

    Note left of sdk : 匹配时掉线

    Note left of sdk : 匹配后、比赛前掉线

    Note left of sdk : 比赛时掉线

    Note left of sdk : 比赛结束时掉线
    ```

5. 比赛时掉线

    ```sequence {theme="simple"}
    Note left of sdk : login
    loginapp --> sdk : 未登录

    Note left of sdk : 未匹配前掉线
    base --> loginapp : lost connection
    loginapp --> sdk : 已登录但没有cell

    Note left of sdk : 匹配时掉线

    Note left of sdk : 匹配后、比赛前掉线

    Note left of sdk : 比赛时掉线

    Note left of sdk : 比赛结束时掉线
    ```

6. 比赛结束时掉线

    ```sequence {theme="simple"}
    Note left of sdk : login
    loginapp --> sdk : 未登录

    Note left of sdk : 未匹配前掉线
    base --> loginapp : lost connection
    loginapp --> sdk : 已登录但没有cell

    Note left of sdk : 匹配时掉线

    Note left of sdk : 匹配后、比赛前掉线

    Note left of sdk : 比赛时掉线

    Note left of sdk : 比赛结束时掉线
    ```