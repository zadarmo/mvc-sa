from pyecharts import options as opts
from pyecharts.charts import *
from pyecharts.faker import Faker

def render_map(data_list):
    c = (
        Map()
        .add("", data_list, "world",
            is_map_symbol_show=False,
        )
        .set_series_opts(label_opts=opts.LabelOpts(is_show=False))
        .set_global_opts(
            title_opts=opts.TitleOpts(title="2012~2022年，各国家上映的电影数", pos_left=320),
            visualmap_opts=opts.VisualMapOpts(max_=100)
        )
    )
    return c

def render_bar(xdata, ydata):
    # xdata = ['a', 'b', 'c']
    # ydata = [1, 2 ,3]
    c = (
        Bar()
        .add_xaxis(xdata)
        .add_yaxis("数量", ydata)
        .set_global_opts(
            title_opts=opts.TitleOpts(title="2012~2022年，各类别电影数量", pos_left=350),
            legend_opts=opts.LegendOpts(is_show=False)
        )
    )
    return c

def render_pie(data):
    c = (
        Pie()
        .add(
            "",
            data,
            radius=["40%", "55%"],
            label_opts=opts.LabelOpts(
                position="outside",
                formatter="{a|{a}}{abg|}\n{hr|}\n {b|{b}: }{c}  {per|{d}%}  ",
                background_color="#eee",
                border_color="#aaa",
                border_width=1,
                border_radius=4,
                rich={
                    "a": {"color": "#999", "lineHeight": 22, "align": "center"},
                    "abg": {
                        "backgroundColor": "#e3e3e3",
                        "width": "100%",
                        "align": "right",
                        "height": 22,
                        "borderRadius": [4, 4, 0, 0],
                    },
                    "hr": {
                        "borderColor": "#aaa",
                        "width": "100%",
                        "borderWidth": 0.5,
                        "height": 0,
                    },
                    "b": {"fontSize": 16, "lineHeight": 33},
                    "per": {
                        "color": "#eee",
                        "backgroundColor": "#334455",
                        "padding": [2, 4],
                        "borderRadius": 2,
                    },
                },
            ),
        )
        .set_global_opts(title_opts=opts.TitleOpts(title="好评率前100各国家电影数（前5）", pos_left=300, pos_bottom=500))
    )
    return c


