"""
上海石油天然气交易中心信息门户系统 - 数据清理脚本
移除重复的'文档类型'字段，统一使用'basic_info_tags'
"""

import json
import os

def remove_duplicate_document_type():
    """移除重复的文档类型字段，统一使用basic_info_tags"""
    
    # 输入和输出文件
    input_file = "上海石油天然气交易中心信息门户系统_完整数据集_51篇.json"
    output_file = "上海石油天然气交易中心信息门户系统_清理重复字段_51篇.json" 