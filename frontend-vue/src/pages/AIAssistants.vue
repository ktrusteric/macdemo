<template>
  <div class="dashboard-container">
    <div class="header-section">
      <h1 class="page-title">
        <el-icon class="title-icon"><ChatDotRound /></el-icon>
        AI 智能助手
      </h1>
      <p class="page-subtitle">智能化的能源资讯咨询和分析服务</p>
    </div>
    
    <el-card class="content-card">
      <h2>AI 助手</h2>
      <p>这里是 AI 助手页面。</p>
    </el-card>

    <!-- 页面宽度占位符 - 不可见但确保页面宽度一致 -->
    <div class="width-placeholder" aria-hidden="true"></div>
  </div>
</template>

<script setup>
import { ChatDotRound } from '@element-plus/icons-vue'
</script>

<style scoped>
.dashboard-container {
  min-height: 100vh;
  max-width: 1280px;
  margin: 0 auto;
}

.header-section {
  text-align: center;
  margin-bottom: 32px;
  padding: 32px;
  background: white;
  border-radius: 16px;
  box-shadow: 0 4px 20px rgba(0,0,0,0.1);
}

.page-title {
  font-size: 32px;
  font-weight: bold;
  color: #1769aa;
  margin-bottom: 12px;
  display: flex;
  align-items: center;
  justify-content: center;
  gap: 16px;
}

.title-icon {
  font-size: 36px;
  color: #1890ff;
}

.page-subtitle {
  font-size: 16px;
  color: #666;
  margin: 0;
}

.content-card {
  border-radius: 12px;
  box-shadow: 0 2px 12px rgba(0,0,0,0.08);
}

/* 页面宽度占位符 - 不可见但确保页面宽度一致 */
.width-placeholder {
  width: 1280px;
  min-width: 1280px;
  height: 1px;
  visibility: hidden;
  pointer-events: none;
  position: relative;
  margin: 0 auto;
}
</style> 