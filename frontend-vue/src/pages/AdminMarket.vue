<template>
  <div class="admin-market">
    <!-- 页面标题 -->
    <div class="page-header">
      <div class="header-left">
        <h1>📈 行情管理</h1>
        <p>管理能源市场行情数据</p>
      </div>
    </div>

    <!-- 功能提示 -->
    <div class="feature-notice">
      <div class="notice-icon">🚧</div>
      <div class="notice-content">
        <h3>功能开发中</h3>
        <p>行情管理功能正在开发中，敬请期待。</p>
        <p>将包括：价格监控、市场分析、数据导入等功能。</p>
      </div>
    </div>

    <!-- 预览功能卡片 -->
    <div class="preview-features">
      <div class="feature-card">
        <div class="feature-icon">💰</div>
        <h3>价格监控</h3>
        <p>实时监控各类能源价格变化</p>
        <span class="status-badge developing">开发中</span>
      </div>
      
      <div class="feature-card">
        <div class="feature-icon">📊</div>
        <h3>市场分析</h3>
        <p>提供专业的市场趋势分析</p>
        <span class="status-badge developing">开发中</span>
      </div>
      
      <div class="feature-card">
        <div class="feature-icon">📥</div>
        <h3>数据导入</h3>
        <p>支持批量导入行情数据</p>
        <span class="status-badge developing">开发中</span>
      </div>
      
      <div class="feature-card">
        <div class="feature-icon">📈</div>
        <h3>图表展示</h3>
        <p>可视化展示价格走势图表</p>
        <span class="status-badge developing">开发中</span>
      </div>
    </div>
  </div>
</template>

<script setup lang="ts">
// 暂时无需逻辑，仅展示页面结构
</script>

<style scoped>
.admin-market {
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

.feature-notice {
  background: white;
  border-radius: 12px;
  padding: 32px;
  margin-bottom: 32px;
  display: flex;
  align-items: center;
  gap: 24px;
  box-shadow: 0 2px 8px rgba(0, 0, 0, 0.1);
  border-left: 4px solid #f6ad55;
}

.notice-icon {
  font-size: 48px;
  opacity: 0.8;
}

.notice-content h3 {
  margin: 0 0 8px 0;
  color: #2d3748;
  font-size: 20px;
  font-weight: 600;
}

.notice-content p {
  margin: 0 0 8px 0;
  color: #4a5568;
  line-height: 1.5;
}

.notice-content p:last-child {
  margin-bottom: 0;
}

.preview-features {
  display: grid;
  grid-template-columns: repeat(auto-fit, minmax(280px, 1fr));
  gap: 24px;
}

.feature-card {
  background: white;
  border-radius: 12px;
  padding: 24px;
  text-align: center;
  box-shadow: 0 2px 8px rgba(0, 0, 0, 0.1);
  transition: transform 0.2s;
  position: relative;
}

.feature-card:hover {
  transform: translateY(-2px);
}

.feature-icon {
  font-size: 48px;
  margin-bottom: 16px;
}

.feature-card h3 {
  margin: 0 0 8px 0;
  color: #2d3748;
  font-size: 18px;
  font-weight: 600;
}

.feature-card p {
  margin: 0 0 16px 0;
  color: #718096;
  line-height: 1.5;
}

.status-badge {
  display: inline-block;
  padding: 4px 12px;
  border-radius: 20px;
  font-size: 12px;
  font-weight: 500;
}

.status-badge.developing {
  background: #fed7d7;
  color: #c53030;
}

/* 响应式设计 */
@media (max-width: 768px) {
  .feature-notice {
    flex-direction: column;
    text-align: center;
  }
  
  .preview-features {
    grid-template-columns: 1fr;
  }
}
</style> 