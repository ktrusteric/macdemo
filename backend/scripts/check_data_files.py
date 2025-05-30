#!/usr/bin/env python3
"""
检查数据文件差异和状态
"""

import json
import os

def check_data_files():
    """检查各个数据文件的状态"""
    print("📊 检查数据文件状态...")
    
    # 检查规范化数据
    normalized_path = "scripts/信息发布文章与标签_规范化.json"
    if os.path.exists(normalized_path):
        try:
            with open(normalized_path, 'r', encoding='utf-8') as f:
                normalized_data = json.load(f)
            print(f"✅ 规范化数据: {len(normalized_data)} 篇文章")
            print(f"   第一篇: {normalized_data[0].get('标题', '未知')[:50]}...")
        except Exception as e:
            print(f"❌ 规范化数据读取失败: {e}")
    else:
        print("❌ 规范化数据文件不存在")
    
    # 检查简化测试数据
    simplified_path = "scripts/简化测试数据.json"
    if os.path.exists(simplified_path):
        try:
            with open(simplified_path, 'r', encoding='utf-8') as f:
                # 尝试读取，可能有格式错误
                content = f.read()
                # 检查是否有明显的JSON格式错误
                if '"重要性/影响力标签": "' in content and '"规范化地域标签":' in content:
                    print("⚠️  简化测试数据: 存在JSON格式错误")
                    print("   错误位置: '重要性/影响力标签' 字段缺少逗号")
                else:
                    simplified_data = json.loads(content)
                    print(f"✅ 简化测试数据: {len(simplified_data)} 篇文章")
        except Exception as e:
            print(f"❌ 简化测试数据读取失败: {e}")
    else:
        print("❌ 简化测试数据文件不存在")
    
    # 检查v2数据
    v2_path = "scripts/shpgx_content_v2_corrected.json"
    if os.path.exists(v2_path):
        try:
            with open(v2_path, 'r', encoding='utf-8') as f:
                v2_data = json.load(f)
            print(f"✅ v2版本数据: {len(v2_data)} 篇文章")
        except Exception as e:
            print(f"❌ v2数据读取失败: {e}")
    else:
        print("❌ v2数据文件不存在")

if __name__ == "__main__":
    check_data_files() 