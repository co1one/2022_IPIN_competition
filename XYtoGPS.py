import math
import numpy as np


def XYtoGPS( x, y, ref_lat, ref_lon):
    # 相对坐标转经纬度
    # 输入：xy相对坐标，经纬度基准值
    # 输出：经纬度
    meterToLong = 0.00001141    # 经度
    meterToLatit = 0.00000899   # 纬度

    lon_rela = x * meterToLong  # 坐标转换
    lat_rela = y * meterToLatit
    lat = ref_lat + lat_rela   # 加上基准值
    lon = ref_lon + lon_rela
    return lon,lat


def GPStoXY(lon, lat, ref_lon, ref_lat):
    # 经纬度转相对坐标
    # 输入：经纬度，绝对坐标基准值，相对坐标基准值
    # 输出：相对坐标(相差一度，转化为米)
    Long_to_meter = 1/ 0.00001141 # 经度
    Latit_to_meter = 1/ 0.00000899

    x = (lon - ref_lon) * Long_to_meter  # 坐标转换
    y = (lat - ref_lat) * Latit_to_meter

    return x,y



# -------------- 网上的方案 ----------------
# 他这里的y代表相对纬度，x代表相对经度，和咱们的不一样

# CONSTANTS_RADIUS_OF_EARTH = 6371000.     # meters (m)


# def GPStoXY(lon, lat, ref_lon, ref_lat):
#     # input GPS and Reference GPS in degrees
#     # output XY in meters (m) X:North Y:East
#     lat_rad = math.radians(lat)
#     lon_rad = math.radians(lon)
#     ref_lat_rad = math.radians(ref_lat)
#     ref_lon_rad = math.radians(ref_lon)
#
#     sin_lat = math.sin(lat_rad)
#     cos_lat = math.cos(lat_rad)
#     ref_sin_lat = math.sin(ref_lat_rad)
#     ref_cos_lat = math.cos(ref_lat_rad)
#
#     cos_d_lon = math.cos(lon_rad - ref_lon_rad)
#
#     arg = np.clip(ref_sin_lat * sin_lat + ref_cos_lat * cos_lat * cos_d_lon, -1.0, 1.0)
#     c = math.acos(arg)
#
#     k = 1.0
#     if abs(c) > 0:
#         k = (c / math.sin(c))
#
#     x = float(k * (ref_cos_lat * sin_lat - ref_sin_lat * cos_lat * cos_d_lon) * CONSTANTS_RADIUS_OF_EARTH)
#     y = float(k * cos_lat * math.sin(lon_rad - ref_lon_rad) * CONSTANTS_RADIUS_OF_EARTH)
#
#     return y, x  # 输出[经度，纬度]
#
#
#
# def XYtoGPS(y, x, ref_lat, ref_lon):
#     x_rad = float(x) / CONSTANTS_RADIUS_OF_EARTH
#     y_rad = float(y) / CONSTANTS_RADIUS_OF_EARTH
#     c = math.sqrt(x_rad * x_rad + y_rad * y_rad)
#
#     ref_lat_rad = math.radians(ref_lat)
#     ref_lon_rad = math.radians(ref_lon)
#
#     ref_sin_lat = math.sin(ref_lat_rad)
#     ref_cos_lat = math.cos(ref_lat_rad)
#
#     if abs(c) > 0:
#         sin_c = math.sin(c)
#         cos_c = math.cos(c)
#
#         lat_rad = math.asin(cos_c * ref_sin_lat + (x_rad * sin_c * ref_cos_lat) / c)
#         lon_rad = (ref_lon_rad + math.atan2(y_rad * sin_c, c * ref_cos_lat * cos_c - x_rad * ref_sin_lat * sin_c))
#
#         lat = math.degrees(lat_rad)
#         lon = math.degrees(lon_rad)
#
#     else:
#         lat = math.degrees(ref_lat)
#         lon = math.degrees(ref_lon)
#
#     return lon, lat



# ------------test ---------------
# lon,lat = XYtoGPS(5,6,41.453242221756,-8.289158860101)
# print("lon,lat: ",lon,',',lat)
#
# x,y = GPStoXY(lon,lat,-8.289158860101,41.453242221756)
# print("x,y: ",x,',',y)