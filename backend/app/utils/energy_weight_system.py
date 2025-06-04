#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
能源产品分层权重管理系统
建立大类（权重3.0）和具体产品（权重5.0）的层级结构
"""

from typing import Dict, List, Optional, Tuple
from enum import Enum

class EnergyProductWeight(float, Enum):
    """能源产品权重枚举"""
    CATEGORY = 3.0      # 大类能源产品权重
    SPECIFIC = 5.0      # 具体能源产品权重

class EnergyWeightSystem:
    """能源产品权重管理系统"""
    
    # 🔥 能源产品分层权重体系
    ENERGY_HIERARCHY = {
        # 🔋 天然气大类 (权重: 3.0)
        "天然气": {
            "weight": EnergyProductWeight.CATEGORY,
            "description": "天然气大类产品",
            "sub_products": {
                "液化天然气(LNG)": EnergyProductWeight.SPECIFIC,
                "管道天然气(PNG)": EnergyProductWeight.SPECIFIC,
                "压缩天然气(CNG)": EnergyProductWeight.SPECIFIC,
                "液化石油气(LPG)": EnergyProductWeight.SPECIFIC,
            }
        },
        
        # 🛢️ 石油大类 (权重: 3.0)
        "原油": {
            "weight": EnergyProductWeight.CATEGORY,
            "description": "石油大类产品",
            "sub_products": {
                "汽油": EnergyProductWeight.SPECIFIC,
                "柴油": EnergyProductWeight.SPECIFIC,
                "航空煤油": EnergyProductWeight.SPECIFIC,
                "沥青": EnergyProductWeight.SPECIFIC,
                "石油焦": EnergyProductWeight.SPECIFIC,
                "润滑油": EnergyProductWeight.SPECIFIC,
                "石脑油": EnergyProductWeight.SPECIFIC,
                "燃料油": EnergyProductWeight.SPECIFIC,
            }
        },
        
        # ⚡ 电力大类 (权重: 3.0)
        "电力": {
            "weight": EnergyProductWeight.CATEGORY,
            "description": "电力大类产品",
            "sub_products": {
                "火力发电": EnergyProductWeight.SPECIFIC,
                "水力发电": EnergyProductWeight.SPECIFIC,
                "风力发电": EnergyProductWeight.SPECIFIC,
                "太阳能发电": EnergyProductWeight.SPECIFIC,
                "核能发电": EnergyProductWeight.SPECIFIC,
                "地热发电": EnergyProductWeight.SPECIFIC,
            }
        },
        
        # ⚫ 煤炭大类 (权重: 3.0)
        "煤炭": {
            "weight": EnergyProductWeight.CATEGORY,
            "description": "煤炭大类产品",
            "sub_products": {
                "动力煤": EnergyProductWeight.SPECIFIC,
                "炼焦煤": EnergyProductWeight.SPECIFIC,
                "喷吹煤": EnergyProductWeight.SPECIFIC,
                "无烟煤": EnergyProductWeight.SPECIFIC,
                "褐煤": EnergyProductWeight.SPECIFIC,
                "焦炭": EnergyProductWeight.SPECIFIC,
            }
        },
        
        # 🌿 可再生能源大类 (权重: 3.0)
        "可再生能源": {
            "weight": EnergyProductWeight.CATEGORY,
            "description": "可再生能源大类产品",
            "sub_products": {
                "生物柴油": EnergyProductWeight.SPECIFIC,
                "生物乙醇": EnergyProductWeight.SPECIFIC,
                "生物质能": EnergyProductWeight.SPECIFIC,
                "氢能": EnergyProductWeight.SPECIFIC,
                "甲醇": EnergyProductWeight.SPECIFIC,
                "氨能": EnergyProductWeight.SPECIFIC,
            }
        },
        
        # 🔬 化工能源大类 (权重: 3.0)
        "化工能源": {
            "weight": EnergyProductWeight.CATEGORY,
            "description": "化工能源大类产品",
            "sub_products": {
                "重烃": EnergyProductWeight.SPECIFIC,
                "乙烯": EnergyProductWeight.SPECIFIC,
                "丙烯": EnergyProductWeight.SPECIFIC,
                "苯": EnergyProductWeight.SPECIFIC,
                "甲苯": EnergyProductWeight.SPECIFIC,
                "二甲苯": EnergyProductWeight.SPECIFIC,
            }
        },
        
        # ⚛️ 核能大类 (权重: 3.0)
        "核能": {
            "weight": EnergyProductWeight.CATEGORY,
            "description": "核能大类产品",
            "sub_products": {
                "铀燃料": EnergyProductWeight.SPECIFIC,
                "核发电": EnergyProductWeight.SPECIFIC,
                "核供热": EnergyProductWeight.SPECIFIC,
            }
        }
    }
    
    # 🔄 兼容性映射：旧版本能源类型到新版本的映射
    LEGACY_MAPPING = {
        "液化天然气(LNG)": ("天然气", "液化天然气(LNG)"),
        "管道天然气(PNG)": ("天然气", "管道天然气(PNG)"),
        "液化石油气(LPG)": ("天然气", "液化石油气(LPG)"),
        "汽油": ("原油", "汽油"),
        "柴油": ("原油", "柴油"),
        "沥青": ("原油", "沥青"),
        "石油焦": ("原油", "石油焦"),
        "生物柴油": ("可再生能源", "生物柴油"),
        "生物质能": ("可再生能源", "生物质能"),
        "氢能": ("可再生能源", "氢能"),
        "重烃": ("化工能源", "重烃"),
    }
    
    @classmethod
    def get_energy_weight(cls, energy_name: str) -> float:
        """
        获取能源产品的权重
        
        Args:
            energy_name: 能源产品名称
            
        Returns:
            float: 权重值 (3.0 for 大类, 5.0 for 具体产品)
        """
        # 检查是否为大类
        if energy_name in cls.ENERGY_HIERARCHY:
            return cls.ENERGY_HIERARCHY[energy_name]["weight"]
        
        # 检查是否为具体产品
        for category, info in cls.ENERGY_HIERARCHY.items():
            if energy_name in info["sub_products"]:
                return info["sub_products"][energy_name]
        
        # 检查兼容性映射
        if energy_name in cls.LEGACY_MAPPING:
            category, product = cls.LEGACY_MAPPING[energy_name]
            return cls.ENERGY_HIERARCHY[category]["sub_products"][product]
        
        # 默认权重（未分类的能源产品）
        return 3.0
    
    @classmethod
    def get_energy_category(cls, energy_name: str) -> Optional[str]:
        """
        获取能源产品所属的大类
        
        Args:
            energy_name: 能源产品名称
            
        Returns:
            Optional[str]: 大类名称，如果未找到返回None
        """
        # 检查是否本身就是大类
        if energy_name in cls.ENERGY_HIERARCHY:
            return energy_name
        
        # 检查是否为具体产品
        for category, info in cls.ENERGY_HIERARCHY.items():
            if energy_name in info["sub_products"]:
                return category
        
        # 检查兼容性映射
        if energy_name in cls.LEGACY_MAPPING:
            category, _ = cls.LEGACY_MAPPING[energy_name]
            return category
        
        return None
    
    @classmethod
    def get_all_categories(cls) -> List[str]:
        """获取所有能源大类列表"""
        return list(cls.ENERGY_HIERARCHY.keys())
    
    @classmethod
    def get_category_products(cls, category: str) -> List[str]:
        """
        获取指定大类下的所有具体产品
        
        Args:
            category: 大类名称
            
        Returns:
            List[str]: 具体产品列表
        """
        if category in cls.ENERGY_HIERARCHY:
            return list(cls.ENERGY_HIERARCHY[category]["sub_products"].keys())
        return []
    
    @classmethod
    def get_all_energy_products(cls) -> List[Dict[str, any]]:
        """
        获取所有能源产品的完整列表（包含权重信息）
        
        Returns:
            List[Dict]: 能源产品信息列表
        """
        products = []
        
        # 添加大类产品
        for category, info in cls.ENERGY_HIERARCHY.items():
            products.append({
                "name": category,
                "type": "category",
                "weight": info["weight"],
                "description": info["description"],
                "parent": None
            })
            
            # 添加具体产品
            for product, weight in info["sub_products"].items():
                products.append({
                    "name": product,
                    "type": "product",
                    "weight": weight,
                    "description": f"{category}类下的{product}",
                    "parent": category
                })
        
        return products
    
    @classmethod
    def get_energy_hierarchy_tree(cls) -> Dict[str, any]:
        """
        获取能源产品层级树结构
        
        Returns:
            Dict: 树状结构的能源产品数据
        """
        tree = {}
        for category, info in cls.ENERGY_HIERARCHY.items():
            tree[category] = {
                "weight": info["weight"],
                "description": info["description"],
                "products": {}
            }
            
            for product, weight in info["sub_products"].items():
                tree[category]["products"][product] = {
                    "weight": weight,
                    "description": f"{category}类下的{product}"
                }
        
        return tree
    
    @classmethod
    def recommend_energy_weights(cls, user_selected_energies: List[str]) -> List[Dict[str, any]]:
        """
        根据用户选择的能源类型，推荐权重配置
        
        Args:
            user_selected_energies: 用户选择的能源类型列表
            
        Returns:
            List[Dict]: 推荐的权重配置
        """
        recommendations = []
        
        for energy in user_selected_energies:
            weight = cls.get_energy_weight(energy)
            category = cls.get_energy_category(energy)
            
            recommendation = {
                "name": energy,
                "recommended_weight": weight,
                "category": category,
                "type": "category" if energy in cls.ENERGY_HIERARCHY else "product"
            }
            
            # 如果选择的是具体产品，建议也添加对应的大类（权重较低）
            if category and category != energy:
                recommendations.append({
                    "name": category,
                    "recommended_weight": EnergyProductWeight.CATEGORY,
                    "category": category,
                    "type": "category",
                    "reason": f"因为您选择了{energy}，建议也关注{category}大类"
                })
            
            recommendations.append(recommendation)
        
        return recommendations
    
    @classmethod
    def validate_energy_selection(cls, energies: List[str]) -> Dict[str, any]:
        """
        验证用户的能源选择，并提供优化建议
        
        Args:
            energies: 用户选择的能源列表
            
        Returns:
            Dict: 验证结果和建议
        """
        valid_energies = []
        invalid_energies = []
        categories_covered = set()
        suggestions = []
        
        for energy in energies:
            if cls.get_energy_weight(energy) > 0:
                valid_energies.append(energy)
                category = cls.get_energy_category(energy)
                if category:
                    categories_covered.add(category)
            else:
                invalid_energies.append(energy)
        
        # 生成建议
        if len(categories_covered) == 1:
            suggestions.append("建议考虑多元化能源组合，关注其他能源大类")
        
        if len(valid_energies) > 10:
            suggestions.append("建议精简能源关注范围，选择最相关的5-8个能源类型")
        
        return {
            "valid_energies": valid_energies,
            "invalid_energies": invalid_energies,
            "categories_covered": list(categories_covered),
            "suggestions": suggestions,
            "total_categories": len(cls.ENERGY_HIERARCHY),
            "coverage_ratio": len(categories_covered) / len(cls.ENERGY_HIERARCHY)
        }

# 工具函数：快速访问
def get_energy_weight(energy_name: str) -> float:
    """快速获取能源权重"""
    return EnergyWeightSystem.get_energy_weight(energy_name)

def get_energy_category(energy_name: str) -> Optional[str]:
    """快速获取能源大类"""
    return EnergyWeightSystem.get_energy_category(energy_name)

def is_energy_category(energy_name: str) -> bool:
    """判断是否为能源大类"""
    return energy_name in EnergyWeightSystem.ENERGY_HIERARCHY

def is_specific_product(energy_name: str) -> bool:
    """判断是否为具体能源产品"""
    for category, info in EnergyWeightSystem.ENERGY_HIERARCHY.items():
        if energy_name in info["sub_products"]:
            return True
    return energy_name in EnergyWeightSystem.LEGACY_MAPPING

if __name__ == "__main__":
    # 测试功能
    print("🔋 能源产品分层权重系统测试")
    print("=" * 50)
    
    # 测试权重获取
    test_energies = ["天然气", "液化天然气(LNG)", "原油", "汽油", "电力", "风力发电"]
    
    print("📊 权重测试：")
    for energy in test_energies:
        weight = get_energy_weight(energy)
        category = get_energy_category(energy)
        energy_type = "大类" if is_energy_category(energy) else "具体产品"
        print(f"   {energy} -> 权重: {weight}, 大类: {category}, 类型: {energy_type}")
    
    print(f"\n🌳 能源产品层级树：")
    tree = EnergyWeightSystem.get_energy_hierarchy_tree()
    for category, info in tree.items():
        print(f"📁 {category} (权重: {info['weight']})")
        for product, product_info in info["products"].items():
            print(f"   └── {product} (权重: {product_info['weight']})")
    
    print(f"\n💡 推荐配置测试：")
    user_selection = ["液化天然气(LNG)", "汽油", "风力发电"]
    recommendations = EnergyWeightSystem.recommend_energy_weights(user_selection)
    for rec in recommendations:
        print(f"   {rec['name']} -> 权重: {rec['recommended_weight']} ({rec['type']})") 