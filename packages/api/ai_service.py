"""
Helios Game - AI服务接口
集成 Vercel AI Gateway、Zep 记忆系统等外部 AI 服务
专为"本我之镜"核心哲学设计的信念涌现系统
"""

import os
import json
import requests
from typing import Dict, List, Optional, Any
import yaml
from datetime import datetime
import hashlib
import random

class AIService:
    """AI 服务管理器 - 本我之镜核心"""
    
    def __init__(self):
        # Vercel AI Gateway 配置
        self.vercel_ai_token = os.getenv("VERCEL_AI_TOKEN")
        self.vercel_ai_url = os.getenv("VERCEL_AI_URL", "https://api.vercel.com/v1/ai/chat")
        
        # Zep 记忆系统配置
        self.zep_api_key = os.getenv("ZEP_API_KEY")
        self.zep_api_url = os.getenv("ZEP_API_URL", "https://api.getzep.com/api/v1")
        
        # 本地开发模式（无需 API Key 即可测试）
        self.local_dev_mode = os.getenv("LOCAL_DEV_MODE", "true").lower() == "true"
        
        # 本地对话记忆存储（仅用于本地开发）
        self.local_conversation_memory = {}
        
        print(f"[AIService] 初始化完成，本地开发模式: {self.local_dev_mode}")
    
    def is_available(self) -> bool:
        """检查 AI 服务是否可用"""
        if self.local_dev_mode:
            return True  # 本地模式始终可用
        return bool(self.vercel_ai_token)
    
    def call_llm(self, model: str, system_prompt: str, user_prompt: str, 
                 max_tokens: int = 2048, temperature: float = 0.7) -> Optional[str]:
        """
        调用 LLM 生成文本
        支持本地模拟和真实 API 调用
        """
        if self.local_dev_mode:
            return self._mock_llm_response(system_prompt, user_prompt)
        
        if not self.vercel_ai_token:
            print("[AIService] 警告: 未配置 Vercel AI Token，使用模拟响应")
            return self._mock_llm_response(system_prompt, user_prompt)
        
        try:
            headers = {
                "Authorization": f"Bearer {self.vercel_ai_token}",
                "Content-Type": "application/json"
            }
            
            # Vercel AI Gateway 格式
            payload = {
                "model": model,
                "messages": [
                    {"role": "system", "content": system_prompt},
                    {"role": "user", "content": user_prompt}
                ],
                "max_tokens": max_tokens,
                "temperature": temperature
            }
            
            response = requests.post(
                self.vercel_ai_url,
                headers=headers,
                json=payload,
                timeout=30
            )
            response.raise_for_status()
            
            result = response.json()
            if "choices" in result and len(result["choices"]) > 0:
                return result["choices"][0]["message"]["content"]
            else:
                print(f"[AIService] API 响应格式异常: {result}")
                return self._mock_llm_response(system_prompt, user_prompt)
                
        except Exception as e:
            print(f"[AIService] LLM 调用失败: {e}")
            return self._mock_llm_response(system_prompt, user_prompt)
    
    def _mock_llm_response(self, system_prompt: str, user_prompt: str) -> str:
        """模拟 LLM 响应（本地开发模式）"""
        # 根据 system prompt 的内容生成不同类型的模拟响应
        if "NPC" in system_prompt or "角色" in system_prompt:
            return self._mock_npc_response(user_prompt)
        elif "信念" in system_prompt or "belief" in system_prompt.lower():
            return self._mock_belief_analysis()
        elif "回响" in system_prompt or "echo" in system_prompt.lower():
            return self._mock_echo_response(user_prompt)
        else:
            return "这是一个模拟响应，用于本地开发测试。实际部署时将调用真实的 LLM API。"
    
    def _mock_npc_response(self, user_message: str) -> str:
        """模拟 NPC 对话响应 - 符合港口酒馆场景"""
        responses = [
            {
                "message": "这里是个繁忙的港口，总有新面孔出现。你看起来像是刚到这里的旅行者？",
                "emotion": "好奇",
                "action": "打量着新来者"
            },
            {
                "message": "酒馆里的消息传得很快，有什么你想了解的吗？",
                "emotion": "友善",
                "action": "擦拭酒杯"
            },
            {
                "message": "这座城市有它自己的规矩，新来的人最好小心一些。",
                "emotion": "警告",
                "action": "压低声音"
            },
            {
                "message": "我看过很多人来来去去，每个人都有自己的故事。",
                "emotion": "沉思",
                "action": "凝视远方"
            },
            {
                "message": "港口的夜晚总是充满未知，你最好找个安全的地方过夜。",
                "emotion": "关切",
                "action": "指向楼上的客房"
            }
        ]
        
        # 基于用户消息内容选择响应
        hash_value = int(hashlib.md5(user_message.encode()).hexdigest(), 16)
        selected_response = responses[hash_value % len(responses)]
        
        return json.dumps(selected_response, ensure_ascii=False)
    
    def _mock_belief_analysis(self) -> str:
        """模拟信念系统分析 - 符合本我之镜哲学"""
        return """worldview:
  port_life_understanding:
    description: "对港口生活有深刻理解，认为这里是各种人生故事交汇的地方"
    weight: 0.8
  social_dynamics_awareness:
    description: "敏锐察觉社交动态，善于从细节判断他人意图"
    weight: 0.7
  change_acceptance:
    description: "接受世界的变化无常，适应新环境和新面孔"
    weight: 0.6

selfview:
  experienced_observer:
    description: "自视为经验丰富的观察者，能够洞察他人的真实意图"
    weight: 0.9
  helpful_guide:
    description: "愿意为新来者提供指导和帮助"
    weight: 0.7
  cautious_survivor:
    description: "在复杂环境中保持谨慎，确保自身安全"
    weight: 0.8

values:
  survival: 0.9
  helpfulness: 0.7
  wisdom: 0.8
  social_connection: 0.6"""
    
    def _mock_echo_response(self, confusion_text: str) -> str:
        """模拟回响之室响应 - 主观因果归因"""
        return json.dumps({
            "subjective_attribution": f"面对'{confusion_text}'这样的情况，我内心的反应源于我对这个复杂世界的理解。我的谨慎来自于过往的经历，我的好奇心则驱使我想要了解更多。这种矛盾的感受正是我内在信念系统的体现。",
            "memory_evidence": [
                "记得初次来到港口时的不安和兴奋交织的心情",
                "曾经因为过于信任他人而遭受的挫折经历"
            ],
            "belief_insight": "我的行为反映出一种'谨慎的开放性' - 既渴望连接，又保持警惕。这是在不确定环境中生存的智慧。"
        }, ensure_ascii=False)

    # =============================================
    # Zep 记忆服务
    # =============================================
    
    def get_conversation_memory(self, session_id: str, limit: int = 20) -> List[Dict[str, Any]]:
        """获取对话记忆"""
        if self.local_dev_mode:
            return self._get_local_memory(session_id, limit)
        
        if not self.zep_api_key:
            print("[AIService] 警告: 未配置 Zep API Key，使用本地记忆")
            return self._get_local_memory(session_id, limit)
        
        try:
            headers = {
                "Authorization": f"Bearer {self.zep_api_key}",
                "Content-Type": "application/json"
            }
            
            response = requests.get(
                f"{self.zep_api_url}/sessions/{session_id}/memory",
                headers=headers,
                params={"limit": limit},
                timeout=10
            )
            
            if response.status_code == 200:
                data = response.json()
                # 转换 Zep 格式为我们的格式
                memories = []
                for msg in data.get("messages", []):
                    memories.append({
                        "timestamp": msg.get("created_at", datetime.now().isoformat()),
                        "character": msg.get("metadata", {}).get("character", "Unknown"),
                        "message": msg.get("content", ""),
                        "role": msg.get("role", "user"),
                        "emotion": msg.get("metadata", {}).get("emotion", "neutral"),
                        "action": msg.get("metadata", {}).get("action")
                    })
                return memories
            else:
                print(f"[AIService] Zep API 错误: {response.status_code}")
                return self._get_local_memory(session_id, limit)
                
        except Exception as e:
            print(f"[AIService] Zep 记忆获取失败: {e}")
            return self._get_local_memory(session_id, limit)
    
    def save_conversation_memory(self, session_id: str, character: str, message: str, 
                                role: str = "user", metadata: Optional[Dict] = None) -> bool:
        """保存对话记忆"""
        if self.local_dev_mode:
            return self._save_local_memory(session_id, character, message, role, metadata)
        
        if not self.zep_api_key:
            print("[AIService] 警告: 未配置 Zep API Key，使用本地记忆")
            return self._save_local_memory(session_id, character, message, role, metadata)
        
        try:
            headers = {
                "Authorization": f"Bearer {self.zep_api_key}",
                "Content-Type": "application/json"
            }
            
            payload = {
                "messages": [{
                    "role": role,
                    "content": message,
                    "metadata": {
                        "character": character,
                        **(metadata or {})
                    }
                }]
            }
            
            response = requests.post(
                f"{self.zep_api_url}/sessions/{session_id}/memory",
                headers=headers,
                json=payload,
                timeout=10
            )
            
            return response.status_code == 200
            
        except Exception as e:
            print(f"[AIService] Zep 记忆保存失败: {e}")
            return self._save_local_memory(session_id, character, message, role, metadata)
    
    def _get_local_memory(self, session_id: str, limit: int) -> List[Dict[str, Any]]:
        """获取本地记忆"""
        memories = self.local_conversation_memory.get(session_id, [])
        return memories[-limit:] if memories else []
    
    def _save_local_memory(self, session_id: str, character: str, message: str, 
                          role: str, metadata: Optional[Dict]) -> bool:
        """保存到本地记忆"""
        if session_id not in self.local_conversation_memory:
            self.local_conversation_memory[session_id] = []
        
        memory_entry = {
            "timestamp": datetime.now().isoformat(),
            "character": character,
            "message": message,
            "role": role,
            "emotion": metadata.get("emotion", "neutral") if metadata else "neutral",
            "action": metadata.get("action") if metadata else None
        }
        
        self.local_conversation_memory[session_id].append(memory_entry)
        
        # 保持最近 100 条记忆
        if len(self.local_conversation_memory[session_id]) > 100:
            self.local_conversation_memory[session_id] = self.local_conversation_memory[session_id][-100:]
        
        return True

    # =============================================
    # 专用 AI 功能 - 本我之镜核心
    # =============================================
    
    def generate_npc_response(self, npc_info: Dict[str, Any], npc_beliefs: str, 
                             conversation_history: List[Dict], user_message: str, 
                             scene_context: Dict[str, Any]) -> Dict[str, Any]:
        """
        生成 NPC 响应 - 基于信念系统的动态对话
        这是"本我之镜"的核心功能之一
        """
        npc_name = npc_info.get("name", "Unknown")
        npc_role = npc_info.get("role", "Unknown")
        npc_motivation = npc_info.get("core_motivation", "Unknown")
        
        # 构建符合"本我之镜"哲学的 system prompt
        system_prompt = f"""你是港口酒馆中的 {npc_name}，一个 {npc_role}。

角色核心信息：
- 姓名: {npc_name}
- 角色: {npc_role}
- 核心动机: {npc_motivation}

你的信念系统（这是你行为的内在驱动）：
{npc_beliefs if npc_beliefs else '你的信念正在通过行为逐渐显现，请根据你的角色设定自然表现'}

场景环境：
{json.dumps(scene_context, ensure_ascii=False, indent=2)}

重要原则：
1. 你的回复应该体现你的内在信念，而不是表面的角色扮演
2. 每次对话都是你信念系统的一次"映照"
3. 保持角色的一致性，但允许信念的微妙演化
4. 回复要自然、有深度，避免刻板的NPC对话

请以 JSON 格式回复，包含：
- message: 你的话语内容
- emotion: 当前情绪状态
- action: 伴随的动作或表情（可选）"""

        # 构建对话历史上下文
        history_context = "对话历史：\n"
        for msg in conversation_history[-5:]:  # 最近5轮对话
            speaker = msg.get("character", "Unknown")
            content = msg.get("message", "")
            if content:
                history_context += f"{speaker}: {content}\n"
        
        user_prompt = f"""{history_context}

玩家刚才说："{user_message}"

请以 {npc_name} 的身份，根据你的信念系统和当前情境回复："""

        response_text = self.call_llm(
            model="claude-3-sonnet",  # 使用 Claude 3 Sonnet
            system_prompt=system_prompt,
            user_prompt=user_prompt,
            temperature=0.8  # 稍高的温度保证回复的多样性
        )
        
        if not response_text:
            return self._fallback_npc_response(npc_name, npc_role)
        
        try:
            # 尝试解析 JSON 响应
            response_data = json.loads(response_text)
            
            # 确保必要字段存在
            if "message" not in response_data:
                response_data["message"] = response_text
            if "emotion" not in response_data:
                response_data["emotion"] = "neutral"
            
            return response_data
            
        except json.JSONDecodeError:
            # 如果不是 JSON，当作纯文本消息处理
            return {
                "message": response_text.strip(),
                "emotion": "neutral",
                "action": None
            }
    
    def _fallback_npc_response(self, npc_name: str, npc_role: str) -> Dict[str, Any]:
        """备用 NPC 响应"""
        fallback_responses = {
            "酒馆老板": "欢迎来到我的酒馆！需要什么帮助吗？",
            "城市卫兵": "这里的秩序由我维护，有什么问题吗？",
            "流浪盗贼": "*在阴影中观察着你*",
            "治疗师": "愿光明指引你的道路，朋友。"
        }
        
        message = fallback_responses.get(npc_role, f"我是 {npc_name}，很高兴见到你。")
        
        return {
            "message": message,
            "emotion": "neutral",
            "action": None
        }
    
    def analyze_belief_system(self, character_logs: List[Dict[str, Any]]) -> str:
        """
        分析角色行为并生成信念系统
        这是"信念观察者"的核心功能
        """
        if not character_logs:
            return "worldview: {}\nselfview: {}\nvalues: {}"
        
        system_prompt = """你是一个行为心理学专家，专门分析"本我之镜"游戏中角色的内在信念系统。

你的任务是根据角色的行为日志，分析其内在的信念驱动，并生成 YAML 格式的信念系统。

信念系统结构：
1. worldview: 世界观信念（对世界运作方式的认知和假设）
2. selfview: 自我认知信念（对自己能力、身份和价值的认知）  
3. values: 价值观权重（重要价值观及其权重 0.0-1.0）

每个信念项应包含：
- description: 信念的具体描述
- weight: 信念的强度权重（0.0-1.0）

重要原则：
- 信念应该从行为中"涌现"，而不是预设
- 关注行为背后的内在驱动和动机
- 信念可能存在矛盾和冲突，这是真实人性的体现
- 权重反映信念对行为的影响强度"""

        user_prompt = f"""请分析以下角色行为日志，生成其信念系统：

{json.dumps(character_logs, ensure_ascii=False, indent=2)}

请基于这些行为模式，生成角色的信念系统 YAML："""

        response = self.call_llm(
            model="claude-3-sonnet",
            system_prompt=system_prompt,
            user_prompt=user_prompt,
            temperature=0.3  # 较低温度确保分析的一致性
        )
        
        return response or self._mock_belief_analysis()
    
    def generate_subjective_attribution(self, player_beliefs: str, confusion_text: str, 
                                      relevant_memories: List[Dict]) -> Dict[str, Any]:
        """
        生成主观因果归因（回响之室）
        这是"本我之镜"的核心体验功能
        """
        system_prompt = f"""你是"回响之室"的引导者，帮助玩家理解他们行为背后的信念驱动。

玩家的信念系统：
{player_beliefs}

你的任务是基于玩家的信念系统，为其困惑提供主观的、第一人称的因果归因。
这不是客观分析，而是从玩家信念角度的自我解释和洞察。

回复要求：
1. 使用第一人称（"我"），让玩家感受到这是自己内心的声音
2. 基于玩家的信念系统进行归因，而非通用心理分析
3. 提供具体的记忆证据支持
4. 帮助玩家"看见"自己的信念如何影响行为

请以 JSON 格式回复，包含：
- subjective_attribution: 主观因果解释（第一人称）
- memory_evidence: 1-2个支持性"记忆证据"
- belief_insight: 关于信念系统的深层洞察"""

        user_prompt = f"""玩家的困惑："{confusion_text}"

相关记忆：
{json.dumps(relevant_memories, ensure_ascii=False, indent=2)}

请生成主观归因："""

        response = self.call_llm(
            model="claude-3-sonnet", 
            system_prompt=system_prompt,
            user_prompt=user_prompt,
            temperature=0.6
        )
        
        try:
            return json.loads(response) if response else {}
        except json.JSONDecodeError:
            return {
                "subjective_attribution": response or "我感到困惑，但这种困惑本身就是我内在信念系统的体现。",
                "memory_evidence": ["记忆证据生成中..."],
                "belief_insight": "每一次困惑都是自我认知的机会。"
            }


# 全局 AI 服务实例
ai_service = AIService() 