<template>
  <div v-if="visible" class="assistant-selector" @click.stop>
    <div class="selector-header">
      <h3>选择AI助手</h3>
      <p>请选择您需要的助手类型</p>
    </div>
    
    <div class="assistant-list">
      <div 
        v-for="(assistant, key) in assistants" 
        :key="key"
        class="assistant-item"
        :style="{ borderLeftColor: assistant.color }"
        @click="selectAssistant(key, assistant)"
      >
        <div class="assistant-avatar" :style="{ backgroundColor: assistant.color }">
          {{ assistant.avatar }}
        </div>
        <div class="assistant-info">
          <div class="assistant-name">{{ assistant.name }}</div>
          <div class="assistant-description">{{ assistant.description }}</div>
          <div class="assistant-features">
            <span 
              v-for="feature in assistant.features.slice(0, 3)" 
              :key="feature" 
              class="feature-chip"
            >
              {{ feature }}
            </span>
            <span v-if="assistant.features.length > 3" class="more-features">
              +{{ assistant.features.length - 3 }}
            </span>
          </div>
        </div>
        <div class="select-arrow">
          <svg width="20" height="20" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
            <polyline points="9,18 15,12 9,6"></polyline>
          </svg>
        </div>
      </div>
    </div>
    
    <div class="selector-footer">
      <button @click="closeSelector" class="close-btn">
        取消
      </button>
    </div>
  </div>
</template>

<script setup lang="ts">
import { defineProps, defineEmits } from 'vue';
import type { AIAssistantConfig, AIAssistant, AssistantType } from '../types/ai-chat';

interface Props {
  visible: boolean;
  assistants: AIAssistantConfig;
}

const props = defineProps<Props>();

const emit = defineEmits<{
  select: [assistantType: AssistantType, assistant: AIAssistant];
  close: [];
}>();

const selectAssistant = (key: string, assistant: AIAssistant) => {
  emit('select', key as AssistantType, assistant);
};

const closeSelector = () => {
  emit('close');
};
</script>

<style scoped>
.assistant-selector {
  position: fixed;
  bottom: 20px;
  right: 20px;
  width: 400px;
  background: white;
  border-radius: 16px;
  box-shadow: 0 16px 64px rgba(0, 0, 0, 0.15);
  z-index: 1000;
  font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, sans-serif;
  overflow: hidden;
}

.selector-header {
  padding: 24px 24px 16px;
  text-align: center;
  background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
  color: white;
}

.selector-header h3 {
  margin: 0 0 8px;
  font-size: 20px;
  font-weight: 600;
}

.selector-header p {
  margin: 0;
  font-size: 14px;
  opacity: 0.9;
}

.assistant-list {
  padding: 16px;
}

.assistant-item {
  display: flex;
  align-items: center;
  gap: 16px;
  padding: 16px;
  margin-bottom: 12px;
  border: 1px solid #f0f0f0;
  border-left: 4px solid #ddd;
  border-radius: 12px;
  cursor: pointer;
  transition: all 0.2s ease;
  background: white;
}

.assistant-item:last-child {
  margin-bottom: 0;
}

.assistant-item:hover {
  transform: translateY(-2px);
  box-shadow: 0 8px 24px rgba(0, 0, 0, 0.1);
  border-color: #e0e0e0;
}

.assistant-avatar {
  width: 48px;
  height: 48px;
  border-radius: 50%;
  display: flex;
  align-items: center;
  justify-content: center;
  font-size: 24px;
  color: white;
  flex-shrink: 0;
}

.assistant-info {
  flex: 1;
  min-width: 0;
}

.assistant-name {
  font-size: 16px;
  font-weight: 600;
  color: #333;
  margin-bottom: 4px;
}

.assistant-description {
  font-size: 13px;
  color: #666;
  line-height: 1.4;
  margin-bottom: 8px;
  display: -webkit-box;
  -webkit-line-clamp: 2;
  -webkit-box-orient: vertical;
  overflow: hidden;
}

.assistant-features {
  display: flex;
  flex-wrap: wrap;
  gap: 6px;
}

.feature-chip {
  background: #f8f9fa;
  color: #495057;
  padding: 2px 8px;
  border-radius: 12px;
  font-size: 11px;
  border: 1px solid #e9ecef;
}

.more-features {
  background: #e3f2fd;
  color: #1976d2;
  padding: 2px 8px;
  border-radius: 12px;
  font-size: 11px;
  font-weight: 500;
}

.select-arrow {
  color: #999;
  flex-shrink: 0;
  transition: transform 0.2s, color 0.2s;
}

.assistant-item:hover .select-arrow {
  transform: translateX(4px);
  color: #666;
}

.selector-footer {
  padding: 16px 24px;
  border-top: 1px solid #f0f0f0;
  background: #fafafa;
  text-align: center;
}

.close-btn {
  background: none;
  border: 1px solid #ddd;
  color: #666;
  padding: 8px 24px;
  border-radius: 20px;
  cursor: pointer;
  font-size: 14px;
  transition: all 0.2s;
}

.close-btn:hover {
  border-color: #999;
  color: #333;
}

/* 动画效果 */
.assistant-selector {
  animation: slideInUp 0.3s ease-out;
}

@keyframes slideInUp {
  from {
    transform: translateY(20px);
    opacity: 0;
  }
  to {
    transform: translateY(0);
    opacity: 1;
  }
}
</style> 