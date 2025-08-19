#!/usr/bin/env python3
"""
Helios AI 对话系统测试脚本
用于验证 AI 服务和 API 端点的功能
"""

import requests
import json
import time
from typing import Dict, Any

API_BASE = "http://localhost:8000/api"

def test_system_status():
    """测试系统状态"""
    print("🔍 测试系统状态...")
    try:
        response = requests.get(f"{API_BASE}/status")
        data = response.json()
        
        print(f"✅ 系统状态: {response.status_code}")
        print(f"   AI 服务可用: {data['ai_service_available']}")
        print(f"   记忆服务可用: {data['memory_service_available']}")
        print(f"   本地开发模式: {data['local_dev_mode']}")
        return True
    except Exception as e:
        print(f"❌ 系统状态检查失败: {e}")
        return False

def test_get_characters():
    """测试获取角色列表"""
    print("\n🎭 测试角色列表...")
    try:
        response = requests.get(f"{API_BASE}/characters")
        data = response.json()
        
        if data['success']:
            print(f"✅ 获取到 {len(data['characters'])} 个角色:")
            for char in data['characters']:
                print(f"   - {char['name']} ({char['role']}): {char['core_motivation']}")
            return data['characters']
        else:
            print("❌ 获取角色失败")
            return []
    except Exception as e:
        print(f"❌ 角色列表获取失败: {e}")
        return []

def test_chat_conversation(characters: list):
    """测试对话功能"""
    if not characters:
        print("❌ 没有可用角色，跳过对话测试")
        return
    
    print("\n💬 测试 AI 对话...")
    
    # 选择第一个角色进行测试
    test_npc = characters[0]
    session_id = f"test_session_{int(time.time())}"
    
    # 测试对话序列
    test_messages = [
        "你好！",
        "这里是什么地方？",
        "你能告诉我一些关于这个港口的事情吗？",
        "谢谢你的帮助。"
    ]
    
    print(f"🎯 与 {test_npc['name']} ({test_npc['role']}) 对话:")
    
    for i, message in enumerate(test_messages, 1):
        print(f"\n第 {i} 轮对话:")
        print(f"🧑 玩家: {message}")
        
        try:
            response = requests.post(f"{API_BASE}/chat", json={
                "session_id": session_id,
                "npc_id": test_npc['id'],
                "user_message": message,
                "scene_context": None
            })
            
            data = response.json()
            
            if data['success']:
                print(f"🤖 {data['character_name']}: {data['message']}")
                if data.get('emotion') and data['emotion'] != 'neutral':
                    print(f"   😊 情绪: {data['emotion']}")
                if data.get('action'):
                    print(f"   🎬 动作: {data['action']}")
            else:
                print(f"❌ 对话失败: {data.get('error', '未知错误')}")
        
        except Exception as e:
            print(f"❌ 对话请求失败: {e}")
        
        # 短暂延迟
        time.sleep(1)
    
    return session_id

def test_memory_retrieval(session_id: str):
    """测试记忆检索"""
    if not session_id:
        print("❌ 没有有效的会话ID，跳过记忆测试")
        return
    
    print(f"\n🧠 测试记忆检索 (会话: {session_id})...")
    
    try:
        response = requests.get(f"{API_BASE}/memory/{session_id}")
        data = response.json()
        
        if data['success']:
            memories = data['memories']
            print(f"✅ 检索到 {len(memories)} 条记忆:")
            
            for i, memory in enumerate(memories, 1):
                print(f"   {i}. [{memory['character']}] {memory['message']}")
                if memory.get('emotion'):
                    print(f"      情绪: {memory['emotion']}")
        else:
            print(f"❌ 记忆检索失败: {data.get('error')}")
    
    except Exception as e:
        print(f"❌ 记忆检索请求失败: {e}")

def test_echo_chamber():
    """测试回响之室功能"""
    print("\n🪞 测试回响之室...")
    
    try:
        response = requests.post(f"{API_BASE}/echo", json={
            "session_id": "test_echo_session",
            "player_id": "test_player",
            "confusion_text": "我不确定为什么我会对这个陌生的地方感到既好奇又紧张。"
        })
        
        data = response.json()
        
        if data['success']:
            print("✅ 回响之室响应:")
            print(f"   🎯 主观归因: {data['subjective_attribution']}")
            print(f"   📝 记忆证据:")
            for evidence in data['memory_evidence']:
                print(f"      - {evidence}")
            print(f"   💡 信念洞察: {data['belief_insight']}")
        else:
            print(f"❌ 回响之室失败: {data.get('error')}")
    
    except Exception as e:
        print(f"❌ 回响之室请求失败: {e}")

def test_belief_analysis():
    """测试信念分析"""
    print("\n🧩 测试信念分析...")
    
    try:
        response = requests.post(f"{API_BASE}/belief/analyze?character_id=bartender")
        data = response.json()
        
        if data['success']:
            print("✅ 信念分析完成:")
            print(f"   角色ID: {data['character_id']}")
            print("   生成的信念系统:")
            # 格式化显示 YAML 内容
            belief_lines = data['belief_yaml'].split('\n')
            for line in belief_lines[:10]:  # 只显示前10行
                if line.strip():
                    print(f"      {line}")
            if len(belief_lines) > 10:
                print(f"      ... (还有 {len(belief_lines) - 10} 行)")
        else:
            print(f"❌ 信念分析失败: {data.get('error')}")
    
    except Exception as e:
        print(f"❌ 信念分析请求失败: {e}")

def main():
    """主测试函数"""
    print("🌟 Helios AI 对话系统测试开始")
    print("=" * 50)
    
    # 1. 测试系统状态
    if not test_system_status():
        print("\n❌ 系统状态检查失败，请确保后端服务正在运行")
        print("启动命令: cd packages/api && python main.py")
        return
    
    # 2. 测试角色列表
    characters = test_get_characters()
    
    # 3. 测试对话功能
    session_id = test_chat_conversation(characters)
    
    # 4. 测试记忆检索
    test_memory_retrieval(session_id)
    
    # 5. 测试回响之室
    test_echo_chamber()
    
    # 6. 测试信念分析
    test_belief_analysis()
    
    print("\n" + "=" * 50)
    print("🎉 测试完成！")
    print("\n💡 接下来你可以:")
    print("   1. 启动前端: npm run dev:web")
    print("   2. 访问: http://localhost:3000/chat")
    print("   3. 开始与 NPC 对话！")

if __name__ == "__main__":
    main() 