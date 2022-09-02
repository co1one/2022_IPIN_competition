import numpy as np
import math
import dataProcessing as dp
import areaSearch as ars    # 判断场景
import pdrProcessing as pp  # 惯导解算
import XYtoGPS as xy
import timeMatching as tm
import mixPositions as mp
# import dataPlot as dplt
import wifiProcessing as wp
import presProcessing as prp

def main3(data, oriPos):
    # 输入数据行，初始坐标点

    # ---------------0、初始化----------------
    x_rela = 0  # 相对坐标
    y_rela = 0
    # 剔除初始部分的数据(在demo里面已经进行了剔除处理了)
    # 初始坐标，数值化，拆开等操作
    x_posi = float(oriPos[0])
    y_posi = float(oriPos[1])
    floor_posi = int(oriPos[2])
    data = dp.apiDataProcessing(data)   #传进来的网络数据进行处理（原来是str类型，转换为二维数组）
    # print(data[0:3])

    # -------------2、惯导解算---------------
    ACCE_data, AHRS_data, GYRO_data, POSI_data, GNSS_data, PRES_data, WIFI_data = pp.getDataInfo(data)  # 获取数据以及数据信息（数据个数以及采样频率）
    steps, acc_all = pp.stepDetection(ACCE_data)  # 从加速度数据中 获取有效的步数、(acc_all内含时间数据)

    step_length = pp.WeinbergApproach(steps)  # 计算步长
    yaw1 = pp.getYawFromAHRS(AHRS_data, steps)  # 从AHRS获取航向角

    # ----------- 3、读取数据 ------------
    # 返回的是 在steps的位置，存了一个传感器的索引
    GNSSIndex_FromStep = mp.dataIndexMatching(GNSS_data, steps)  # 读取GNSS数据(返回的是索引号)
    PRESIndex_FromStep = mp.dataIndexMatching(PRES_data, steps)  # 读取PRES数据
    WIFIIndex_FromStep = mp.dataIndexMatching(WIFI_data, steps)  # 读取WIFI数据

    # ------ 6、计算楼层高度 -------
    floor_step = np.zeros(len(steps))  # 定义一个全0列表，存楼层数据
    for i in range(len(steps)):
        # 如果这个位置不为0，说明在这一步有PRES数据
        if (PRESIndex_FromStep[i] != 0):
            floor = prp.presProcessing(float(PRES_data[int(PRESIndex_FromStep[i])][3]), PRES_data, floor_posi)  # 自定义函数，输入气压值，输出楼层高度
            floor_step[i] = floor  # 存楼层数据
    # print(floor_step)

    # -------- 4、根据上一个位置输出一个当前位置-------------
    positions = np.empty(shape=[0, 2], dtype=float)  # 创建一个位置矩阵
    positions = np.append(positions, [[x_rela, y_rela]], axis=0)  # 赋初值（自己设定的）

    for i in range(len(steps)):
        # ------ GNSS融合部分(仅室外用)------
        # 主要思路就是匹配两个列表的坐标值，然后把对应的传感器数据插入step列表中
        if (GNSSIndex_FromStep[i] != 0):  # 如果这个位置不为0，说明有GNSS数据
            GNSS_latit = float(GNSS_data[int(GNSSIndex_FromStep[i])][3])
            GNSS_long = float(GNSS_data[int(GNSSIndex_FromStep[i])][4])
            long_positions, lati_positions = xy.XYtoGPS(positions[i][0], positions[i][1], y_posi, x_posi)  # 相对坐标转换绝对坐标
            area_num = ars.areaSearch(lati_positions, long_positions)  # 判断不同区域,返回90-93
            GNSS_positions = xy.GPStoXY(GNSS_long, GNSS_latit, x_posi, y_posi)  # 经纬坐标转换相对坐标函数
            # print(positions[i]," and ",GNSS_positions)  # 输出某位置GNSS相对坐标
            positions = mp.mixPositions(GNSS_positions, positions, area_num)  # 融合算法(默认不处理突变)

        # ------- WIFI融合部分（仅室内用） ----------
        # 主要思路同上面GNSS数据融合
        if (WIFIIndex_FromStep[i] != 0):  # 如果在这一步上有WIFI数据
            wifiTime = float(WIFI_data[int(WIFIIndex_FromStep[i])][1])
            rssiData = []
            # 构建待匹配指纹RSSi，后面拿这个和已知指纹库匹配
            for row in range(len(WIFI_data)):
                if (abs(float(WIFI_data[row][1]) - wifiTime) < 2):
                    rssiData.append(WIFI_data[row])

            # 提取楼层（仅做1、2层楼的判断，0是默认值）
            if (len(rssiData) != 0):
                floor1or2 = wp.floor_get(rssiData)
                if (floor1or2 > 0 and floor_step[i] != 0):
                    floor_step[i] = floor1or2  # 更新1、2层楼数据
                wifiPosition = wp.rssi_get(rssiData, floor_step[i])  # RSS指纹匹配
                if (len(wifiPosition) != 0):
                    area_num = ars.areaSearch(wifiPosition[0][2], wifiPosition[0][1])  # 判断区域,返回90-93
                    if (area_num == 90):  # 如果位于室内，则进行wifi校正
                        WIFI_Positions = xy.GPStoXY(wifiPosition[0][1], wifiPosition[0][2], x_posi, y_posi) # 坐标转化
                        positions = mp.mixWIFIPositions(WIFI_Positions, positions)

        # ------- 生成新位置 ----------
        newXY_positions = pp.new_position(positions[i], yaw1[i], step_length[i])  # 生成新位置
        positions = np.append(positions, [newXY_positions], axis=0)

    # --------- 5、坐标转换函数（根据上一套数据生成新数据） ----------
    for row in range(len(positions)):
        positions[row][0], positions[row][1] = xy.XYtoGPS(positions[row][0], positions[row][1], y_posi, x_posi)
        # 输出位置坐标
        # if (row % 30 == 0):
        #     print("位置坐标: ",positions[row])

    # ------ 7、输出结果（只输出最新的一行数据） ------
    lenPos = len(positions)-1
    lenFloor = len(floor_step)-1
    # 先判断有没有生成新的坐标楼层数据
    if len(positions) != 1:
        x_posi = positions[lenPos][0]
        y_posi = positions[lenPos][1]
    if len(floor_step) != 0:
        floor_posi = floor_step[lenFloor]

    return x_posi, y_posi, floor_posi