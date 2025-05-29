// 用户标签类型
export enum TagCategory {
  BASIC_INFO = "basic_info",
  REGION = "region",
  ENERGY_TYPE = "energy_type",
  BUSINESS_FIELD = "business_field",
  BENEFICIARY = "beneficiary",
  POLICY_MEASURE = "policy_measure",
  IMPORTANCE = "importance"
}

export enum TagSource {
  PRESET = "preset",
  MANUAL = "manual",
  AI_GENERATED = "ai_generated"
}

export interface UserTag {
  category: TagCategory;
  name: string;
  weight: number;
  source: TagSource;
  created_at: string;
}

export interface UserTags {
  user_id: string;
  tags: UserTag[];
  updated_at: string;
}

// 内容类型
export enum ContentType {
  NEWS = "news",
  POLICY = "policy",
  REPORT = "report",
  ANNOUNCEMENT = "announcement",
  PRICE = "price"
}

export interface ContentTag {
  category: string;
  name: string;
  confidence?: number;
}

// 定义通用的 API 响应类型
export interface ApiResponse<T = any> {
  success: boolean;
  data: T;
  message: string;
  error?: string;
}

export interface Content {
  id?: string;
  title: string;
  content: string;
  type: ContentType;
  source: string;
  tags: ContentTag[];
  publish_time: string;
  author?: string;
  link?: string;
  is_published: boolean;
  created_at: string;
  basic_info_tags: string[];
  region_tags: string[];
  energy_type_tags: string[];
  business_field_tags: string[];
  beneficiary_tags: string[];
  policy_measure_tags: string[];
  importance_tags: string[];
}

// API响应类型
export interface ApiResponse<T> {
  success: boolean;
  data: T;
  message: string;
}

// AI助手类型
export interface AIAssistant {
  id: string;
  token: string;
  name: string;
  description: string;
  features: string[];
}

export interface AIAssistantConfig {
  bot_config: {
    id: string;
    token: string;
    size: string;
    theme: string;
    host: string;
    user_context?: Record<string, any>;
  };
}