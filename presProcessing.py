import numpy as np
# import wifiProcessing as wp
import math
import dataProcessing as dp
import matplotlib.pyplot as plt
import pdrProcessing as pp  # 惯导解算

def calcuThreshold(PRES_data):
    # 输入：所有气压数据，开始的真实楼层值
    # 输出：动态计算阈值
    presData = []
    for row in range(int(len(PRES_data) / 1)):
        presData.append(float(PRES_data[row][3]))  # 求气压值
    presMax = np.max(presData)
    presMin = np.min(presData)
    return presMax,presMin


def presProcessing(PRES, PRES_data, floor_posi):
    # 输入：某时刻气压值，气压数据列表，真实楼层起点。
    # 输出：楼层高度

    serv = 0  # 备份
    presMax,presMin = calcuThreshold(PRES_data)
    distance0 = PRES - 992
    distance1 = PRES - 996
    if (PRES < presMax + 0.35 and PRES > presMax - 0.35 and distance0 <= 2):
        serv = 0
        return 0
    if (PRES < presMin + 0.35 and PRES > presMin - 0.35 and distance1 <= 2):
        if (floor_posi == 2):
            serv = 2
            return 2
        else:
            serv = 1
            return 1
    else:
        return serv


# -------test1 --------
# dataRoute = "./TrainingData/IPIN2022_T3_TrainingTrial52_User03.txt"
# # data = dp.oridataProcessing(dataRoute)  # 原始数据处理（未剔除）
# data = pp.dataProcessing(dataRoute)
# floor_posi = 0
#
# PRES_Data = []
# presdata = []
# for row in range(len(data)):
#     if (data[row][0] == 'PRES'):
#         PRES_Data.append(data[row])
#         presdata.append(float(data[row][3]))
#
# floorMaxMin = calcuThreshold(PRES_Data, floor_posi)
# print(floorMaxMin)
#
# plt.figure()
# xx = range(len(presdata))
# plt.plot(xx,presdata)
# plt.show()


# 12层切换完全看不出来。


