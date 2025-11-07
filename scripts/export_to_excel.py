# -*- coding: utf-8 -*-
# ============================================================
# Script 3: Export Results to Excel
# 脚本3: 导出结果为Excel
# 
# 功能:
# 1. 将Road_Intersections导出为Excel(含SEARCH_KEY)
# 2. 将Road_Segments导出为Excel
# 3. 将Segment_Endpoints导出为Excel
# ============================================================

import arcpy
import os

# ========== 环境设置 ==========
arcpy.env.overwriteOutput = True

workspace = r"C:\Users\29873\Desktop\Road Search"
arcpy.env.workspace = workspace

print "="*60
print "Export Results to Excel"
print "导出结果为Excel"
print "="*60

# ========== 文件路径定义 ==========
# 输入文件(Shapefiles)
intersections_shp = os.path.join(workspace, "Road_Intersections.shp")
segments_shp = os.path.join(workspace, "Road_Segments.shp")
endpoints_shp = os.path.join(workspace, "Segment_Endpoints.shp")

# 输出文件(Excel)
intersections_xls = os.path.join(workspace, "Road_Intersections.xls")
segments_xls = os.path.join(workspace, "Road_Segments.xls")
endpoints_xls = os.path.join(workspace, "Segment_Endpoints.xls")

# ========== 检查文件是否存在 ==========
print "Checking input files..."

required_files = [
    ("Road_Intersections.shp", intersections_shp),
    ("Road_Segments.shp", segments_shp),
    ("Segment_Endpoints.shp", endpoints_shp)
]

missing_files = []
for name, path in required_files:
    if not arcpy.Exists(path):
        missing_files.append(name)
        print "  [MISSING]", name
    else:
        print "  [FOUND]", name

if missing_files:
    print "\nError: Missing required files:"
    for name in missing_files:
        print "  -", name
    print "\nPlease run Script 1 and Script 2 first."
    exit()

print "\nAll input files found"

# ========== 导出Excel ==========
print "\n" + "="*60
print "Starting Excel Export..."
print "="*60

# 导出1: Road_Intersections
print "\n[1/3] Exporting Road_Intersections..."
try:
    arcpy.TableToExcel_conversion(intersections_shp, intersections_xls)
    print "  SUCCESS:", intersections_xls
except Exception as e:
    print "  ERROR:", str(e)

# 导出2: Road_Segments
print "\n[2/3] Exporting Road_Segments..."
try:
    arcpy.TableToExcel_conversion(segments_shp, segments_xls)
    print "  SUCCESS:", segments_xls
except Exception as e:
    print "  ERROR:", str(e)

# 导出3: Segment_Endpoints
print "\n[3/3] Exporting Segment_Endpoints..."
try:
    arcpy.TableToExcel_conversion(endpoints_shp, endpoints_xls)
    print "  SUCCESS:", endpoints_xls
except Exception as e:
    print "  ERROR:", str(e)

# ========== 完成 ==========
print "\n" + "="*60
print "Script 3 Completed Successfully!"
print "="*60
print "Excel files exported to:"
print "  -", intersections_xls
print "  -", segments_xls
print "  -", endpoints_xls
print "="*60