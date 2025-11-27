# GIS 网络拓扑分析工具

基于 ArcMap Python (ArcPy) 开发的GIS网络自动化分析工具，包括道路网络拓扑分析和污水管网异常检测。

## 项目简介

本项目通过Python脚本自动化处理GIS网络数据，实现道路交叉口识别、路段切割、端点分析和污水管网异常检测等功能。

### 主要功能

**道路网络分析**
- 自动识别道路交叉口并计算位置
- 按交叉口切割道路为多个路段
- 分析端点连接关系
- 批量导出Excel格式结果

**污水管网分析**
- 自动检测污水管网中的堵塞井

### 核心优势

- **自动化处理** - 原本需要数小时的手工操作，现在只需几分钟
- **智能过滤** - 自动排除高架、地铁、隧道等非地面道路
- **精确去重** - 智能合并相近交叉点，避免数据冗余
- **多方向搜索** - 生成所有可能的搜索组合，支持任意顺序查询

## 项目结构
```
GIS-Road-Network-Analysis/
├── README.md                          # 项目说明文档
├── .gitignore                         # Git忽略配置
│
├── scripts/                           # Python脚本
│   ├── 1_find_intersections.py       # 识别道路交叉口
│   ├── 2_segment_and_endpoints.py    # 切割路段并标注端点
│   ├── 3_export_to_excel.py          # 导出结果为Excel
│   └── 4_anomaly_manholes.py         # 污水管网异常井检测
│
├── road_search_data/                  # 数据文件夹（本地存在，Git中隐藏）
│   ├── input/                         # 输入数据
│   └── output/                        # 输出数据
│       ├── shapefiles/                # Shapefile输出
│       └── excel/                     # Excel输出
│
└── docs/                              # 文档
    ├── installation.md                # 安装指南
    └── introduction.md                # ArcMap软件介绍
```

## 快速开始

### 环境要求

- ArcGIS Desktop 10.x 或更高版本
- Python 2.7 (ArcGIS内置)
- ArcPy库 (随ArcGIS安装)

### 运行步骤

1. **准备数据** - 将道路网络Shapefile放入 `road_search_data/input/` 文件夹
2. **打开ArcMap** - 添加路网数据到地图
3. **运行脚本** - 在ArcMap Python窗口依次执行：
```python
# 步骤1: 识别交叉口
execfile(r"C:\path\to\scripts\1_find_intersections.py")

# 步骤2: 切割路段与识别端点
execfile(r"C:\path\to\scripts\2_segment_and_endpoints.py")

# 步骤3: 导出Excel
execfile(r"C:\path\to\scripts\3_export_to_excel.py")
```

4. **查看结果** - Excel文件保存在 `road_search_data/output/excel/`

**注意**: 将 `C:\path\to\` 替换为实际路径

### 数据要求

- 格式: Shapefile (.shp)
- 类型: Polyline (线要素)
- 必须字段: NAME (可以为空)
- 坐标系统: 建议使用投影坐标系(单位:米)

## 核心技术

### 主要ArcPy工具

| 工具 | 用途 |
|------|------|
| Intersect_analysis | 计算道路交叉点 |
| SplitLineAtPoint_management | 在交叉口切割道路 |
| TableToExcel_conversion | 导出分析结果 |
| arcpy.da.SearchCursor | 读取要素数据 |
| arcpy.da.InsertCursor | 写入新要素 |

### 关键算法

- **未命名道路处理** - 使用OBJECTID为未命名道路分配唯一编号
- **交叉点去重** - 坐标四舍五入合并相近点
- **搜索组合生成** - 使用itertools生成所有可能的搜索关键词
- **字符编码处理** - 正确处理中文字符的GBK编码

## 输出数据说明

### 道路交叉口 (Road_Intersections)

包含字段: INT_NAME (交叉口名称)、SEARCH_KEY (搜索关键词)、POINT_X/Y (坐标)

用途: Excel查询交叉口位置

### 道路路段 (Road_Segments)

包含字段: SEG_NAME (路段名称)、BASE_NAME (道路名称)、LENGTH (长度)、START_X/Y、END_X/Y

用途: 路段级别的道路管理和分析

### 路段端点 (Segment_Endpoints)

包含字段: NAME (连接路段列表)、POINT_X/Y (坐标)、SEG_COUNT (连接数量)

用途: 网络拓扑分析，识别关键节点

## 污水管网异常检测

### 使用方法
```python
# 修改工作空间路径
arcpy.env.workspace = r"你的数据路径"

# 运行脚本
execfile(r"C:\path\to\scripts\4_anomaly_manholes.py")
```

### 检测逻辑

- 统计每个污水井的流入、流出管道数量
- 识别"有进无出"且连接≥2条管道的异常井
- 排除边缘正常出口井

### 输入要求

- `ps_pipe.shp` - 污水管道图层 (包含 In_JuncID、Out_JuncID 字段)
- `ps_manhole.shp` - 污水井图层 (包含 ManholeID 字段)

### 输出结果

生成 `anomaly_manholes.shp`，包含字段: InflowCnt (流入数)、OutflowCnt (流出数)、TotalCnt (总连接数)

## 常见问题

**Q: 运行脚本时找不到文件？**  
A: 检查脚本中的 workspace 路径是否正确

**Q: 中文显示乱码？**  
A: 确保脚本开头有 `# -*- coding: utf-8 -*-`，且使用u前缀表示unicode字符串

**Q: 生成了很多.lock文件？**  
A: 这是ArcGIS的文件锁定机制，关闭ArcMap后会自动删除

**Q: 交叉点数量比预期少？**  
A: 检查过滤关键词设置，可能有些道路被意外过滤了

## 项目背景

本项目开发于实际GIS数据处理需求，通过自动化脚本显著提升了道路网络分析和污水管网检测的效率。

**应用场景**: 城市道路网络拓扑分析、交通流量研究、道路资产管理、导航数据预处理、污水管网维护与异常检测

**处理能力**: 200+条道路、400+个交叉口、600+条路段、3.5平方公里管网区域、处理时间<2分钟

## 致谢

感谢实习期间积累的GIS数据处理实际项目经验，以及对GIS自动化处理需求的深入理解。

---

**注意事项**:
- 本工具基于ArcGIS，需要相应软件许可
- 由于保密协议，不包含实际原始数据文件
- 项目代码开源仅供学习参考

**技术栈**: Python 2.7 · ArcPy · ArcGIS Desktop

**应用领域**: GIS分析 · 道路网络 · 市政管理 · 数据自动化