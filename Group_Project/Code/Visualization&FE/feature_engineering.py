import pandas as pd
import numpy as np
import os
import re
import math

PATH_INTREM = "data/interm"
PATH_FINAL = "data/final"

city = "guangzhou"

def feature(city):
    data = pd.read_csv(os.path.join(PATH_INTREM, city + "/" + city + ".csv"),encoding = "gbk")
    '''获取地铁站数据'''
    if city == "shenzhen":
        metro_station = pd.read_csv(os.path.join(PATH_INTREM, "shenzhen/metro_station_shenzhen.csv"), index_col=0)
        longitude = [float(x.split(",")[0]) for x in metro_station["coordinate"]]
        latitude = [float(x.split(",")[1]) for x in metro_station["coordinate"]]
        metro_station["latitude"] = latitude
        metro_station["longitude"] = longitude
    else:
        metro_station = pd.read_csv(os.path.join(PATH_INTREM, city + "/" + "metro_station_" + city + ".csv"))
        metro_station["latitude"] = metro_station["lat"]
        metro_station["longitude"] = metro_station["lon"]
    '''获取商场数据'''
    CBD = pd.read_csv(os.path.join(PATH_INTREM,city + "/" + "shopping_mall_" + city + ".csv"),index_col = 0)
    CBD_np = CBD[["lat","lon"]].values
    '''获取学校数据'''
    school = pd.read_csv(os.path.join(PATH_INTREM, city + "/" + city + "_school.csv"),index_col = 0)
    bool_series = np.zeros(school.shape[0])
    school_type = school["type"].tolist()
    for x in range(school.shape[0]):
        #print (school["type"][x].values)
        if "小学" in  school_type[x].split(";") or "中学" in  school_type[x].split(";"):
            bool_series[x] = True
    school["bool_series"] = bool_series
    school = school[school["bool_series"] == 1]
    school_np = school[["lat","lon"]].values
    '''获取医院数据'''
    hospital = pd.read_csv(os.path.join(PATH_INTREM,"hospital-more.csv"),index_col = 0)
    city_name = pd.Series(["深圳市","广州市","北京市"],index = ["shenzhen","guangzhou","beijing"])
    hospital = hospital[hospital["city"] == city_name[city]]
    longitude = [float(x.split(",")[0]) for x in hospital["coordinate"]]
    latitude = [float(x.split(",")[1]) for x in hospital["coordinate"]]
    hospital["latitude"] = latitude
    hospital["longitude"] = longitude
    hospital_np = hospital[["latitude","longitude"]].values
    '''计算到各种服务设施距离'''
    metro_distance, metro_number = get_metro_distance(data,metro_station)
    CBD_distance = np.zeros(data.shape[0])
    CBD_numebr = np.zeros(data.shape[0])
    hosp_distance = np.zeros(data.shape[0])
    hosp_number = np.zeros(data.shape[0])
    sch_distance = np.zeros(data.shape[0])
    sch_number = np.zeros(data.shape[0])
    for x in data.index:
        if (np.isnan(data.loc[x][-2])) or (np.isnan(data.loc[x][-1])):
            CBD_distance[x] = np.nan
            hosp_distance[x] = np.nan
            sch_distance[x] = np.nan
        else:
            CBD_distance[x],CBD_numebr[x] = min_distance(data,x,CBD_np,1)
            hosp_distance[x],hosp_number[x] = min_distance(data,x,hospital_np,1)
            sch_distance[x],sch_number[x] = min_distance(data,x,school_np,1)
    '''构造特征'''
    processed_data = pd.DataFrame(index =  data.index)
    num_bed_room = [int(x[0]) if not x is None else None for x in data["room_type"].tolist() ]
    num_living_room = [int(x[2])  if not x is None else None for x in data["room_type"].tolist()]
    room_area = [float(x.replace("平米",""))  if not x is None else None for x in data["room_area"].tolist()]
    height_type,total_height = get_height_info(data["room_height"])
    processed_data["num_bed_room"] = num_bed_room
    processed_data["num_living_room"] = num_living_room
    processed_data["room_area"] = room_area
    processed_data["height_type"] = height_type
    processed_data["total_height"] = total_height
    processed_data["renting_type"] = data["renting_type"]
    processed_data["room_face_type"] = data["room_fase_to"]
    processed_data["district"] = data["district"]
    processed_data["metro_distance"] = metro_distance
    processed_data["metro_number"] = metro_number
    processed_data["CBD_distance"] = CBD_distance
    processed_data["CBD_number"] = CBD_numebr
    processed_data["hosp_distance"] = hosp_distance
    processed_data["hosp_number"] = hosp_number
    processed_data["school_distance"] = sch_distance
    processed_data["sch_number"] = sch_number
    processed_data["elevator"] = data["room_televator"]
    processed_data["price"] = data["price"]
    '''填充空值'''
    processed_data = fill_na(processed_data)
    '''转换为哑变量'''
    dummy_data = pd.get_dummies(processed_data[["height_type","room_face_type","renting_type","district","elevator"]],drop_first = True)
    train_data = processed_data.drop(["height_type","room_face_type","renting_type","district","price","elevator"],axis = 1)
    label = processed_data["price"]
    train_data = pd.concat([train_data,dummy_data],axis = 1)
    pd.concat([train_data,label],axis = 1).to_csv(os.path.join(PATH_FINAL,"train_data_" + city + ".csv"),encoding = "utf-8")
    return

def get_height_info(height_info_series):
    '''获取房屋高度和总楼层数据'''
    def extract_height_info(x):
        if '(' in x:
            height_type = x.split("(")[0]
            total_height = x.split("(")[1].split(")")[0]
            total_height = int(re.findall(r"\d+\.?\d*",total_height)[0])
        else:
            height_type = None
            total_height = None
        return height_type,total_height
    height_type = [extract_height_info(x)[0] for x in height_info_series]
    total_height = [extract_height_info(x)[1] for x in height_info_series]
    #height_type_dict = {"低层":0,
    #                   "中层":1,
    #                   "高层":2}
    #height_type = [height_type_dict[x]  if not x is None else None for x in height_type]
    #height_type = get_type_num(pd.Series(height_type))
    return height_type,total_height

def cal_dis(latitude1, longitude1,latitude2, longitude2):
    '''利用经纬度计算两点之间距离'''
    latitude1 = (math.pi/180.0)*latitude1
    latitude2 = (math.pi/180.0)*latitude2
    longitude1 = (math.pi/180.0)*longitude1
    longitude2= (math.pi/180.0)*longitude2
    #因此AB两点的球面距离为:{arccos[sina*sinx+cosb*cosx*cos(b-y)]}*R  (a,b,x,y)
    #地球半径
    R = 6378.140
    temp=math.sin(latitude1)*math.sin(latitude2)+ math.cos(latitude1)*math.cos(latitude2)*math.cos(longitude2-longitude1)
    if float(repr(temp))>1.0:
        temp = 1.0
    d = math.acos(temp)*R
    return d;

def get_metro_distance(data,metro_station):
    '''获取地铁距离'''
    metro_distance = np.zeros(data.shape[0])
    metro_number = np.zeros(data.shape[0])
    for x in data.index:
        #metro_lines = re.findall(r"\d+\.?\d*",data.loc[x].metro_line)
        x_latitude = data.loc[x][-1]
        x_longitude = data.loc[x][-2]
        if np.isnan(x_latitude) or np.isnan(x_longitude):
            res = np.nan
        else:
            res,number = min_distance(data,x,metro_station[["latitude","longitude"]].values,1.)
            metro_number[x] = number
        metro_distance[x] = res
    return metro_distance,metro_number

def min_distance(data,x,locations,nearest_threshold):
    '''计算距离服务设施的最小距离和位于一定范围内服务设施的数量'''
    distance_list =  np.zeros(locations.shape[0])
    single_line_stat = locations
    x_latitude = data.loc[x][-1]
    x_longitude = data.loc[x][-2]
    for ii in range(single_line_stat.shape[0]):
        distance  = (cal_dis(x_latitude,x_longitude,single_line_stat[ii,0],single_line_stat[ii,1]))
        distance_list[ii] = distance
    res = np.min(distance_list)
    number = (distance_list < nearest_threshold).sum()
    #print (np.argmin(distance_list))
    return res,number

def fill_na(df, method = 0):
    '''部分使用众数填充'''
    mode = df.mode(axis = 0).iloc[0]
    mean = df[["metro_distance","CBD_distance","hosp_distance","school_distance","price"]].mean(axis = 0)
    '''部分使用均值填充'''
    mode[["metro_distance","CBD_distance","hosp_distance","school_distance","price"]] = mean
    return df.fillna(mode)


def get_type_num(type_series):

    _type = type_series.unique()
    _type_dict = dict(zip(_type.tolist(),range(len(_type.tolist()))))
    _type_dict[None] = None
    _type = [_type_dict[x] for x in type_series]
    return _type

feature("guangzhou")
feature("shenzhen")
feature("beijing")