import numpy as np
import math
import dataProcessing as dp
import areaSearch as ars    # 判断场景
import pdrProcessing as pp  # 惯导解算
import XYtoGPS as xy
import timeMatching as tm
import mixPositions as mp
import dataPlot as dplt
import wifiProcessing as wp
import presProcessing as prp

# ---------------0、初始化----------------
x_rela = 0      # 相对坐标
y_rela = 0
# data_route = "./TestingData/"
# data_name = "IPIN2022_T3_TestingTrial51_User03.txt"
data_route = "./TrainingData/"
data_name = "IPIN2022_T3_TrainingTrial51_User03.txt"

# 两个函数二选一，视情况而定
# data = dp.oridataProcessing(data_route + data_name)  # 原始数据处理（未剔除）
data = pp.dataProcessing(data_route + data_name)   #剔除了第一个posi前的数据


# ------ 1、获取初始点 ------(可选手动或自动)
# (1)自动
for row in range(len(data)):
    if (data[row][0] == 'POSI'):
        x_posi = float(data[row][4])
        y_posi = float(data[row][3])
        floor_posi = int(data[row][5])
        break
# x_posi, y_posi = dp.getOriPoint(data)
# floor_posi = 0
# (2)手动
x_posi = 0
y_posi = 0
floor_posi = 0

# -------------2、惯导解算---------------
ACCE_data,AHRS_data,GYRO_data,POSI_data,GNSS_data,PRES_data,WIFI_data= pp.getDataInfo(data)  # 获取数据以及数据信息（数据个数以及采样频率）
steps,acc_all = pp.stepDetection(ACCE_data)  # 从加速度数据中 获取有效的步数、(acc_all内含时间数据)

step_length = pp.WeinbergApproach(steps)  # 计算步长
yaw1 = pp.getYawFromAHRS(AHRS_data, steps)  # 从AHRS获取航向角


# ----------- 3、读取数据 ------------
# 返回的是 在steps的位置，存了一个传感器的索引
GNSSIndex_FromStep = mp.dataIndexMatching(GNSS_data,steps)  # 读取GNSS数据(返回的是索引号)
PRESIndex_FromStep = mp.dataIndexMatching(PRES_data,steps)  # 读取PRES数据
WIFIIndex_FromStep = mp.dataIndexMatching(WIFI_data,steps)  # 读取WIFI数据


# ------ 6、计算楼层高度 -------
floor_step = np.zeros(len(steps))   # 定义一个全0列表，存楼层数据
for i in range(len(steps)):
    if (PRESIndex_FromStep[i] != 0):  # 如果这个位置不为0，说明在这一步有PRES数据
        floor = prp.presProcessing(float(PRES_data[int(PRESIndex_FromStep[i])][3]),PRES_data,floor_posi)  # 自定义函数，输入气压值，输出楼层高度
        floor_step[i] = floor  # 存数据


# -------- 4、根据上一个位置输出一个当前位置-------------
positions = np.empty(shape=[0, 2], dtype=float)   # 创建一个位置矩阵
positions = np.append(positions, [[x_rela, y_rela]], axis=0)  # 赋初值（自己设定的）

for i in range(len(steps)):
    # ------ GNSS融合部分(仅室外用)------
    if (GNSSIndex_FromStep[i] != 0):  # 如果这个位置不为0，说明有GNSS数据
        GNSS_latit = float(GNSS_data[int(GNSSIndex_FromStep[i])][3])
        GNSS_long = float(GNSS_data[int(GNSSIndex_FromStep[i])][4])
        long_positions, lati_positions = xy.XYtoGPS(positions[i][0], positions[i][1], y_posi, x_posi)
        area_num = ars.areaSearch(lati_positions, long_positions)  # 判断区域,返回90-93
        GNSS_positions = xy.GPStoXY(GNSS_long, GNSS_latit, x_posi, y_posi)  # 经纬坐标转换相对坐标函数
        # print(positions[i]," and ",GNSS_positions)  # 输出某位置GNSS相对坐标
        positions = mp.mixPositions(GNSS_positions, positions, area_num)  # 融合算法(默认不处理突变)

    # ------- WIFI融合部分（仅室内用） ----------
    if (WIFIIndex_FromStep[i] != 0):  # 在这一步上有WIFI数据
        wifiTime = float(WIFI_data[int(WIFIIndex_FromStep[i])][1])
        rssiData = []
        # 筛选WiFi数据
        for row in range(len(WIFI_data)):
            if (abs(float(WIFI_data[row][1]) - wifiTime) < 2):
                rssiData.append(WIFI_data[row])

        if (len(rssiData) != 0):
            floor1or2 = wp.floor_get(rssiData)  # 提取楼层
            if (floor1or2 > 0 and floor_step[i] != 0):
                floor_step[i] = floor1or2  #更新1、2层楼数据
            wifiPosition = wp.rssi_get(rssiData, floor_step[i])
            if (len(wifiPosition) != 0):
                area_num = ars.areaSearch(wifiPosition[0][2], wifiPosition[0][1])  # 判断区域,返回90-93
                if (area_num == 90):
                    WIFI_Positions = xy.GPStoXY(wifiPosition[0][1],wifiPosition[0][2],x_posi,y_posi)
                    positions = mp.mixWIFIPositions(WIFI_Positions,positions)

    # ------- 生成新位置 ----------
    newXY_positions = pp.new_position(positions[i], yaw1[i], step_length[i])  # 生成新位置
    positions = np.append(positions, [newXY_positions],axis=0)


#--------- 5、坐标转换函数 ----------
for row in range(len(positions)):
    positions[row][0],positions[row][1] = xy.XYtoGPS(positions[row][0], positions[row][1], y_posi, x_posi)
    # 输出位置坐标
    # if (row % 30 == 0):
    #     print("位置坐标: ",positions[row])

# ------ 7、画效果图，出结果 ------
for i in range(len(steps)):
    if (i % 10 == 0):
        print("位置：",positions[i]," 层高：",floor_step[i])

# dplt.dataPlot(positions, floor_step, POSI_data, GNSS_data,PRES_data,AHRS_data)