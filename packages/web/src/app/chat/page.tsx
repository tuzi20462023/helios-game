'use client'

import { useState, useEffect, useRef } from 'react'

interface Character {
  id: string
  name: string
  role: string
  core_motivation: string
}

interface Message {
  id: string
  character: string
  message: string
  role: 'user' | 'assistant'
  emotion?: string
  action?: string
  timestamp: string
}

interface ChatResponse {
  success: boolean
  message: string
  emotion: string
  action?: string
  character_name: string
  error?: string
}

export default function ChatPage() {
  const [characters, setCharacters] = useState<Character[]>([])
  const [selectedNpc, setSelectedNpc] = useState<string>('')
  const [messages, setMessages] = useState<Message[]>([])
  const [inputMessage, setInputMessage] = useState('')
  const [isLoading, setIsLoading] = useState(false)
  const [sessionId] = useState(`session_${Date.now()}`)
  const [systemStatus, setSystemStatus] = useState<any>(null)
  const messagesEndRef = useRef<HTMLDivElement>(null)

  const API_BASE = 'http://localhost:8000/api'

  useEffect(() => {
    loadCharacters()
    loadSystemStatus()
  }, [])

  useEffect(() => {
    scrollToBottom()
  }, [messages])

  const scrollToBottom = () => {
    messagesEndRef.current?.scrollIntoView({ behavior: 'smooth' })
  }

  const loadCharacters = async () => {
    try {
      const response = await fetch(`${API_BASE}/characters`)
      const data = await response.json()
      if (data.success) {
        setCharacters(data.characters)
        if (data.characters.length > 0) {
          setSelectedNpc(data.characters[0].id)
        }
      }
    } catch (error) {
      console.error('Failed to load characters:', error)
    }
  }

  const loadSystemStatus = async () => {
    try {
      const response = await fetch(`${API_BASE}/status`)
      const data = await response.json()
      setSystemStatus(data)
    } catch (error) {
      console.error('Failed to load system status:', error)
    }
  }

  const sendMessage = async () => {
    if (!inputMessage.trim() || !selectedNpc || isLoading) return

    const userMessage = inputMessage.trim()
    setInputMessage('')
    setIsLoading(true)

    // 添加用户消息到界面
    const userMsg: Message = {
      id: `user_${Date.now()}`,
      character: 'Player',
      message: userMessage,
      role: 'user',
      timestamp: new Date().toISOString()
    }
    setMessages(prev => [...prev, userMsg])

    try {
      const response = await fetch(`${API_BASE}/chat`, {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify({
          session_id: sessionId,
          npc_id: selectedNpc,
          user_message: userMessage,
          scene_context: null
        })
      })

      const data: ChatResponse = await response.json()

      // 添加 NPC 响应到界面
      const npcMsg: Message = {
        id: `npc_${Date.now()}`,
        character: data.character_name,
        message: data.message,
        role: 'assistant',
        emotion: data.emotion,
        action: data.action,
        timestamp: new Date().toISOString()
      }
      setMessages(prev => [...prev, npcMsg])

      if (!data.success && data.error) {
        console.error('Chat error:', data.error)
      }

    } catch (error) {
      console.error('Failed to send message:', error)
      // 添加错误消息
      const errorMsg: Message = {
        id: `error_${Date.now()}`,
        character: 'System',
        message: '抱歉，发生了网络错误。请检查后端服务是否正在运行。',
        role: 'assistant',
        emotion: 'error',
        timestamp: new Date().toISOString()
      }
      setMessages(prev => [...prev, errorMsg])
    } finally {
      setIsLoading(false)
    }
  }

  const clearConversation = async () => {
    try {
      await fetch(`${API_BASE}/memory/${sessionId}`, {
        method: 'DELETE'
      })
      setMessages([])
    } catch (error) {
      console.error('Failed to clear conversation:', error)
    }
  }

  const handleKeyPress = (e: React.KeyboardEvent) => {
    if (e.key === 'Enter' && !e.shiftKey) {
      e.preventDefault()
      sendMessage()
    }
  }

  const selectedCharacter = characters.find(c => c.id === selectedNpc)

  return (
    <main className="min-h-screen bg-gradient-to-br from-indigo-900 via-purple-900 to-pink-900 text-white">
      <div className="container mx-auto px-4 py-8">
        {/* 页面标题 */}
        <div className="text-center mb-8">
          <h1 className="text-4xl font-bold mb-4 bg-gradient-to-r from-yellow-400 via-pink-500 to-purple-600 bg-clip-text text-transparent">
            本我之镜 - AI 对话系统
          </h1>
          <p className="text-lg text-gray-300">
            与 NPC 对话，探索信念的涌现与映照
          </p>
        </div>

        {/* 系统状态 */}
        {systemStatus && (
          <div className="bg-white/10 backdrop-blur-sm rounded-lg p-4 mb-6">
            <h3 className="text-sm font-semibold mb-2 text-cyan-300">系统状态</h3>
            <div className="grid grid-cols-2 md:grid-cols-4 gap-4 text-xs">
              <div className={`flex items-center ${systemStatus.ai_service_available ? 'text-green-400' : 'text-red-400'}`}>
                <div className={`w-2 h-2 rounded-full mr-2 ${systemStatus.ai_service_available ? 'bg-green-400' : 'bg-red-400'}`}></div>
                AI 服务
              </div>
              <div className={`flex items-center ${systemStatus.memory_service_available ? 'text-green-400' : 'text-red-400'}`}>
                <div className={`w-2 h-2 rounded-full mr-2 ${systemStatus.memory_service_available ? 'bg-green-400' : 'bg-red-400'}`}></div>
                记忆服务
              </div>
              <div className="text-gray-400">
                活跃会话: {systemStatus.active_sessions}
              </div>
              <div className="text-gray-400">
                总对话数: {systemStatus.total_conversations}
              </div>
            </div>
          </div>
        )}

        <div className="grid grid-cols-1 lg:grid-cols-4 gap-6">
          {/* 角色选择面板 */}
          <div className="lg:col-span-1">
            <div className="bg-white/10 backdrop-blur-sm rounded-lg p-6">
              <h3 className="text-lg font-semibold mb-4 text-cyan-300">选择对话角色</h3>
              
              {characters.map((character) => (
                <div
                  key={character.id}
                  className={`p-4 rounded-lg mb-3 cursor-pointer transition-all ${
                    selectedNpc === character.id 
                      ? 'bg-cyan-500/30 border-2 border-cyan-400' 
                      : 'bg-white/5 hover:bg-white/10 border-2 border-transparent'
                  }`}
                  onClick={() => setSelectedNpc(character.id)}
                >
                  <h4 className="font-semibold text-white">{character.name}</h4>
                  <p className="text-sm text-gray-300 mb-2">{character.role}</p>
                  <p className="text-xs text-gray-400">{character.core_motivation}</p>
                </div>
              ))}

              {selectedCharacter && (
                <div className="mt-6 p-4 bg-gradient-to-r from-cyan-500/20 to-blue-500/20 rounded-lg">
                  <h4 className="font-semibold text-cyan-300 mb-2">当前对话角色</h4>
                  <p className="text-sm text-white">{selectedCharacter.name}</p>
                  <p className="text-xs text-gray-300">{selectedCharacter.role}</p>
                </div>
              )}

              <button
                onClick={clearConversation}
                className="w-full mt-4 px-4 py-2 bg-red-500/20 hover:bg-red-500/30 text-red-300 rounded-lg transition-colors text-sm"
              >
                清除对话记录
              </button>
            </div>
          </div>

          {/* 对话区域 */}
          <div className="lg:col-span-3">
            <div className="bg-white/10 backdrop-blur-sm rounded-lg h-[600px] flex flex-col">
              {/* 对话历史 */}
              <div className="flex-1 overflow-y-auto p-6 space-y-4">
                {messages.length === 0 ? (
                  <div className="text-center text-gray-400 mt-20">
                    <p className="text-lg mb-2">🎭 欢迎来到海港酒馆</p>
                    <p>选择一个角色开始对话吧！</p>
                  </div>
                ) : (
                  messages.map((message) => (
                    <div
                      key={message.id}
                      className={`flex ${message.role === 'user' ? 'justify-end' : 'justify-start'}`}
                    >
                      <div
                        className={`max-w-[80%] rounded-lg p-4 ${
                          message.role === 'user'
                            ? 'bg-cyan-500/30 text-white'
                            : message.character === 'System'
                            ? 'bg-red-500/20 text-red-300'
                            : 'bg-white/20 text-gray-100'
                        }`}
                      >
                        <div className="flex items-center justify-between mb-2">
                          <span className="text-sm font-semibold">
                            {message.character}
                          </span>
                          {message.emotion && message.emotion !== 'neutral' && (
                            <span className="text-xs text-gray-400 bg-white/10 px-2 py-1 rounded">
                              {message.emotion}
                            </span>
                          )}
                        </div>
                        <p className="text-sm leading-relaxed">{message.message}</p>
                        {message.action && (
                          <p className="text-xs text-gray-400 italic mt-2">
                            *{message.action}*
                          </p>
                        )}
                      </div>
                    </div>
                  ))
                )}
                <div ref={messagesEndRef} />
              </div>

              {/* 输入区域 */}
              <div className="border-t border-white/20 p-4">
                <div className="flex space-x-4">
                  <textarea
                    value={inputMessage}
                    onChange={(e) => setInputMessage(e.target.value)}
                    onKeyPress={handleKeyPress}
                    placeholder={selectedCharacter ? `与 ${selectedCharacter.name} 对话...` : '请先选择一个角色'}
                    className="flex-1 bg-white/10 border border-white/20 rounded-lg px-4 py-2 text-white placeholder-gray-400 focus:outline-none focus:border-cyan-400 resize-none"
                    rows={2}
                    disabled={!selectedNpc || isLoading}
                  />
                  <button
                    onClick={sendMessage}
                    disabled={!selectedNpc || !inputMessage.trim() || isLoading}
                    className="px-6 py-2 bg-cyan-500 hover:bg-cyan-600 disabled:bg-gray-600 disabled:cursor-not-allowed text-white rounded-lg transition-colors font-semibold"
                  >
                    {isLoading ? '发送中...' : '发送'}
                  </button>
                </div>
                <p className="text-xs text-gray-400 mt-2">
                  按 Enter 发送消息，Shift + Enter 换行
                </p>
              </div>
            </div>
          </div>
        </div>

        {/* 说明文档 */}
        <div className="mt-8 bg-white/5 backdrop-blur-sm rounded-lg p-6">
          <h3 className="text-lg font-semibold mb-4 text-yellow-300">💡 使用说明</h3>
          <div className="grid grid-cols-1 md:grid-cols-2 gap-6 text-sm text-gray-300">
            <div>
              <h4 className="font-semibold text-white mb-2">🎭 角色系统</h4>
              <ul className="space-y-1">
                <li>• 每个 NPC 都有独特的信念系统</li>
                <li>• 信念会根据对话动态演化</li>
                <li>• 选择不同角色体验不同的对话风格</li>
              </ul>
            </div>
            <div>
              <h4 className="font-semibold text-white mb-2">🧠 本我之镜</h4>
              <ul className="space-y-1">
                <li>• 对话会被记录并分析</li>
                <li>• 系统会"发现"而非"预设"角色信念</li>
                <li>• 每次对话都是信念的一次映照</li>
              </ul>
            </div>
          </div>
        </div>
      </div>
    </main>
  )
} 