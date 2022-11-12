import pandas as pd
from visual import *

countries_name = {
  "Afghanistan": "阿富汗",
  "Singapore": "新加坡",
  "Angola": "安哥拉",
  "Albania": "阿尔巴尼亚",
  "United Arab Emirates": "阿拉伯联合酋长国",
  "Argentina": "阿根廷",
  "Armenia": "亚美尼亚",
  "French Southern and Antarctic Lands": "法属南半球和南极领地",
  "Australia": "澳大利亚",
  "Austria": "奥地利",
  "Azerbaijan": "阿塞拜疆",
  "Burundi": "布隆迪",
  "Belgium": "比利时",
  "Benin": "贝宁",
  "Burkina Faso": "布基纳法索",
  "Bangladesh": "孟加拉",
  "Bulgaria": "保加利亚",
  "Bahamas": "巴哈马",
  "Bosnia and Herz.": "波黑",
  "Belarus": "白俄罗斯",
  "Belize": "伯利兹",
  "Bermuda": "百慕大",
  "Bolivia": "玻利维亚",
  "Brazil": "巴西",
  "Brunei": "文莱",
  "Bhutan": "不丹",
  "Botswana": "博茨瓦纳",
  "Central African Rep.": "中非",
  "Canada": "加拿大",
  "Switzerland": "瑞士",
  "Chile": "智利",
  "China": "中国",
  "Côte d'Ivoire": "科特迪瓦",
  "Cameroon": "喀麦隆",
  "Dem. Rep. Congo": "刚果（金）",
  "Congo": "刚果",
  "Colombia": "哥伦比亚",
  "Costa Rica": "哥斯达黎加",
  "Cuba": "古巴",
  "Northern Cyprus": "北塞浦路斯",
  "Cyprus": "塞浦路斯",
  "Czech Rep.": "捷克",
  "Germany": "德国",
  "Djibouti": "吉布提",
  "Denmark": "丹麦",
  "Algeria": "阿尔及利亚",
  "Ecuador": "厄瓜多尔",
  "Egypt": "埃及",
  "Eritrea": "厄立特里亚",
  "Spain": "西班牙",
  "Estonia": "爱沙尼亚",
  "Ethiopia": "埃塞俄比亚",
  "Finland": "芬兰",
  "Fiji": "斐济",
  "Falkland Is.": "福克兰群岛",
  "France": "法国",
  "Gabon": "加蓬",
  "United Kingdom": "英国",
  "Georgia": "格鲁吉亚",
  "Ghana": "加纳",
  "Gambia": "冈比亚",
  "Guinea": "几内亚",
  "Guinea-Bissau": "几内亚比绍",
  "Eq. Guinea": "赤道几内亚",
  "Greece": "希腊",
  "Greenland": "格陵兰",
  "Guatemala": "危地马拉",
  "Fr. S. Antarctic Lands": "凯尔盖朗群岛(法)",
  "Guyana": "圭亚那",
  "Honduras": "洪都拉斯",
  "Croatia": "克罗地亚",
  "Haiti": "海地",
  "Hungary": "匈牙利",
  "Indonesia": "印度尼西亚",
  "India": "印度",
  "Ireland": "爱尔兰",
  "Iran": "伊朗",
  "Iraq": "伊拉克",
  "Iceland": "冰岛",
  "Israel": "以色列",
  "Italy": "意大利",
  "Jamaica": "牙买加",
  "Jordan": "约旦",
  "Japan": "日本本土",
  "Kazakhstan": "哈萨克斯坦",
  "Kenya": "肯尼亚",
  "Kyrgyzstan": "吉尔吉斯斯坦",
  "Cambodia": "柬埔寨",
  "Korea": "韩国",
  "Dem. Rep. Korea": "北朝鲜",
  "Kosovo": "科索沃",
  "Kuwait": "科威特",
  "Lao PDR": "老挝",
  "Lebanon": "黎巴嫩",
  "Liberia": "利比里亚",
  "Libya": "利比亚",
  "Sri Lanka": "斯里兰卡",
  "Lesotho": "莱索托",
  "Lithuania": "立陶宛",
  "Luxembourg": "卢森堡",
  "Latvia": "拉脱维亚",
  "Morocco": "摩洛哥",
  "Moldova": "摩尔多瓦",
  "Madagascar": "马达加斯加",
  "Mexico": "墨西哥",
  "Macedonia": "北马其顿",
  "Mali": "马里",
  "Myanmar": "缅甸",
  "Montenegro": "黑山",
  "Mongolia": "蒙古",
  "Mozambique": "莫桑比克",
  "Mauritania": "毛里塔尼亚",
  "Malawi": "马拉维",
  "Malaysia": "马来西亚",
  "Namibia": "纳米比亚",
  "New Caledonia": "新喀里多尼亚",
  "Niger": "尼日尔",
  "Nigeria": "尼日利亚",
  "Nicaragua": "尼加拉瓜",
  "Netherlands": "荷兰",
  "Norway": "挪威",
  "Nepal": "尼泊尔",
  "New Zealand": "新西兰",
  "Oman": "阿曼",
  "Pakistan": "巴基斯坦",
  "Panama": "巴拿马",
  "Peru": "秘鲁",
  "Philippines": "菲律宾",
  "Papua New Guinea": "巴布亚新几内亚",
  "Poland": "波兰",
  "Puerto Rico": "波多黎各",
  "Portugal": "葡萄牙",
  "Paraguay": "巴拉圭",
  "Qatar": "卡塔尔",
  "Romania": "罗马尼亚",
  "Russia": "俄罗斯",
  "Rwanda": "卢旺达",
  "W. Sahara": "西撒哈拉",
  "Saudi Arabia": "沙特阿拉伯",
  "Sudan": "苏丹",
  "S. Sudan": "南苏丹",
  "Senegal": "塞内加尔",
  "Solomon Is.": "所罗门群岛",
  "Sierra Leone": "塞拉利昂",
  "El Salvador": "萨尔瓦多",
  "Somaliland": "索马里兰",
  "Somalia": "索马里",
  "Serbia": "塞尔维亚",
  "Suriname": "苏里南",
  "Slovakia": "斯洛伐克",
  "Slovenia": "斯洛文尼亚",
  "Sweden": "瑞典",
  "Swaziland": "斯威士兰",
  "Syria": "叙利亚",
  "Chad": "乍得",
  "Togo": "多哥",
  "Thailand": "泰国",
  "Tajikistan": "塔吉克斯坦",
  "Turkmenistan": "土库曼斯坦",
  "Timor-Leste": "东帝汶",
  "Trinidad and Tobago": "特立尼达和多巴哥",
  "Tunisia": "突尼斯",
  "Turkey": "土耳其",
  "Tanzania": "坦桑尼亚",
  "Uganda": "乌干达",
  "Ukraine": "乌克兰",
  "Uruguay": "乌拉圭",
  "United States": "美国",
  "Uzbekistan": "乌兹别克斯坦",
  "Venezuela": "委内瑞拉",
  "Vietnam": "越南",
  "Vanuatu": "瓦努阿图",
  "West Bank": "西岸",
  "Yemen": "也门",
  "South Africa": "南非",
  "Zambia": "赞比亚",
  "Zimbabwe": "津巴布韦",
  "Aland": "奥兰群岛",
  "American Samoa": "美属萨摩亚",
  "Andorra": "安道尔",
  "Anguilla": "安圭拉",
  "Antigua and Barb.": "安提瓜和巴布达",
  "Aruba": "阿鲁巴",
  "Bahrain": "巴林",
  "Barbados": "巴巴多斯",
  "Bouvet Island": "布维岛",
  "Cape Verde": "佛得角",
  "Christmas Islands": "圣诞岛",
  "Cocos (keeling) Islands": "科科斯（基林）群岛",
  "Comoros": "科摩罗",
  "Cook Islands": "库克群岛",
  "Dominica": "多米尼克",
  "Dominican Rep.": "多明尼加共和国",
  "Faeroe Is.": "法罗群岛",
  "MetropolitanFrance": "法国大都会",
  "French Polynesia": "法属波利尼西亚",
  "Gibraltar": "直布罗陀",
  "Grenada": "格林纳达",
  "Guam": "关岛",
  "Guernsey": "根西岛",
  "Isle of Man": "马恩岛",
  "Jersey": "泽西岛",
  "Kiribati": "基里巴斯",
  "Liechtenstein": "列支敦士登公国",
  "Maldives": "马尔代夫",
  "Malta": "马耳他",
  "Marshall Islands": "马绍尔群岛",
  "Mauritius": "毛里求斯",
  "Micronesia": "密克罗尼西亚",
  "Monaco": "摩纳哥",
  "Montserrat": "蒙特塞拉特",
  "Nauru": "瑙鲁",
  "Niue": "纽埃",
  "Norfolk Island": "诺福克岛",
  "Palau": "帕劳",
  "Palestine": "巴勒斯坦",
  "Pitcairn Islands": "皮特凯恩群岛",
  "Russian Federation": "俄罗斯联邦",
  "Saint Helena": "圣赫勒拿",
  "Saint Lucia": "圣卢西亚",
  "Saint Kitts-Nevis": "圣基茨和尼维斯",
  "St. Vin. and Gren.": "圣文森特和格林纳丁斯",
  "St. Pierre and Miquelon": "圣皮埃尔和密克隆群岛（法属岛屿）",
  "Samoa": "萨摩亚",
  "San Marino": "圣马力诺",
  "Sao Tome and Principe": "圣多美和普林西比",
  "Seychelles": "塞舌尔",
  "Tokelau": "托克劳",
  "Tonga": "汤加",
  "Tuvalu": "图瓦卢",
  "Vatican City": "梵蒂冈",
  "Wallis and Futuna": "瓦利斯群岛和富图纳群岛",
  "Yugoslavia": "南斯拉夫",
  "Fr. Polynesia":"法属玻里尼西亚",
  "Turks and Caicos Is.":"特克斯和凯科斯群岛",
  "Cayman Is.":"开曼群岛",
  "U.S. Virgin Is.":"美属维尔京群岛",
  "Curaçao":"库拉索岛",
  "S. Geo. and S. Sandw. Is.":"南乔治亚岛和南桑威奇群岛",
  "Heard I. and McDonald Is.":"赫德岛和麦克唐纳群岛",
  "Br. Indian Ocean Ter.":"英属印度洋领土",
  "N. Mariana Is.":"北马里亚纳群岛",
  "São Tomé and Principe":"圣多美和普林西比",
  "Siachen Glacier":"锡亚琴冰川"
}

# 读取文件
df = pd.read_excel("./result/各国家电影数量.xlsx")

# 数据清洗
df.dropna(inplace=True)

data_list = []
# 地图数据
for index, row in df.iterrows():
    country = row["movie_nation"]
    for en_name, ch_name in countries_name.items():
        if ch_name == "中国":
            print(ch_name)
        if country == ch_name:
            data_list.append([en_name, row["movie_count"]])

print(data_list)

# 画地图
c = render_map(data_list)
c.render("./figures/各国家上映电影数.html")

