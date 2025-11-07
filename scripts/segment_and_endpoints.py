# -*- coding: utf-8 -*-
# ============================================================
# Script 2: Road Segmentation and Endpoint Analysis
# 脚本2: 道路路段切割与端点分析
# 
# 功能:
# 1. 使用交叉口切割完整道路为路段
# 2. 为每个路段编号(如"A路_1", "支路5_2")
# 3. 计算路段长度和起终点坐标
# 4. 识别每个端点连接的所有路段
# 5. 输出两个Shapefile图层
# ============================================================

import arcpy
import os

# ========== 环境设置 ==========
arcpy.env.overwriteOutput = True

workspace = r"C:\Users\29873\Desktop\Road Search"
arcpy.env.workspace = workspace

print "="*60
print "Road Segmentation and Endpoint Analysis"
print "道路路段切割与端点分析"
print "="*60

# ========== 文件路径定义 ==========
road_layer = os.path.join(workspace, "Export_Output.shp")
intersections = os.path.join(workspace, "Road_Intersections.shp")

road_segments = os.path.join(workspace, "Road_Segments.shp")
segment_endpoints = os.path.join(workspace, "Segment_Endpoints.shp")
temp_split = os.path.join(workspace, "Temp_Split.shp")

# 检查必要文件
if not arcpy.Exists(road_layer):
    print "Error: Cannot find road network file"
    exit()

if not arcpy.Exists(intersections):
    print "Error: Cannot find intersections layer"
    print "Please run Script 1 first"
    exit()

print "Input files found"

# ========== 建立道路名称映射 ==========
print "Step 1: Building road name mapping..."

filter_keywords = [u"高架", u"轨道交通", u"隧道"]

def should_filter(road_name):
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

oid_to_name = {}
unnamed_counter = 1

with arcpy.da.SearchCursor(road_layer, ["OBJECTID", "NAME"]) as cursor:
    for row in cursor:
        oid = row[0]
        name = row[1] if row[1] else ""
        
        if should_filter(name):
            oid_to_name[oid] = ""
            continue
        
        if name and name.strip():
            oid_to_name[oid] = name
        else:
            oid_to_name[oid] = u"支路" + unicode(unnamed_counter)
            unnamed_counter += 1

print "Road name mapping completed"

# ========== 切割道路 ==========
print "Step 2: Splitting roads at intersections..."

arcpy.SplitLineAtPoint_management(
    in_features=road_layer,
    point_features=intersections,
    out_feature_class=temp_split,
    search_radius="10 Meters"
)

print "Roads split successfully"

# ========== 创建路段图层 ==========
print "Step 3: Creating road segments layer..."

arcpy.CreateFeatureclass_management(
    out_path=workspace,
    out_name="Road_Segments.shp",
    geometry_type="POLYLINE",
    spatial_reference=temp_split
)

arcpy.AddField_management(road_segments, "SEG_NAME", "TEXT", field_length=200)
arcpy.AddField_management(road_segments, "BASE_NAME", "TEXT", field_length=150)
arcpy.AddField_management(road_segments, "SEG_ID", "SHORT")
arcpy.AddField_management(road_segments, "LENGTH", "DOUBLE")
arcpy.AddField_management(road_segments, "START_X", "DOUBLE")
arcpy.AddField_management(road_segments, "START_Y", "DOUBLE")
arcpy.AddField_management(road_segments, "END_X", "DOUBLE")
arcpy.AddField_management(road_segments, "END_Y", "DOUBLE")

print "Road segments layer created"

# ========== 处理路段数据 ==========
print "Step 4: Processing segments..."

road_segment_counter = {}
endpoint_segments = {}

def round_coord(x, y):
    return (round(x, 1), round(y, 1))

segment_fields = ["SHAPE@", "OBJECTID", "SHAPE@LENGTH"]
insert_fields = ["SHAPE@", "SEG_NAME", "BASE_NAME", "SEG_ID", "LENGTH", "START_X", "START_Y", "END_X", "END_Y"]

with arcpy.da.SearchCursor(temp_split, segment_fields) as search_cursor:
    with arcpy.da.InsertCursor(road_segments, insert_fields) as insert_cursor:
        for row in search_cursor:
            geometry = row[0]
            orig_oid = row[1]
            length = row[2]
            
            base_name = oid_to_name.get(orig_oid, u"未知道路")
            
            if not base_name:
                continue
            
            start_point = geometry.firstPoint
            end_point = geometry.lastPoint
            
            start_x = start_point.X
            start_y = start_point.Y
            end_x = end_point.X
            end_y = end_point.Y
            
            if base_name not in road_segment_counter:
                road_segment_counter[base_name] = 1
            else:
                road_segment_counter[base_name] += 1
            
            seg_id = road_segment_counter[base_name]
            seg_name = base_name + u"_" + unicode(seg_id)
            
            insert_cursor.insertRow([
                geometry,
                seg_name,
                base_name,
                seg_id,
                length,
                start_x,
                start_y,
                end_x,
                end_y
            ])
            
            start_key = round_coord(start_x, start_y)
            end_key = round_coord(end_x, end_y)
            
            if start_key not in endpoint_segments:
                endpoint_segments[start_key] = {"coord": (start_x, start_y), "segments": []}
            endpoint_segments[start_key]["segments"].append(seg_name)
            
            if end_key not in endpoint_segments:
                endpoint_segments[end_key] = {"coord": (end_x, end_y), "segments": []}
            endpoint_segments[end_key]["segments"].append(seg_name)

print "Segments processed:", sum(road_segment_counter.values())

# ========== 创建端点图层 ==========
print "Step 5: Creating endpoints layer..."

arcpy.CreateFeatureclass_management(
    out_path=workspace,
    out_name="Segment_Endpoints.shp",
    geometry_type="POINT",
    spatial_reference=temp_split
)

arcpy.AddField_management(segment_endpoints, "NAME", "TEXT", field_length=254)
arcpy.AddField_management(segment_endpoints, "POINT_X", "DOUBLE")
arcpy.AddField_management(segment_endpoints, "POINT_Y", "DOUBLE")
arcpy.AddField_management(segment_endpoints, "SEG_COUNT", "SHORT")

print "Endpoints layer created"

# ========== 写入端点数据 ==========
print "Step 6: Writing endpoint data..."

endpoint_fields = ["SHAPE@XY", "NAME", "POINT_X", "POINT_Y", "SEG_COUNT"]

with arcpy.da.InsertCursor(segment_endpoints, endpoint_fields) as cursor:
    for key, data in endpoint_segments.items():
        coord = data["coord"]
        segments = data["segments"]
        
        unique_segments = list(set(segments))
        
        if len(unique_segments) >= 1:
            seg_list_str = u"、".join(sorted(unique_segments))
            
            cursor.insertRow([
                coord,
                seg_list_str,
                coord[0],
                coord[1],
                len(unique_segments)
            ])

print "Endpoints processed:", len(endpoint_segments)

# ========== 清理临时文件 ==========
print "Step 7: Cleaning up..."

if arcpy.Exists(temp_split):
    arcpy.Delete_management(temp_split)

try:
    arcpy.DeleteField_management(road_segments, "Id")
    arcpy.DeleteField_management(segment_endpoints, "Id")
except:
    pass

# ========== 添加到地图 ==========
print "Step 8: Adding layers to map..."

mxd = arcpy.mapping.MapDocument("CURRENT")
df = arcpy.mapping.ListDataFrames(mxd)[0]

for layer_name in ["Road_Segments", "Segment_Endpoints"]:
    for lyr in arcpy.mapping.ListLayers(mxd, layer_name, df):
        arcpy.mapping.RemoveLayer(df, lyr)

segments_layer = arcpy.mapping.Layer(road_segments)
arcpy.mapping.AddLayer(df, segments_layer, "TOP")

endpoints_layer = arcpy.mapping.Layer(segment_endpoints)
arcpy.mapping.AddLayer(df, endpoints_layer, "TOP")

arcpy.RefreshActiveView()
arcpy.RefreshTOC()

# ========== 完成 ==========
print "="*60
print "Script 2 Completed Successfully!"
print "Road Segments:", sum(road_segment_counter.values())
print "Segment Endpoints:", len(endpoint_segments)
print "Output files:"
print "  - Road_Segments.shp"
print "  - Segment_Endpoints.shp"
print "="*60
