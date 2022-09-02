import math
import numpy as np
import timeMatching as tm

def dataIndexMatching(sensor_data, step_data):
    # 数据匹配函数
    # 输入：单一的传感器数据，步长数据列表
    # 输出：对应的索引列表
    Index_FromStep = np.zeros(len(step_data))  # 定义一个零向量，存放Step索引
    for row in range(len(sensor_data)):
        sensor_time = sensor_data[row][1]
        step_num = tm.timeMatching(sensor_time, step_data)  # 时间匹配函数
        if (step_num != -1):
            Index_FromStep[step_num] = row  # 在step的索引位置存放一个gnss的索引号(通过索引号互相对应)
    return Index_FromStep



def mixPositions(GNSS_Positions, positions, area_num, mut_sign = False):
    # 输入GNSS相对坐标，positions相对坐标集合，区域代号, 突变点处理标识符
    # 输出更新后的positions集合

    # 0、初始化
    len_posi = len(positions)-1  # 数组长度
    mut_point = 15  # 大概是10米 (这里已经拉不回来了)
    weight1 = 0.6   # 当前点GNSS权重(不能固定)（用卡尔曼滤波试一下）
    weight2 = 0.4   # -1 点GNSS权重
    weight3 = 0.2  # -2 点GNSS权重

    # for i in range(len_posi):
    #     # 每隔一段时间使用GNSS纠正一次，将GNSS的前几次数据和GNSS数据进行加权平均
    #     distance = math.sqrt(math.pow(positions[i][0] - GNSS_Positions[0], 2) + math.pow(positions[i][1] - GNSS_Positions[1], 2))
    #     if (i % 10 == 0 and i > 3 and area_num!=90 and distance < mut_point):  #每3len个点使用GNSS纠正一次
    #         positions[i][0] = (1 - weight1) * positions[i][0] + weight1 * GNSS_Positions[0]
    #         positions[i][1] = (1 - weight1) * positions[i][1] + weight1 * GNSS_Positions[1]
    #         positions[i-1][0] = (1 - weight2) * positions[i-1][0] + weight2 * GNSS_Positions[0]
    #         positions[i-1][1] = (1 - weight2) * positions[i-1][1] + weight2 * GNSS_Positions[1]
    #         positions[i-2][0] = (1 - weight3) * positions[i-2][0] + weight3 * GNSS_Positions[0]
    #         positions[i-2][1] = (1 - weight3) * positions[i-2][1] + weight3 * GNSS_Positions[1]

    distance = math.sqrt(math.pow(positions[len_posi][0] - GNSS_Positions[0], 2) + math.pow(positions[len_posi][1] - GNSS_Positions[1], 2))
    if (len_posi>3 and area_num!=90 and distance < mut_point):  #每3len个点使用GNSS纠正一次
        positions[len_posi][0] = (1 - weight1) * positions[len_posi][0] + weight1 * GNSS_Positions[0]
        positions[len_posi][1] = (1 - weight1) * positions[len_posi][1] + weight1 * GNSS_Positions[1]
        positions[len_posi-1][0] = (1 - weight2) * positions[len_posi-1][0] + weight2 * GNSS_Positions[0]
        positions[len_posi-1][1] = (1 - weight2) * positions[len_posi-1][1] + weight2 * GNSS_Positions[1]
        positions[len_posi-2][0] = (1 - weight3) * positions[len_posi-2][0] + weight3 * GNSS_Positions[0]
        positions[len_posi-2][1] = (1 - weight3) * positions[len_posi-2][1] + weight3 * GNSS_Positions[1]

    return positions  # 输出的相对坐标




def mixWIFIPositions(WIFI_Positions,positions):
    # 输入：

    # 0、初始化
    length = len(positions)-1  # 数组长度
    mut_point = 30  # 大概是10米 (这里已经拉不回来了)
    weight1 = 0.6  # 当前点权重(不能固定)（用卡尔曼滤波试一下）
    weight2 = 0.3  # -1 点权重
    weight3 = 0.1  # -2 点权重

    # 每隔一段时间使用纠正一次，将GNSS的前几次数据和GNSS数据进行加权平均
    distance = math.sqrt(math.pow(positions[length][0] - WIFI_Positions[0], 2) + math.pow(positions[length][1] - WIFI_Positions[1], 2))
    if (length>3 and distance < mut_point):  # 每3len个点使用GNSS纠正一次
        positions[length][0] = (1 - weight1) * positions[length][0] + weight1 * WIFI_Positions[0]
        positions[length][1] = (1 - weight1) * positions[length][1] + weight1 * WIFI_Positions[1]
        positions[length -1][0] = (1 - weight2) * positions[length - 1][0] + weight2 * WIFI_Positions[0]
        positions[length - 1][1] = (1 - weight2) * positions[length - 1][1] + weight2 * WIFI_Positions[1]
        positions[length - 2][0] = (1 - weight3) * positions[length - 2][0] + weight3 * WIFI_Positions[0]
        positions[length - 2][1] = (1 - weight3) * positions[length - 2][1] + weight3 * WIFI_Positions[1]
    return positions  # 输出的相对坐标