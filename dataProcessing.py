import numpy as np

def apiDataProcessing(data):
    dataArray = []
    dataList = data.split('\n')
    for dataRow in dataList:
        dataArray.append(dataRow.split(';'))
    return dataArray


def oridataProcessing(data_route):
    #数据处理函数，把原始数据txt文件处理成python可以利用的list格式
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


# 获取初始点
def getOriPoint(data):
    #根据GNSS数据获取到初始坐标点（不大准）
    num = 0
    x_posi = 0
    y_posi = 0
    floor_posi = 0
    for data_row in data:
        if (data_row[0] == "GNSS" and num < 3):
            num = num + 1
            x_posi = x_posi + float(data_row[4])
            y_posi = y_posi + float(data_row[3])
    x_posi = x_posi / 3
    y_posi = y_posi / 3
    return x_posi,y_posi




# ---------测试----------
# data_route = "./T01_01.txt"
# data = dataProcessing(data_route)
# print(data[1:3][0:5])
# print(type(data))
