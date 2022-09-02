import numpy as np
import math
import matplotlib.pyplot as plt
from scipy import signal
from scipy.spatial.transform import Rotation as R


# 数据处理函数，把原始数据包处理成python可以利用的list格式  直接获取第一个POSI之后的真实数据
# 和那个同名函数不大一样
def dataProcessing(data_route): # (剔除前面数据的版本)
    #数据处理函数，把原始数据包处理成python可以利用的list格式  直接获取第一个POSI之后的真实数据
    #输入：文件路径（比如"E:/program/T01_01.txt"）
    #输出：二维列表（可以通过data[1][1]获取到某个数据）
    raw_data = []
    data = []
    with open(data_route, 'r', encoding="utf-8") as f:
        lines = f.readlines()   #按行读取
        for line in lines:
            if '%' in line:  #切除注释行
                continue
            line1 = line[:-1].split(';')
            raw_data.append(line1)
    f.close()
    np.array(raw_data, dtype=object)
    num = 0
    start = 0
    for row in range(0, len(raw_data)):
        if (raw_data[row][0] == 'POSI'):
            start = row
            break
    for row in range(start, len(raw_data)):
         data.append(raw_data[row])
         num = num + 1
    return data


# raw_data格式为 （数据个数）*（标签个数）
# 返回值 采样频率与采样时间
def getDataFre(raw_data):
    sensor_timestamp = []
    for i in range(len(raw_data)):
        sensor_timestamp.append(float(raw_data[i][2]))
    if (len(sensor_timestamp) == 0):
        return 100, 0.5
    time_interval = []
    for i in range(len(sensor_timestamp) - 1):
        time_interval.append(sensor_timestamp[i + 1] - sensor_timestamp[i])
    sampling_frequency = 1 / np.mean(time_interval)
    sampling_time = sensor_timestamp[len(sensor_timestamp) - 1] - sensor_timestamp[0]
    # print(raw_data[0][0],"当前的采样频率 ：", sampling_frequency, "Hz","当前的采样时间：", sampling_time, "秒")

    return sampling_frequency,sampling_time


# 通过前四个字母标志，获取单一的某一条数据
def getDataInfo(data):
    ACCE_data = []
    AHRS_data = []
    GYRO_data = []
    POSI_data = []
    GNSS_data = []
    PRES_data = []
    WIFI_data = []
    for row in range(len(data)):
        if data[row][0] == 'ACCE':
            ACCE_data.append(data[row])
        if data[row][0] == 'AHRS':
            AHRS_data.append(data[row])
        if data[row][0] == 'GYRO':
            GYRO_data.append(data[row])
        if data[row][0] == 'POSI':
            POSI_data.append(data[row])
        if data[row][0] == 'GNSS':
            GNSS_data.append(data[row])
        if data[row][0] == 'PRES':
            PRES_data.append(data[row])
        if data[row][0] == 'WIFI':
            WIFI_data.append(data[row])
    # print("一共有", len(data), "条数据", "其中ACCE数据有", len(ACCE_data), "条，AHRS数据有", len(AHRS_data), "条,GYRO数据有", len(GYRO_data), "条,","MAGN数据有",len(MAGN_data),"条，","POSI数据有",len(POSI_data), "条,","GNSS数据有",len(GNSS_data), "条。")

    getDataFre(ACCE_data)
    getDataFre(AHRS_data)
    getDataFre(GYRO_data)
    # getDataFre(GNSS_data)
    return ACCE_data,AHRS_data,GYRO_data,POSI_data,GNSS_data,PRES_data,WIFI_data


# 对数据进行一个对齐 一个ACCE对应一个AHRS
def data_Alignment(data) :
    temp_row1 = 0

    ahrs = np.empty(shape=[0, 3], dtype=float)
    for row in range(len(data)):
        a = np.empty(shape=[0, 3], dtype=float)
        if (data[row][0] == 'ACCE'):
            temp_row2 = row
            data.append(data[row])
            ahrs_temp = np.empty(shape=[0, 3], dtype=float)
            for i in range(temp_row1, temp_row2):
                if (data[i][0] == 'AHRS'):
                    ahrs_temp = np.append(ahrs_temp,
                                          [[float(data[i][3]), float(data[i][4]), float(data[i][5])]],
                                          axis=0)
            if (len(ahrs_temp)):
                a = np.mean(ahrs_temp, axis=0)
                temp_row1 = temp_row2
                ahrs = np.append(ahrs, [a], axis=0)

    print("ahrs的个数", len(ahrs))


# 输入三个数，输出平方求和开方
def square_sum_sqrt(num,x1,x2,x3):
    res = []
    for i in range(num):
        res.append(math.sqrt(x1[i] ** 2 + x2[i] ** 2 + x3[i] ** 2))
    return res


# 坐标系转换：输入Euler AcceData数组 返回坐标变换后的数据 AcceDataInNewCoordinate
# Euler规模(n*3)
def CoordinateConvert(Euler,AcceData):
    row = math.radians(Euler[0])
    pitch = math.radians(Euler[1])
    yaw = math.radians(Euler[2])

    R1 = np.array([ [np.cos(row), 0, -np.sin(row)],
          [0, 1, 0],
          [np.sin(row), 0, np.cos(row)]])
    R2 = np.array([ [1, 0, 0],
          [0, np.cos(pitch), np.sin(pitch)],
          [0, -np.sin(pitch), np.cos(pitch)]])
    R3 = np.array([[np.cos(yaw), np.sin(yaw),0],
          [-np.sin(yaw), np.cos(yaw),0],
          [0, 0, 1]])
    C1 = np.dot(R1,R2)
    C = np.dot(C1,R3)
    AcceDataInNewCoordinate = np.dot(C, AcceData)
    return AcceDataInNewCoordinate


# 四元数 -> 欧拉角
def quaternion2euler(quaternion):
    r = R.from_quat(quaternion)
    euler = r.as_euler('xyz', degrees=True)
    return euler


# 均值滤波
def ava_filter(x,length):
    N = len(x)
    res = []
    for i in range(N):
        if i <= length //2 or i >= N - (length // 2):
            temp = x[i]
        else:
            sum = 0
            for j in range(length):
                sum += x[i-length//2+j]
            temp = sum*1.0 / length
        res.append(temp)
    return res


# 用于显示POSI 显示出大致的轨迹
def show_POSI(POSI_data):
    Latitude = []
    Longitude = []
    for i in range(len(POSI_data)):
        Latitude.append(float(POSI_data[i][3]))
        Longitude.append(float(POSI_data[i][4]))
        print(POSI_data[i])
    # plt.figure(1)
    # plt.plot(Latitude, Longitude, color='blue', label='acce_all')
    # plt.plot(Latitude, Longitude, 'o')
    # for j in range(len(POSI_data)):
    #     plt.text(Latitude[j],Longitude[j],POSI_data[j][2])
    # plt.show()


# 寻找信号波峰波谷  输入acc合加速度
def find_peaks_self_adaption(acc_data):
    peaks_num = 0
    peaks_value = []
    if (len(acc_data) == 0):
        return [],0,0
    peaks = signal.find_peaks(acc_data, distance=30 ,height=0)
    peaks_temp = list(peaks[1].values())
    peak_max = np.max(peaks_temp)
    peak_min = np.min(peaks_temp)
    # print(peak_max, peak_min)
    #定义了一个经验化的数值
    #
    height = peak_max * 0.5 + peak_min * 0.5
    if(height > 0.8 and height < 5 ):
    # print(height)
        peaks = signal.find_peaks(acc_data, distance=35 ,height= height)
        # print("height=",height)
        peaks_num = len(peaks[0])
        peaks_value = np.array(list(peaks[1].values())[0])

    return peaks[0],peaks_num,peaks_value


# 进行步数检测的模块
# 输入 加速度数据
# 输出 步数 每一步的区间
def stepDetection(ACCE_data):
    acc = np.empty(shape=[0, 4], dtype=float)
    for row in range(len(ACCE_data)):
        acc = np.append(acc, [[float(ACCE_data[row][1]), float(ACCE_data[row][3]), float(ACCE_data[row][4]), float(ACCE_data[row][5])]], axis=0)

    # plt.figure(0)
    # plt.plot(acc.T[1],color='blue', label='x')
    # plt.plot(acc.T[2],color='red', label='y')
    # plt.plot(acc.T[3],color='green', label='z')
    # plt.legend()
    # plt.title('ACC_ROW_DATA')
    # plt.show()

    # 获得加速度的初始数据 （时间，x，y，z）
    # 坐标变换 先省略
    # 进行一个三轴的均值滤波
    acc_x = ava_filter(acc.T[1],12)
    acc_y = ava_filter(acc.T[2],12)
    acc_z = ava_filter(acc.T[3],12)
    # plt.figure(0)
    # plt.plot(acc_x,color='blue', label='x')
    # plt.plot(acc_y,color='red', label='y')
    # plt.plot(acc_z,color='green', label='z')
    # plt.legend()
    # plt.title('ACC_SMOOTH_DATA')
    # plt.show()

    smooth_all = square_sum_sqrt(len(ACCE_data), acc_x, acc_y, acc_z)
    acc_all = np.empty(shape=[0, 2], dtype=float)
    for i in range(len(ACCE_data)):
        acc_all = np.append(acc_all, [[float(acc.T[0][i]), smooth_all[i]-9.8]], axis=0)
         # 画出减去重力之后的和加速度
         #acc_all 的结构  n行2列 第一列 是时间序列 第二列是加速度序列
    # plt.figure(1)
    # plt.plot(acc_all.T[1],color='blue', label='acce_all')
    # plt.title('ACC')
    # plt.show()


    #接下来进行峰值检测
    peaks_position,peaks_num,peaks_value = find_peaks_self_adaption(acc_all.T[1])

    peaks_time = []
    for i in range(peaks_num):
        peaks_time.append(acc_all.T[0][peaks_position[i]])

    peaks = np.empty(shape=[0, 3], dtype=float)
    for k in range(peaks_num):
        peaks = np.append(peaks, [[peaks_time[k], peaks_value[k], peaks_position[k]]], axis=0)
    # print(peaks)

    # #波谷检测
    valleys = np.empty(shape=[0, 3], dtype=float)
    for i in range(peaks_num-1):

        valley_temp = np.empty(shape=[0, 3], dtype=float)
        for j in range(peaks_position[i],peaks_position[i+1]):
            valley_temp = np.append(valley_temp, [[acc_all.T[0][j],acc_all.T[1][j],j]], axis=0)

            ## 找到temp 中最小的 加入到valleys中。
        # print(len(valley_temp))
        tem_min = valley_temp[0]
        for row in range(len(valley_temp-1)):
            if(tem_min[1] > valley_temp[row][1] ):
                tem_min = valley_temp[row]
        valleys = np.append(valleys, [[tem_min[0], tem_min[1], tem_min[2]]], axis=0)
          #到这里其实最后一步的波谷还未找到，想法：在之后的30个点内找一个最小值 设置为最后一个波谷
    if (len(peaks) == 0):
        return [], acc_all

    last_peak_position = int(peaks[-1][2])
    last_valley = peaks[-1]
    if (last_peak_position + 30) < len(acc_all):
        for i in range(last_peak_position,last_peak_position+30):
            if(last_valley[1] > acc_all.T[1][i]):
                last_valley = [acc_all.T[0][i], acc_all.T[1][i], i]
        valleys = np.append(valleys,[last_valley],axis=0)
    # else :
        # peaks[-1] = None

    # print("峰值的个数:", len(peaks))
    # print("波谷的个数：",len(valleys))
    # # 峰值可视化
    # for i in range(len(peaks_position)):
    #     plt.plot(peaks_position[i], acc_all.T[1][peaks_position[i]], 'o', markersize=6)
    # #波谷可视化
    # for i in range(len(valleys)):
    #     plt.plot(valleys.T[2], valleys.T[1], 'x', markersize=6)
    # plt.show()
    # 至此获取到了波峰 与波谷 结构为一个n*3的数组 每一行的数据分别是（峰值所在的传感器时间、峰值的大小、峰值在acc数据中的位置（主要用于显示））
    step = np.empty(shape=[0, 6], dtype=float)
    # print(peaks[0][0],valleys[0][0],peaks[0][2],valleys[0][2])
    for i in range(len(valleys)):
        if (valleys[i][2]-peaks[i][2]) > 10 :
            step = np.append(step, [[peaks[i][0], valleys[i][0], peaks[i][1], valleys[i][1],peaks[i][2],valleys[i][2]]], axis=0)
    print("检测到的有效步数： ",len(step))

    return step, acc_all


# 计算步长  输出步长
# Weinberg 方法： 一种基于经验的经典模型  主要是k值怎么确定
def WeinbergApproach(step):
    if (len(step) == 0):
        return 0
    step_length = []

    k = 0.47
    for i in range(len(step)):
        a = step[i][2]-step[i][3]
        length = k * math.sqrt(math.sqrt(a))
        step_length.append(length)
    # print(step_length)
    return step_length


# GYRO数据的积分 虽然数值不是很准确 但是可以很明显的反映出出现转弯的行为，筛选出转弯的区间
def getYawFromGYRO(GYRO_data,steps):
    #先对GYRO_data 数据进行积分处理
    yaw_data = np.empty(shape=[0, 4], dtype=int)
    for i in range(len(GYRO_data)-1):
        time_interval = float(GYRO_data[i+1][1])-float(GYRO_data[i][1])
        yaw_data = np.append(yaw_data,[[float(GYRO_data[i][5]),float(GYRO_data[i+1][1]),time_interval,0]],axis=0)
        #yaw-data格式（z轴的陀螺仪数据、数据的传感器时间，此条数据与上一条数据的差值,积分数据）
    temp = 0
    # plt.figure(1)
    # plt.plot(yaw_data.T[0], color='green', label='GYRO_Z')
    # plt.show()

    for j in range(len(yaw_data)):
        temp = temp + yaw_data[j][2] * yaw_data[j][0]
        angle_in_deg = math.degrees(temp)
        yaw_data[j][3] = angle_in_deg
    # plt.figure(1)
    # plt.plot(yaw_data.T[3], color='red', label='Integral_GYRO_Z')
    # plt.show()
    # return yaw_data.T[3]
   # # 从积分后的数据总选出每一步的值
   #
    start = 0
    yaw = []
    for i in range(len(steps)):
        end = steps[i][1]

        temp_yaw = []
        for j in range(len(yaw_data)):
            if (float(yaw_data[j][1]) > start) and (float(yaw_data[j][1]) < end):
                temp_yaw.append(float(yaw_data[j][3]))
        yaw.append(np.mean(temp_yaw))
        start = end
    # plt.figure(2)
    # plt.plot(yaw, color='red')
    # plt.title('GYRO_BY_STEP')
    # plt.show()
    delta_yaw = []
    for i in range(len(yaw) - 1):
        delta_yaw.append(yaw[i + 1] - yaw[i])
    # plt.figure(4)
    # plt.plot(delta_yaw)
    # plt.show()
    position1 = signal.find_peaks(delta_yaw, distance=4, height=10)
    value1 = np.array(list(position1[1].values())[0])
    inverse_delta_yaw = [-l for l in delta_yaw]
    position2 = signal.find_peaks(inverse_delta_yaw, distance=4, height=10)
    value2 = np.array(list(position2[1].values())[0])
    position = []
    # position.append(0)
    # position.append(len(steps))
    for i in range(len(position1[0])):
        position.append([position1[0][i],value1[i]])
    for i in range(len(position2[0])):
        position.append([position2[0][i],value2[i]])
    # position = sorted(position)
    position.append([0,0])
    position.append([len(steps),0])
    position = sorted(position)
    return position



# 获取到每一步对应的航向角  返回yaw
def getYawFromAHRS(AHRS_data,steps):
    yaw = []
    start = 0
    for i in range(len(steps)):
        # start = steps[i][0]
        end = steps[i][1]
        # print(start,end)
        temp_yaw = []
        for j in range(len(AHRS_data)):
            if (float(AHRS_data[j][1]) > start) and (float(AHRS_data[j][1]) < end):
                temp_yaw.append(float(AHRS_data[j][5]))
       # 问题所在 对所有的航行进行一个求均值的过程非常的粗暴
        if (len(temp_yaw) == 0):
            return 0
        difference = np.max(temp_yaw) - np.min(temp_yaw)
        # print(difference)
        if difference < 10:
            angle = np.mean(temp_yaw)
        else:
            angle = averageByNum(temp_yaw)
       #  angle = np.max(temp_yaw)
        yaw.append(angle)
        start = end
    # yaw = dp.ava_filter(yaw,5)
    # plt.figure(1)
    # plt.plot(yaw, color='red', label='yawZ')
    # plt.title("yaw from getYawFromAHRS")
    # plt.show()
    return yaw


# 结合AHRS和GYRO两个的输出角
def getYawCombineAHRSandGYRO(corner_position,yaw):
    new_yaw = []
    for i in range(len(corner_position) - 1):
        temp = []
        for j in range(corner_position[i][0], corner_position[i+1][0]):
            temp.append(yaw[j])
        temp = ava_filter(temp, 5)
        for k in range(len(temp)):
            new_yaw.append(temp[k])
    # plt.figure(1)
    # plt.plot(new_yaw)
    # plt.title("new_yaw from getYawCombineAHRSandGYRO")
    # plt.show()
    return new_yaw


# 输入旧位置，输出新位置
def new_position(previous_position,angel,step_length):
    x = previous_position[0]
    y = previous_position[1]
    new_x = x - step_length * np.sin(math.radians(angel))  # 在西半球
    new_y = y + step_length * np.cos(math.radians(angel))
    position = [new_x, new_y]
    return position


# 进行一个分正负求均值的过程， 正数多 返回正数均值 ，负数多 返回负数均值
def averageByNum(x):
    p = 0
    p_temp = 0
    n = 0
    n_temp = 0
    for i in range(len(x)):
        if x[i] >= 0:
            p = p+1
            p_temp = p_temp + x[i]
        else:
            n = n + 1
            n_temp = n_temp + x[i]
    if p >= n :
        return float(p_temp/p)
    else:
        return float(n_temp/n)


# 绝对值的平均值
def averageByAbs(x):
    for i in range(len(x)):
        if x[i] < 0 :
            x[i] = math.fabs(x[i])
    return np.mean(x)



