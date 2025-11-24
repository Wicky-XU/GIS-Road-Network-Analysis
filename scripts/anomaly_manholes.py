# -*- coding: utf-8 -*-
"""
污水管网异常井检测脚本
功能：分析污水管道网络，识别管网内部的堵塞井
"""

import arcpy
import os
import glob

# 设置工作空间路径
arcpy.env.workspace = r"C:\Users\29873\Desktop\3.5 Square Kilometers"

# 定义输入和输出图层名称
pipe_fc = "ps_pipe"              # 管道图层
manhole_fc = "ps_manhole"        # 污水井图层
output_fc = "anomaly_manholes"   # 输出的异常井图层

# 如果输出文件已存在，删除相关文件（.shp, .shx, .dbf等）
workspace_path = arcpy.env.workspace
output_pattern = os.path.join(workspace_path, "anomaly_manholes.*")
for file_path in glob.glob(output_pattern):
    try:
        os.remove(file_path)
        print(u"已删除旧文件: " + file_path)
    except Exception as e:
        print(u"无法删除文件: " + file_path + " - " + str(e))

# ========== 初始化数据结构 ==========
inflow_dict = {}         # 流入管道数量
outflow_dict = {}        # 流出管道数量
total_connect_dict = {}  # 每个井连接的管道总数

# 遍历所有污水井，初始化字典
with arcpy.da.SearchCursor(manhole_fc, ["ManholeID"]) as cursor:
    for row in cursor:
        manhole_id = row[0]
        inflow_dict[manhole_id] = 0
        outflow_dict[manhole_id] = 0
        total_connect_dict[manhole_id] = 0

# ========== 分析管道流向 ==========
# 遍历所有管道，统计每个井的流入、流出和总连接数
# 流向规则：水流从 In_JuncID（起点井）流向 Out_JuncID（终点井）
with arcpy.da.SearchCursor(pipe_fc, ["In_JuncID", "Out_JuncID"]) as cursor:
    for row in cursor:
        in_junc = row[0]   # 管道起点井ID
        out_junc = row[1]  # 管道终点井ID
        
        # 对于终点井：这条管道是流入
        if out_junc in inflow_dict:
            inflow_dict[out_junc] += 1
            total_connect_dict[out_junc] += 1
        
        # 对于起点井：这条管道是流出
        if in_junc in outflow_dict:
            outflow_dict[in_junc] += 1
            total_connect_dict[in_junc] += 1

# ========== 识别异常井 ==========
# 异常井判断标准：
# 1. 有流入（inflow > 0）
# 2. 无流出（outflow == 0）
# 3. 连接多条管道（total >= 2）- 排除边缘的正常出口井
anomaly_ids = []
for manhole_id in inflow_dict.keys():
    inflow = inflow_dict[manhole_id]
    outflow = outflow_dict[manhole_id]
    total = total_connect_dict[manhole_id]
    
    # 判断是否为异常井
    if inflow > 0 and outflow == 0 and total >= 2:
        anomaly_ids.append(manhole_id)
        print(u"发现异常井: {} (流入:{}, 流出:{}, 总连接:{})".format(
            manhole_id, inflow, outflow, total))

print(u"\n========== 检测完成 ==========")
print(u"异常井总计: {} 个".format(len(anomaly_ids)))

# ========== 生成输出图层 ==========
if len(anomaly_ids) > 0:
    # 复制原始污水井图层
    arcpy.CopyFeatures_management(manhole_fc, output_fc)
    
    # 添加新字段记录统计信息
    arcpy.AddField_management(output_fc, "InflowCnt", "SHORT")    # 流入数量
    arcpy.AddField_management(output_fc, "OutflowCnt", "SHORT")   # 流出数量
    arcpy.AddField_management(output_fc, "TotalCnt", "SHORT")     # 总连接数
    
    # 更新字段值，删除非异常井
    with arcpy.da.UpdateCursor(output_fc, 
        ["ManholeID", "InflowCnt", "OutflowCnt", "TotalCnt"]) as cursor:
        for row in cursor:
            manhole_id = row[0]
            if manhole_id in anomaly_ids:
                # 如果是异常井，填充统计数据
                row[1] = inflow_dict[manhole_id]
                row[2] = outflow_dict[manhole_id]
                row[3] = total_connect_dict[manhole_id]
                cursor.updateRow(row)
            else:
                # 如果不是异常井，删除该记录
                cursor.deleteRow()
    
    print(u"输出图层已创建: " + output_fc)
else:
    print(u"未发现异常井，无需创建输出图层")

print(u"========== 脚本执行完成 ==========")
