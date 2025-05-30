#!/usr/bin/env python3
"""
能源信息服务数据处理工具集
提供完整的数据处理流程，从规范化到导入系统
"""

import asyncio
import os
import sys
import subprocess
from pathlib import Path

def print_banner(title: str):
    """打印工具横幅"""
    print("\n" + "="*60)
    print(f"  🔧 {title}")
    print("="*60)

def print_step(step: int, description: str):
    """打印步骤"""
    print(f"\n📋 步骤 {step}: {description}")
    print("-" * 40)

async def run_energy_data_pipeline():
    """运行完整的能源数据处理流程"""
    
    print_banner("能源信息服务系统 - 数据处理工具集")
    
    print("🎯 本工具将执行以下流程：")
    print("   1. 规范化能源品种标签")
    print("   2. 简化测试数据")
    print("   3. 导入数据到系统")
    print("   4. 显示数据统计报告")
    
    # 检查文件存在性
    scripts_dir = Path(__file__).parent
    required_files = [
        "信息发布文章与标签.json",
        "normalize_energy_tags.py",
        "simplify_test_data.py", 
        "import_sample_data.py"
    ]
    
    missing_files = []
    for file in required_files:
        if not (scripts_dir / file).exists():
            missing_files.append(file)
    
    if missing_files:
        print(f"\n❌ 缺少必要文件: {', '.join(missing_files)}")
        return
    
    try:
        # 步骤1: 规范化能源标签
        print_step(1, "规范化能源品种标签")
        result = subprocess.run([
            sys.executable, "normalize_energy_tags.py"
        ], capture_output=True, text=True, cwd=scripts_dir)
        
        if result.returncode != 0:
            print(f"❌ 规范化失败: {result.stderr}")
            return
            
        print("✅ 能源标签规范化完成")
        
        # 步骤2: 简化测试数据
        print_step(2, "简化测试数据")
        result = subprocess.run([
            sys.executable, "simplify_test_data.py"
        ], capture_output=True, text=True, cwd=scripts_dir)
        
        if result.returncode != 0:
            print(f"❌ 数据简化失败: {result.stderr}")
            return
            
        print("✅ 测试数据简化完成")
        
        # 步骤3: 导入数据
        print_step(3, "导入数据到系统")
        
        # 导入文章数据
        from import_sample_data import import_articles, create_sample_users
        await import_articles(use_simplified=True)
        
        # 创建示例用户
        await create_sample_users()
        
        print("✅ 数据导入完成")
        
        # 步骤4: 显示完成报告
        print_step(4, "处理完成报告")
        
        print("🎉 数据处理流程全部完成！")
        print("\n📊 处理结果：")
        print("   ✅ 原始数据已规范化")
        print("   ✅ 能源类型标签标准化")
        print("   ✅ 测试数据已简化（每篇3-5个标签）")
        print("   ✅ 数据已导入MongoDB")
        print("   ✅ 示例用户已创建")
        
        print("\n🚀 下一步操作建议：")
        print("   1. 启动后端服务：cd ../.. && python -m uvicorn app.main:app --reload")
        print("   2. 启动前端服务：cd ../../frontend-vue && npm run dev")
        print("   3. 访问系统进行测试推荐效果")
        
        print("\n🔍 重点验证功能：")
        print("   • 地域和能源类型标签的推荐权重")
        print("   • LNG vs PNG vs 天然气的精确区分")
        print("   • Dashboard页面的文章链接功能")
        
    except Exception as e:
        print(f"\n❌ 处理过程中出错: {str(e)}")
        print("\n🔧 故障排除建议：")
        print("   1. 检查MongoDB服务是否启动")
        print("   2. 检查Python依赖是否安装完整")
        print("   3. 检查数据文件格式是否正确")

def show_individual_tools():
    """显示单独工具选项"""
    print_banner("单独工具选项")
    
    print("可用的单独工具：")
    print("  1. normalize  - 仅运行能源标签规范化")
    print("  2. simplify   - 仅运行数据简化")
    print("  3. import     - 仅运行数据导入")
    print("  4. full       - 运行完整流程（默认）")
    print("\n使用方法：")
    print("  python energy_data_toolkit.py [工具名]")
    print("  python energy_data_toolkit.py normalize")

async def run_single_tool(tool_name: str):
    """运行单独工具"""
    scripts_dir = Path(__file__).parent
    
    if tool_name == "normalize":
        print_banner("能源标签规范化")
        result = subprocess.run([
            sys.executable, "normalize_energy_tags.py"
        ], cwd=scripts_dir)
        return result.returncode == 0
        
    elif tool_name == "simplify":
        print_banner("数据简化")
        result = subprocess.run([
            sys.executable, "simplify_test_data.py"
        ], cwd=scripts_dir)
        return result.returncode == 0
        
    elif tool_name == "import":
        print_banner("数据导入")
        from import_sample_data import import_articles, create_sample_users
        await import_articles(use_simplified=True)
        await create_sample_users()
        return True
        
    else:
        print(f"❌ 未知工具: {tool_name}")
        show_individual_tools()
        return False

def main():
    """主函数"""
    if len(sys.argv) > 1:
        tool_name = sys.argv[1].lower()
        if tool_name in ["help", "-h", "--help"]:
            show_individual_tools()
            return
        elif tool_name == "full":
            asyncio.run(run_energy_data_pipeline())
        else:
            success = asyncio.run(run_single_tool(tool_name))
            if success:
                print("\n✅ 工具执行完成")
            else:
                print("\n❌ 工具执行失败")
    else:
        # 默认运行完整流程
        asyncio.run(run_energy_data_pipeline())

if __name__ == "__main__":
    main() 