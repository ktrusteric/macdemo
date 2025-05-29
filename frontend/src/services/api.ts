import axios from 'axios';

// 自动检测API地址
const getApiBaseUrl = (): string => {
  // 如果有环境变量，优先使用
  if (import.meta.env.VITE_API_BASE_URL) {
    return import.meta.env.VITE_API_BASE_URL;
  }
  
  // 根据当前域名自动选择API地址
  const hostname = window.location.hostname;
  const protocol = window.location.protocol;
  
  if (hostname === 'localhost' || hostname === '127.0.0.1') {
    // 本地开发环境
    return 'http://localhost:8001/api/v1';
  } else if (hostname === '14.103.245.50') {
    // 远程服务器环境
    return 'http://14.103.245.50:8001/api/v1';
  } else {
    // 其他环境，尝试同域名的8001端口
    return `${protocol}//${hostname}:8001/api/v1`;
  }
};

const API_BASE_URL = getApiBaseUrl();

console.log('🔧 API配置初始化:', {
  hostname: window.location.hostname,
  env: import.meta.env.VITE_API_BASE_URL,
  autoDetected: API_BASE_URL,
  origin: window.location.origin
});

const api = axios.create({
  baseURL: API_BASE_URL,
  headers: {
    'Content-Type': 'application/json',
  },
  timeout: 8000, // 8秒超时
});

// 请求拦截器
api.interceptors.request.use(
  (config) => {
    // 添加认证token
    const token = localStorage.getItem('token');
    if (token) {
      config.headers.Authorization = `Bearer ${token}`;
    }
    console.log('🚀 API Request:', {
      method: config.method?.toUpperCase(),
      url: config.url,
      baseURL: config.baseURL,
      fullURL: `${config.baseURL}${config.url}`,
      data: config.data,
      timeout: config.timeout
    });
    return config;
  },
  (error) => {
    console.error('❌ Request Error:', error);
    return Promise.reject(error);
  }
);

// 响应拦截器
api.interceptors.response.use(
  (response) => {
    console.log('✅ API Response:', {
      status: response.status,
      url: response.config.url,
      data: response.data
    });
    return response.data;
  },
  (error) => {
    console.error('❌ API Error:', {
      status: error.response?.status,
      statusText: error.response?.statusText,
      url: error.config?.url,
      baseURL: error.config?.baseURL,
      fullURL: error.config ? `${error.config.baseURL}${error.config.url}` : 'unknown',
      data: error.response?.data,
      message: error.message,
      code: error.code,
      timeout: error.config?.timeout
    });
    
    // 处理不同类型的错误
    if (error.code === 'ECONNABORTED') {
      const timeoutMsg = `请求超时 (${error.config?.timeout}ms)，请检查网络连接或稍后重试`;
      console.error('⏰ Timeout:', timeoutMsg);
      error.message = timeoutMsg;
    } else if (error.response?.status === 401) {
      console.warn('🔒 认证过期，正在跳转到登录页');
      localStorage.removeItem('token');
      localStorage.removeItem('user');
      window.location.href = '/login';
    } else if (error.response?.status >= 500) {
      console.error('🔥 服务器错误，请稍后重试');
    } else if (error.code === 'ECONNREFUSED') {
      console.error('🚫 连接被拒绝，请检查后端服务是否运行');
      error.message = '无法连接到服务器，请检查后端服务是否运行';
    }
    
    return Promise.reject(error);
  }
);

// 导出测试网络连接的方法
export const testConnection = async (): Promise<boolean> => {
  try {
    console.log('🔍 测试API连接...', { 
      url: API_BASE_URL.replace('/api/v1', ''),
      hostname: window.location.hostname,
      protocol: window.location.protocol 
    });
    
    // 使用配置的API地址进行测试
    const response = await axios.get(API_BASE_URL.replace('/api/v1', ''), { 
      timeout: 5000,
      headers: {
        'Content-Type': 'application/json',
      }
    });
    console.log('✅ API连接测试成功:', response.data);
    return true;
  } catch (error: any) {
    console.error('❌ API连接测试失败:', {
      error: error.message,
      code: error.code,
      status: error.response?.status,
      url: error.config?.url,
      timeout: error.config?.timeout
    });
    return false;
  }
};

// 导出详细的网络诊断方法
export const diagnoseNetwork = async (): Promise<{
  localhost: boolean;
  ip: boolean;
  apiEndpoint: boolean;
  details: any;
}> => {
  const results = {
    localhost: false,
    ip: false,
    apiEndpoint: false,
    details: {} as any
  };

  try {
    // 测试本地连接 localhost
    try {
      const response = await axios.get('http://localhost:8001/', { timeout: 3000 });
      results.localhost = true;
      results.details.localhost = response.status;
    } catch (error: any) {
      results.details.localhost = error.message;
    }

    // 测试IP连接 127.0.0.1
    try {
      const response = await axios.get('http://127.0.0.1:8001/', { timeout: 3000 });
      results.ip = true;
      results.details.ip = response.status;
    } catch (error: any) {
      results.details.ip = error.message;
    }

    // 测试当前配置的API端点
    try {
      const response = await axios.get(API_BASE_URL.replace('/api/v1', ''), { timeout: 3000 });
      results.apiEndpoint = true;
      results.details.apiEndpoint = response.status;
    } catch (error: any) {
      results.details.apiEndpoint = error.message;
    }

  } catch (error) {
    console.error('网络诊断过程出错:', error);
  }

  return results;
};

export default api; 