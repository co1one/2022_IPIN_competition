import numpy  # 用来处理数据
import matplotlib.pyplot as plt
import numpy as np
import pandas as pd
import os
import csv


path = "./wifi2_xy.csv"
data = np.loadtxt(path,delimiter=',', dtype=np.float32)
out = open('./wifi2.csv', 'w', newline='')
csv_writer = csv.writer(out, dialect='excel')
a = np.zeros(330)
num = 0
x = data[0][-2]
y = data[0][-1]
for i in range (len(data)):
    if data[i][-2] != x and data[i][-1] != y :
        for n in range (330):
            for h in range(num):
                a[n] += data[i-h-1][n]
            a[n] = a[n] / num
        num = 0
        a = np.append(a, x)
        a = np.append(a, y)
        csv_writer.writerow(a)
        a = np.zeros(330)
        x = data[i][-2]
        y = data[i][-1]
    else: num += 1
print(a)
print(num)
for n in range (330):
    for h in range(num):
        a[n] += data[len(data)-h-2][n]
    a[n] = a[n] / num
a = np.append(a, x)
a = np.append(a, y)
csv_writer.writerow(a)

