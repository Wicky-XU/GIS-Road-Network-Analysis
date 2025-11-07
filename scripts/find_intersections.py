# -*- coding: utf-8 -*-
# ============================================================
# Script 1: Road Intersection Identification
# 脚本1: 道路交叉口识别
# 
# 功能:
# 1. 从路网数据中自动识别所有交叉点
# 2. 过滤高架、轨道交通、隧道等非地面道路
# 3. 为未命名道路分配唯一编号(支路1, 支路2...)
# 4. 生成可多方向搜索的交叉口名称组合
# 5. 输出Shapefile图层(包含SEARCH_KEY字段)
# ============================================================

import arcpy
import os
from itertools import combinations

# ========== 环境设置 ==========
arcpy.env.overwriteOutput = True

# 工作空间设置
workspace = r"C:\Users\29873\Desktop\Road Search"
arcpy.env.workspace = workspace

print "="*60
print "Road Intersection Identification"
print "道路交叉口识别"
print "="*60

# ========== 文件路径定义 ==========
# 输入文件
road_layer = os.path.join(workspace, "Export_Output.shp")

# 输出文件
intersect_temp = os.path.join(workspace, "Temp_Intersect.shp")
intersections_output = os.path.join(workspace, "Road_Intersections.shp")

# 检查输入文件
if not arcpy.Exists(road_layer):
    print "Error: Cannot find road network file"
    print "Expected location:", road_layer
    exit()

print "Input file found"

# ========== 过滤规则定义 ==========
filter_keywords = [u"高架", u"轨道交通", u"隧道"]

def should_filter(road_name):
    """
    判断道路是否需要被过滤
    参数: road_name - 道路名称字符串
    返回: True表示需要过滤, False表示保留
    """
    if not road_name:
        return False
    
    try:
        if isinstance(road_name, str):
            road_name_unicode = road_name.decode('gbk')
        else:
            road_name_unicode = unicode(road_name)
    except:
        return False
    
    for keyword in filter_keywords:
        if keyword in road_name_unicode:
            return True
    return False

# ========== 为未命名道路分配名称 ==========
print "Step 1: Assigning names to unnamed roads..."

unnamed_road_mapping = {}
unnamed_counter = 1

with arcpy.da.SearchCursor(road_layer, ["OBJECTID", "NAME", "SHAPE@"]) as cursor:
    for row in cursor:
        oid = row[0]
        name = row[1] if row[1] else ""
        
        if should_filter(name):
            continue
        
        if not name or not name.strip():
            unnamed_road_mapping[oid] = u"支路" + unicode(unnamed_counter)
            unnamed_counter += 1

print "Unnamed roads processed:", len(unnamed_road_mapping)

# ========== 计算交叉点 ==========
print "Step 2: Finding intersections..."

arcpy.Intersect_analysis(
    in_features=[road_layer, road_layer],
    out_feature_class=intersect_temp,
    join_attributes="ALL",
    output_type="POINT"
)

print "Intersections calculated"

# ========== 创建输出图层 ==========
print "Step 3: Creating output layer..."

arcpy.CreateFeatureclass_management(
    out_path=workspace,
    out_name="Road_Intersections.shp",
    geometry_type="POINT",
    spatial_reference=intersect_temp
)

# 添加字段(包含SEARCH_KEY用于Excel导出)
arcpy.AddField_management(intersections_output, "INT_NAME", "TEXT", field_length=200)
arcpy.AddField_management(intersections_output, "SEARCH_KEY", "TEXT", field_length=254)
arcpy.AddField_management(intersections_output, "POINT_X", "DOUBLE")
arcpy.AddField_management(intersections_output, "POINT_Y", "DOUBLE")

# ========== 处理交叉点数据 ==========
print "Step 4: Processing intersection data..."

intersection_data = {}

def generate_search_combinations(road_list):
    """
    生成所有可能的道路组合搜索词
    用于SEARCH_KEY字段,支持任意顺序搜索
    """
    search_terms = []
    
    if len(road_list) == 2:
        search_terms.append(road_list[0] + u"与" + road_list[1])
        search_terms.append(road_list[1] + u"与" + road_list[0])
    
    elif len(road_list) == 3:
        for combo in combinations(road_list, 2):
            search_terms.append(combo[0] + u"与" + combo[1])
            search_terms.append(combo[1] + u"与" + combo[0])
        search_terms.append(road_list[0] + u"与" + road_list[1] + u"与" + road_list[2])
        search_terms.append(road_list[2] + u"与" + road_list[1] + u"与" + road_list[0])
    
    else:
        for combo in combinations(road_list, 2):
            search_terms.append(combo[0] + u"与" + combo[1])
            search_terms.append(combo[1] + u"与" + combo[0])
    
    return u"|".join(search_terms)

# 读取临时交叉点数据
cursor_fields = ["SHAPE@XY", "NAME", "NAME_1", "OBJECTID", "OBJECTID_1"]
with arcpy.da.SearchCursor(intersect_temp, cursor_fields) as cursor:
    for row in cursor:
        coord = row[0]
        name1 = row[1] if row[1] else ""
        name2 = row[2] if row[2] else ""
        oid1 = row[3]
        oid2 = row[4]
        
        # 处理第一条道路
        if should_filter(name1):
            continue
        if not name1 or not name1.strip():
            name1 = unnamed_road_mapping.get(oid1, u"支路未知")
        
        # 处理第二条道路
        if should_filter(name2):
            continue
        if not name2 or not name2.strip():
            name2 = unnamed_road_mapping.get(oid2, u"支路未知")
        
        # 跳过同一条路自己相交
        if name1 == name2:
            continue
        
        # 合并相近的交叉点
        x = round(coord[0], 2)
        y = round(coord[1], 2)
        key = (x, y)
        
        if key not in intersection_data:
            intersection_data[key] = {"coord": coord, "roads": set()}
        
        intersection_data[key]["roads"].add(name1)
        intersection_data[key]["roads"].add(name2)

print "Unique intersections found:", len(intersection_data)

# ========== 写入输出图层 ==========
print "Step 5: Writing intersection data..."

output_fields = ["SHAPE@XY", "INT_NAME", "SEARCH_KEY", "POINT_X", "POINT_Y"]

with arcpy.da.InsertCursor(intersections_output, output_fields) as cursor:
    for key, data in intersection_data.items():
        roads = data["roads"]
        coord = data["coord"]
        
        if len(roads) >= 2:
            road_list = sorted(list(roads))
            
            # 生成INT_NAME(显示用)
            if len(road_list) == 2:
                int_name = road_list[0] + u"与" + road_list[1] + u"交口"
            elif len(road_list) == 3:
                int_name = road_list[0] + u"与" + road_list[1] + u"与" + road_list[2] + u"交口"
            else:
                int_name = u"与".join(road_list) + u"交口"
            
            # 生成SEARCH_KEY(搜索用)
            search_key = generate_search_combinations(road_list)
            
            cursor.insertRow([coord, int_name, search_key, coord[0], coord[1]])

print "Intersection data written"

# ========== 清理临时文件 ==========
print "Step 6: Cleaning up..."

if arcpy.Exists(intersect_temp):
    arcpy.Delete_management(intersect_temp)

try:
    arcpy.DeleteField_management(intersections_output, "Id")
except:
    pass

# ========== 添加到地图 ==========
print "Step 7: Adding layer to map..."

mxd = arcpy.mapping.MapDocument("CURRENT")
df = arcpy.mapping.ListDataFrames(mxd)[0]

# 移除旧图层
for lyr in arcpy.mapping.ListLayers(mxd, "Road_Intersections", df):
    arcpy.mapping.RemoveLayer(df, lyr)

# 添加新图层
new_layer = arcpy.mapping.Layer(intersections_output)
arcpy.mapping.AddLayer(df, new_layer, "TOP")

arcpy.RefreshActiveView()
arcpy.RefreshTOC()

# ========== 完成 ==========
print "="*60
print "Script 1 Completed Successfully!"
print "="*60
print "Total intersections:", len(intersection_data)
print "Output file:", intersections_output
print "="*60
print "Note: SEARCH_KEY field is included for Excel export"
print "Run Script 3 to export to Excel"
print "="*60
