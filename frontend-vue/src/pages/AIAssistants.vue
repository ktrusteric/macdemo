<template>
  <div class="ai-assistants-page">
    <!-- 页面头部 -->
    <div class="header-section">
      <h1 class="page-title">
        <el-icon class="title-icon"><ChatDotRound /></el-icon>
        AI 智能助手
      </h1>
      <p class="page-subtitle">专业的能源行业AI咨询服务，助力您的业务决策</p>
    </div>
    
    <!-- AI助手卡片区域 -->
    <div class="assistants-grid">
      <div 
        class="assistant-card" 
        v-for="(assistant, key) in assistants" 
        :key="key"
        :class="getCardClass(key)"
      >
        <!-- 卡片头部 - 始终可见 -->
        <div class="card-header">
          <div class="avatar-container">
            <div class="avatar-background" :style="getAvatarStyle(key)">
              <span class="avatar-emoji">{{ assistant.avatar }}</span>
            </div>
            <div class="status-indicator" :class="assistantStatus[key]">
              <div class="status-dot"></div>
            </div>
          </div>
          <div class="assistant-meta">
            <h3 class="assistant-title">{{ assistant.name }}</h3>
            <p class="assistant-desc">{{ assistant.description }}</p>
          </div>
        </div>

        <!-- 功能标签 - 始终可见 -->
        <div class="features-section">
          <div class="features-grid">
            <span 
              v-for="feature in assistant.features.slice(0, 3)" 
              :key="feature" 
              class="feature-pill"
            >
              {{ feature }}
            </span>
          </div>
        </div>

        <!-- 聊天区域 - 独立区域，状态只在这里显示 -->
        <div class="chat-container">
          <!-- AI聊天界面 - 连接成功时显示 -->
          <div 
            v-if="assistantStatus[key] === 'connected'"
            :id="`bot-container-${key}`" 
            class="chat-widget"
          ></div>
          
          <!-- 状态显示区域 - 未连接时显示，只在聊天容器内 -->
          <div v-else class="chat-status">
            <!-- 空闲状态 -->
            <div v-if="assistantStatus[key] === 'idle'" class="status-content idle">
              <div class="status-icon">
                <el-icon><ChatLineRound /></el-icon>
              </div>
              <p class="status-text">准备就绪</p>
              <el-button 
                type="primary" 
                size="large"
                @click="startChat(key)"
                class="action-button"
                :loading="assistantStatus[key] === 'loading'"
              >
                开始对话
              </el-button>
            </div>
            
            <!-- 加载状态 -->
            <div v-if="assistantStatus[key] === 'loading'" class="status-content loading">
              <div class="loading-animation">
                <div class="loading-dots">
                  <span></span>
                  <span></span>
                  <span></span>
                </div>
              </div>
              <p class="status-text">正在连接AI助手...</p>
            </div>
            
            <!-- 错误状态 -->
            <div v-if="assistantStatus[key] === 'error'" class="status-content error">
              <div class="status-icon">
                <el-icon><WarningFilled /></el-icon>
              </div>
              <p class="status-text">连接失败</p>
              <el-button 
                @click="startChat(key)" 
                size="default" 
                type="primary"
                plain
              >
                重新连接
              </el-button>
            </div>
          </div>
        </div>
      </div>
    </div>
  </div>
</template>

<script setup>
import { ref, onMounted, onUnmounted } from 'vue'
import { ChatDotRound, ChatLineRound, WarningFilled } from '@element-plus/icons-vue'
import { ElMessage } from 'element-plus'
import { aiChatService } from '@/api/ai-chat'

// AI助手配置
const assistants = ref({})
const assistantStatus = ref({
  customer_service: 'idle',
  news_assistant: 'idle', 
  trading_assistant: 'idle'
})

// 助手主题配色
const assistantThemes = {
  customer_service: {
    gradient: 'linear-gradient(135deg, #667eea 0%, #764ba2 100%)',
    color: '#667eea'
  },
  news_assistant: {
    gradient: 'linear-gradient(135deg, #f093fb 0%, #f5576c 100%)',
    color: '#f093fb'
  },
  trading_assistant: {
    gradient: 'linear-gradient(135deg, #4facfe 0%, #00f2fe 100%)',
    color: '#4facfe'
  }
}

// 获取卡片样式类
const getCardClass = (key) => {
  return `theme-${key}`
}

// 获取头像样式
const getAvatarStyle = (key) => {
  return {
    background: assistantThemes[key]?.gradient || assistantThemes.customer_service.gradient
  }
}

// 开始聊天 - 全新的简化实现
const startChat = async (assistantType) => {
  const assistant = assistants.value[assistantType]
  if (!assistant || !assistant.id || !assistant.token) {
    ElMessage.error('助手配置错误')
    return
  }

  // 防止重复点击
  if (assistantStatus.value[assistantType] === 'loading') {
    return
  }

  console.log(`🚀 启动${assistant.name}`)
  assistantStatus.value[assistantType] = 'loading'
  
  try {
    // 清理容器
    const containerId = `bot-container-${assistantType}`
    const container = document.getElementById(containerId)
    if (container) {
      container.innerHTML = ''
    }

    // 简单直接的方式加载机器人
    await loadBot(assistant, containerId)
    
    // 标记成功
    assistantStatus.value[assistantType] = 'connected'
    console.log(`✅ ${assistant.name} 连接成功`)
    
  } catch (error) {
    console.error(`❌ ${assistant.name} 连接失败:`, error)
    assistantStatus.value[assistantType] = 'error'
  }
}

// 加载机器人 - 最简单的实现
const loadBot = async (assistant, containerId) => {
  return new Promise((resolve, reject) => {
    // 机器人配置
    const config = {
      id: assistant.id,
      token: assistant.token,
      size: 'normal',
      theme: 'light', 
      host: 'https://ai.wiseocean.cn',
      container: containerId
    }

    // 如果SDK已存在，直接使用
    if (window.WiseBotInit) {
      console.log('🔄 使用现有SDK')
      setTimeout(() => {
        try {
          window.WiseBotInit(config)
          resolve()
        } catch (e) {
          reject(e)
        }
      }, 100)
      return
    }

    // 加载SDK
    console.log('📥 加载SDK')
    const script = document.createElement('script')
    script.src = 'https://ai.wiseocean.cn/bot/robot.js'
    
    script.onload = () => {
      console.log('✅ SDK加载完成')
      setTimeout(() => {
        try {
          if (window.WiseBotInit) {
            window.WiseBotInit(config)
            resolve()
          } else {
            reject(new Error('SDK未加载'))
          }
        } catch (e) {
          reject(e)
        }
      }, 200)
    }
    
    script.onerror = () => {
      reject(new Error('SDK加载失败'))
    }
    
    document.head.appendChild(script)
  })
}

// 加载助手配置
const loadAssistants = () => {
  // 直接使用默认配置，简化流程
  assistants.value = {
    customer_service: {
      id: '9714d9bc-31ca-40b5-a720-4329f5fc4af7',
      token: 'e0dc8833077b48669a04ad4a70a7ebe2',
      name: '客服助手',
      avatar: '🤖',
      description: '提供账户问题、功能咨询、技术支持、操作指导等服务',
      features: ['账户问题', '功能咨询', '技术支持']
    },
    news_assistant: {
      id: '158ab70e-2996-4cce-9822-6f8195a7cfa5',
      token: '9bc6008decb94efeaee65dd076aab5e8',
      name: '资讯助手',
      avatar: '📰',
      description: '提供市场快讯、政策解读、行业分析、趋势预测等信息',
      features: ['市场快讯', '政策解读', '行业分析']
    },
    trading_assistant: {
      id: '1e72acc1-43a8-4cda-8d54-f409c9c5d5ed',
      token: '18703d14357040c88f32ae5e4122c2d6',
      name: '交易助手',
      avatar: '💼',
      description: '提供策略建议、风险评估、交易分析、市场机会等服务',
      features: ['策略建议', '风险评估', '交易分析']
    }
  }
  console.log('✅ 助手配置加载完成')
}

onMounted(() => {
  loadAssistants()
})

onUnmounted(() => {
  // 简单清理
  Object.keys(assistantStatus.value).forEach(key => {
    const container = document.getElementById(`bot-container-${key}`)
    if (container) {
      container.innerHTML = ''
    }
  })
})
</script>

<style scoped>
.ai-assistants-page {
  min-height: 100vh;
  background: #f5f7fa;
  padding: 0;
  position: relative;
  overflow-x: hidden;
  max-width: 1280px;
  margin: 0 auto;
}

/* 页面头部 */
.header-section {
  text-align: center;
  margin-bottom: 32px;
  padding: 24px;
  background: white;
  border-radius: 16px;
  box-shadow: 0 4px 20px rgba(0,0,0,0.1);
}

.page-title {
  font-size: 32px;
  font-weight: bold;
  color: #1769aa;
  margin-bottom: 8px;
  display: flex;
  align-items: center;
  justify-content: center;
  gap: 12px;
}

.title-icon {
  font-size: 36px;
  color: #1890ff;
}

.page-subtitle {
  font-size: 16px;
  color: #666;
  margin: 0;
}

/* 助手网格 */
.assistants-grid {
  max-width: 100%;
  margin: 0 auto;
  padding: 0 20px 40px;
  display: grid;
  grid-template-columns: repeat(3, 1fr);
  gap: 20px;
  position: relative;
  z-index: 2;
}

/* 助手卡片 */
.assistant-card {
  background: white;
  border-radius: 16px;
  padding: 28px;
  box-shadow: 0 4px 12px rgba(0, 0, 0, 0.05);
  border: 1px solid #e1e8ed;
  height: 520px;
  display: flex;
  flex-direction: column;
  position: relative;
  transform: none !important;
  transition: none !important;
}

.assistant-card::before {
  content: '';
  position: absolute;
  top: 0;
  left: 0;
  right: 0;
  height: 4px;
  background: var(--card-gradient);
}

.assistant-card.theme-customer_service {
  --card-gradient: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
}

.assistant-card.theme-news_assistant {
  --card-gradient: linear-gradient(135deg, #f093fb 0%, #f5576c 100%);
}

.assistant-card.theme-trading_assistant {
  --card-gradient: linear-gradient(135deg, #4facfe 0%, #00f2fe 100%);
}

/* 卡片头部 - 始终可见，永不被遮盖 */
.card-header {
  display: flex;
  align-items: flex-start;
  gap: 20px;
  margin-bottom: 24px;
  flex-shrink: 0;
  position: relative;
  z-index: 20; /* 确保在最上层 */
}

.avatar-container {
  position: relative;
  flex-shrink: 0;
}

.avatar-background {
  width: 64px;
  height: 64px;
  border-radius: 12px;
  display: flex;
  align-items: center;
  justify-content: center;
  box-shadow: 0 2px 8px rgba(0, 0, 0, 0.1);
}

.avatar-emoji {
  font-size: 28px;
  line-height: 1;
}

.status-indicator {
  position: absolute;
  bottom: -2px;
  right: -2px;
  width: 18px;
  height: 18px;
  border-radius: 50%;
  background: white;
  display: flex;
  align-items: center;
  justify-content: center;
  box-shadow: 0 1px 4px rgba(0, 0, 0, 0.1);
  border: 2px solid white;
}

.status-dot {
  width: 8px;
  height: 8px;
  border-radius: 50%;
  background: #e0e0e0;
}

.status-indicator.connected .status-dot {
  background: #4CAF50;
}

.status-indicator.loading .status-dot {
  background: #FF9800;
  animation: pulse 1.5s infinite;
}

.status-indicator.error .status-dot {
  background: #f44336;
}

@keyframes pulse {
  0%, 100% { opacity: 1; }
  50% { opacity: 0.5; }
}

.assistant-meta {
  flex: 1;
  min-width: 0;
}

.assistant-title {
  font-size: 24px;
  font-weight: 700;
  margin: 0 0 8px 0;
  color: #1a1a1a;
}

.assistant-desc {
  font-size: 15px;
  color: #666;
  margin: 0;
  line-height: 1.5;
}

/* 功能标签 - 始终可见，永不被遮盖 */
.features-section {
  margin-bottom: 20px;
  flex-shrink: 0;
  position: relative;
  z-index: 20; /* 确保在最上层 */
}

.features-grid {
  display: flex;
  flex-wrap: wrap;
  gap: 8px;
}

.feature-pill {
  padding: 6px 12px;
  background: #f5f7fa;
  border-radius: 20px;
  font-size: 12px;
  color: #5a6c7d;
  font-weight: 500;
  border: 1px solid #e1e8ed;
  transition: all 0.2s ease;
}

.feature-pill:hover {
  background: #e3f2fd;
  border-color: #1976d2;
  color: #1976d2;
}

/* 聊天容器 - 独立区域 */
.chat-container {
  flex: 1;
  min-height: 240px;
  border-radius: 12px;
  background: #f8fafb;
  border: 1px solid #e1e8ed;
  position: relative;
  overflow: hidden;
}

/* AI聊天界面 */
.chat-widget {
  width: 100%;
  height: 100%;
  border-radius: 11px;
  background: white;
  position: static !important;
  transform: none !important;
  transition: none !important;
  left: auto !important;
  top: auto !important;
  right: auto !important;
  bottom: auto !important;
  margin: 0 !important;
  z-index: auto !important;
}

.chat-widget * {
  position: static !important;
  transform: none !important;
  transition: none !important;
}

/* 聊天状态显示 - 只在聊天容器内显示 */
.chat-status {
  width: 100%;
  height: 100%;
  display: flex;
  align-items: center;
  justify-content: center;
  background: #f8fafb;
  border-radius: 11px;
}

.status-content {
  text-align: center;
  padding: 20px;
}

.status-icon {
  font-size: 32px;
  color: #1976d2;
  margin-bottom: 12px;
}

.status-content.error .status-icon {
  color: #f44336;
}

.status-text {
  font-size: 16px;
  color: #5a6c7d;
  margin: 0 0 16px 0;
  font-weight: 500;
}

.action-button {
  border-radius: 12px;
  padding: 12px 24px;
  font-weight: 600;
  border: none;
  background: linear-gradient(135deg, #1976d2 0%, #1565c0 100%);
  box-shadow: 0 4px 12px rgba(25, 118, 210, 0.3);
}

.action-button:hover {
  transform: translateY(-2px);
  box-shadow: 0 6px 20px rgba(25, 118, 210, 0.4);
}

/* 加载动画 */
.loading-animation {
  margin-bottom: 16px;
}

.loading-dots {
  display: inline-flex;
  gap: 4px;
}

.loading-dots span {
  width: 8px;
  height: 8px;
  border-radius: 50%;
  background: #1976d2;
  animation: loading-bounce 1.4s infinite ease-in-out both;
}

.loading-dots span:nth-child(1) { animation-delay: -0.32s; }
.loading-dots span:nth-child(2) { animation-delay: -0.16s; }

@keyframes loading-bounce {
  0%, 80%, 100% { transform: scale(0); }
  40% { transform: scale(1); }
}

/* 响应式设计 */
@media (max-width: 1200px) {
  .assistants-grid {
    gap: 16px;
  }
  
  .assistant-card {
    padding: 24px;
    height: 480px;
  }
}

@media (max-width: 900px) {
  .assistants-grid {
    grid-template-columns: 1fr;
    max-width: 100%;
    gap: 20px;
  }
  
  .assistant-card {
    height: 420px;
  }
  
  .chat-container {
    min-height: 200px;
  }
}

@media (max-width: 768px) {
  .ai-assistants-page {
    padding: 0 16px;
  }
  
  .header-section {
    padding: 16px;
  }
  
  .page-title {
    font-size: 24px;
  }
  
  .title-icon {
    font-size: 28px;
  }
  
  .page-subtitle {
    font-size: 14px;
  }
  
  .assistants-grid {
    padding: 0 0 32px;
    gap: 16px;
  }
  
  .assistant-card {
    padding: 20px;
    height: 380px;
  }
  
  .card-header {
    gap: 12px;
    margin-bottom: 16px;
  }
  
  .avatar-background {
    width: 56px;
    height: 56px;
  }
  
  .avatar-emoji {
    font-size: 24px;
  }
  
  .assistant-title {
    font-size: 18px;
  }
  
  .features-section {
    margin-bottom: 16px;
  }
  
  .chat-container {
    min-height: 160px;
  }
}

/* 全局禁用机器人可能的悬停跟随效果 */
.ai-assistants-page iframe,
.ai-assistants-page [class*="bot"],
.ai-assistants-page [class*="chat"],
.ai-assistants-page [id*="wise"] {
  position: static !important;
  transform: none !important;
  left: auto !important;
  top: auto !important;
  pointer-events: auto !important;
}
</style> 