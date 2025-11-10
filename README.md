# GIS 道路网络拓扑分析工具

基于 ArcMap Python (ArcPy) 开发的道路网络自动化分析工具,用于识别交叉口、切割路段、分析端点连接关系。

---

## 项目简介

本项目通过Python脚本自动化处理道路网络数据,实现以下功能:

1. **识别道路交叉口** - 自动计算路网中所有交叉点位置
2. **切割道路路段** - 按交叉口将完整道路切分为多个路段
3. **分析端点连接** - 识别每个端点连接的所有路段
4. **批量导出Excel** - 将所有结果导出为Excel格式供查询分析

### 核心优势

- **自动化处理** - 原本需要数小时的手工操作,现在只需几分钟
- **智能过滤** - 自动排除高架、地铁、隧道等非地面道路
- **未命名道路处理** - 为未命名道路自动分配唯一编号
- **多方向搜索** - 生成所有可能的搜索组合,支持任意顺序查询
- **精确去重** - 智能合并相近交叉点,避免数据冗余

---

## 项目结构
```
GIS-Road-Network-Analysis/
│
├── README.md                          # 项目说明文档
├── .gitignore                         # Git忽略配置
│
├── scripts/                           # Python脚本
│   ├── 1_find_intersections.py       # 步骤1: 识别道路交叉口
│   ├── 2_segment_and_endpoints.py    # 步骤2: 切割路段并标注端点
│   └── 3_export_to_excel.py          # 步骤3: 导出结果为Excel
│
├── road_search_data/                  # 数据文件夹
│   ├── input/                         # 输入数据
│   │   └── road_network.shp          # 原始路网数据（已隐藏）
│   └── output/                        # 输出数据
│       ├── shapefiles/                # Shapefile输出（已隐藏）
│       └── excel/                     # Excel输出（已隐藏）
│
└── docs/                              # 文档
    ├── installation.md                # 安装指南
    └── introduction.md                # ArcMap软件介绍
```

---

## 环境要求

- **ArcGIS Desktop 10.x** 或更高版本
- **Python 2.7** (ArcGIS内置)
- **ArcPy库** (随ArcGIS安装)

---

## 快速开始

### 1. 准备数据

将道路网络数据(Shapefile格式)放入 `road_search_data/input/` 文件夹。

**数据要求:**
- 格式: Shapefile (.shp)
- 类型: Polyline (线要素)
- 必须字段: NAME (可以为空)
- 坐标系统: 建议使用投影坐标系(单位:米)

### 2. 打开ArcMap

在ArcMap中添加路网数据到地图。

### 3. 运行脚本

在ArcMap的Python窗口中依次运行三个脚本:
```python
# 步骤1: 识别交叉口
execfile(r"C:\path\to\scripts\1_find_intersections.py")

# 步骤2: 切割路段与识别端点
execfile(r"C:\path\to\scripts\2_segment_and_endpoints.py")

# 步骤3: 导出Excel
execfile(r"C:\path\to\scripts\3_export_to_excel.py")
```

**注意:** 将 `C:\path\to\` 替换为你的实际路径。

### 4. 查看结果

- **地图中:** 三个新图层自动添加
- **文件夹中:** Excel文件保存在 `road_search_data/output/excel/`

---

## 程序逻辑与核心流程

### 整体流程图
```
原始路网数据 (Polyline)
         ↓
┌────────────────────────────────┐
│  脚本1: 识别道路交叉口          │
│  - Intersect自相交分析         │
│  - 过滤非地面道路              │
│  - 为未命名道路分配编号        │
│  - 生成搜索关键词              │
└────────┬───────────────────────┘
         ↓
  Road_Intersections.shp
         ↓
┌────────────────────────────────┐
│  脚本2: 切割路段与识别端点      │
│  - SplitLineAtPoint切割道路   │
│  - 路段编号(如"A路_1")        │
│  - 计算路段长度                │
│  - 分析端点连接关系            │
└────────┬───────────────────────┘
         ↓
  Road_Segments.shp + Segment_Endpoints.shp
         ↓
┌────────────────────────────────┐
│  脚本3: 导出Excel              │
│  - 批量导出三个图层            │
│  - 保留完整字段信息            │
└────────┬───────────────────────┘
         ↓
  3个Excel文件 (.xls)
```

### 脚本1: 识别道路交叉口

**核心逻辑:**

1. **扫描未命名道路** - 遍历原始路网,为每条未命名道路分配唯一编号
2. **计算交叉点** - 使用`Intersect_analysis`让路网与自己相交
3. **过滤与处理** - 排除高架、地铁等,使用OBJECTID映射获取道路名称
4. **去重合并** - 坐标四舍五入,合并相近交叉点
5. **生成搜索词** - 为每个交叉口生成所有可能的搜索组合

**输出:**
- **Road_Intersections.shp** - 包含字段: INT_NAME, SEARCH_KEY, POINT_X, POINT_Y

### 脚本2: 切割路段与识别端点

**核心逻辑:**

1. **建立映射** - 复用脚本1的未命名道路映射逻辑
2. **切割道路** - 使用`SplitLineAtPoint_management`在交叉口切割道路
3. **路段编号** - 为同一道路的不同路段依次编号(1, 2, 3...)
4. **记录端点** - 收集每个路段的起点和终点,记录哪些路段连接到哪个端点
5. **去重写入** - 合并相同位置的端点,避免重复

**输出:**
- **Road_Segments.shp** - 包含字段: SEG_NAME, BASE_NAME, SEG_ID, LENGTH, START_X/Y, END_X/Y
- **Segment_Endpoints.shp** - 包含字段: NAME, POINT_X, POINT_Y, SEG_COUNT

### 脚本3: 导出Excel

**核心逻辑:**

1. **检查文件** - 验证三个shapefile是否存在
2. **批量导出** - 使用`TableToExcel_conversion`依次导出
3. **错误处理** - 捕获导出异常,显示详细信息

**输出:**
- **Road_Intersections.xls**
- **Road_Segments.xls**
- **Segment_Endpoints.xls**

---

## 主要技术与工具

### ArcPy 核心工具

| 工具 | 用途 | 应用场景 |
|------|------|---------|
| `Intersect_analysis` | 计算要素相交 | 识别道路交叉点 |
| `SplitLineAtPoint_management` | 用点切割线 | 在交叉口切割道路 |
| `CreateFeatureclass_management` | 创建要素类 | 创建输出图层 |
| `AddField_management` | 添加字段 | 添加属性字段 |
| `DeleteField_management` | 删除字段 | 删除自动生成的空字段 |
| `TableToExcel_conversion` | 导出Excel | 导出分析结果 |
| `arcpy.da.SearchCursor` | 读取数据 | 遍历要素获取信息 |
| `arcpy.da.InsertCursor` | 插入数据 | 写入新要素 |
| `arcpy.mapping.AddLayer` | 添加图层 | 将结果添加到地图 |

### Python 标准库

| 功能 | 用途 |
|------|------|
| `os.path.join()` | 构建跨平台文件路径 |
| `itertools.combinations()` | 生成道路名称的所有组合 |
| `set()` | 自动去重道路名称 |
| `sorted()` | 排序保证一致性 |
| `round()` | 坐标四舍五入用于去重 |

### 关键数据结构

**未命名道路映射字典:**
```python
oid_to_name = {
    75: "支路1",
    82: "支路2",
    103: "支路3"
}
```

**交叉点数据字典:**
```python
intersection_data = {
    (521403.65, 3523498.57): {
        "coord": (521403.6473, 3523498.5704),
        "roads": {"A路", "B路"}
    }
}
```

**端点路段字典:**
```python
endpoint_segments = {
    (521403.6, 3523498.6): {
        "coord": (521403.6473, 3523498.5704),
        "segments": ["A路_1", "A路_2", "B路_1"]
    }
}
```

---

## 技术难点与解决方案

### 1. 过滤非地面道路

**问题描述:**
道路数据中包含高架、地铁、隧道等非地面道路,它们不应该与地面道路形成交叉口。

**解决方案:**
```python
# 定义过滤关键词
filter_keywords = [u"高架", u"轨道交通", u"隧道"]

def should_filter(road_name):
    """判断道路是否需要被过滤"""
    if not road_name:
        return False
    
    # 转换为unicode以正确处理中文
    try:
        if isinstance(road_name, str):
            road_name_unicode = road_name.decode('gbk')
        else:
            road_name_unicode = unicode(road_name)
    except:
        return False
    
    # 检查是否包含过滤关键词
    for keyword in filter_keywords:
        if keyword in road_name_unicode:
            return True
    return False
```

**关键点:**
- 使用中文关键词列表
- 处理字符编码问题
- 在数据读取阶段就过滤,提高效率

### 2. 处理字符编码问题

**问题描述:**
ArcMap使用Python 2.7,从shapefile读取的中文字符串是GBK编码,直接使用会导致`UnicodeDecodeError`。

**问题表现:**
```python
# 错误示例
name = u"珞珈西路"
if "高架" in name:  # UnicodeDecodeError!
```

**解决方案:**
```python
# 方法1: 统一转换为unicode
if isinstance(road_name, str):
    road_name_unicode = road_name.decode('gbk')
else:
    road_name_unicode = unicode(road_name)

# 方法2: 关键词使用unicode
filter_keywords = [u"高架", u"轨道交通", u"隧道"]  # 注意u前缀

# 方法3: 在脚本开头声明编码
# -*- coding: utf-8 -*-
```

**关键点:**
- 代码中的中文字符串前加 `u`
- 从数据库读取的字符串需要decode
- 比较时确保两边编码一致

### 3. 处理未命名道路

**问题描述:**
原始数据中部分道路的NAME字段为空,需要为它们分配唯一且稳定的名称。

**错误方案:**
```python
# 每次运行时重新编号,同一条路可能得到不同名称
unnamed_counter = 1
for row in cursor:
    if not row['NAME']:
        row['NAME'] = "支路" + str(unnamed_counter)
        unnamed_counter += 1
```

**正确方案:**
```python
# 使用OBJECTID作为稳定标识
unnamed_road_mapping = {}
unnamed_counter = 1

# 第一步:建立映射
with arcpy.da.SearchCursor(road_layer, ["OBJECTID", "NAME"]) as cursor:
    for row in cursor:
        oid = row[0]
        name = row[1] if row[1] else ""
        
        if not name or not name.strip():
            unnamed_road_mapping[oid] = u"支路" + unicode(unnamed_counter)
            unnamed_counter += 1

# 第二步:使用映射
name1 = unnamed_road_mapping.get(oid1, u"支路未知")
```

**关键点:**
- 使用OBJECTID作为唯一标识
- 预先建立完整的映射字典
- 在所有脚本中使用相同的映射逻辑
- 确保同一条道路在不同阶段获得相同名称

### 4. 交叉点去重

**问题描述:**
`Intersect_analysis`会产生大量重复交叉点:
- 两条路相交产生1个点
- 三条路相交产生3个点(A-B, B-C, A-C)
- 由于浮点数精度,同一位置可能有多个坐标略有不同的点

**解决方案:**
```python
# 坐标四舍五入作为字典key
x = round(coord[0], 2)  # 保留2位小数
y = round(coord[1], 2)
key = (x, y)

# 使用set自动去重道路名称
if key not in intersection_data:
    intersection_data[key] = {"coord": coord, "roads": set()}

intersection_data[key]["roads"].add(name1)
intersection_data[key]["roads"].add(name2)
```

**关键点:**
- 坐标四舍五入到合适精度(0.01米)
- 使用字典避免重复处理
- 使用set自动去重道路名称

### 5. 生成多方向搜索组合

**问题描述:**
用户可能以任意顺序搜索交叉口(如"A路与B路"或"B路与A路"),需要支持所有可能的搜索方式。

**解决方案:**
```python
from itertools import combinations

def generate_search_combinations(road_list):
    """生成所有可能的搜索组合"""
    search_terms = []
    
    # 两条路:A与B, B与A
    if len(road_list) == 2:
        search_terms.append(road_list[0] + u"与" + road_list[1])
        search_terms.append(road_list[1] + u"与" + road_list[0])
    
    # 三条路:所有两两组合 + 完整组合
    elif len(road_list) == 3:
        for combo in combinations(road_list, 2):
            search_terms.append(combo[0] + u"与" + combo[1])
            search_terms.append(combo[1] + u"与" + combo[0])
        search_terms.append(road_list[0] + u"与" + road_list[1] + u"与" + road_list[2])
        search_terms.append(road_list[2] + u"与" + road_list[1] + u"与" + road_list[0])
    
    return u"|".join(search_terms)
```

**输出示例:**
```
2条路: "A道路与B道路|B道路与A道路"
3条路: "A与B|B与A|A与C|C与A|B与C|C与B|A与B与C|C与B与A"
```

---

## 输出数据说明

### Road_Intersections (道路交叉口)

| 字段 | 类型 | 说明 | 示例 |
|------|------|------|------|
| FID | Long | 唯一标识符 | 0, 1, 2... |
| INT_NAME | Text | 交叉口名称 | "A道路与B道路交口" |
| SEARCH_KEY | Text | 搜索关键词组合 | "A道路与B道路\|B道路与A道路" |
| POINT_X | Double | X坐标 | 521403.6473 |
| POINT_Y | Double | Y坐标 | 3523498.5704 |

**用途:** Excel查询交叉口位置

### Road_Segments (道路路段)

| 字段 | 类型 | 说明 | 示例 |
|------|------|------|------|
| FID | Long | 唯一标识符 | 0, 1, 2... |
| SEG_NAME | Text | 路段名称 | "A路_1", "支路5_2" |
| BASE_NAME | Text | 道路基础名称 | "A路", "支路5" |
| SEG_ID | Short | 路段编号 | 1, 2, 3... |
| LENGTH | Double | 长度(米) | 235.67 |
| START_X | Double | 起点X坐标 | 521403.65 |
| START_Y | Double | 起点Y坐标 | 3523498.57 |
| END_X | Double | 终点X坐标 | 521650.23 |
| END_Y | Double | 终点Y坐标 | 3523720.89 |

**用途:** 路段级别的道路管理和分析

### Segment_Endpoints (路段端点)

| 字段 | 类型 | 说明 | 示例 |
|------|------|------|------|
| FID | Long | 唯一标识符 | 0, 1, 2... |
| NAME | Text | 连接的路段列表 | "A路_1、A路_2、B路_3" |
| POINT_X | Double | X坐标 | 521403.65 |
| POINT_Y | Double | Y坐标 | 3523498.57 |
| SEG_COUNT | Short | 连接路段数量 | 3 |

**用途:** 网络拓扑分析,识别关键节点

---

## 使用示例

### 在Excel中搜索交叉口

1. 打开 `Road_Intersections.xls`
2. 在SEARCH_KEY列使用Excel筛选功能
3. 输入"包含"条件,如"A路"
4. 查看POINT_X和POINT_Y获取坐标

### 分析路段连通性

1. 打开 `Segment_Endpoints.xls`
2. 按SEG_COUNT排序
3. SEG_COUNT值最大的端点是关键交叉节点

---

## 常见问题

### Q1: 运行脚本时找不到文件
**A:** 检查脚本中的 `workspace` 路径是否正确,需要改为你的实际路径。

### Q2: 中文显示乱码
**A:** 确保脚本开头有 `# -*- coding: utf-8 -*-`,且使用u前缀表示unicode字符串。

### Q3: 生成了很多.lock文件
**A:** 这是ArcGIS的文件锁定机制,关闭ArcMap后会自动删除,不影响使用。

### Q4: Excel中的SEARCH_KEY字段显示不全
**A:** Shapefile的TEXT字段最大254字符,对于路段特别多的交叉口可能会被截断。

### Q5: 交叉点数量比预期少
**A:** 检查过滤关键词设置,可能有些道路被意外过滤了。

---

## 项目背景

本项目开发于实际GIS数据处理需求,通过自动化脚本显著提升了道路网络分析的效率。

**应用场景:**
- 城市道路网络拓扑分析
- 交通流量研究
- 道路资产管理
- 导航数据预处理

**处理能力示例:**
- 路网规模: 200+ 条道路
- 识别交叉口: 400+ 个
- 生成路段: 600+ 条
- 处理时间: < 2分钟

---

## 致谢

感谢实习期间积累的GIS数据处理实际项目经验,以及对GIS自动化处理需求的深入理解。

---

**注意事项:**
- 本工具基于ArcGIS,需要下载相应软件
- 由于保密协议,不包含实际原始数据文件
- 项目代码开源仅供参考,作者不承担任何责任

---
