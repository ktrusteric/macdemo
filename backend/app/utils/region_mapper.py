from typing import Dict, List, Optional
from enum import Enum

class RegionCode(str, Enum):
    """区域代码枚举"""
    EAST_CHINA = "east_china"
    SOUTH_CHINA = "south_china"  
    NORTH_CHINA = "north_china"
    SOUTHWEST_CHINA = "southwest_china"
    NORTHWEST_CHINA = "northwest_china"
    NORTHEAST_CHINA = "northeast_china"
    CENTRAL_CHINA = "central_china"
    NATIONAL = "national"
    INTERNATIONAL = "international"

class ProvinceCode(str, Enum):
    """省份代码枚举"""
    SHANGHAI = "shanghai"
    BEIJING = "beijing"
    TIANJIN = "tianjin"
    CHONGQING = "chongqing"
    GUANGDONG = "guangdong"
    JIANGSU = "jiangsu"
    ZHEJIANG = "zhejiang"
    SHANDONG = "shandong"
    FUJIAN = "fujian"
    JIANGXI = "jiangxi"
    ANHUI = "anhui"
    HENAN = "henan"
    HUBEI = "hubei"
    HUNAN = "hunan"
    GUANGXI = "guangxi"
    HAINAN = "hainan"
    SICHUAN = "sichuan"
    YUNNAN = "yunnan"
    GUIZHOU = "guizhou"
    TIBET = "tibet"
    SHAANXI = "shaanxi"
    GANSU = "gansu"
    QINGHAI = "qinghai"
    NINGXIA = "ningxia"
    XINJIANG = "xinjiang"
    HEBEI = "hebei"
    SHANXI = "shanxi"
    INNER_MONGOLIA = "inner_mongolia"
    LIAONING = "liaoning"
    JILIN = "jilin"
    HEILONGJIANG = "heilongjiang"

class RegionMapper:
    """城市-省份-区域映射器"""
    
    # 城市到省份的映射关系
    CITY_TO_PROVINCE: Dict[str, str] = {
        # 直辖市
        "上海": ProvinceCode.SHANGHAI,
        "北京": ProvinceCode.BEIJING,
        "天津": ProvinceCode.TIANJIN,
        "重庆": ProvinceCode.CHONGQING,
        
        # 广东省
        "广州": ProvinceCode.GUANGDONG,
        "深圳": ProvinceCode.GUANGDONG,
        "珠海": ProvinceCode.GUANGDONG,
        "佛山": ProvinceCode.GUANGDONG,
        "东莞": ProvinceCode.GUANGDONG,
        "中山": ProvinceCode.GUANGDONG,
        "惠州": ProvinceCode.GUANGDONG,
        "汕头": ProvinceCode.GUANGDONG,
        
        # 江苏省
        "南京": ProvinceCode.JIANGSU,
        "苏州": ProvinceCode.JIANGSU,
        "无锡": ProvinceCode.JIANGSU,
        
        # 浙江省
        "杭州": ProvinceCode.ZHEJIANG,
        "宁波": ProvinceCode.ZHEJIANG,
        "温州": ProvinceCode.ZHEJIANG,
        
        # 山东省
        "济南": ProvinceCode.SHANDONG,
        "青岛": ProvinceCode.SHANDONG,
        
        # 福建省
        "福州": ProvinceCode.FUJIAN,
        "厦门": ProvinceCode.FUJIAN,
        
        # 江西省
        "南昌": ProvinceCode.JIANGXI,
        
        # 安徽省
        "合肥": ProvinceCode.ANHUI,
        
        # 河南省
        "郑州": ProvinceCode.HENAN,
        "洛阳": ProvinceCode.HENAN,
        "开封": ProvinceCode.HENAN,
        "新乡": ProvinceCode.HENAN,
        
        # 湖北省
        "武汉": ProvinceCode.HUBEI,
        
        # 湖南省
        "长沙": ProvinceCode.HUNAN,
        "株洲": ProvinceCode.HUNAN,
        "湘潭": ProvinceCode.HUNAN,
        "岳阳": ProvinceCode.HUNAN,
        
        # 广西壮族自治区
        "南宁": ProvinceCode.GUANGXI,
        "桂林": ProvinceCode.GUANGXI,
        
        # 海南省
        "海口": ProvinceCode.HAINAN,
        "三亚": ProvinceCode.HAINAN,
        
        # 四川省
        "成都": ProvinceCode.SICHUAN,
        "绵阳": ProvinceCode.SICHUAN,
        "德阳": ProvinceCode.SICHUAN,
        "宜宾": ProvinceCode.SICHUAN,
        
        # 云南省
        "昆明": ProvinceCode.YUNNAN,
        "大理": ProvinceCode.YUNNAN,
        
        # 贵州省
        "贵阳": ProvinceCode.GUIZHOU,
        
        # 西藏自治区
        "拉萨": ProvinceCode.TIBET,
        
        # 陕西省
        "西安": ProvinceCode.SHAANXI,
        "咸阳": ProvinceCode.SHAANXI,
        "宝鸡": ProvinceCode.SHAANXI,
        "榆林": ProvinceCode.SHAANXI,
        
        # 甘肃省
        "兰州": ProvinceCode.GANSU,
        
        # 青海省
        "西宁": ProvinceCode.QINGHAI,
        
        # 宁夏回族自治区
        "银川": ProvinceCode.NINGXIA,
        
        # 新疆维吾尔自治区
        "乌鲁木齐": ProvinceCode.XINJIANG,
        
        # 河北省
        "石家庄": ProvinceCode.HEBEI,
        "唐山": ProvinceCode.HEBEI,
        "秦皇岛": ProvinceCode.HEBEI,
        "保定": ProvinceCode.HEBEI,
        
        # 山西省
        "太原": ProvinceCode.SHANXI,
        
        # 内蒙古自治区
        "呼和浩特": ProvinceCode.INNER_MONGOLIA,
        "包头": ProvinceCode.INNER_MONGOLIA,
        
        # 辽宁省
        "沈阳": ProvinceCode.LIAONING,
        "大连": ProvinceCode.LIAONING,
        "鞍山": ProvinceCode.LIAONING,
        "抚顺": ProvinceCode.LIAONING,
        
        # 吉林省
        "长春": ProvinceCode.JILIN,
        "吉林": ProvinceCode.JILIN,
        
        # 黑龙江省
        "哈尔滨": ProvinceCode.HEILONGJIANG,
        "齐齐哈尔": ProvinceCode.HEILONGJIANG,
    }
    
    # 省份到区域的映射关系
    PROVINCE_TO_REGION: Dict[str, str] = {
        # 华东地区
        ProvinceCode.SHANGHAI: RegionCode.EAST_CHINA,
        ProvinceCode.JIANGSU: RegionCode.EAST_CHINA,
        ProvinceCode.ZHEJIANG: RegionCode.EAST_CHINA,
        ProvinceCode.SHANDONG: RegionCode.EAST_CHINA,
        ProvinceCode.FUJIAN: RegionCode.EAST_CHINA,
        ProvinceCode.JIANGXI: RegionCode.EAST_CHINA,
        ProvinceCode.ANHUI: RegionCode.EAST_CHINA,
        
        # 华南地区
        ProvinceCode.GUANGDONG: RegionCode.SOUTH_CHINA,
        ProvinceCode.GUANGXI: RegionCode.SOUTH_CHINA,
        ProvinceCode.HAINAN: RegionCode.SOUTH_CHINA,
        
        # 华北地区
        ProvinceCode.BEIJING: RegionCode.NORTH_CHINA,
        ProvinceCode.TIANJIN: RegionCode.NORTH_CHINA,
        ProvinceCode.HEBEI: RegionCode.NORTH_CHINA,
        ProvinceCode.SHANXI: RegionCode.NORTH_CHINA,
        ProvinceCode.INNER_MONGOLIA: RegionCode.NORTH_CHINA,
        
        # 西南地区
        ProvinceCode.CHONGQING: RegionCode.SOUTHWEST_CHINA,
        ProvinceCode.SICHUAN: RegionCode.SOUTHWEST_CHINA,
        ProvinceCode.YUNNAN: RegionCode.SOUTHWEST_CHINA,
        ProvinceCode.GUIZHOU: RegionCode.SOUTHWEST_CHINA,
        ProvinceCode.TIBET: RegionCode.SOUTHWEST_CHINA,
        
        # 西北地区
        ProvinceCode.SHAANXI: RegionCode.NORTHWEST_CHINA,
        ProvinceCode.GANSU: RegionCode.NORTHWEST_CHINA,
        ProvinceCode.QINGHAI: RegionCode.NORTHWEST_CHINA,
        ProvinceCode.NINGXIA: RegionCode.NORTHWEST_CHINA,
        ProvinceCode.XINJIANG: RegionCode.NORTHWEST_CHINA,
        
        # 东北地区
        ProvinceCode.LIAONING: RegionCode.NORTHEAST_CHINA,
        ProvinceCode.JILIN: RegionCode.NORTHEAST_CHINA,
        ProvinceCode.HEILONGJIANG: RegionCode.NORTHEAST_CHINA,
        
        # 华中地区
        ProvinceCode.HENAN: RegionCode.CENTRAL_CHINA,
        ProvinceCode.HUBEI: RegionCode.CENTRAL_CHINA,
        ProvinceCode.HUNAN: RegionCode.CENTRAL_CHINA,
    }
    
    # 城市到区域的映射关系（旧版兼容）
    CITY_TO_REGION: Dict[str, str] = {
        # 华东地区
        "上海": RegionCode.EAST_CHINA,
        "杭州": RegionCode.EAST_CHINA,
        "南京": RegionCode.EAST_CHINA,
        "苏州": RegionCode.EAST_CHINA,
        "无锡": RegionCode.EAST_CHINA,
        "宁波": RegionCode.EAST_CHINA,
        "温州": RegionCode.EAST_CHINA,
        "福州": RegionCode.EAST_CHINA,
        "厦门": RegionCode.EAST_CHINA,
        "南昌": RegionCode.EAST_CHINA,
        "济南": RegionCode.EAST_CHINA,
        "青岛": RegionCode.EAST_CHINA,
        "合肥": RegionCode.EAST_CHINA,
        
        # 华南地区
        "广州": RegionCode.SOUTH_CHINA,
        "深圳": RegionCode.SOUTH_CHINA,
        "珠海": RegionCode.SOUTH_CHINA,
        "佛山": RegionCode.SOUTH_CHINA,
        "东莞": RegionCode.SOUTH_CHINA,
        "中山": RegionCode.SOUTH_CHINA,
        "惠州": RegionCode.SOUTH_CHINA,
        "汕头": RegionCode.SOUTH_CHINA,
        "海口": RegionCode.SOUTH_CHINA,
        "三亚": RegionCode.SOUTH_CHINA,
        "南宁": RegionCode.SOUTH_CHINA,
        "桂林": RegionCode.SOUTH_CHINA,
        
        # 华北地区
        "北京": RegionCode.NORTH_CHINA,
        "天津": RegionCode.NORTH_CHINA,
        "石家庄": RegionCode.NORTH_CHINA,
        "太原": RegionCode.NORTH_CHINA,
        "呼和浩特": RegionCode.NORTH_CHINA,
        "包头": RegionCode.NORTH_CHINA,
        "唐山": RegionCode.NORTH_CHINA,
        "秦皇岛": RegionCode.NORTH_CHINA,
        "保定": RegionCode.NORTH_CHINA,
        
        # 西南地区
        "成都": RegionCode.SOUTHWEST_CHINA,
        "重庆": RegionCode.SOUTHWEST_CHINA,
        "昆明": RegionCode.SOUTHWEST_CHINA,
        "贵阳": RegionCode.SOUTHWEST_CHINA,
        "拉萨": RegionCode.SOUTHWEST_CHINA,
        "绵阳": RegionCode.SOUTHWEST_CHINA,
        "德阳": RegionCode.SOUTHWEST_CHINA,
        "宜宾": RegionCode.SOUTHWEST_CHINA,
        "大理": RegionCode.SOUTHWEST_CHINA,
        
        # 西北地区
        "西安": RegionCode.NORTHWEST_CHINA,
        "兰州": RegionCode.NORTHWEST_CHINA,
        "银川": RegionCode.NORTHWEST_CHINA,
        "西宁": RegionCode.NORTHWEST_CHINA,
        "乌鲁木齐": RegionCode.NORTHWEST_CHINA,
        "咸阳": RegionCode.NORTHWEST_CHINA,
        "宝鸡": RegionCode.NORTHWEST_CHINA,
        "榆林": RegionCode.NORTHWEST_CHINA,
        
        # 东北地区
        "沈阳": RegionCode.NORTHEAST_CHINA,
        "大连": RegionCode.NORTHEAST_CHINA,
        "哈尔滨": RegionCode.NORTHEAST_CHINA,
        "长春": RegionCode.NORTHEAST_CHINA,
        "吉林": RegionCode.NORTHEAST_CHINA,
        "鞍山": RegionCode.NORTHEAST_CHINA,
        "抚顺": RegionCode.NORTHEAST_CHINA,
        "齐齐哈尔": RegionCode.NORTHEAST_CHINA,
        
        # 华中地区
        "武汉": RegionCode.CENTRAL_CHINA,
        "长沙": RegionCode.CENTRAL_CHINA,
        "郑州": RegionCode.CENTRAL_CHINA,
        "洛阳": RegionCode.CENTRAL_CHINA,
        "株洲": RegionCode.CENTRAL_CHINA,
        "湘潭": RegionCode.CENTRAL_CHINA,
        "岳阳": RegionCode.CENTRAL_CHINA,
        "开封": RegionCode.CENTRAL_CHINA,
        "新乡": RegionCode.CENTRAL_CHINA,
    }
    
    # 区域代码到中文名称的映射
    REGION_NAMES: Dict[str, str] = {
        RegionCode.EAST_CHINA: "华东地区",
        RegionCode.SOUTH_CHINA: "华南地区",
        RegionCode.NORTH_CHINA: "华北地区",
        RegionCode.SOUTHWEST_CHINA: "西南地区",
        RegionCode.NORTHWEST_CHINA: "西北地区",
        RegionCode.NORTHEAST_CHINA: "东北地区",
        RegionCode.CENTRAL_CHINA: "华中地区",
        RegionCode.NATIONAL: "全国",
        RegionCode.INTERNATIONAL: "国际"
    }
    
    # 省份代码到中文名称的映射
    PROVINCE_NAMES: Dict[str, str] = {
        ProvinceCode.SHANGHAI: "上海市",
        ProvinceCode.BEIJING: "北京市",
        ProvinceCode.TIANJIN: "天津市",
        ProvinceCode.CHONGQING: "重庆市",
        ProvinceCode.GUANGDONG: "广东省",
        ProvinceCode.JIANGSU: "江苏省",
        ProvinceCode.ZHEJIANG: "浙江省",
        ProvinceCode.SHANDONG: "山东省",
        ProvinceCode.FUJIAN: "福建省",
        ProvinceCode.JIANGXI: "江西省",
        ProvinceCode.ANHUI: "安徽省",
        ProvinceCode.HENAN: "河南省",
        ProvinceCode.HUBEI: "湖北省",
        ProvinceCode.HUNAN: "湖南省",
        ProvinceCode.GUANGXI: "广西壮族自治区",
        ProvinceCode.HAINAN: "海南省",
        ProvinceCode.SICHUAN: "四川省",
        ProvinceCode.YUNNAN: "云南省",
        ProvinceCode.GUIZHOU: "贵州省",
        ProvinceCode.TIBET: "西藏自治区",
        ProvinceCode.SHAANXI: "陕西省",
        ProvinceCode.GANSU: "甘肃省",
        ProvinceCode.QINGHAI: "青海省",
        ProvinceCode.NINGXIA: "宁夏回族自治区",
        ProvinceCode.XINJIANG: "新疆维吾尔自治区",
        ProvinceCode.HEBEI: "河北省",
        ProvinceCode.SHANXI: "山西省",
        ProvinceCode.INNER_MONGOLIA: "内蒙古自治区",
        ProvinceCode.LIAONING: "辽宁省",
        ProvinceCode.JILIN: "吉林省",
        ProvinceCode.HEILONGJIANG: "黑龙江省",
    }

    @classmethod
    def get_province_by_city(cls, city: str) -> Optional[str]:
        """根据城市获取省份代码"""
        return cls.CITY_TO_PROVINCE.get(city)
    
    @classmethod
    def get_region_by_city(cls, city: str) -> Optional[str]:
        """根据城市获取区域代码"""
        return cls.CITY_TO_REGION.get(city)
    
    @classmethod
    def get_region_by_province(cls, province_code: str) -> Optional[str]:
        """根据省份获取区域代码"""
        return cls.PROVINCE_TO_REGION.get(province_code)

    @classmethod
    def get_region_name(cls, region_code: str) -> str:
        """获取区域中文名称"""
        return cls.REGION_NAMES.get(region_code, region_code)
    
    @classmethod
    def get_province_name(cls, province_code: str) -> str:
        """获取省份中文名称"""
        return cls.PROVINCE_NAMES.get(province_code, province_code)

    @classmethod
    def get_full_location_info(cls, city: str) -> Dict[str, str]:
        """获取城市的完整位置信息（城市、省份、地区）"""
        province_code = cls.get_province_by_city(city)
        region_code = cls.get_region_by_city(city)
        
        result = {
            "city": city,
            "city_code": city.lower().replace(" ", "_"),
        }
        
        if province_code:
            result.update({
                "province": cls.get_province_name(province_code),
                "province_code": province_code
            })
        
        if region_code:
            result.update({
                "region": cls.get_region_name(region_code),
                "region_code": region_code
            })
        
        return result

    @classmethod
    def get_regions_by_cities(cls, cities: List[str]) -> List[str]:
        """批量获取城市对应的区域"""
        regions = []
        for city in cities:
            region = cls.get_region_by_city(city)
            if region and region not in regions:
                regions.append(region)
        return regions

    @classmethod
    def get_all_cities(cls) -> List[str]:
        """获取所有支持的城市列表"""
        return list(cls.CITY_TO_REGION.keys())

    @classmethod
    def get_cities_by_region(cls, region_code: str) -> List[str]:
        """根据区域获取城市列表"""
        return [city for city, region in cls.CITY_TO_REGION.items() if region == region_code]

    @classmethod
    def get_all_regions(cls) -> List[Dict[str, str]]:
        """获取所有区域信息"""
        return [
            {"code": code, "name": name} 
            for code, name in cls.REGION_NAMES.items()
            if code not in [RegionCode.NATIONAL, RegionCode.INTERNATIONAL]
        ]
    
    @classmethod
    def get_all_provinces(cls) -> List[Dict[str, str]]:
        """获取所有省份信息"""
        return [
            {"code": code, "name": name} 
            for code, name in cls.PROVINCE_NAMES.items()
        ] 