<template>
  <div class="admin-ai">
    <!-- 页面标题 -->
    <div class="page-header">
      <div class="header-left">
        <h1>🤖 AI助手管理</h1>
        <p>管理系统中的AI助手配置</p>
      </div>
    </div>

    <!-- AI助手列表 -->
    <div class="ai-assistants">
      <div class="assistant-card">
        <div class="assistant-header">
          <div class="assistant-icon">🛠️</div>
          <div class="assistant-info">
            <h3>客服助手</h3>
            <p>为用户提供智能客服支持</p>
          </div>
          <div class="assistant-status">
            <span class="status-badge active">运行中</span>
          </div>
        </div>
        
        <div class="assistant-details">
          <div class="detail-item">
            <span class="detail-label">助手ID:</span>
            <span class="detail-value">9714d9bc-31ca-40b5-a720-4329f5fc4af7</span>
          </div>
          <div class="detail-item">
            <span class="detail-label">Token:</span>
            <span class="detail-value">e0dc8833077b48669a04ad4a70a7ebe2</span>
          </div>
          <div class="detail-item">
            <span class="detail-label">功能:</span>
            <span class="detail-value">用户咨询、问题解答、系统帮助</span>
          </div>
        </div>
      </div>

      <div class="assistant-card">
        <div class="assistant-header">
          <div class="assistant-icon">📰</div>
          <div class="assistant-info">
            <h3>资讯助手</h3>
            <p>提供能源资讯智能推荐</p>
          </div>
          <div class="assistant-status">
            <span class="status-badge active">运行中</span>
          </div>
        </div>
        
        <div class="assistant-details">
          <div class="detail-item">
            <span class="detail-label">助手ID:</span>
            <span class="detail-value">158ab70e-2996-4cce-9822-6f8195a7cfa5</span>
          </div>
          <div class="detail-item">
            <span class="detail-label">Token:</span>
            <span class="detail-value">9bc6008decb94efeaee65dd076aab5e8</span>
          </div>
          <div class="detail-item">
            <span class="detail-label">功能:</span>
            <span class="detail-value">资讯推荐、内容分析、趋势预测</span>
          </div>
        </div>
      </div>

      <div class="assistant-card">
        <div class="assistant-header">
          <div class="assistant-icon">💼</div>
          <div class="assistant-info">
            <h3>交易助手</h3>
            <p>协助用户进行能源交易</p>
          </div>
          <div class="assistant-status">
            <span class="status-badge active">运行中</span>
          </div>
        </div>
        
        <div class="assistant-details">
          <div class="detail-item">
            <span class="detail-label">助手ID:</span>
            <span class="detail-value">1e72acc1-43a8-4cda-8d54-f409c9c5d5ed</span>
          </div>
          <div class="detail-item">
            <span class="detail-label">Token:</span>
            <span class="detail-value">18703d14357040c88f32ae5e4122c2d6</span>
          </div>
          <div class="detail-item">
            <span class="detail-label">功能:</span>
            <span class="detail-value">交易咨询、价格分析、风险评估</span>
          </div>
        </div>
      </div>
    </div>

    <!-- AI服务配置 -->
    <div class="ai-config">
      <h2>🔧 AI服务配置</h2>
      <div class="config-grid">
        <div class="config-item">
          <label>后端服务地址</label>
          <input type="text" value="https://ai.wiseocean.cn" readonly />
        </div>
        
        <div class="config-item">
          <label>API超时时间</label>
          <input type="text" value="30秒" readonly />
        </div>
        
        <div class="config-item">
          <label>服务状态</label>
          <span class="status-badge active">正常运行</span>
        </div>
        
        <div class="config-item">
          <label>最后检查时间</label>
          <span class="time-value">{{ currentTime }}</span>
        </div>
      </div>
    </div>

    <!-- 使用统计 -->
    <div class="usage-stats">
      <h2>📊 使用统计</h2>
      <div class="stats-grid">
        <div class="stat-item">
          <div class="stat-icon">💬</div>
          <div class="stat-content">
            <h3>1,234</h3>
            <p>今日对话次数</p>
          </div>
        </div>
        
        <div class="stat-item">
          <div class="stat-icon">👥</div>
          <div class="stat-content">
            <h3>567</h3>
            <p>活跃用户数</p>
          </div>
        </div>
        
        <div class="stat-item">
          <div class="stat-icon">⚡</div>
          <div class="stat-content">
            <h3>98.5%</h3>
            <p>服务可用率</p>
          </div>
        </div>
        
        <div class="stat-item">
          <div class="stat-icon">⏱️</div>
          <div class="stat-content">
            <h3>1.2s</h3>
            <p>平均响应时间</p>
          </div>
        </div>
      </div>
    </div>
  </div>
</template>

<script setup lang="ts">
import { ref, onMounted } from 'vue'

const currentTime = ref('')

// 更新当前时间
const updateTime = () => {
  currentTime.value = new Date().toLocaleString('zh-CN')
}

// 组件挂载时更新时间
onMounted(() => {
  updateTime()
  // 每分钟更新一次时间
  setInterval(updateTime, 60000)
})
</script>

<style scoped>
.admin-ai {
  background: #f5f7fa;
  min-height: 100%;
}

.page-header {
  background: white;
  border-radius: 12px;
  padding: 24px;
  margin-bottom: 24px;
  box-shadow: 0 2px 8px rgba(0, 0, 0, 0.1);
}

.header-left h1 {
  margin: 0 0 8px 0;
  color: #2d3748;
  font-size: 24px;
  font-weight: 600;
}

.header-left p {
  margin: 0;
  color: #718096;
  font-size: 14px;
}

.ai-assistants {
  display: flex;
  flex-direction: column;
  gap: 20px;
  margin-bottom: 32px;
}

.assistant-card {
  background: white;
  border-radius: 12px;
  padding: 24px;
  box-shadow: 0 2px 8px rgba(0, 0, 0, 0.1);
  transition: transform 0.2s;
}

.assistant-card:hover {
  transform: translateY(-2px);
}

.assistant-header {
  display: flex;
  align-items: center;
  gap: 16px;
  margin-bottom: 16px;
}

.assistant-icon {
  font-size: 32px;
  width: 60px;
  height: 60px;
  display: flex;
  align-items: center;
  justify-content: center;
  background: #edf2f7;
  border-radius: 12px;
}

.assistant-info {
  flex: 1;
}

.assistant-info h3 {
  margin: 0 0 4px 0;
  color: #2d3748;
  font-size: 18px;
  font-weight: 600;
}

.assistant-info p {
  margin: 0;
  color: #718096;
  font-size: 14px;
}

.assistant-status {
  margin-left: auto;
}

.status-badge {
  display: inline-block;
  padding: 4px 12px;
  border-radius: 20px;
  font-size: 12px;
  font-weight: 500;
}

.status-badge.active {
  background: #c6f6d5;
  color: #22543d;
}

.assistant-details {
  display: flex;
  flex-direction: column;
  gap: 8px;
  padding-top: 16px;
  border-top: 1px solid #e2e8f0;
}

.detail-item {
  display: flex;
  align-items: center;
  gap: 12px;
}

.detail-label {
  font-weight: 500;
  color: #4a5568;
  min-width: 80px;
  font-size: 14px;
}

.detail-value {
  color: #2d3748;
  font-family: monospace;
  font-size: 13px;
  background: #f7fafc;
  padding: 2px 8px;
  border-radius: 4px;
}

.ai-config, .usage-stats {
  background: white;
  border-radius: 12px;
  padding: 24px;
  margin-bottom: 24px;
  box-shadow: 0 2px 8px rgba(0, 0, 0, 0.1);
}

.ai-config h2, .usage-stats h2 {
  margin: 0 0 20px 0;
  color: #2d3748;
  font-size: 20px;
  font-weight: 600;
}

.config-grid {
  display: grid;
  grid-template-columns: repeat(auto-fit, minmax(250px, 1fr));
  gap: 20px;
}

.config-item {
  display: flex;
  flex-direction: column;
  gap: 8px;
}

.config-item label {
  font-weight: 500;
  color: #4a5568;
  font-size: 14px;
}

.config-item input {
  padding: 10px 12px;
  border: 2px solid #e2e8f0;
  border-radius: 8px;
  font-size: 14px;
  background: #f7fafc;
}

.time-value {
  color: #2d3748;
  font-size: 14px;
  padding: 10px 12px;
  background: #f7fafc;
  border-radius: 8px;
}

.stats-grid {
  display: grid;
  grid-template-columns: repeat(auto-fit, minmax(200px, 1fr));
  gap: 20px;
}

.stat-item {
  display: flex;
  align-items: center;
  gap: 16px;
  padding: 20px;
  background: #f7fafc;
  border-radius: 12px;
  transition: transform 0.2s;
}

.stat-item:hover {
  transform: translateY(-2px);
}

.stat-icon {
  font-size: 32px;
  width: 50px;
  height: 50px;
  display: flex;
  align-items: center;
  justify-content: center;
  background: white;
  border-radius: 10px;
}

.stat-content h3 {
  margin: 0 0 4px 0;
  font-size: 24px;
  font-weight: 600;
  color: #2d3748;
}

.stat-content p {
  margin: 0;
  color: #718096;
  font-size: 14px;
}

/* 响应式设计 */
@media (max-width: 768px) {
  .assistant-header {
    flex-direction: column;
    align-items: flex-start;
    gap: 12px;
  }
  
  .assistant-status {
    margin-left: 0;
    align-self: flex-end;
  }
  
  .config-grid, .stats-grid {
    grid-template-columns: 1fr;
  }
  
  .detail-item {
    flex-direction: column;
    align-items: flex-start;
    gap: 4px;
  }
  
  .detail-label {
    min-width: auto;
  }
}
</style> 