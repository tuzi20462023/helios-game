from fastapi import FastAPI, HTTPException
from fastapi.responses import JSONResponse
from fastapi.middleware.cors import CORSMiddleware
import os
import uuid
from datetime import datetime
from typing import Dict, List, Any

# 导入我们的模型和服务
from models import (
    ChatRequest, ChatResponse, EchoRequest, EchoResponse, 
    SystemStatus, SuccessResponse, ErrorResponse,
    ConversationMemory, SceneContext
)
from ai_service import ai_service

app = FastAPI(
    title="Helios Agent Core", 
    version="0.2.0",
    description="Helios 游戏 AI 代理核心服务 - 本我之镜"
)

# 添加 CORS 中间件支持前端调用
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # 生产环境中应该限制具体域名
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# 模拟数据库 - 在真实项目中将连接到 Supabase
MOCK_CHARACTERS = {
    "bartender": {
        "id": "bartender",
        "name": "马库斯",
        "role": "酒馆老板",
        "core_motivation": "维护酒馆的繁荣，为客人提供温暖的避风港"
    },
    "guard": {
        "id": "guard",
        "name": "艾莉娜",
        "role": "城市卫兵",
        "core_motivation": "保护港口的秩序与安全，维护正义"
    },
    "thief": {
        "id": "thief", 
        "name": "影子",
        "role": "流浪盗贼",
        "core_motivation": "在城市阴影中生存，寻找获利机会"
    },
    "healer": {
        "id": "healer",
        "name": "塞拉菲娜",
        "role": "治疗师",
        "core_motivation": "用光明的力量治愈他人，传播希望"
    }
}

# 模拟信念系统存储
MOCK_BELIEFS = {}

# 默认场景上下文
DEFAULT_SCENE = {
    "scene_id": "port_tavern",
    "scene_name": "海港酒馆",
    "description": "这是一个位于繁忙港口的温馨酒馆，昏黄的灯光下，各色人物聚集于此。空气中弥漫着麦酒的香味和海风的咸腥。",
    "characters_present": ["bartender", "guard", "thief", "healer"],
    "environmental_factors": {
        "lighting": "昏黄温暖",
        "noise_level": "适中的交谈声",
        "crowd": "中等密度",
        "weather": "外面刮着海风"
    },
    "time_of_day": "夜晚",
    "atmosphere": "温馨而神秘"
}

@app.get("/")
async def root():
    return {
        "message": "Helios Agent Core is running", 
        "version": "0.2.0",
        "philosophy": "本我之镜 - 发现信念，映照内心"
    }

@app.get("/api/health")
async def health_check():
    return {"status": "healthy", "service": "helios-agent-core"}

@app.get("/api/status", response_model=SystemStatus)
async def get_system_status():
    """获取系统状态"""
    return SystemStatus(
        ai_service_available=ai_service.is_available(),
        memory_service_available=True,  # 本地开发模式下始终可用
        database_connected=True,  # 模拟数据库连接
        local_dev_mode=ai_service.local_dev_mode,
        active_sessions=len(ai_service.local_conversation_memory),
        total_conversations=sum(len(memories) for memories in ai_service.local_conversation_memory.values())
    )

@app.get("/api/characters")
async def get_characters():
    """获取所有可用的 NPC 角色"""
    return {
        "success": True,
        "characters": list(MOCK_CHARACTERS.values()),
        "scene": DEFAULT_SCENE
    }

@app.post("/api/chat", response_model=ChatResponse)
async def chat_with_npc(request: ChatRequest):
    """
    与 NPC 进行对话
    这是"本我之镜"的核心交互功能
    """
    try:
        # 验证 NPC 是否存在
        if request.npc_id not in MOCK_CHARACTERS:
            raise HTTPException(status_code=404, detail=f"NPC {request.npc_id} not found")
        
        npc_info = MOCK_CHARACTERS[request.npc_id]
        
        # 获取或创建会话记忆
        conversation_history = ai_service.get_conversation_memory(request.session_id, limit=10)
        
        # 获取 NPC 的信念系统
        npc_beliefs = MOCK_BELIEFS.get(request.npc_id, "")
        
        # 准备场景上下文
        scene_context = request.scene_context or DEFAULT_SCENE
        
        print(f"[Chat] {request.session_id}: 玩家 -> {npc_info['name']}: {request.user_message}")
        
        # 生成 NPC 响应
        npc_response = ai_service.generate_npc_response(
            npc_info=npc_info,
            npc_beliefs=npc_beliefs,
            conversation_history=conversation_history,
            user_message=request.user_message,
            scene_context=scene_context
        )
        
        # 保存对话到记忆系统
        # 保存玩家消息
        ai_service.save_conversation_memory(
            session_id=request.session_id,
            character="Player",
            message=request.user_message,
            role="user"
        )
        
        # 保存 NPC 响应
        ai_service.save_conversation_memory(
            session_id=request.session_id,
            character=npc_info["name"],
            message=npc_response["message"],
            role="assistant",
            metadata={
                "emotion": npc_response.get("emotion", "neutral"),
                "action": npc_response.get("action"),
                "npc_id": request.npc_id
            }
        )
        
        # TODO: 保存到 agent_logs 表（触发信念观察者）
        # 这里应该调用 Supabase 插入 agent_logs
        
        print(f"[Chat] {request.session_id}: {npc_info['name']} -> 玩家: {npc_response['message']}")
        
        return ChatResponse(
            success=True,
            message=npc_response["message"],
            emotion=npc_response.get("emotion", "neutral"),
            action=npc_response.get("action"),
            character_name=npc_info["name"]
        )
        
    except Exception as e:
        print(f"[Chat] 错误: {str(e)}")
        return ChatResponse(
            success=False,
            message="抱歉，我现在无法回应。请稍后再试。",
            emotion="困惑",
            action=None,
            character_name=MOCK_CHARACTERS.get(request.npc_id, {}).get("name", "Unknown"),
            error=str(e)
        )

@app.post("/api/echo", response_model=EchoResponse)
async def echo_chamber(request: EchoRequest):
    """
    回响之室 - 主观因果归因
    帮助玩家理解自己的行为背后的信念驱动
    """
    try:
        # 获取玩家的对话记忆
        conversation_history = ai_service.get_conversation_memory(request.session_id, limit=20)
        
        # 获取玩家的信念系统
        player_beliefs = MOCK_BELIEFS.get(request.player_id, "")
        
        # 筛选相关记忆
        relevant_memories = [
            memory for memory in conversation_history 
            if memory.get("character") == "Player"
        ][-5:]  # 最近 5 条玩家记忆
        
        print(f"[Echo] {request.session_id}: 玩家困惑: {request.confusion_text}")
        
        # 生成主观归因
        attribution_result = ai_service.generate_subjective_attribution(
            player_beliefs=player_beliefs,
            confusion_text=request.confusion_text,
            relevant_memories=relevant_memories
        )
        
        print(f"[Echo] {request.session_id}: 生成归因完成")
        
        return EchoResponse(
            success=True,
            subjective_attribution=attribution_result.get("subjective_attribution", ""),
            memory_evidence=attribution_result.get("memory_evidence", []),
            belief_insight=attribution_result.get("belief_insight", "")
        )
        
    except Exception as e:
        print(f"[Echo] 错误: {str(e)}")
        return EchoResponse(
            success=False,
            subjective_attribution="我感到困惑，但这种困惑本身就是成长的机会。",
            memory_evidence=["记忆检索遇到了困难"],
            belief_insight="每一次困惑都是自我认知的机会。",
            error=str(e)
        )

@app.get("/api/memory/{session_id}")
async def get_conversation_memory(session_id: str, limit: int = 20):
    """获取会话记忆"""
    try:
        memories = ai_service.get_conversation_memory(session_id, limit)
        return {
            "success": True,
            "session_id": session_id,
            "memories": memories,
            "count": len(memories)
        }
    except Exception as e:
        return {
            "success": False,
            "error": str(e)
        }

@app.post("/api/belief/analyze")
async def analyze_character_beliefs(character_id: str):
    """
    分析角色信念系统
    这将在实际项目中由 Supabase 触发器自动调用
    """
    try:
        # 模拟获取角色行为日志
        # 在真实项目中，这将从 agent_logs 表获取
        mock_logs = [
            {
                "timestamp": "2025-01-20T10:00:00",
                "action_type": "conversation",
                "input": "你好",
                "output": "欢迎来到我的酒馆！",
                "scene_id": "port_tavern"
            }
        ]
        
        # 调用信念分析
        belief_yaml = ai_service.analyze_belief_system(mock_logs)
        
        # 保存信念系统
        MOCK_BELIEFS[character_id] = belief_yaml
        
        print(f"[Belief] 为角色 {character_id} 生成信念系统")
        
        return {
            "success": True,
            "character_id": character_id,
            "belief_yaml": belief_yaml,
            "message": "信念系统分析完成"
        }
        
    except Exception as e:
        print(f"[Belief] 错误: {str(e)}")
        return {
            "success": False,
            "error": str(e)
        }

@app.delete("/api/memory/{session_id}")
async def clear_session_memory(session_id: str):
    """清除会话记忆（用于测试）"""
    if session_id in ai_service.local_conversation_memory:
        del ai_service.local_conversation_memory[session_id]
    
    return {
        "success": True,
        "message": f"会话 {session_id} 的记忆已清除"
    }

# 错误处理
@app.exception_handler(HTTPException)
async def http_exception_handler(request, exc):
    return JSONResponse(
        status_code=exc.status_code,
        content={
            "success": False,
            "error": exc.detail,
            "error_code": exc.status_code
        }
    )

@app.exception_handler(Exception)
async def general_exception_handler(request, exc):
    return JSONResponse(
        status_code=500,
        content={
            "success": False,
            "error": "Internal server error",
            "error_code": 500,
            "detail": str(exc)
        }
    )

if __name__ == "__main__":
    import uvicorn
    print("[Helios] 启动 AI 代理核心服务...")
    print(f"[Helios] 本地开发模式: {ai_service.local_dev_mode}")
    print(f"[Helios] AI 服务可用: {ai_service.is_available()}")
    uvicorn.run(app, host="0.0.0.0", port=8000)