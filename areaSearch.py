import numpy as np

def linearEquation(x1,y1,x2,y2):
    # 输入：两点坐标
    # 线性方程y=kx+b，
    # 输出：输出两个参数k和b
    k = (y2-y1) / (x2-x1)
    b = (x2 * y1 - x1 * y2) / (x2 - x1)
    return k,b

# 90（室内），91（小花园），92（楼前凹位置），93（停车场），94（楼后凹位置）
def areaSearch(test_x, test_y):
    # 输入：待测试坐标值,(先纬度再经度)
    # 输出：90（室内），91（小花园），92（楼前凹位置），93（停车场），94（楼后凹位置）

    # ------ 91小花园 ------
    k, b = linearEquation(41.45326685807951, -8.290345562839377, 41.45367010327917, -8.28957206710138)
    area1 = test_y > (k * test_x + b)
    k, b = linearEquation(41.452587377465576, -8.289786063432178, 41.4528902887724, -8.289188146076148)
    area2 = test_y < (k * test_x + b)
    k, b = linearEquation(41.45326685807951, -8.290345562839377, 41.452587377465576, -8.289786063432178)
    area3 = test_y > (k * test_x + b)
    k, b = linearEquation(41.45367010327917, -8.28957206710138, 41.4528902887724, -8.289188146076148)
    area4 = test_y < (k * test_x + b)
    if area1 and area2 and area3 and area4:
        return 91

    # ------ 93停车场 ------
    k, b = linearEquation(41.45367010327917, -8.28957206710138, 41.454139382637315, -8.288777177520398)
    area1 = test_y > (k * test_x + b)
    k, b = linearEquation(41.45335123951265, -8.289593567914327, 41.453881359371735, -8.288509565958382)
    area2 = test_y < (k * test_x + b)
    k, b = linearEquation(41.45367010327917, -8.28957206710138,41.45335123951265, -8.289593567914327)
    area3 = test_y > (k * test_x + b)
    k, b = linearEquation(41.454139382637315, -8.288777177520398, 41.453881359371735, -8.288509565958382)
    area4 = test_y < (k * test_x + b)
    if area1 and area2 and area3 and area4:
        return 93

    # ------ 90室内、92，94凹位置 ------
    k, b = linearEquation(41.45335123951265, -8.289593567914327, 41.453881359371735, -8.288509565958382)
    area1 = test_y > (k * test_x + b)
    k, b = linearEquation(41.45296143011597, -8.28925823462342,41.45349818178868, -8.288212173109278)
    area2 = test_y < (k * test_x + b)
    k, b = linearEquation(41.45335123951265, -8.289593567914327, 41.45296143011597, -8.28925823462342)
    area3 = test_y > (k * test_x + b)
    k, b = linearEquation(41.453881359371735, -8.288509565958382, 41.45349818178868, -8.288212173109278)
    area4 = test_y < (k * test_x + b)
    area_in = area1 and area2 and area3 and area4

    # ------ 92 楼前凹位置 ------
    k, b = linearEquation(41.45322333877898, -8.289492294877052,41.453329125852434, -8.289284964249559)
    area1 = test_y > (k * test_x + b)
    k, b = linearEquation(41.453122101850155, -8.289401062252711,41.45323588979672, -8.289171729829926)
    area2 = test_y < (k * test_x + b)
    k, b = linearEquation(41.45322333877898, -8.289492294877052,41.453122101850155, -8.289401062252711)
    area3 = test_y > (k * test_x + b)
    k, b = linearEquation(41.453329125852434, -8.289284964249559,41.45323588979672, -8.289171729829926)
    area4 = test_y < (k * test_x + b)
    area_front = area1 and area2 and area3 and area4

    # ------ 94 楼后凹位置 ------
    k, b = linearEquation(41.453808772020935, -8.288652055370724,41.453881359371735, -8.288509565958382)
    area1 = test_y > (k * test_x + b)
    k, b = linearEquation(41.45371127298343, -8.28854610811739,41.453773591972755, -8.288420044296974)
    area2 = test_y < (k * test_x + b)
    k, b = linearEquation(41.453808772020935, -8.288652055370724,41.45371127298343, -8.28854610811739)
    area3 = test_y > (k * test_x + b)
    k, b = linearEquation(41.453881359371735, -8.288509565958382,41.453773591972755, -8.288420044296974)
    area4 = test_y < (k * test_x + b)
    area_back = area1 and area2 and area3 and area4

    if  area_in and area_front:
        return 92
    if area_in and area_back:
        return 94
    if area_in and ~area_front and ~area_back:
        return 90




# 90（室内），91（小花园），92（楼前凹位置），93（停车场），94（楼后凹位置）
# ------ test ------
# t1 = areaSearch(41.453000779750,-8.289786138722)  #91小花园
# t2 = areaSearch(41.453281465591,-8.289242701351)  #90室内(接近楼前凹)
# t3 = areaSearch(41.453543487021,-8.288734943024)  #90室内
# t4 = areaSearch(41.453777212088,-8.288928273481)  #93停车场
# t5 = areaSearch(41.453691710555,-8.288532766625)  #90室内（接近楼后凹）
#
# print(t1,t2,t3,t4,t5)