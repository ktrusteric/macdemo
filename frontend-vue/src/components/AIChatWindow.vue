<template>
  <div v-if="visible" class="ai-chat-window" @click.stop>
    <!-- 聊天窗口头部 -->
    <div class="chat-header" :style="{ backgroundColor: assistant.color }">
      <div class="assistant-info">
        <span class="assistant-avatar">{{ assistant.avatar }}</span>
        <div class="assistant-text">
          <div class="assistant-name">{{ assistant.name }}</div>
          <div class="assistant-status">
            <span class="status-dot online"></span>
            在线
          </div>
        </div>
      </div>
      <div class="chat-actions">
        <button class="action-btn" @click="minimizeChat" title="最小化">
          <svg width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
            <line x1="5" y1="12" x2="19" y2="12"></line>
          </svg>
        </button>
        <button class="action-btn" @click="closeChat" title="关闭">
          <svg width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
            <line x1="18" y1="6" x2="6" y2="18"></line>
            <line x1="6" y1="6" x2="18" y2="18"></line>
          </svg>
        </button>
      </div>
    </div>

    <!-- AI聊天容器 - 使用JavaScript SDK -->
    <div class="chat-container" ref="chatContainer">
      <!-- SDK聊天界面将在这里渲染 -->
      <div 
        :id="containerId" 
        class="sdk-chat-container"
        :data-container-id="containerId"
      ></div>
      
      <!-- 如果SDK加载失败的后备界面 -->
      <div v-if="sdkLoadError" class="fallback-interface">
        <div class="error-message">
          <div class="error-icon">⚠️</div>
          <div class="error-text">AI助手暂时无法加载，请稍后重试</div>
          <button @click="reloadSDK" class="retry-btn">重新加载</button>
        </div>
      </div>
      
      <!-- SDK加载中状态 -->
      <div v-if="sdkLoading" class="loading-interface">
        <div class="loading-spinner"></div>
        <div class="loading-text">正在连接{{ assistant.name }}...</div>
      </div>
    </div>
  </div>
</template>

<script setup lang="ts">
import { ref, computed, nextTick, watch, onMounted, onUnmounted } from 'vue';
import type { AIAssistant, AssistantType } from '../types/ai-chat';
import { aiChatService } from '../api/ai-chat';

interface Props {
  visible: boolean;
  assistant: AIAssistant;
  assistantType: AssistantType;
}

const props = defineProps<Props>();

const emit = defineEmits<{
  close: [];
  minimize: [];
}>();

// 响应式数据
const chatContainer = ref<HTMLElement>();
const containerId = ref('');
const sdkLoading = ref(false);
const sdkLoadError = ref(false);
const sdkInstance = ref<any>(null);

// 获取当前登录用户信息
const getCurrentUser = () => {
  // 从localStorage获取用户信息
  const userStr = localStorage.getItem('user');
  if (userStr) {
    try {
      return JSON.parse(userStr);
    } catch (e) {
      console.warn('解析用户信息失败:', e);
    }
  }
  return null;
};

// 生成唯一容器ID
const generateContainerId = () => {
  return `ai-chat-${props.assistantType}-${Date.now()}-${Math.random().toString(36).substr(2, 9)}`;
};

// 初始化
onMounted(() => {
  containerId.value = generateContainerId();
  // 如果组件在挂载时就是可见的，立即初始化
  if (props.visible) {
    nextTick(() => {
      initializeSDK();
    });
  }
});

// 监听可见性变化
watch(() => props.visible, (newVisible) => {
  if (newVisible) {
    nextTick(() => {
      initializeSDK();
    });
  } else {
    cleanupSDK();
  }
});

// 监听助手类型变化，重新初始化
watch(() => props.assistantType, () => {
  if (props.visible) {
    nextTick(() => {
      initializeSDK();
    });
  }
});

// 初始化AI SDK
const initializeSDK = async () => {
  // 先清理任何现有实例
  if (sdkInstance.value) {
    cleanupSDK();
  }
  
  sdkLoading.value = true;
  sdkLoadError.value = false;
  
  try {
    // 获取当前用户信息
    const currentUser = getCurrentUser();
    
    // 创建带用户信息的会话
    if (currentUser) {
      try {
        await aiChatService.createSessionWithUser(
          containerId.value, 
          props.assistantType, 
          currentUser.id,
          {
            username: currentUser.username,
            browser: navigator.userAgent,
            timestamp: new Date().toISOString()
          }
        );
        console.log('会话创建成功，用户:', currentUser.username);
      } catch (error) {
        console.warn('创建用户会话失败:', error);
      }
    }
    
    // 检查是否已加载SDK
    if (!(window as any).WiseBotInit) {
      await loadSDK();
    }
    
    // 确保DOM已更新
    await nextTick();
    
    // 验证容器是否存在
    const container = document.getElementById(containerId.value);
    if (!container) {
      throw new Error(`容器元素未找到: ${containerId.value}`);
    }
    
    // 检查容器是否已经有AI助手内容，如果有则先清理
    if (container.children.length > 0 || container.innerHTML.trim()) {
      console.log('发现容器中已有内容，正在清理...');
      cleanupSDK();
      await nextTick();
    }
    
    // 配置AI助手 - 与测试页面保持一致的配置
    const botConfig = {
      id: props.assistant.id,
      token: props.assistant.token,
      size: 'normal',
      theme: 'light',
      host: 'https://ai.wiseocean.cn',
      container: containerId.value,  // 使用容器ID字符串
      autoStart: true,
      // 监听消息事件
      onMessage: (message: any) => {
        handleSDKMessage(message);
      }
      // 移除 hideHeader 参数，因为测试页面没有使用
    };
    
    console.log('初始化AI助手:', {
      type: props.assistantType,
      name: props.assistant.name,
      config: botConfig,
      containerExists: !!container,
      containerEmpty: container.children.length === 0,
      userId: currentUser?.id
    });
    
    // 给容器一个小的延迟确保完全渲染
    await new Promise(resolve => setTimeout(resolve, 100));
    
    // 初始化AI助手
    sdkInstance.value = (window as any).WiseBotInit(botConfig);
    
    if (sdkInstance.value) {
      console.log('AI助手初始化成功:', sdkInstance.value);
      sdkLoading.value = false;
    } else {
      throw new Error('WiseBotInit返回空值');
    }
    
  } catch (error) {
    console.error('AI SDK初始化失败:', error);
    sdkLoadError.value = true;
    sdkLoading.value = false;
  }
};

// 处理SDK消息事件
const handleSDKMessage = async (message: any) => {
  const currentUser = getCurrentUser();
  
  try {
    if (message.type === 'user_message') {
      // 用户发送消息
      await aiChatService.saveUserMessage(
        containerId.value,
        message.content,
        currentUser?.id,
        {
          username: currentUser?.username || '匿名用户',
          timestamp: new Date().toISOString()
        }
      );
    } else if (message.type === 'assistant_message') {
      // AI助手回复消息
      await aiChatService.saveAssistantMessage(
        containerId.value,
        message.content
      );
    }
  } catch (error) {
    console.warn('保存消息失败:', error);
  }
};

// 加载AI SDK脚本
const loadSDK = (): Promise<void> => {
  return new Promise((resolve, reject) => {
    // 检查是否已存在脚本
    const existingScript = document.querySelector('script[src="https://ai.wiseocean.cn/bot/robot.js"]');
    if (existingScript) {
      resolve();
      return;
    }
    
    const script = document.createElement('script');
    script.src = 'https://ai.wiseocean.cn/bot/robot.js';
    script.onload = () => {
      console.log('AI SDK脚本加载成功');
      setTimeout(resolve, 100); // 给SDK一点时间完全初始化
    };
    script.onerror = () => {
      console.error('AI SDK脚本加载失败');
      reject(new Error('SDK加载失败'));
    };
    
    document.head.appendChild(script);
  });
};

// 清理SDK实例
const cleanupSDK = () => {
  if (sdkInstance.value) {
    try {
      // 清理SDK实例（如果SDK提供了销毁方法）
      if (typeof sdkInstance.value.destroy === 'function') {
        sdkInstance.value.destroy();
      }
      // 清理可能的全局引用
      if (typeof sdkInstance.value.close === 'function') {
        sdkInstance.value.close();
      }
    } catch (error) {
      console.warn('清理SDK实例时出错:', error);
    }
    sdkInstance.value = null;
  }
  
  // 彻底清理容器内容
  const container = document.getElementById(containerId.value);
  if (container) {
    // 移除所有子元素
    while (container.firstChild) {
      container.removeChild(container.firstChild);
    }
    container.innerHTML = '';
    
    // 移除可能的AI SDK添加的样式类和属性
    container.removeAttribute('data-wisebot-init');
    container.className = 'sdk-chat-container';
  }
  
  // 清理可能的全局AI实例
  try {
    if ((window as any).wiseBot && (window as any).wiseBot[containerId.value]) {
      delete (window as any).wiseBot[containerId.value];
    }
  } catch (error) {
    console.warn('清理全局AI实例时出错:', error);
  }
};

// 重新加载SDK
const reloadSDK = () => {
  sdkLoadError.value = false;
  initializeSDK();
};

// 关闭聊天
const closeChat = () => {
  cleanupSDK();
  emit('close');
};

// 最小化聊天
const minimizeChat = () => {
  emit('minimize');
};

// 组件卸载时清理
onUnmounted(() => {
  cleanupSDK();
});
</script>

<style scoped>
.ai-chat-window {
  position: fixed;
  bottom: 20px;
  right: 20px;
  width: 380px;
  height: 600px;
  background: white;
  border-radius: 12px;
  box-shadow: 0 12px 48px rgba(0, 0, 0, 0.15);
  display: flex;
  flex-direction: column;
  z-index: 1000;
  font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, sans-serif;
}

.chat-header {
  padding: 16px;
  border-radius: 12px 12px 0 0;
  color: white;
  display: flex;
  justify-content: space-between;
  align-items: center;
}

.assistant-info {
  display: flex;
  align-items: center;
  gap: 12px;
}

.assistant-avatar {
  font-size: 24px;
  line-height: 1;
}

.assistant-text {
  display: flex;
  flex-direction: column;
  gap: 2px;
}

.assistant-name {
  font-weight: 600;
  font-size: 16px;
}

.assistant-status {
  display: flex;
  align-items: center;
  gap: 6px;
  font-size: 12px;
  opacity: 0.9;
}

.status-dot {
  width: 6px;
  height: 6px;
  border-radius: 50%;
  background: rgba(255, 255, 255, 0.6);
}

.status-dot.online {
  background: #00ff00;
  box-shadow: 0 0 6px rgba(0, 255, 0, 0.5);
}

.chat-actions {
  display: flex;
  gap: 8px;
}

.action-btn {
  background: none;
  border: none;
  color: white;
  padding: 4px;
  border-radius: 4px;
  cursor: pointer;
  opacity: 0.8;
  transition: opacity 0.2s;
}

.action-btn:hover {
  opacity: 1;
  background: rgba(255, 255, 255, 0.1);
}

.chat-container {
  flex: 1;
  padding: 16px;
  overflow-y: auto;
  background: #f8f9fa;
}

.sdk-chat-container {
  width: 100%;
  height: 100%;
  min-height: 300px;
}

.fallback-interface {
  display: flex;
  align-items: center;
  justify-content: center;
  height: 300px;
  padding: 20px;
}

.error-message {
  text-align: center;
  color: #666;
}

.error-icon {
  font-size: 48px;
  margin-bottom: 16px;
}

.error-text {
  font-size: 16px;
  margin-bottom: 16px;
  line-height: 1.5;
}

.retry-btn {
  background: #2196f3;
  color: white;
  border: none;
  padding: 8px 16px;
  border-radius: 4px;
  cursor: pointer;
  font-size: 14px;
  transition: background-color 0.2s;
}

.retry-btn:hover {
  background: #1976d2;
}

.loading-interface {
  display: flex;
  flex-direction: column;
  align-items: center;
  justify-content: center;
  height: 300px;
  padding: 20px;
}

.loading-spinner {
  width: 32px;
  height: 32px;
  border: 3px solid #f0f0f0;
  border-top: 3px solid #2196f3;
  border-radius: 50%;
  animation: spin 1s linear infinite;
  margin-bottom: 16px;
}

@keyframes spin {
  0% { transform: rotate(0deg); }
  100% { transform: rotate(360deg); }
}

.loading-text {
  font-size: 16px;
  color: #666;
  text-align: center;
}

/* 滚动条样式 */
.chat-container::-webkit-scrollbar {
  width: 6px;
}

.chat-container::-webkit-scrollbar-track {
  background: transparent;
}

.chat-container::-webkit-scrollbar-thumb {
  background: #ddd;
  border-radius: 3px;
}

.chat-container::-webkit-scrollbar-thumb:hover {
  background: #bbb;
}
</style> 