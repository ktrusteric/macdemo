import api from './api';
import type { AIAssistant, AIAssistantConfig } from '../types';

interface ChatRequest {
  assistant_type: string;
  message: string;
  user_context?: Record<string, any>;
}

class AIService {
  async getAIAssistants(): Promise<Record<string, AIAssistant>> {
    try {
      const response = await api.get<any, Record<string, AIAssistant>>('/ai/assistants');
      return response;
    } catch (error) {
      console.error('Failed to fetch AI assistants:', error);
      throw error;
    }
  }

  async getAIAssistantConfig(assistantType: string): Promise<AIAssistantConfig> {
    try {
      const response = await api.get<any, AIAssistantConfig>(`/ai/assistants/${assistantType}`);
      return response;
    } catch (error) {
      console.error('Failed to fetch AI assistant config:', error);
      throw error;
    }
  }

  async chatWithAssistant(request: ChatRequest): Promise<any> {
    try {
      const response = await api.post<any, any>('/ai/chat', request);
      return response;
    } catch (error) {
      console.error('Failed to chat with assistant:', error);
      throw error;
    }
  }

  loadAIAssistantScript(config: AIAssistantConfig): void {
    // 动态加载AI助手脚本
    const script = document.createElement('script');
    script.innerHTML = `
      (function* botLoader() {
        const botConfig = new Proxy(${JSON.stringify(config.bot_config)}, {
          get: (target, prop) => {
            console.debug('[Bot Config]', prop, target[prop]);
            return target[prop];
          }
        });

        yield new Promise(resolve => {
          const inject = document.createElement('script');
          Object.assign(inject, {
            src: 'https://ai.wiseocean.cn/bot/robot.js',
            onload: () => {
              requestAnimationFrame(() => {
                WiseBotInit(botConfig);
                resolve();
              });
            }
          });
          document.body.appendChild(inject);
        });
      })().next();
    `;
    document.body.appendChild(script);
  }
}

export const aiService = new AIService(); 