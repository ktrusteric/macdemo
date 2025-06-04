<template>
  <!-- 遮罩层 -->
  <div v-if="showOverlay" class="ai-float-overlay" @click="handleOverlayClick"></div>

  <!-- 悬浮按钮 -->
  <div 
    v-if="!currentChatVisible && !selectorVisible"
    class="ai-float-button"
    @click="toggleSelector"
    :class="{ 'bounce': shouldBounce }"
    title="点击打开AI助手"
  >
    <div class="float-icon">
      <svg width="28" height="28" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
        <path d="m3 21 1.9-5.7a8.5 8.5 0 1 1 3.8 3.8z"></path>
      </svg>
    </div>
    <div class="float-text">AI助手</div>
    <div class="notification-dot" v-if="hasNewNotification"></div>
  </div>

  <!-- 助手选择器 -->
  <AIAssistantSelector
    :visible="selectorVisible"
    :assistants="assistants"
    @select="handleAssistantSelect"
    @close="closeSelectorAction"
  />

  <!-- 聊天窗口 -->
  <AIChatWindow
    v-if="currentAssistant"
    :visible="currentChatVisible"
    :assistant="currentAssistant"
    :assistant-type="currentAssistantType!"
    @close="closeChatAction"
    @minimize="minimizeChatAction"
  />

  <!-- 最小化状态栏 -->
  <div 
    v-if="isChatMinimized && currentAssistant" 
    class="minimized-chat-bar"
    @click="restoreChat"
  >
    <div class="minimized-info">
      <span class="minimized-avatar">{{ currentAssistant.avatar }}</span>
      <span class="minimized-name">{{ currentAssistant.name }}</span>
    </div>
    <div class="minimized-actions">
      <button @click.stop="restoreChat" class="restore-btn" title="恢复">
        <svg width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
          <polyline points="15,3 21,3 21,9"></polyline>
          <polyline points="9,21 3,21 3,15"></polyline>
          <line x1="21" y1="3" x2="14" y2="10"></line>
          <line x1="3" y1="21" x2="10" y2="14"></line>
        </svg>
      </button>
      <button @click.stop="closeChatAction" class="close-min-btn" title="关闭">
        <svg width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
          <line x1="18" y1="6" x2="6" y2="18"></line>
          <line x1="6" y1="6" x2="18" y2="18"></line>
        </svg>
      </button>
    </div>
  </div>
</template>

<script setup lang="ts">
import { ref, computed, onMounted, onUnmounted } from 'vue';
import AIAssistantSelector from './AIAssistantSelector.vue';
import AIChatWindow from './AIChatWindow.vue';
import type { AIAssistantConfig, AIAssistant, AssistantType } from '../types/ai-chat';
import { aiChatService } from '../api/ai-chat';

// 响应式状态
const assistants = ref<AIAssistantConfig>({} as AIAssistantConfig);
const selectorVisible = ref(false);
const currentChatVisible = ref(false);
const isChatMinimized = ref(false);
const currentAssistant = ref<AIAssistant | null>(null);
const currentAssistantType = ref<AssistantType | null>(null);
const hasNewNotification = ref(false);
const shouldBounce = ref(false);

// 计算属性
const showOverlay = computed(() => selectorVisible.value || currentChatVisible.value);

// 初始化
onMounted(async () => {
  console.log('🚀 AI助手组件开始初始化...');
  try {
    console.log('📡 正在加载AI助手配置...');
    assistants.value = await aiChatService.getAssistants();
    console.log('✅ AI助手配置加载成功:', assistants.value);
    
    // 添加入场动画效果
    setTimeout(() => {
      shouldBounce.value = true;
      console.log('🎯 触发弹跳动画');
      setTimeout(() => {
        shouldBounce.value = false;
      }, 1000);
    }, 500);
    
    // 定时显示通知点（示例）
    setTimeout(() => {
      hasNewNotification.value = true;
      console.log('🔔 显示通知点');
    }, 3000);
    
  } catch (error) {
    console.error('❌ 加载AI助手配置失败:', error);
  }
});

// 页面卸载时清理
onUnmounted(() => {
  // 清理定时器等
});

// 切换选择器显示
const toggleSelector = () => {
  if (isChatMinimized.value) {
    restoreChat();
  } else {
    selectorVisible.value = !selectorVisible.value;
    hasNewNotification.value = false;
  }
};

// 处理遮罩层点击
const handleOverlayClick = () => {
  if (selectorVisible.value) {
    closeSelectorAction();
  }
  // 注意：不在这里关闭聊天窗口，因为聊天窗口有自己的关闭逻辑
};

// 处理助手选择
const handleAssistantSelect = (assistantType: AssistantType, assistant: AIAssistant) => {
  currentAssistantType.value = assistantType;
  currentAssistant.value = assistant;
  selectorVisible.value = false;
  currentChatVisible.value = true;
  isChatMinimized.value = false;
};

// 关闭选择器
const closeSelectorAction = () => {
  selectorVisible.value = false;
};

// 关闭聊天
const closeChatAction = () => {
  currentChatVisible.value = false;
  isChatMinimized.value = false;
  currentAssistant.value = null;
  currentAssistantType.value = null;
};

// 最小化聊天
const minimizeChatAction = () => {
  currentChatVisible.value = false;
  isChatMinimized.value = true;
};

// 恢复聊天
const restoreChat = () => {
  if (currentAssistant.value) {
    currentChatVisible.value = true;
    isChatMinimized.value = false;
  }
};

// 键盘快捷键支持
const handleKeyPress = (event: KeyboardEvent) => {
  // ESC 键关闭弹窗
  if (event.key === 'Escape') {
    if (selectorVisible.value) {
      closeSelectorAction();
    } else if (currentChatVisible.value) {
      minimizeChatAction();
    }
  }
  
  // Ctrl + K 快速打开AI助手
  if (event.ctrlKey && event.key === 'k') {
    event.preventDefault();
    toggleSelector();
  }
};

onMounted(() => {
  window.addEventListener('keydown', handleKeyPress);
});

onUnmounted(() => {
  window.removeEventListener('keydown', handleKeyPress);
});
</script>

<style scoped>
.ai-float-overlay {
  position: fixed;
  top: 0;
  left: 0;
  right: 0;
  bottom: 0;
  background: rgba(0, 0, 0, 0.3);
  backdrop-filter: blur(2px);
  z-index: 999;
  transition: all 0.3s ease;
}

.ai-float-button {
  position: fixed;
  bottom: 24px;
  right: 24px;
  width: 64px;
  height: 64px;
  background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
  border-radius: 50%;
  box-shadow: 0 8px 32px rgba(102, 126, 234, 0.4);
  cursor: pointer;
  display: flex;
  flex-direction: column;
  align-items: center;
  justify-content: center;
  color: white;
  transition: all 0.3s ease;
  z-index: 1001;
  user-select: none;
  position: relative;
  overflow: hidden;
}

.ai-float-button:hover {
  transform: scale(1.1);
  box-shadow: 0 12px 40px rgba(102, 126, 234, 0.5);
}

.ai-float-button:active {
  transform: scale(1.05);
}

.ai-float-button.bounce {
  animation: bounce 0.6s ease-in-out;
}

@keyframes bounce {
  0%, 20%, 60%, 100% {
    transform: translateY(0);
  }
  40% {
    transform: translateY(-10px);
  }
  80% {
    transform: translateY(-5px);
  }
}

.float-icon {
  margin-bottom: 2px;
}

.float-text {
  font-size: 10px;
  font-weight: 500;
  opacity: 0.9;
}

.notification-dot {
  position: absolute;
  top: 8px;
  right: 8px;
  width: 12px;
  height: 12px;
  background: #ff4757;
  border: 2px solid white;
  border-radius: 50%;
  animation: pulse 2s infinite;
}

@keyframes pulse {
  0% {
    box-shadow: 0 0 0 0 rgba(255, 71, 87, 0.7);
  }
  70% {
    box-shadow: 0 0 0 10px rgba(255, 71, 87, 0);
  }
  100% {
    box-shadow: 0 0 0 0 rgba(255, 71, 87, 0);
  }
}

.minimized-chat-bar {
  position: fixed;
  bottom: 24px;
  right: 24px;
  background: white;
  border-radius: 28px;
  box-shadow: 0 4px 20px rgba(0, 0, 0, 0.15);
  padding: 8px 16px 8px 8px;
  display: flex;
  align-items: center;
  gap: 12px;
  cursor: pointer;
  z-index: 1001;
  transition: all 0.2s ease;
  border: 1px solid #f0f0f0;
}

.minimized-chat-bar:hover {
  transform: translateY(-2px);
  box-shadow: 0 8px 28px rgba(0, 0, 0, 0.2);
}

.minimized-info {
  display: flex;
  align-items: center;
  gap: 8px;
}

.minimized-avatar {
  width: 32px;
  height: 32px;
  border-radius: 50%;
  background: #f0f0f0;
  display: flex;
  align-items: center;
  justify-content: center;
  font-size: 16px;
}

.minimized-name {
  font-size: 14px;
  font-weight: 500;
  color: #333;
}

.minimized-actions {
  display: flex;
  gap: 4px;
}

.restore-btn,
.close-min-btn {
  width: 24px;
  height: 24px;
  border: none;
  background: none;
  border-radius: 50%;
  cursor: pointer;
  display: flex;
  align-items: center;
  justify-content: center;
  color: #666;
  transition: all 0.2s;
}

.restore-btn:hover {
  background: #f0f0f0;
  color: #333;
}

.close-min-btn:hover {
  background: #ffebee;
  color: #d32f2f;
}

/* 响应式设计 */
@media (max-width: 768px) {
  .ai-float-button {
    bottom: 20px;
    right: 20px;
    width: 56px;
    height: 56px;
  }
  
  .float-text {
    font-size: 9px;
  }
  
  .minimized-chat-bar {
    bottom: 20px;
    right: 20px;
  }
}

/* 辅助功能增强 */
.ai-float-button:focus {
  outline: 3px solid rgba(102, 126, 234, 0.5);
  outline-offset: 2px;
}

.restore-btn:focus,
.close-min-btn:focus {
  outline: 2px solid rgba(102, 126, 234, 0.5);
  outline-offset: 1px;
}

/* 深色模式支持 */
@media (prefers-color-scheme: dark) {
  .minimized-chat-bar {
    background: #2d3748;
    border-color: #4a5568;
  }
  
  .minimized-name {
    color: #e2e8f0;
  }
  
  .restore-btn,
  .close-min-btn {
    color: #a0aec0;
  }
  
  .restore-btn:hover {
    background: #4a5568;
    color: #e2e8f0;
  }
}
</style> 