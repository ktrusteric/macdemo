#!/usr/bin/env python3
"""
标签处理工具类 - 统一标签解析、验证和规范化
提供安全、一致的标签处理方法
"""

import ast
import json
import logging
from typing import List, Dict, Any, Optional, Union

logger = logging.getLogger(__name__)

class TagProcessor:
    """标签处理器 - 提供统一的标签处理方法"""
    
    # 能源类型标准词典 - 与TagsManagement.vue完全一致
    STANDARD_ENERGY_TYPES = [
        "原油", "管道天然气(PNG)", "天然气", "液化天然气(LNG)", 
        "液化石油气(LPG)", "汽油", "柴油", "沥青", "石油焦", 
        "生物柴油", "电力", "煤炭", "重烃", "核能", "可再生能源", 
        "生物质能", "氢能"
    ]
    
    # 内容类型标准映射 - 用于文章分类
    CONTENT_TYPE_MAP = {
        "policy": "政策法规",
        "news": "行业资讯", 
        "price": "调价公告",
        "announcement": "交易公告"
    }
    
    # 基础信息标签标准词典 - 统一为5个类型，与内容分类保持一致
    STANDARD_BASIC_INFO_TAGS = [
        "政策法规", "行业资讯", "交易公告", "调价公告", "研报分析"
    ]
    
    # 业务领域标签标准词典 - 与TagsManagement.vue完全一致
    STANDARD_BUSINESS_FIELD_TAGS = [
        "市场动态", "价格变化", "交易信息", "科技创新", 
        "政策解读", "国际合作", "投资支持", "民营经济发展", 
        "市场准入优化", "公平竞争"
    ]
    
    # 受益主体标签标准词典 - 与TagsManagement.vue完全一致
    STANDARD_BENEFICIARY_TAGS = [
        "能源企业", "政府机构", "交易方", "民营企业", 
        "国有企业", "外资企业", "LNG交易方"
    ]
    
    # 政策措施标签标准词典 - 与TagsManagement.vue完全一致
    STANDARD_POLICY_MEASURE_TAGS = [
        "市场监管", "技术合作", "竞价规则", "投资支持", 
        "市场准入", "创新投融资", "风险管控", "市场准入措施", 
        "价格调整", "区域价格调整"
    ]
    
    # 重要性标签标准词典 - 与TagsManagement.vue完全一致
    STANDARD_IMPORTANCE_TAGS = [
        "国家级", "权威发布", "重要政策", "行业影响", 
        "常规公告", "国际影响"
    ]
    
    @classmethod
    def safe_parse_tags(cls, tag_input: Union[str, List, None]) -> List[str]:
        """
        安全解析标签 - 支持多种输入格式
        
        Args:
            tag_input: 标签输入，可以是字符串、列表或None
            
        Returns:
            List[str]: 解析后的标签列表
        """
        if not tag_input:
            return []
        
        # 如果已经是列表，直接处理
        if isinstance(tag_input, list):
            return cls._normalize_tag_list(tag_input)
        
        # 如果是字符串，尝试解析
        if isinstance(tag_input, str):
            return cls._parse_tag_string(tag_input)
        
        # 其他类型尝试转换为字符串
        try:
            return cls._parse_tag_string(str(tag_input))
        except Exception as e:
            logger.warning(f"无法解析标签类型: {type(tag_input)}, 值: {tag_input}, 错误: {str(e)}")
            return []
    
    @classmethod
    def _parse_tag_string(cls, tag_string: str) -> List[str]:
        """解析标签字符串"""
        tag_string = tag_string.strip()
        if not tag_string:
            return []
        
        try:
            # 方法1：JSON数组格式 ["tag1", "tag2"]
            if tag_string.startswith('[') and tag_string.endswith(']'):
                try:
                    result = json.loads(tag_string)
                    if isinstance(result, list):
                        return cls._normalize_tag_list(result)
                except json.JSONDecodeError:
                    pass
            
            # 方法2：Python literal格式，使用ast.literal_eval (安全)
            try:
                result = ast.literal_eval(tag_string)
                if isinstance(result, list):
                    return cls._normalize_tag_list(result)
                elif isinstance(result, str):
                    return [result.strip()] if result.strip() else []
                elif isinstance(result, (int, float)):
                    return [str(result)]
            except (ValueError, SyntaxError):
                pass
            
            # 方法3：逗号分割格式 "tag1, tag2, tag3"
            if ',' in tag_string:
                tags = [tag.strip().strip("'\"[]") for tag in tag_string.split(',')]
                return [tag for tag in tags if tag]
            
            # 方法4：单个标签，去除可能的引号和方括号
            cleaned_tag = tag_string.strip("'\"[]")
            return [cleaned_tag] if cleaned_tag else []
            
        except Exception as e:
            logger.warning(f"解析标签字符串失败: {tag_string}, 错误: {str(e)}")
            return []
    
    @classmethod
    def _normalize_tag_list(cls, tag_list: List) -> List[str]:
        """规范化标签列表"""
        normalized = []
        for tag in tag_list:
            if tag is not None:
                tag_str = str(tag).strip()
                if tag_str:
                    normalized.append(tag_str)
        return normalized
    
    @classmethod
    def validate_energy_type_tags(cls, tags: List[str]) -> Dict[str, Any]:
        """
        验证能源类型标签
        
        Returns:
            Dict包含：valid_tags, invalid_tags, suggestions
        """
        valid_tags = []
        invalid_tags = []
        suggestions = []
        
        for tag in tags:
            if tag in cls.STANDARD_ENERGY_TYPES:
                valid_tags.append(tag)
            else:
                invalid_tags.append(tag)
                # 提供建议
                suggestion = cls._find_similar_tag(tag, cls.STANDARD_ENERGY_TYPES)
                if suggestion:
                    suggestions.append(f"{tag} -> {suggestion}")
        
        return {
            "valid_tags": valid_tags,
            "invalid_tags": invalid_tags,
            "suggestions": suggestions
        }
    
    @classmethod
    def _find_similar_tag(cls, tag: str, standard_tags: List[str]) -> Optional[str]:
        """查找相似的标准标签"""
        tag_lower = tag.lower()
        
        # 精确匹配
        for standard_tag in standard_tags:
            if tag_lower == standard_tag.lower():
                return standard_tag
        
        # 包含匹配
        for standard_tag in standard_tags:
            if tag_lower in standard_tag.lower() or standard_tag.lower() in tag_lower:
                return standard_tag
        
        return None
    
    @classmethod
    def normalize_tags_by_category(cls, tags: Dict[str, List[str]]) -> Dict[str, List[str]]:
        """
        按分类规范化标签
        
        Args:
            tags: 分类标签字典
            
        Returns:
            规范化后的标签字典
        """
        normalized = {}
        
        # 能源类型标签
        if "energy_type_tags" in tags:
            validation = cls.validate_energy_type_tags(tags["energy_type_tags"])
            normalized["energy_type_tags"] = validation["valid_tags"]
            if validation["invalid_tags"]:
                logger.warning(f"无效的能源类型标签: {validation['invalid_tags']}")
        
        # 其他标签类型直接规范化
        for category in ["basic_info_tags", "region_tags", "business_field_tags", 
                        "beneficiary_tags", "policy_measure_tags", "importance_tags"]:
            if category in tags:
                normalized[category] = cls._normalize_tag_list(tags[category])
        
        return normalized
    
    @classmethod
    def extract_tags_from_content(cls, title: str, content: str = "") -> Dict[str, List[str]]:
        """
        从文章标题和内容中提取标签
        
        Args:
            title: 文章标题
            content: 文章内容（可选）
            
        Returns:
            提取的标签字典
        """
        extracted_tags = {
            "basic_info_tags": [],
            "region_tags": [],
            "energy_type_tags": [],
            "business_field_tags": [],
            "beneficiary_tags": [],
            "policy_measure_tags": [],
            "importance_tags": []
        }
        
        text = f"{title} {content}".lower()
        
        # 基础信息标签提取
        if any(keyword in text for keyword in ["政策", "法规", "规定", "办法"]):
            extracted_tags["basic_info_tags"].append("政策法规")
        elif any(keyword in text for keyword in ["公告", "通知"]):
            if any(keyword in text for keyword in ["调价", "价格"]):
                extracted_tags["basic_info_tags"].append("调价公告")
            elif any(keyword in text for keyword in ["交易", "竞价", "拍卖"]):
                extracted_tags["basic_info_tags"].append("交易公告")
            else:
                extracted_tags["basic_info_tags"].append("行业资讯")
        else:
            extracted_tags["basic_info_tags"].append("行业资讯")
        
        # 能源类型标签提取
        for energy_type in cls.STANDARD_ENERGY_TYPES:
            # 特殊处理带括号的能源类型
            if "(" in energy_type:
                main_name = energy_type.split("(")[0]
                abbr = energy_type.split("(")[1].rstrip(")")
                if main_name.lower() in text or abbr.lower() in text:
                    extracted_tags["energy_type_tags"].append(energy_type)
            else:
                if energy_type.lower() in text:
                    extracted_tags["energy_type_tags"].append(energy_type)
        
        # 业务领域标签提取
        business_keywords = {
            "竞价交易": ["竞价", "拍卖", "交易"],
            "进口贸易": ["进口", "国外", "海外"],
            "企业动态": ["集团", "公司", "企业"],
            "系统运营": ["系统", "运营", "管网"],
            "储运": ["储存", "运输", "储运"],
            "销售": ["销售", "零售"]
        }
        
        for business_tag, keywords in business_keywords.items():
            if any(keyword in text for keyword in keywords):
                extracted_tags["business_field_tags"].append(business_tag)
        
        # 重要性标签提取
        if any(keyword in text for keyword in ["重要", "重大", "关键"]):
            extracted_tags["importance_tags"].append("重要")
        elif any(keyword in text for keyword in ["公告", "通知"]):
            extracted_tags["importance_tags"].append("一般")
        
        return extracted_tags
    
    @classmethod
    def get_tag_statistics(cls, tags_list: List[Dict[str, List[str]]]) -> Dict[str, Any]:
        """
        计算标签统计信息
        
        Args:
            tags_list: 标签字典列表
            
        Returns:
            统计信息字典
        """
        stats = {
            "total_documents": len(tags_list),
            "category_stats": {},
            "tag_frequency": {},
            "coverage_analysis": {}
        }
        
        category_names = [
            "basic_info_tags", "region_tags", "energy_type_tags",
            "business_field_tags", "beneficiary_tags", 
            "policy_measure_tags", "importance_tags"
        ]
        
        for category in category_names:
            category_tags = []
            document_count = 0
            
            for doc_tags in tags_list:
                if category in doc_tags and doc_tags[category]:
                    document_count += 1
                    category_tags.extend(doc_tags[category])
            
            # 统计该分类下的标签频率
            from collections import Counter
            tag_counter = Counter(category_tags)
            
            stats["category_stats"][category] = {
                "total_tags": len(category_tags),
                "unique_tags": len(tag_counter),
                "document_coverage": document_count / len(tags_list) * 100 if tags_list else 0,
                "top_tags": tag_counter.most_common(5)
            }
            
            stats["tag_frequency"][category] = dict(tag_counter)
        
        return stats 