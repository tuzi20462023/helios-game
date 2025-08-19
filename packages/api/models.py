"""
Helios Game - API 数据模型
定义所有 API 请求和响应的数据结构
"""

from pydantic import BaseModel, Field
from typing import Dict, List, Optional, Any
from datetime import datetime

# =============================================
# 基础数据模型
# =============================================

class Character(BaseModel):
    """角色基础信息"""
    id: str = Field(..., description="角色唯一标识")
    name: str = Field(..., description="角色姓名")
    role: str = Field(..., description="角色职业/身份")
    core_motivation: str = Field(..., description="核心动机")
    is_player: bool = Field(default=False, description="是否为玩家角色")

class BeliefSystem(BaseModel):
    """信念系统"""
    character_id: str = Field(..., description="角色ID")
    belief_yaml: str = Field(..., description="YAML格式的信念系统")
    last_updated: datetime = Field(default_factory=datetime.now, description="最后更新时间")

class AgentLog(BaseModel):
    """代理日志"""
    id: Optional[str] = Field(None, description="日志ID")
    timestamp: datetime = Field(default_factory=datetime.now, description="时间戳")
    character_id: str = Field(..., description="角色ID")
    scene_id: str = Field(..., description="场景ID")
    action_type: str = Field(..., description="行动类型")
    input: str = Field(..., description="输入内容")
    output: str = Field(..., description="输出内容")
    belief_snapshot: Optional[str] = Field(None, description="信念快照")

# =============================================
# 对话相关模型
# =============================================

class ChatRequest(BaseModel):
    """聊天请求"""
    session_id: str = Field(..., description="会话ID")
    npc_id: str = Field(..., description="NPC角色ID")
    user_message: str = Field(..., description="用户消息")
    scene_context: Optional[Dict[str, Any]] = Field(default={}, description="场景上下文")

class ChatResponse(BaseModel):
    """聊天响应"""
    success: bool = Field(..., description="请求是否成功")
    message: str = Field(..., description="NPC回复内容")
    emotion: str = Field(..., description="NPC情绪状态")
    action: Optional[str] = Field(None, description="NPC动作描述")
    character_name: str = Field(..., description="NPC角色名")
    timestamp: datetime = Field(default_factory=datetime.now, description="响应时间")
    error: Optional[str] = Field(None, description="错误信息")

class ConversationMemory(BaseModel):
    """对话记忆"""
    timestamp: datetime = Field(..., description="时间戳")
    character: str = Field(..., description="说话角色")
    message: str = Field(..., description="消息内容")
    role: str = Field(..., description="角色类型：user/assistant")
    emotion: str = Field(default="neutral", description="情绪状态")
    action: Optional[str] = Field(None, description="动作描述")

# =============================================
# 信念系统相关模型
# =============================================

class BeliefAnalysisRequest(BaseModel):
    """信念分析请求"""
    character_id: str = Field(..., description="角色ID")
    behavior_logs: List[Dict[str, Any]] = Field(..., description="行为日志")

class BeliefAnalysisResponse(BaseModel):
    """信念分析响应"""
    success: bool = Field(..., description="分析是否成功")
    belief_yaml: str = Field(..., description="生成的信念系统YAML")
    character_id: str = Field(..., description="角色ID")
    analysis_timestamp: datetime = Field(default_factory=datetime.now, description="分析时间")
    error: Optional[str] = Field(None, description="错误信息")

# =============================================
# 回响之室相关模型
# =============================================

class EchoRequest(BaseModel):
    """回响之室请求"""
    session_id: str = Field(..., description="会话ID")
    player_id: str = Field(..., description="玩家ID")
    confusion_text: str = Field(..., description="困惑描述")

class EchoResponse(BaseModel):
    """回响之室响应"""
    success: bool = Field(..., description="请求是否成功")
    subjective_attribution: str = Field(..., description="主观因果归因")
    memory_evidence: List[str] = Field(..., description="记忆证据")
    belief_insight: str = Field(..., description="信念洞察")
    timestamp: datetime = Field(default_factory=datetime.now, description="响应时间")
    error: Optional[str] = Field(None, description="错误信息")

# =============================================
# 场景和游戏状态模型
# =============================================

class SceneContext(BaseModel):
    """场景上下文"""
    scene_id: str = Field(..., description="场景ID")
    scene_name: str = Field(..., description="场景名称")
    description: str = Field(..., description="场景描述")
    characters_present: List[str] = Field(default=[], description="在场角色列表")
    environmental_factors: Dict[str, Any] = Field(default={}, description="环境因素")
    time_of_day: str = Field(default="evening", description="时间")
    atmosphere: str = Field(default="neutral", description="氛围")

class GameState(BaseModel):
    """游戏状态"""
    session_id: str = Field(..., description="会话ID")
    active_scene: SceneContext = Field(..., description="当前场景")
    player_character: Character = Field(..., description="玩家角色")
    npc_characters: List[Character] = Field(default=[], description="NPC角色列表")
    conversation_turn: int = Field(default=0, description="对话轮次")

# =============================================
# 通用响应模型
# =============================================

class SuccessResponse(BaseModel):
    """成功响应"""
    success: bool = Field(True, description="操作成功")
    message: str = Field(..., description="响应消息")
    data: Optional[Dict[str, Any]] = Field(None, description="响应数据")
    timestamp: datetime = Field(default_factory=datetime.now, description="响应时间")

class ErrorResponse(BaseModel):
    """错误响应"""
    success: bool = Field(False, description="操作失败")
    error: str = Field(..., description="错误信息")
    error_code: Optional[str] = Field(None, description="错误代码")
    timestamp: datetime = Field(default_factory=datetime.now, description="错误时间")

# =============================================
# 系统状态模型
# =============================================

class SystemStatus(BaseModel):
    """系统状态"""
    ai_service_available: bool = Field(..., description="AI服务是否可用")
    memory_service_available: bool = Field(..., description="记忆服务是否可用")
    database_connected: bool = Field(..., description="数据库是否连接")
    local_dev_mode: bool = Field(..., description="是否为本地开发模式")
    active_sessions: int = Field(default=0, description="活跃会话数")
    total_conversations: int = Field(default=0, description="总对话数")

# =============================================
# 批量操作模型
# =============================================

class BatchChatRequest(BaseModel):
    """批量聊天请求"""
    session_id: str = Field(..., description="会话ID")
    interactions: List[Dict[str, Any]] = Field(..., description="交互列表")
    scene_context: Optional[SceneContext] = Field(None, description="场景上下文")

class BatchChatResponse(BaseModel):
    """批量聊天响应"""
    success: bool = Field(..., description="批量操作是否成功")
    results: List[ChatResponse] = Field(..., description="各个响应结果")
    total_processed: int = Field(..., description="处理总数")
    failed_count: int = Field(default=0, description="失败数量")
    timestamp: datetime = Field(default_factory=datetime.now, description="响应时间")

# =============================================
# 导出所有模型
# =============================================

__all__ = [
    # 基础模型
    "Character", "BeliefSystem", "AgentLog",
    # 对话模型
    "ChatRequest", "ChatResponse", "ConversationMemory",
    # 信念系统模型
    "BeliefAnalysisRequest", "BeliefAnalysisResponse",
    # 回响之室模型
    "EchoRequest", "EchoResponse",
    # 场景模型
    "SceneContext", "GameState",
    # 通用响应模型
    "SuccessResponse", "ErrorResponse",
    # 系统状态模型
    "SystemStatus",
    # 批量操作模型
    "BatchChatRequest", "BatchChatResponse"
] 