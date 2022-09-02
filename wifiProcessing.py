import numpy as np
import XYtoGPS as xy

def get_xy(rssi,floor):
    if floor == 0:
        path_xy = "./wifi/wifi0.csv"
    if floor == 1:
        path_xy = "./wifi/wifi1.csv"
    if floor == 2:
        path_xy = "./wifi/wifi2.csv"
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
        path_ham = "D:\Self_File\个人\研究生\工作·实验·研究\IPIN竞赛\\2022smartphone\IPIN_webAPI_demo\program\wifi\wifi0_ham.csv"
    elif floor == 1:
        path_ham = "D:\Self_File\个人\研究生\工作·实验·研究\IPIN竞赛\\2022smartphone\IPIN_webAPI_demo\program\wifi\wifi1_ham.csv"
    elif floor ==2:
        path_ham = "D:\Self_File\个人\研究生\工作·实验·研究\IPIN竞赛\\2022smartphone\IPIN_webAPI_demo\program\wifi\wifi2_ham.csv"
    ham_data = np.loadtxt(path_ham, delimiter=',', dtype=np.float32)
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



def rssi_get(WIFI_data,floor):
    # 输入：WIFI_data 一批数据，floor一个数
    res = []
    tt = WIFI_data[0][1]
    # print(tt)
    a = -100 * np.ones(330)
    b = np.zeros(330)
    for i in range(len(WIFI_data)):
        if WIFI_data[i][1] == tt:
            num = int((WIFI_data[i][4])[-5:-3] + (WIFI_data[i][4])[-2:])
            if(num > 330):
                continue
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
    # 写转成GPS
    for i in range(len(res)):
        lon, lat = xy.XYtoGPS(y,x,41.453242221756,-8.289158860101)   # 输出经纬度
        res[i][1] = lon
        res[i][2] = lat
    return res  # [time, long, lati]


def floor_get(WIFI_data):
    floor1 = [62,92,98,104,109,142,223,287]
    floor2 = [16,119,125,151,178,182,184,188,215]
    floor_new = []
    tt = WIFI_data[0][1]
    a = 0
    for i in range(len(WIFI_data)):
        if WIFI_data[i][1] == tt:
            num = int((WIFI_data[i][4])[-5:-3] + (WIFI_data[i][4])[-2:])
            # print(int(WIFI_data[i][6]))
            if num in floor1:
                # print(int(WIFI_data[i][6]))
                if int(WIFI_data[i][6]) < -90:
                    a += 1
                    print(a)
                else: a -= 1
            if num in floor2:
                if int(WIFI_data[i][6]) < -90: a -= 1
                else: a += 1
        else:
            if a >= 0: floor_new.append(1)
            if a < 0: floor_new.append(2)
            tt = WIFI_data[i][1]
            a = 0
            num = int((WIFI_data[i][4])[-5:-3] + (WIFI_data[i][4])[-2:])
            if num in floor1:
                if int(WIFI_data[i][6]) < -90: a += 1
                else: a -= 1
            if num in floor2:
                if int(WIFI_data[i][6]) < -90: a -= 1
                else: a += 1

    if a >= 0: floor_new.append(1)
    if a < 0: floor_new.append(2)
    floor1or2 = floor_new[-1]  #取最后一位

    return floor1or2