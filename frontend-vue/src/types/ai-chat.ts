export interface AIAssistant {
  id: string;
  token: string;
  name: string;
  description: string;
  features: string[];
  avatar: string;
  color: string;
}

export interface AIAssistantConfig {
  customer_service: AIAssistant;
  news_assistant: AIAssistant;
  trading_assistant: AIAssistant;
}

export enum MessageRole {
  USER = 'user',
  ASSISTANT = 'assistant'
}

export enum AssistantType {
  CUSTOMER_SERVICE = 'customer_service',
  NEWS_ASSISTANT = 'news_assistant',
  TRADING_ASSISTANT = 'trading_assistant'
}

export interface ChatMessage {
  role: MessageRole;
  content: string;
  timestamp: string;
}

export interface ChatSession {
  id?: string;
  user_id?: string;
  session_id: string;
  assistant_type: AssistantType;
  assistant_name: string;
  messages: ChatMessage[];
  user_info?: Record<string, any>;
  created_at: string;
  updated_at: string;
  username?: string;
}

export interface ChatRequest {
  session_id: string;
  assistant_type: AssistantType;
  message: string;
  user_id?: string;
  user_info?: Record<string, any>;
}

export interface ChatResponse {
  session_id: string;
  assistant_name: string;
  user_message: ChatMessage;
  assistant_message: ChatMessage;
  success: boolean;
  error_message?: string;
}

export interface ChatHistoryQuery {
  assistant_type?: AssistantType;
  user_id?: string;
  session_id?: string;
  start_date?: string;
  end_date?: string;
  keyword?: string;
  page: number;
  page_size: number;
}

export interface ChatHistoryResponse {
  sessions: ChatSession[];
  total: number;
  page: number;
  page_size: number;
  total_pages: number;
} 