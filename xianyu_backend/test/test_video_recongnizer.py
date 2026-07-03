#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
视频识别工作流测试脚本

测试视频信息的自动识别和处理功能
"""

import asyncio
import sys
import os
import ssl

# 跳过 SSL 证书验证（测试用）
ssl._create_default_https_context = ssl._create_unverified_context

# 添加项目根目录到Python路径
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from app.workflow.video_recongnizer import VideoRecongnizer
from test.test_data import test_data

test_text = test_data[4]

async def test_full_workflow():
    """测试完整的视频识别工作流"""
    print("\n=== 完整视频识别工作流测试 ===")
    
    try:
        print("\n1. 创建视频识别器...")
        recognizer = VideoRecongnizer()
        print(f"✅ 视频识别器创建成功")
        
        print("\n2. 准备测试视频文本...")
        # 使用 test_data 中的第一个测试用例
        video_text = test_text
        print(f"   视频文本长度: {len(video_text)} 字符")
        print(f"   视频标题: {video_text.split('名称：')[1].split('\n')[0].strip()}")
        
        print("\n3. 运行完整工作流...")
        print("   （这将调用实际的LLM API进行视频信息识别）")
        
        result = await recognizer.run(video_text=video_text)
        
        print("\n4. 工作流执行完成!")
        
        if result:
            print("\n✅ 完整工作流运行成功!")
            print(f"   返回结果: {result}")
            return True
        else:
            print("\n⚠️  工作流运行完成，但结果为空")
            return False
            
    except Exception as e:
        print(f"\n❌ 完整工作流运行失败: {str(e)}")
        import traceback
        traceback.print_exc()
        return False


async def test_single_baseinfo_workflow():
    """测试仅基础信息提取工作流"""
    print("\n=== 仅基础信息提取工作流测试 ===")
    
    try:
        print("\n1. 创建视频识别器（仅基础信息）...")
        recognizer = VideoRecongnizer(workflow_type="baseinfo")
        print(f"✅ 视频识别器创建成功")
        
        print("\n2. 准备测试视频文本...")
        # 使用 test_data 中的第二个测试用例
        video_text = test_text
        
        print(f"   视频文本长度: {len(video_text)} 字符")
        print(f"   视频标题: {video_text.split('名称：')[1].split('\n')[0].strip()}")
        
        print("\n3. 运行基础信息提取工作流...")
        print("   （这将调用实际的LLM API进行基础信息识别）")
        
        result = await recognizer.run(video_text=video_text)
        
        print("\n4. 工作流执行完成!")
        
        if result:
            print("\n✅ 基础信息提取工作流运行成功!")
            print(f"   返回结果: {result}")
            return True
        else:
            print("\n⚠️  工作流运行完成，但结果为空")
            return False
            
    except Exception as e:
        print(f"\n❌ 基础信息提取工作流运行失败: {str(e)}")
        import traceback
        traceback.print_exc()
        return False


async def test_single_searchinfo_workflow():
    """测试仅搜索信息提取工作流"""
    print("\n=== 仅搜索信息提取工作流测试 ===")
    
    try:
        print("\n1. 创建视频识别器（仅搜索信息）...")
        recognizer = VideoRecongnizer(workflow_type="searchinfo")
        print(f"✅ 视频识别器创建成功")
        
        print("\n2. 准备测试视频文本...")
        # 使用 test_data 中的第三个测试用例
        video_text = test_text
        print(f"   视频文本长度: {len(video_text)} 字符")
        print(f"   视频标题: {video_text.split('名称：')[1].split('\n')[0].strip()}")
        
        print("\n3. 运行搜索信息提取工作流...")
        print("   （这将调用实际的LLM API进行搜索信息识别）")
        
        result = await recognizer.run(video_text=video_text)
        
        print("\n4. 工作流执行完成!")
        
        if result:
            print("\n✅ 搜索信息提取工作流运行成功!")
            print(f"   返回结果: {result}")
            return True
        else:
            print("\n⚠️  工作流运行完成，但结果为空")
            return False
            
    except Exception as e:
        print(f"\n❌ 搜索信息提取工作流运行失败: {str(e)}")
        import traceback
        traceback.print_exc()
        return False


async def test_single_hotinfo_workflow():
    """测试仅热度信息提取工作流"""
    print("\n=== 仅热度信息提取工作流测试 ===")
    
    try:
        print("\n1. 创建视频识别器（仅热度信息）...")
        recognizer = VideoRecongnizer(workflow_type="hotinfo")
        print(f"✅ 视频识别器创建成功")
        
        print("\n2. 准备测试视频文本...")
        # 使用 test_data 中的第四个测试用例
        video_text = test_text
        print(f"   视频文本长度: {len(video_text)} 字符")
        print(f"   视频标题: {video_text.split('名称：')[1].split('\n')[0].strip()}")
        
        print("\n3. 运行热度信息提取工作流...")
        print("   （这将调用实际的LLM API进行热度信息识别）")
        
        result = await recognizer.run(video_text=video_text)
        
        print("\n4. 工作流执行完成!")
        
        if result:
            print("\n✅ 热度信息提取工作流运行成功!")
            print(f"   返回结果: {result}")
            return True
        else:
            print("\n⚠️  工作流运行完成，但结果为空")
            return False
            
    except Exception as e:
        print(f"\n❌ 热度信息提取工作流运行失败: {str(e)}")
        import traceback
        traceback.print_exc()
        return False


async def run_all_tests():
    """运行所有测试"""
    print("🎬 开始视频识别工作流测试...")
    print("=" * 50)
    
    try:
        # 运行所有测试
        tests = [
            #test_full_workflow,
            #test_single_baseinfo_workflow,
            #test_single_searchinfo_workflow,
            test_single_hotinfo_workflow
        ]
        
        passed = 0
        total = len(tests)
        
        for test_func in tests:
            print(f"\n{'='*50}")
            try:
                if await test_func():
                    passed += 1
                    print(f"✅ {test_func.__name__} 测试通过")
                else:
                    print(f"❌ {test_func.__name__} 测试失败")
            except Exception as e:
                print(f"💥 {test_func.__name__} 测试异常: {str(e)}")
        
        print("\n" + "=" * 50)
        print(f"🎯 测试结果: {passed}/{total} 通过")
        
        if passed == total:
            print("🎉 所有测试通过! 视频识别工作流功能正常")
            return True
        else:
            print("⚠️  部分测试失败，请检查相关功能")
            return False
            
    except Exception as e:
        print(f"\n💥 测试执行异常: {str(e)}")
        import traceback
        traceback.print_exc()
        return False


def main():
    """主测试函数"""
    try:
        success = asyncio.run(run_all_tests())
        return success
    except Exception as e:
        print(f"\n💥 测试执行异常: {str(e)}")
        import traceback
        traceback.print_exc()
        return False


if __name__ == "__main__":
    # 设置环境变量（实际API密钥，需要从.env文件中获取）
    print("⚠️  注意: 此测试将调用实际的LLM API")
    print("   请确保已配置正确的API密钥和网络连接")
    print("=" * 50)
    
    success = main()
    sys.exit(0 if success else 1)