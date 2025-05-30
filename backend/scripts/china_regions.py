#!/usr/bin/env python3
"""
中国行政区划完整数据
包含所有省份、直辖市、自治区、主要城市和地区的完整列表
"""

# 省份、直辖市、自治区（34个）
PROVINCES = [
    # 直辖市
    "北京", "北京市", 
    "上海", "上海市",
    "天津", "天津市", 
    "重庆", "重庆市",
    
    # 省份
    "河北", "河北省", "山西", "山西省", 
    "辽宁", "辽宁省", "吉林", "吉林省", "黑龙江", "黑龙江省",
    "江苏", "江苏省", "浙江", "浙江省", "安徽", "安徽省", 
    "福建", "福建省", "江西", "江西省", "山东", "山东省",
    "河南", "河南省", "湖北", "湖北省", "湖南", "湖南省", 
    "广东", "广东省", "海南", "海南省", "四川", "四川省",
    "贵州", "贵州省", "云南", "云南省", "陕西", "陕西省", 
    "甘肃", "甘肃省", "青海", "青海省",
    
    # 自治区
    "内蒙古", "内蒙古自治区", "广西", "广西壮族自治区",
    "西藏", "西藏自治区", "宁夏", "宁夏回族自治区", 
    "新疆", "新疆维吾尔自治区",
    
    # 特别行政区
    "香港", "香港特别行政区", "澳门", "澳门特别行政区", "台湾", "台湾省"
]

# 主要城市（包含省会城市、计划单列市、重要地级市）
MAJOR_CITIES = [
    # 直辖市
    "北京", "上海", "天津", "重庆",
    
    # 省会城市
    "石家庄", "太原", "沈阳", "长春", "哈尔滨",
    "南京", "杭州", "合肥", "福州", "南昌", "济南",
    "郑州", "武汉", "长沙", "广州", "海口", "成都", 
    "贵阳", "昆明", "西安", "兰州", "西宁",
    "呼和浩特", "南宁", "拉萨", "银川", "乌鲁木齐",
    
    # 计划单列市
    "深圳", "厦门", "青岛", "大连", "宁波",
    
    # 重要地级市（经济发达或能源相关城市）
    "苏州", "无锡", "常州", "南通", "徐州", "扬州", "泰州", "镇江", "盐城", "淮安", "连云港", "宿迁",
    "温州", "嘉兴", "湖州", "绍兴", "金华", "衢州", "舟山", "台州", "丽水",
    "佛山", "东莞", "中山", "珠海", "江门", "湛江", "茂名", "肇庆", "惠州", "梅州", "汕头", "潮州", "揭阳",
    "青岛", "烟台", "威海", "潍坊", "济宁", "泰安", "临沂", "德州", "聊城", "滨州", "菏泽",
    "洛阳", "开封", "安阳", "鹤壁", "新乡", "焦作", "濮阳", "许昌", "漯河", "三门峡", "南阳", "商丘", "信阳", "周口", "驻马店",
    "芜湖", "蚌埠", "淮南", "马鞍山", "淮北", "铜陵", "安庆", "黄山", "滁州", "阜阳", "宿州", "六安", "亳州", "池州", "宣城",
    "唐山", "秦皇岛", "邯郸", "邢台", "保定", "张家口", "承德", "沧州", "廊坊", "衡水",
    "大同", "阳泉", "长治", "晋城", "朔州", "晋中", "运城", "忻州", "临汾", "吕梁",
    "大连", "鞍山", "抚顺", "本溪", "丹东", "锦州", "营口", "阜新", "辽阳", "盘锦", "铁岭", "朝阳", "葫芦岛",
    "吉林", "四平", "辽源", "通化", "白山", "松原", "白城", "延边",
    "齐齐哈尔", "鸡西", "鹤岗", "双鸭山", "大庆", "伊春", "佳木斯", "七台河", "牡丹江", "黑河", "绥化", "大兴安岭",
    "宜昌", "襄阳", "荆州", "荆门", "十堰", "随州", "恩施", "黄冈", "咸宁", "黄石", "孝感", "鄂州", "仙桃", "潜江", "天门", "神农架",
    "株洲", "湘潭", "衡阳", "邵阳", "岳阳", "常德", "张家界", "益阳", "郴州", "永州", "怀化", "娄底", "湘西",
    "绵阳", "德阳", "南充", "宜宾", "自贡", "乐山", "泸州", "达州", "内江", "遂宁", "攀枝花", "广元", "眉山", "广安", "资阳", "凉山", "甘孜", "阿坝", "雅安",
    "包头", "乌海", "赤峰", "通辽", "鄂尔多斯", "呼伦贝尔", "巴彦淖尔", "乌兰察布", "兴安盟", "锡林郭勒盟", "阿拉善盟",
    "柳州", "桂林", "梧州", "北海", "防城港", "钦州", "贵港", "玉林", "百色", "贺州", "河池", "来宾", "崇左",
    "三亚", "三沙", "儋州",
    "遵义", "六盘水", "安顺", "毕节", "铜仁", "黔西南", "黔东南", "黔南",
    "曲靖", "玉溪", "保山", "昭通", "丽江", "普洱", "临沧", "楚雄", "红河", "文山", "西双版纳", "大理", "德宏", "怒江", "迪庆",
    "宝鸡", "咸阳", "铜川", "渭南", "延安", "榆林", "汉中", "安康", "商洛",
    "嘉峪关", "金昌", "白银", "天水", "武威", "张掖", "平凉", "酒泉", "庆阳", "定西", "陇南", "临夏", "甘南",
    "格尔木", "德令哈", "海东",
    "克拉玛依", "吐鲁番", "哈密", "阿克苏", "喀什", "和田", "伊犁", "塔城", "阿勒泰", "博尔塔拉", "昌吉", "巴音郭楞", "克孜勒苏",
    "中卫", "固原", "石嘴山", "吴忠",
    "山南", "日喀则", "昌都", "林芝", "那曲", "阿里"
]

# 经济区域划分
ECONOMIC_REGIONS = {
    "华北地区": ["北京", "天津", "河北", "山西", "内蒙古"],
    "东北地区": ["辽宁", "吉林", "黑龙江"],
    "华东地区": ["上海", "江苏", "浙江", "安徽", "福建", "江西", "山东"],
    "华中地区": ["河南", "湖北", "湖南"],
    "华南地区": ["广东", "广西", "海南"],
    "西南地区": ["重庆", "四川", "贵州", "云南", "西藏"],
    "西北地区": ["陕西", "甘肃", "青海", "宁夏", "新疆"],
}

# 能源相关重点区域
ENERGY_REGIONS = {
    "环渤海": ["北京", "天津", "河北", "山东", "辽宁"],
    "长三角": ["上海", "江苏", "浙江", "安徽"],
    "珠三角": ["广东"],
    "成渝": ["重庆", "四川"],
    "京津冀": ["北京", "天津", "河北"],
    "长江经济带": ["上海", "江苏", "浙江", "安徽", "江西", "湖北", "湖南", "重庆", "四川", "云南", "贵州"],
    "一带一路": ["新疆", "陕西", "甘肃", "宁夏", "青海", "内蒙古"],
}

# 方向性地区表述
DIRECTIONAL_REGIONS = [
    "华北", "华东", "华中", "华南", "西南", "西北", "东北",
    "北方", "南方", "东部", "西部", "中部", "沿海", "内陆",
    "环渤海", "长三角", "珠三角", "成渝", "京津冀", "长江经济带", "一带一路",
    "中原", "关中", "江南", "岭南", "塞北", "西域", "东疆", "南疆", "北疆"
]

def get_all_region_keywords():
    """获取所有地域关键词的综合列表"""
    all_keywords = set()
    
    # 添加省份
    all_keywords.update(PROVINCES)
    
    # 添加城市
    all_keywords.update(MAJOR_CITIES)
    
    # 添加经济区域
    for region_name, provinces in ECONOMIC_REGIONS.items():
        all_keywords.add(region_name)
        all_keywords.update(provinces)
    
    # 添加能源区域
    for region_name, provinces in ENERGY_REGIONS.items():
        all_keywords.add(region_name)
        all_keywords.update(provinces)
    
    # 添加方向性地区
    all_keywords.update(DIRECTIONAL_REGIONS)
    
    return list(all_keywords)

def classify_region_type(region_name: str) -> dict:
    """
    分类地域名称的类型和权重
    返回: {type: str, weight: float, level: int}
    """
    region_info = {
        "type": "unknown",
        "weight": 1.0,
        "level": 0,  # 0=未知, 1=国家级, 2=区域级, 3=省级, 4=市级
        "name": region_name
    }
    
    # 直辖市 - 最高权重
    if region_name in ["北京", "北京市", "上海", "上海市", "天津", "天津市", "重庆", "重庆市"]:
        region_info.update({"type": "municipality", "weight": 3.0, "level": 4})
    
    # 省会城市和计划单列市 - 高权重
    elif region_name in ["石家庄", "太原", "沈阳", "长春", "哈尔滨", "南京", "杭州", "合肥", 
                        "福州", "南昌", "济南", "郑州", "武汉", "长沙", "广州", "海口", "成都",
                        "贵阳", "昆明", "西安", "兰州", "西宁", "呼和浩特", "南宁", "拉萨", 
                        "银川", "乌鲁木齐", "深圳", "厦门", "青岛", "大连", "宁波"]:
        region_info.update({"type": "major_city", "weight": 2.5, "level": 4})
    
    # 其他重要城市 - 中高权重
    elif region_name in MAJOR_CITIES:
        region_info.update({"type": "city", "weight": 2.0, "level": 4})
    
    # 省份/自治区 - 中等权重
    elif any(prov in region_name for prov in PROVINCES):
        region_info.update({"type": "province", "weight": 1.8, "level": 3})
    
    # 经济区域 - 中等权重
    elif region_name in ECONOMIC_REGIONS or region_name in ENERGY_REGIONS:
        region_info.update({"type": "economic_zone", "weight": 1.5, "level": 2})
    
    # 方向性地区 - 较低权重
    elif region_name in DIRECTIONAL_REGIONS:
        region_info.update({"type": "directional", "weight": 1.2, "level": 2})
    
    # 特殊处理：过于宽泛的地区权重降低
    if region_name in ["全国", "国内", "国际", "中国", "海外", "境外", "国外"]:
        region_info.update({"type": "too_broad", "weight": 0.5, "level": 1})
    
    return region_info

def find_regions_in_text(text: str) -> list:
    """
    在文本中查找所有地域关键词
    返回: [{"name": str, "type": str, "weight": float, "level": int}]
    """
    found_regions = []
    text_lower = text.lower()
    all_keywords = get_all_region_keywords()
    
    # 按长度降序排序，优先匹配长的地名（避免"南京"被"南"匹配）
    sorted_keywords = sorted(all_keywords, key=len, reverse=True)
    
    for keyword in sorted_keywords:
        if keyword.lower() in text_lower:
            region_info = classify_region_type(keyword)
            # 避免重复添加同一个地区
            if not any(existing["name"] == keyword for existing in found_regions):
                found_regions.append(region_info)
    
    # 按权重和级别排序
    found_regions.sort(key=lambda x: (x["level"], x["weight"]), reverse=True)
    
    return found_regions

def get_region_priority_list():
    """
    获取地域优先级列表，用于标签选择
    返回按优先级排序的地域列表
    """
    priority_regions = []
    
    # 1. 直辖市（最高优先级）
    municipalities = ["北京", "上海", "天津", "重庆"]
    priority_regions.extend([(region, 4, 3.0) for region in municipalities])
    
    # 2. 省会城市和计划单列市
    major_cities = ["石家庄", "太原", "沈阳", "长春", "哈尔滨", "南京", "杭州", "合肥", 
                   "福州", "南昌", "济南", "郑州", "武汉", "长沙", "广州", "海口", "成都",
                   "贵阳", "昆明", "西安", "兰州", "西宁", "呼和浩特", "南宁", "拉萨", 
                   "银川", "乌鲁木齐", "深圳", "厦门", "青岛", "大连", "宁波"]
    priority_regions.extend([(region, 4, 2.5) for region in major_cities])
    
    # 3. 省份
    provinces_simple = ["河北", "山西", "辽宁", "吉林", "黑龙江", "江苏", "浙江", "安徽", 
                       "福建", "江西", "山东", "河南", "湖北", "湖南", "广东", "海南", "四川",
                       "贵州", "云南", "陕西", "甘肃", "青海", "内蒙古", "广西", "西藏", 
                       "宁夏", "新疆", "香港", "澳门", "台湾"]
    priority_regions.extend([(region, 3, 1.8) for region in provinces_simple])
    
    return priority_regions

if __name__ == "__main__":
    # 测试功能
    test_text = "上海市发展和改革委员会关于调整本市非居民天然气销售基准价格的通知，影响江苏、浙江等长三角地区"
    
    print("🗺️ 中国行政区划数据测试")
    print("=" * 50)
    
    print(f"📊 数据统计：")
    print(f"   省份/自治区: {len(set(PROVINCES))} 个")
    print(f"   主要城市: {len(set(MAJOR_CITIES))} 个") 
    print(f"   经济区域: {len(ECONOMIC_REGIONS)} 个")
    print(f"   能源区域: {len(ENERGY_REGIONS)} 个")
    print(f"   方向性地区: {len(DIRECTIONAL_REGIONS)} 个")
    print(f"   总关键词: {len(get_all_region_keywords())} 个")
    
    print(f"\n🔍 文本地域识别测试：")
    print(f"测试文本: {test_text}")
    
    found_regions = find_regions_in_text(test_text)
    print(f"\n发现地域: {len(found_regions)} 个")
    for region in found_regions:
        print(f"   {region['name']} - 类型:{region['type']}, 权重:{region['weight']}, 级别:{region['level']}") 