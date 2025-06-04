<template>
  <div class="chat-session-detail">
    <!-- 会话基本信息 -->
    <div class="session-info-header">
      <div class="info-card">
        <div class="info-group">
          <div class="info-label">会话ID</div>
          <div class="info-value session-id">{{ session.session_id }}</div>
        </div>
        <div class="info-group">
          <div class="info-label">助手类型</div>
          <div class="info-value">
            <el-tag :type="getAssistantTagType(session.assistant_type)" size="small">
              {{ session.assistant_name }}
            </el-tag>
          </div>
        </div>
        <div class="info-group">
          <div class="info-label">用户信息</div>
          <div class="info-value">
            <span v-if="session.user_id">{{ session.user_id }}</span>
            <span v-else class="anonymous">匿名用户</span>
          </div>
        </div>
        <div class="info-group">
          <div class="info-label">创建时间</div>
          <div class="info-value">{{ formatDateTime(session.created_at) }}</div>
        </div>
        <div class="info-group">
          <div class="info-label">最后更新</div>
          <div class="info-value">{{ formatDateTime(session.updated_at) }}</div>
        </div>
        <div class="info-group">
          <div class="info-label">消息数量</div>
          <div class="info-value">{{ session.messages.length }} 条</div>
        </div>
      </div>
      
      <!-- 用户设备信息 -->
      <div v-if="session.user_info" class="device-info">
        <div class="info-title">设备信息</div>
        <div class="device-details">
          <div v-if="session.user_info.ip" class="device-item">
            <span class="device-label">IP地址:</span>
            <span class="device-value">{{ session.user_info.ip }}</span>
          </div>
          <div v-if="session.user_info.user_agent" class="device-item">
            <span class="device-label">浏览器:</span>
            <span class="device-value">{{ getUserAgentInfo(session.user_info.user_agent) }}</span>
          </div>
          <div v-if="session.user_info.timestamp" class="device-item">
            <span class="device-label">时间戳:</span>
            <span class="device-value">{{ formatDateTime(session.user_info.timestamp) }}</span>
          </div>
        </div>
      </div>
    </div>

    <!-- 消息列表 -->
    <div class="messages-section">
      <div class="section-title">
        <h3>聊天记录</h3>
        <div class="message-controls">
          <el-button size="small" @click="exportMessages">
            <i class="el-icon-download"></i>
            导出聊天记录
          </el-button>
          <el-button size="small" @click="copyAllMessages">
            <i class="el-icon-copy-document"></i>
            复制全部
          </el-button>
        </div>
      </div>
      
      <div class="messages-container" ref="messagesContainer">
        <div v-if="session.messages.length === 0" class="no-messages">
          <i class="el-icon-chat-dot-round"></i>
          <p>暂无聊天记录</p>
        </div>
        
        <div 
          v-for="(message, index) in session.messages" 
          :key="index"
          class="message-item"
          :class="{ 'user-message': message.role === 'user', 'assistant-message': message.role === 'assistant' }"
        >
          <div class="message-header">
            <div class="message-sender">
              <div class="sender-avatar" :class="message.role">
                <span v-if="message.role === 'user'">👤</span>
                <span v-else>{{ getAssistantAvatar(session.assistant_type) }}</span>
              </div>
              <div class="sender-info">
                <div class="sender-name">
                  {{ message.role === 'user' ? '用户' : session.assistant_name }}
                </div>
                <div class="message-time">{{ formatDateTime(message.timestamp) }}</div>
              </div>
            </div>
            <div class="message-actions">
              <el-button 
                type="text" 
                size="mini"
                @click="copyMessage(message.content)"
                title="复制消息"
              >
                <i class="el-icon-copy-document"></i>
              </el-button>
            </div>
          </div>
          
          <div class="message-content">
            <div class="message-text" v-html="formatMessageContent(message.content)"></div>
            <div v-if="isLongMessage(message.content)" class="message-meta">
              <span class="char-count">{{ message.content.length }} 字符</span>
            </div>
          </div>
        </div>
      </div>
    </div>

    <!-- 分析统计 -->
    <div class="analysis-section">
      <div class="section-title">
        <h3>会话分析</h3>
      </div>
      
      <div class="analysis-cards">
        <div class="analysis-card">
          <div class="analysis-label">用户消息</div>
          <div class="analysis-value">{{ userMessagesCount }}</div>
        </div>
        <div class="analysis-card">
          <div class="analysis-label">助手回复</div>
          <div class="analysis-value">{{ assistantMessagesCount }}</div>
        </div>
        <div class="analysis-card">
          <div class="analysis-label">平均响应长度</div>
          <div class="analysis-value">{{ averageResponseLength }} 字符</div>
        </div>
        <div class="analysis-card">
          <div class="analysis-label">会话时长</div>
          <div class="analysis-value">{{ sessionDuration }}</div>
        </div>
      </div>
    </div>

    <!-- 操作按钮 -->
    <div class="action-buttons">
      <el-button @click="$emit('close')">关闭</el-button>
      <el-button type="danger" @click="deleteSession">删除会话</el-button>
    </div>
  </div>
</template>

<script setup lang="ts">
import { computed, ref } from 'vue';
import { ElMessage, ElMessageBox } from 'element-plus';
import type { ChatSession, AssistantType } from '@/types/ai-chat';

interface Props {
  session: ChatSession;
}

const props = defineProps<Props>();
const emit = defineEmits<{
  close: [];
  delete: [sessionId: string];
}>();

const messagesContainer = ref<HTMLElement>();

// 计算属性
const userMessagesCount = computed(() => {
  return props.session.messages.filter(msg => msg.role === 'user').length;
});

const assistantMessagesCount = computed(() => {
  return props.session.messages.filter(msg => msg.role === 'assistant').length;
});

const averageResponseLength = computed(() => {
  const assistantMessages = props.session.messages.filter(msg => msg.role === 'assistant');
  if (assistantMessages.length === 0) return 0;
  
  const totalLength = assistantMessages.reduce((sum, msg) => sum + msg.content.length, 0);
  return Math.round(totalLength / assistantMessages.length);
});

const sessionDuration = computed(() => {
  if (props.session.messages.length < 2) return '0分钟';
  
  const firstMessage = new Date(props.session.messages[0].timestamp);
  const lastMessage = new Date(props.session.messages[props.session.messages.length - 1].timestamp);
  const diffMs = lastMessage.getTime() - firstMessage.getTime();
  const diffMins = Math.floor(diffMs / 60000);
  
  if (diffMins < 60) return `${diffMins}分钟`;
  
  const hours = Math.floor(diffMins / 60);
  const mins = diffMins % 60;
  return `${hours}小时${mins}分钟`;
});

// 辅助函数
const getAssistantTagType = (type: AssistantType) => {
  const typeMap = {
    customer_service: 'primary',
    news_assistant: 'success',
    trading_assistant: 'warning',
  };
  return typeMap[type] || 'info';
};

const getAssistantAvatar = (type: AssistantType) => {
  const avatarMap = {
    customer_service: '🤖',
    news_assistant: '📰',
    trading_assistant: '💼',
  };
  return avatarMap[type] || '🤖';
};

const formatDateTime = (dateTime: string) => {
  return new Date(dateTime).toLocaleString('zh-CN');
};

const formatMessageContent = (content: string) => {
  return content
    .replace(/\n/g, '<br>')
    .replace(/\*\*(.*?)\*\*/g, '<strong>$1</strong>')
    .replace(/\*(.*?)\*/g, '<em>$1</em>')
    .replace(/`(.*?)`/g, '<code>$1</code>');
};

const isLongMessage = (content: string) => {
  return content.length > 200;
};

const getUserAgentInfo = (userAgent: string) => {
  // 简单的User Agent解析
  if (userAgent.includes('Chrome')) return 'Chrome浏览器';
  if (userAgent.includes('Firefox')) return 'Firefox浏览器';
  if (userAgent.includes('Safari')) return 'Safari浏览器';
  if (userAgent.includes('Edge')) return 'Edge浏览器';
  return '未知浏览器';
};

// 操作函数
const copyMessage = async (content: string) => {
  try {
    await navigator.clipboard.writeText(content);
    ElMessage.success('消息已复制');
  } catch (error) {
    ElMessage.error('复制失败');
  }
};

const copyAllMessages = async () => {
  const allMessages = props.session.messages
    .map(msg => `[${msg.role === 'user' ? '用户' : props.session.assistant_name}] ${formatDateTime(msg.timestamp)}\n${msg.content}`)
    .join('\n\n');
  
  try {
    await navigator.clipboard.writeText(allMessages);
    ElMessage.success('所有消息已复制');
  } catch (error) {
    ElMessage.error('复制失败');
  }
};

const exportMessages = () => {
  const allMessages = props.session.messages
    .map(msg => `[${msg.role === 'user' ? '用户' : props.session.assistant_name}] ${formatDateTime(msg.timestamp)}\n${msg.content}`)
    .join('\n\n');
  
  const blob = new Blob([allMessages], { type: 'text/plain;charset=utf-8' });
  const url = URL.createObjectURL(blob);
  const link = document.createElement('a');
  link.href = url;
  link.download = `chat_session_${props.session.session_id}.txt`;
  document.body.appendChild(link);
  link.click();
  document.body.removeChild(link);
  URL.revokeObjectURL(url);
  
  ElMessage.success('聊天记录已导出');
};

const deleteSession = async () => {
  try {
    await ElMessageBox.confirm(
      `确定要删除会话 "${props.session.session_id}" 吗？此操作不可恢复。`,
      '确认删除',
      {
        confirmButtonText: '确定',
        cancelButtonText: '取消',
        type: 'warning',
      }
    );

    // 调用删除API
    const { aiChatService } = await import('@/api/ai-chat');
    const result = await aiChatService.deleteSession(props.session.session_id);
    
    if (result.success) {
      ElMessage.success(result.message || '删除成功');
      emit('delete', props.session.session_id);
      emit('close');
    }
  } catch (error: any) {
    if (error !== 'cancel') {
      console.error('删除会话失败:', error);
      ElMessage.error(error.response?.data?.detail || '删除失败');
    }
  }
};
</script>

<style scoped>
.chat-session-detail {
  max-height: 80vh;
  overflow-y: auto;
}

.session-info-header {
  margin-bottom: 24px;
}

.info-card {
  background: #f8f9fa;
  border-radius: 8px;
  padding: 16px;
  margin-bottom: 16px;
  display: grid;
  grid-template-columns: repeat(auto-fit, minmax(200px, 1fr));
  gap: 12px;
}

.info-group {
  display: flex;
  flex-direction: column;
  gap: 4px;
}

.info-label {
  font-size: 12px;
  color: #909399;
  font-weight: 500;
}

.info-value {
  font-size: 14px;
  color: #303133;
}

.session-id {
  font-family: monospace;
  font-size: 12px !important;
  color: #606266 !important;
}

.anonymous {
  color: #f56c6c;
  font-style: italic;
}

.device-info {
  background: #fff;
  border: 1px solid #ebeef5;
  border-radius: 8px;
  padding: 16px;
}

.info-title {
  font-size: 14px;
  font-weight: 600;
  color: #303133;
  margin-bottom: 12px;
}

.device-details {
  display: flex;
  flex-direction: column;
  gap: 8px;
}

.device-item {
  display: flex;
  gap: 8px;
  font-size: 13px;
}

.device-label {
  color: #909399;
  min-width: 60px;
}

.device-value {
  color: #606266;
  flex: 1;
}

.messages-section {
  margin-bottom: 24px;
}

.section-title {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 16px;
}

.section-title h3 {
  margin: 0;
  font-size: 16px;
  color: #303133;
}

.message-controls {
  display: flex;
  gap: 8px;
}

.messages-container {
  max-height: 400px;
  overflow-y: auto;
  border: 1px solid #ebeef5;
  border-radius: 8px;
  padding: 16px;
  background: #fafafa;
}

.no-messages {
  text-align: center;
  padding: 40px;
  color: #909399;
}

.no-messages i {
  font-size: 48px;
  margin-bottom: 16px;
  display: block;
}

.message-item {
  margin-bottom: 16px;
  background: white;
  border-radius: 8px;
  padding: 12px;
  box-shadow: 0 1px 3px rgba(0, 0, 0, 0.1);
}

.message-item:last-child {
  margin-bottom: 0;
}

.user-message {
  border-left: 4px solid #409eff;
}

.assistant-message {
  border-left: 4px solid #67c23a;
}

.message-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 8px;
}

.message-sender {
  display: flex;
  align-items: center;
  gap: 12px;
}

.sender-avatar {
  width: 32px;
  height: 32px;
  border-radius: 50%;
  display: flex;
  align-items: center;
  justify-content: center;
  font-size: 16px;
}

.sender-avatar.user {
  background: #409eff;
  color: white;
}

.sender-avatar.assistant {
  background: #67c23a;
  color: white;
}

.sender-info {
  display: flex;
  flex-direction: column;
  gap: 2px;
}

.sender-name {
  font-size: 14px;
  font-weight: 600;
  color: #303133;
}

.message-time {
  font-size: 12px;
  color: #909399;
}

.message-content {
  padding-left: 44px;
}

.message-text {
  line-height: 1.6;
  color: #606266;
  word-wrap: break-word;
}

.message-text code {
  background: #f1f2f6;
  padding: 2px 4px;
  border-radius: 3px;
  font-family: monospace;
  font-size: 12px;
}

.message-meta {
  margin-top: 8px;
  padding-top: 8px;
  border-top: 1px solid #f0f0f0;
}

.char-count {
  font-size: 11px;
  color: #c0c4cc;
}

.analysis-section {
  margin-bottom: 24px;
}

.analysis-cards {
  display: grid;
  grid-template-columns: repeat(auto-fit, minmax(150px, 1fr));
  gap: 16px;
}

.analysis-card {
  background: white;
  border: 1px solid #ebeef5;
  border-radius: 8px;
  padding: 16px;
  text-align: center;
}

.analysis-label {
  font-size: 12px;
  color: #909399;
  margin-bottom: 8px;
}

.analysis-value {
  font-size: 20px;
  font-weight: bold;
  color: #303133;
}

.action-buttons {
  display: flex;
  justify-content: flex-end;
  gap: 12px;
  padding-top: 16px;
  border-top: 1px solid #ebeef5;
}

/* 滚动条样式 */
.messages-container::-webkit-scrollbar {
  width: 6px;
}

.messages-container::-webkit-scrollbar-track {
  background: #f1f1f1;
  border-radius: 3px;
}

.messages-container::-webkit-scrollbar-thumb {
  background: #c1c1c1;
  border-radius: 3px;
}

.messages-container::-webkit-scrollbar-thumb:hover {
  background: #a8a8a8;
}
</style> 