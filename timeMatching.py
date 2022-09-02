
def timeMatching(aimtime, steptimes):
    # 输入的是单一的GNSS或WIFI数据，和含有每一步的apptime的steps矩阵（二维矩阵n×6）
    # 输出一个num，代表的是第几步的位置索引

    num = 0  #索引初始值
    isSubTime = []  # 存满足条件的时间数据
    isSubTimeNum = []  #存时间数据对应的索引num
    for row in range(len(steptimes)):
        steptime = steptimes[row][0]  # 每一步的时间

        # 时间暴力匹配
        # 先框选一个大的时间差范围，把满足条件的差值和对应的num都取出来
        # 再取steptime里最小的值，返回对应的num
        subTime = abs(float(steptime) - float(aimtime))   #两时间差值
        if (subTime <= 3):
            # print("1、差值：",subTime," 对应的数字：",num)
            isSubTime.append(subTime)   # 添加到数组
            isSubTimeNum.append(num)    # 满足条件的steptime位于第num步
        num = num + 1  # 更新第num步

    # 如果数组里没有满足条件的值，扩大范围再找一圈
    if (len(isSubTime) == 0):
        # print(aimtime)
        num = 0
        isSubTime = []  # 重新定义
        isSubTimeNum = []
        for row in range(len(steptimes)):
            steptime = steptimes[row][0]  # 每一步的时间
            subTime = abs(float(steptime) - float(aimtime))  # 两时间差值
            if (subTime <= 10):
                # print("2、差值：",subTime," 对应的数字：",num)
                isSubTime.append(subTime)  # 添加到数组
                isSubTimeNum.append(num)
            num = num + 1  # 更新第num步
    if (len(isSubTime) == 0):
        # print(aimtime)
        return -1   # 实在找不到就算了吧，返回一个-1
    # 求数组内的最小值返回num
    min_isSubTime = min(isSubTime)   #求最小值
    index_minSubTime = isSubTime.index(min_isSubTime)  #求最小值对应的索引号

    # print("最小差值：",min_isSubTime," 对应的数字：",isSubTimeNum[index_minSubTime])
    # print("--------------------------------------")
    return isSubTimeNum[index_minSubTime]
    # 返回的是aimtime在steptime内部的位置的序列号
