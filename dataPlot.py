import numpy as np
import matplotlib.pyplot as plt
import matplotlib as mpl
from mpl_toolkits.mplot3d import Axes3D

def dataPlot(positions, floor_step, POSI_data, GNSS_data,PRES_data,AHRS_data):

    positions = positions.T
    plt.figure(1)

# ------ 画预测路的图
    plt.xlim(-8.290433482496269,-8.28807139845192)
    plt.ylim(41.4525947805016, 41.45418090796697)
    plt.plot(positions[0],positions[1], color='blue',zorder=1)
    plt.plot(positions[0],positions[1],'o',zorder=1)
    plt.title("Predicted Route Figure")
    plt.xlabel("Longitude(degrees)")
    plt.ylabel("Latitude(degrees)")

    # ------ 标记初始点 ------
    ori_positions = np.zeros([2,1])
    ori_positions[0] = positions[0][:1]
    ori_positions[1] = positions[1][:1]
    plt.scatter(ori_positions[0],ori_positions[1],color="orange",zorder=3)
    # zorder 表示图层层数，数越大表示越靠上层显示

    # ------ 画POSI的路线图 ------
    x_posi = []
    y_posi = []
    floor_posi = []
    for row in range(len(POSI_data)):
        x_posi.append(float(POSI_data[row][4]))
        y_posi.append(float(POSI_data[row][3]))
        floor_posi.append(float(POSI_data[row][5]))
    plt.plot(x_posi,y_posi, color='red',zorder=2)
    plt.plot(x_posi,y_posi,'o',color='red',zorder=2)

    # ---- 画三维图------
    fig = plt.figure(2)
    ax = fig.gca(projection='3d')
    ax.plot(x_posi, y_posi, floor_posi)
    plt.title("3D floor")
    plt.show()


    # ------ 画只有GNSS的图 ------
    # x_gnss = []
    # y_gnss = []
    # high_gnss = []
    # num = 0
    # for row in range(len(GNSS_data)):
    #     if (num % 10 == 0):
    #         x_gnss.append(float(GNSS_data[row][4]))
    #         y_gnss.append(float(GNSS_data[row][3]))
    #         high_gnss.append(float(GNSS_data[row][5]))
    #     num = num + 1
    # plt.figure(2)
    # plt.xlim(-8.290433482496269, -8.28807139845192)
    # plt.ylim(41.4525947805016, 41.45418090796697)
    # plt.title("Only GNSS")
    # plt.plot(x_gnss, y_gnss, color="purple")
    # plt.plot(x_gnss, y_gnss, 'o',color="purple")
    # plt.plot(high_gnss)

    # ---------画 层高示意图 ----------
    plt.figure(3)
    plt.ylim(-0.2,2.2)
    plt.title("real floor")
    xx1 = range(len(floor_posi))
    plt.plot(xx1,floor_posi,color='red')

    plt.figure(4)
    plt.ylim(-0.2, 2.2)
    plt.title("estimate floor")
    xx2 = range(len(floor_step))
    plt.plot(xx2,floor_step,color='blue')

    plt.figure(5)
    plt.title("PRES data")
    presData = []
    for row in range(len(PRES_data)):
        presData.append(float(PRES_data[row][3]))
    xx3 = range(len(presData))
    plt.plot(xx3,presData)

    # ------ 画角度的坐标 -------
    # plt.figure(6)
    # ahrsX = []
    # ahrsY = []
    # ahrsZ = []
    # for row in range(len(AHRS_data)):
    #     ahrsX.append(float(AHRS_data[row][3]))
    #     ahrsY.append(float(AHRS_data[row][4]))
    #     ahrsZ.append(float(AHRS_data[row][5]))
    # xx = range(len(ahrsX))
    # plt.plot(xx,ahrsX,color='blue')
    # plt.plot(xx,ahrsY,color='red')
    # plt.plot(xx,ahrsZ,color='green')
    # plt.title("AHRS yaw data")

    # ------ 显示图像------
    plt.show()