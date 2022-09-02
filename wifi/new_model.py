import  matplotlib.pyplot as plt
import numpy as np
import math


CONSTANTS_RADIUS_OF_EARTH = 6371000.     # meters (m)
def GPStoXY(lat, lon):
    # input GPS and Reference GPS in degrees
    # output XY in meters (m) X:North Y:East
    lat_rad = math.radians(lat)
    lon_rad = math.radians(lon)
    ref_lat_rad = math.radians(41.453242221756)
    ref_lon_rad = math.radians(-8.289158860101)

    sin_lat = math.sin(lat_rad)
    cos_lat = math.cos(lat_rad)
    ref_sin_lat = math.sin(ref_lat_rad)
    ref_cos_lat = math.cos(ref_lat_rad)

    cos_d_lon = math.cos(lon_rad - ref_lon_rad)

    arg = np.clip(ref_sin_lat * sin_lat + ref_cos_lat * cos_lat * cos_d_lon, -1.0, 1.0)
    c = math.acos(arg)

    k = 1.0
    if abs(c) > 0:
        k = (c / math.sin(c))

    x = float(k * (ref_cos_lat * sin_lat - ref_sin_lat * cos_lat * cos_d_lon) * CONSTANTS_RADIUS_OF_EARTH)
    y = float(k * cos_lat * math.sin(lon_rad - ref_lon_rad) * CONSTANTS_RADIUS_OF_EARTH)

    return x, y


def XYtoGPS(self, x, y, ref_lat, ref_lon):
    x_rad = float(x) / self.CONSTANTS_RADIUS_OF_EARTH
    y_rad = float(y) / self.CONSTANTS_RADIUS_OF_EARTH
    c = math.sqrt(x_rad * x_rad + y_rad * y_rad)

    ref_lat_rad = math.radians(ref_lat)
    ref_lon_rad = math.radians(ref_lon)

    ref_sin_lat = math.sin(ref_lat_rad)
    ref_cos_lat = math.cos(ref_lat_rad)

    if abs(c) > 0:
        sin_c = math.sin(c)
        cos_c = math.cos(c)

        lat_rad = math.asin(cos_c * ref_sin_lat + (x_rad * sin_c * ref_cos_lat) / c)
        lon_rad = (ref_lon_rad + math.atan2(y_rad * sin_c, c * ref_cos_lat * cos_c - x_rad * ref_sin_lat * sin_c))

        lat = math.degrees(lat_rad)
        lon = math.degrees(lon_rad)

    else:
        lat = math.degrees(ref_lat)
        lon = math.degrees(ref_lon)

    return lat, lon


def oridataProcessing(data_route):
    #数据处理函数，把原始数据包处理成python可以利用的list格式
    #输入：文件路径（比如"E:/program/T01_01.txt"）
    #输出：二维列表（可以通过data[1][1]获取到某个数据）
    data = []
    with open(data_route, 'r', encoding="utf-8") as f:
        lines = f.readlines()   #按行读取
        for line in lines:
            if '%' in line:  #切除注释行
                continue
            line1 = line[:-1].split(';')
            data.append(line1)
    f.close()
    np.array(data, dtype=object)
    return data


def get_xy(rssi,floor):
    if floor == 0:
        path_xy = "./wifi0.csv"
    if floor == 1:
        path_xy = "./wifi1.csv"
    if floor == 2:
        path_xy = "./wifi2.csv"
    xy_data = np.loadtxt(path_xy,delimiter=',', dtype=np.float32)
    res = 80
    ans = False
    x = 0
    y = 0
    for i in range(len(xy_data)):
        a = []
        for n in range(330):
            a.append(xy_data[i][n])
        a = np.array(a)
        dis = np.sqrt(np.sum(np.square(a-rssi)))
        # print(dis)
        if dis < res:
            ans = True
            res = dis
            x = xy_data[i][-2]
            y = xy_data[i][-1]
    return ans,x,y



def ok_point(ham, floor):
    if floor == 0:
        path_ham = "./wifi0_ham.csv"
    elif floor == 1:
        path_ham = "./wifi1_ham.csv"
    elif floor ==2:
        path_ham = "./wifi2_ham.csv"
    ham_data = np.loadtxt(path_ham,delimiter=',', dtype=np.float32)
    res = 0
    ans = 0
    for i in range (len(ham_data)):
        res = 0
        for n in range(330):
            if ham[n] == ham_data[i][n] and ham[n]==1:
                res += 1
            if res > ans:
                ans = res
    return ans


# 就这个
def rssi_get(WIFI_data,floor):
    res = []
    tt = WIFI_data[0][1]
    print(tt)
    a = -100 * np.ones(330)
    b = np.zeros(330)
    for i in range(len(WIFI_data)):
        if WIFI_data[i][1] == tt:
            num = int((WIFI_data[i][4])[-5:-3] + (WIFI_data[i][4])[-2:])
            a[num - 1] = WIFI_data[i][6]
        else:
            # if ok_point(b,)
            for n in range(330):
                if a[n] != -100:
                    b[n] = 1
            if ok_point(b,floor) > 20:
                ans, x, y =get_xy(a,floor)
                if ans :
                    res.append([WIFI_data[i - 1][1], x, y])
            tt = WIFI_data[i][1]
            a = -100 * np.ones(330)
            b = np.zeros(330)
            num = int((WIFI_data[i][4])[-5:-3] + (WIFI_data[i][4])[-2:])
            a[num - 1] = WIFI_data[i][6]
    for n in range(330):
        if a[n] != -100:
            b[n] = 1
    if ok_point(b, floor) > 20:
        ans, x, y = get_xy(a, floor)
        if ans:
            res.append([WIFI_data[- 1][1], x, y])
    return res



# ----------test --------------
data = oridataProcessing("./47.txt")
data1 = oridataProcessing("./47.1.txt")

pos = rssi_get(data,0)   # 从data中提取指纹数据
print(pos)  # [时间，x纬度，y经度]
# print((pos[0][1]).tolist())
x = []
y = []
for i in range (len(pos)):
    x.append((pos[i][1]).tolist())  # x
    y.append((pos[i][2]).tolist())  # y


#
# x1 = []
# y1 = []
# for i in range(len(data1)):  # 测试数据
#     if data1[i][0] == "POSI":
#         # print(float(data1[i][3]))
#         a,b = GPStoXY(float(data1[i][3]),float(data1[i][4]))
#         x1.append(a)
#         y1.append(b)
# # 生成一个Figure画布和一个Axes坐标系
# fig, ax = plt.subplots()
# # 在生成的坐标系下画折线图
# ax.plot(x, y, "ro-", 1)
# ax.plot(x1, y1, "b", 1)
# # 显示图形
# plt.show()
