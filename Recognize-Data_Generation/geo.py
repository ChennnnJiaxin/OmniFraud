#!/usr/bin/env python
# -*- coding: utf-8 -*-
from pyecharts.charts import Geo
from pyecharts import options as opts
from pyecharts.globals import ChartType, SymbolType

# 初始化地图
geo = Geo(init_opts=opts.InitOpts(width="1000px", height="600px"))

# ----------------------------
# 1: 添加缺失的中国省份包
# 需先安装：pip install echarts-china-provinces-pypkg
# geo.add_coordinate('新地点', 122.480539, 35.235929)

# ----------------------------
# 2: 配置地图区域颜色
geo.add_schema(
    maptype="china",
    itemstyle_opts=opts.ItemStyleOpts(
        color="#323c48",       # 地图区域填充色
        border_color="#111"   # 边界线颜色
    )
)

# ----------------------------
# 3: 添加数据点并关联颜色
geo.add(
    "城市受到诈骗风险程度",
    [("北京",10), ("上海",20), ("广州",30), ("成都",40), ("哈尔滨",50)],
    type_=ChartType.EFFECT_SCATTER,
    symbol_size=10,
    color="orange"  # 数据点颜色
)

# ----------------------------
# 4: 配置流向线样式
geo.add(
    "诈骗金额流向线",
    [
        ("北京", "广州"),
        ("上海", "上海"),
        ("广州", "成都"),
        ("成都", "哈尔滨"),
    ],
    type_=ChartType.LINES,
    effect_opts=opts.EffectOpts(
        symbol=SymbolType.ARROW, symbol_size=10, color="cyan"  # 动态线颜色
    ),
    linestyle_opts=opts.LineStyleOpts(
        curve=0.2, color="rgba(0, 255, 255, 0.6)", width=2  # 线颜色
    ),
    is_large=True,
    label_opts=opts.LabelOpts(is_show=False),
)

# ----------------------------
# 5: 添加视觉映射配置
geo.set_global_opts(
    title_opts=opts.TitleOpts(title="城市诈骗金额流向图"),
    visualmap_opts=opts.VisualMapOpts(
        is_show=True,
        min_=0,
        max_=100,
        range_color=["#FFE4B5", "#FF6347"],  # 颜色渐变
        pos_left="30px",
        pos_bottom="30px"
    )
)

# 生成文件
geo.render("multicolor_china_map.html")
