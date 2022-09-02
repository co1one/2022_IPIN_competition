import numpy as np
import math
import dataProcessing as dp
import areaSearch as ars    # 判断场景
import pdrProcessing as pp  # 惯导解算
import XYtoGPS as xy
import timeMatching as tm
import mixPositions as mp
import dataPlot as dplt


# 这个例程是纯惯导的，效果已经比较接近了，不行就用这一段
# ---------------初始化----------------
x_rela = 0      # 相对坐标
y_rela = 0
data_route = "./TrainingData/"
data_name = "IPIN2022_T3_TrainingTrial51_User03.txt"
# 两个函数二选一，视情况而定
# data = dp.oridataProcessing(data_route + data_name)  # 原始数据处理（未剔除）
data = pp.dataProcessing(data_route + data_name)   #剔除了第一个posi前的数据（未处理呢）


# ------ 自动获取初始点 ------
for row in range(len(data)):
    if (data[row][0] == 'POSI'):
        x_posi = float(data[row][4])
        y_posi = float(data[row][3])
        floor_posi = int(data[row][5])
        break

# -------------惯导解算---------------
ACCE_data,AHRS_data,GYRO_data,POSI_data,GNSS_data,PRES_data,WIFI_data= pp.getDataInfo(data)  # 获取数据以及数据信息（数据个数以及采样频率）
steps,acc_all = pp.stepDetection(ACCE_data)  # 从加速度数据中 获取有效的步数、(acc_all内含时间数据)

step_length = pp.WeinbergApproach(steps)  # 计算步长
yaw1 = pp.getYawFromAHRS(AHRS_data, steps)  # 从AHRS获取航向角


# ------------- 根据上一个位置输出一个当前位置-------------
positions = np.empty(shape=[0, 2], dtype=float)   # 创建一个位置矩阵
positions = np.append(positions, [[x_rela, y_rela]], axis=0)  # 赋初值（自己设定的）

for i in range(len(steps)):

    newXY_positions = pp.new_position(positions[i], yaw1[i], step_length[i])  # 生成新位置
    positions = np.append(positions,[newXY_positions],axis=0)


#------ 坐标转换函数 -------
for row in range(len(positions)):
    positions[row][0],positions[row][1] = xy.XYtoGPS(positions[row][0], positions[row][1], y_posi, x_posi)
    # 输出位置坐标
    if (row % 30 == 0):
        print("位置坐标: ",positions[row])


# ------ 画效果图 ------
dplt.dataPlot(positions, floor_posi, POSI_data,  GNSS_data,PRES_data)