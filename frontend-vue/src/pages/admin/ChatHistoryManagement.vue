<template>
  <div class="chat-history-management">
    <div class="page-header">
      <div class="header-title">
        <h1>AI聊天记录管理</h1>
        <p>管理和查看所有用户的AI助手聊天记录</p>
      </div>
      <div class="header-actions">
        <el-button @click="refreshData" :loading="loading">
          <i class="el-icon-refresh"></i>
          刷新数据
        </el-button>
        <el-button type="primary" @click="exportData">
          <i class="el-icon-download"></i>
          导出数据
        </el-button>
      </div>
    </div>

    <!-- 统计卡片 -->
    <div class="stats-cards">
      <div class="stat-card">
        <div class="stat-icon" style="background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);">
          <i class="el-icon-chat-dot-round"></i>
        </div>
        <div class="stat-content">
          <div class="stat-value">{{ statistics.summary?.total_sessions || 0 }}</div>
          <div class="stat-label">总会话数</div>
        </div>
      </div>
      <div class="stat-card">
        <div class="stat-icon" style="background: linear-gradient(135deg, #f093fb 0%, #f5576c 100%);">
          <i class="el-icon-message"></i>
        </div>
        <div class="stat-content">
          <div class="stat-value">{{ statistics.summary?.total_messages || 0 }}</div>
          <div class="stat-label">总消息数</div>
        </div>
      </div>
      <div class="stat-card">
        <div class="stat-icon" style="background: linear-gradient(135deg, #4facfe 0%, #00f2fe 100%);">
          <i class="el-icon-service"></i>
        </div>
        <div class="stat-content">
          <div class="stat-value">{{ Object.keys(statistics).filter(key => key !== 'summary').length }}</div>
          <div class="stat-label">活跃助手</div>
        </div>
      </div>
      <div class="stat-card">
        <div class="stat-icon" style="background: linear-gradient(135deg, #fa709a 0%, #fee140 100%);">
          <i class="el-icon-calendar"></i>
        </div>
        <div class="stat-content">
          <div class="stat-value">{{ todaySessionsCount }}</div>
          <div class="stat-label">今日会话</div>
        </div>
      </div>
    </div>

    <!-- 搜索和筛选 -->
    <div class="search-filters">
      <el-card>
        <el-form :model="searchForm" :inline="true" class="filter-form">
          <el-form-item label="助手类型">
            <el-select v-model="searchForm.assistant_type" placeholder="选择助手类型" clearable>
              <el-option label="客服助手" value="customer_service" />
              <el-option label="资讯助手" value="news_assistant" />
              <el-option label="交易助手" value="trading_assistant" />
            </el-select>
          </el-form-item>
          <el-form-item label="关键词">
            <el-input 
              v-model="searchForm.keyword" 
              placeholder="搜索聊天内容或用户信息"
              style="width: 200px;"
              clearable
            />
          </el-form-item>
          <el-form-item label="日期范围">
            <el-date-picker
              v-model="dateRange"
              type="datetimerange"
              range-separator="至"
              start-placeholder="开始日期"
              end-placeholder="结束日期"
              format="YYYY-MM-DD HH:mm:ss"
              value-format="YYYY-MM-DD HH:mm:ss"
              @change="handleDateRangeChange"
            />
          </el-form-item>
          <el-form-item>
            <el-button type="primary" @click="handleSearch" :loading="loading">
              <i class="el-icon-search"></i>
              搜索
            </el-button>
            <el-button @click="handleReset">
              <i class="el-icon-refresh-left"></i>
              重置
            </el-button>
          </el-form-item>
        </el-form>
      </el-card>
    </div>

    <!-- 聊天会话列表 -->
    <div class="sessions-list">
      <el-card>
        <div class="list-header">
          <h3>聊天会话记录</h3>
          <div class="list-actions">
            <el-button 
              v-if="selectedSessions.length > 0" 
              type="danger" 
              size="small"
              @click="handleBatchDelete"
            >
              <i class="el-icon-delete"></i>
              批量删除 ({{ selectedSessions.length }})
            </el-button>
          </div>
        </div>

        <el-table 
          :data="sessionsList" 
          v-loading="loading"
          @selection-change="handleSelectionChange"
          row-key="id"
        >
          <el-table-column type="selection" width="55" />
          <el-table-column label="助手类型" width="120">
            <template #default="{ row }">
              <el-tag 
                :type="getAssistantTagType(row.assistant_type)"
                size="small"
              >
                {{ getAssistantName(row.assistant_type) }}
              </el-tag>
            </template>
          </el-table-column>
          <el-table-column label="用户信息" width="150">
            <template #default="{ row }">
              <div class="user-info">
                <div class="username">
                  <span v-if="row.username">{{ row.username }}</span>
                  <span v-else-if="row.user_id" class="user-id">ID: {{ row.user_id.slice(-8) }}</span>
                  <span v-else class="anonymous">匿名用户</span>
                </div>
                <div v-if="row.user_info?.browser" class="user-detail">
                  {{ extractBrowserName(row.user_info.browser) }}
                </div>
              </div>
            </template>
          </el-table-column>
          <el-table-column label="会话信息" min-width="200">
            <template #default="{ row }">
              <div class="session-info">
                <div class="session-id">{{ row.session_id }}</div>
                <div v-if="row.user_info?.ip" class="ip-info">
                  IP: {{ row.user_info.ip }}
                </div>
              </div>
            </template>
          </el-table-column>
          <el-table-column label="消息统计" width="120">
            <template #default="{ row }">
              <div class="message-stats">
                <div class="message-count">{{ row.messages?.length || 0 }} 条消息</div>
                <div class="last-message" v-if="row.messages?.length > 0">
                  最后: {{ getLastMessagePreview(row.messages) }}
                </div>
              </div>
            </template>
          </el-table-column>
          <el-table-column label="创建时间" width="160">
            <template #default="{ row }">
              <div class="time-info">
                <div>{{ formatDateTime(row.created_at) }}</div>
                <div class="update-time">更新: {{ formatDateTime(row.updated_at) }}</div>
              </div>
            </template>
          </el-table-column>
          <el-table-column label="操作" width="180" fixed="right">
            <template #default="{ row }">
              <el-button type="primary" size="small" @click="viewSessionDetails(row)">
                <i class="el-icon-view"></i>
                查看详情
              </el-button>
              <el-button type="danger" size="small" @click="deleteSession(row)">
                <i class="el-icon-delete"></i>
                删除
              </el-button>
            </template>
          </el-table-column>
        </el-table>

        <!-- 分页 -->
        <div class="pagination-wrapper">
          <el-pagination
            v-model:current-page="pagination.page"
            v-model:page-size="pagination.pageSize"
            :page-sizes="[10, 20, 50, 100]"
            :total="pagination.total"
            layout="total, sizes, prev, pager, next, jumper"
            @size-change="handleSizeChange"
            @current-change="handlePageChange"
          />
        </div>
      </el-card>
    </div>

    <!-- 会话详情弹窗 -->
    <el-dialog 
      v-model="detailDialogVisible" 
      title="聊天会话详情" 
      width="800px"
      :before-close="handleDetailDialogClose"
    >
      <ChatSessionDetail 
        v-if="selectedSession" 
        :session="selectedSession"
        @close="detailDialogVisible = false"
      />
    </el-dialog>
  </div>
</template>

<script setup lang="ts">
import { ref, reactive, computed, onMounted } from 'vue';
import { ElMessage, ElMessageBox } from 'element-plus';
import { aiChatService } from '@/api/ai-chat';
import type { ChatSession, ChatHistoryQuery, AssistantType } from '@/types/ai-chat';
import ChatSessionDetail from '@/components/ChatSessionDetail.vue';

// 响应式数据
const loading = ref(false);
const sessionsList = ref<ChatSession[]>([]);
const selectedSessions = ref<ChatSession[]>([]);
const selectedSession = ref<ChatSession | null>(null);
const detailDialogVisible = ref(false);
const statistics = ref<any>({});
const dateRange = ref<[string, string] | null>(null);

// 搜索表单
const searchForm = reactive<Partial<ChatHistoryQuery>>({
  assistant_type: undefined,
  keyword: '',
  start_date: undefined,
  end_date: undefined,
});

// 分页参数
const pagination = reactive({
  page: 1,
  pageSize: 20,
  total: 0,
});

// 计算属性
const todaySessionsCount = computed(() => {
  const today = new Date().toISOString().split('T')[0];
  return sessionsList.value.filter(session => 
    session.created_at.startsWith(today)
  ).length;
});

// 初始化
onMounted(() => {
  loadData();
  loadStatistics();
});

// 加载数据
const loadData = async () => {
  loading.value = true;
  try {
    const query: any = {
      page: pagination.page,
      page_size: pagination.pageSize,
      ...searchForm,
    };

    const response = await aiChatService.adminGetAllSessions(query);
    sessionsList.value = response.sessions;
    pagination.total = response.total;
  } catch (error) {
    console.error('加载聊天记录失败:', error);
    ElMessage.error('加载聊天记录失败');
  } finally {
    loading.value = false;
  }
};

// 加载统计信息
const loadStatistics = async () => {
  try {
    statistics.value = await aiChatService.adminGetDetailedStatistics();
  } catch (error) {
    console.error('加载统计信息失败:', error);
  }
};

// 刷新数据
const refreshData = () => {
  loadData();
  loadStatistics();
};

// 处理搜索
const handleSearch = () => {
  pagination.page = 1;
  loadData();
};

// 重置搜索
const handleReset = () => {
  Object.assign(searchForm, {
    assistant_type: undefined,
    keyword: '',
    start_date: undefined,
    end_date: undefined,
  });
  dateRange.value = null;
  pagination.page = 1;
  loadData();
};

// 处理日期范围变化
const handleDateRangeChange = (value: [string, string] | null) => {
  if (value) {
    searchForm.start_date = value[0];
    searchForm.end_date = value[1];
  } else {
    searchForm.start_date = undefined;
    searchForm.end_date = undefined;
  }
};

// 分页处理
const handlePageChange = (page: number) => {
  pagination.page = page;
  loadData();
};

const handleSizeChange = (size: number) => {
  pagination.pageSize = size;
  pagination.page = 1;
  loadData();
};

// 选择处理
const handleSelectionChange = (selection: ChatSession[]) => {
  selectedSessions.value = selection;
};

// 查看会话详情
const viewSessionDetails = (session: ChatSession) => {
  selectedSession.value = session;
  detailDialogVisible.value = true;
};

// 关闭详情弹窗
const handleDetailDialogClose = () => {
  detailDialogVisible.value = false;
  selectedSession.value = null;
};

// 删除会话
const deleteSession = async (session: ChatSession) => {
  try {
    await ElMessageBox.confirm(
      `确定要删除会话 "${session.session_id}" 吗？此操作不可恢复。`,
      '确认删除',
      {
        confirmButtonText: '确定',
        cancelButtonText: '取消',
        type: 'warning',
      }
    );

    // 调用删除API
    const result = await aiChatService.deleteSession(session.session_id);
    if (result.success) {
      ElMessage.success(result.message || '删除成功');
      loadData();
    }
  } catch (error: any) {
    if (error !== 'cancel') {
      console.error('删除会话失败:', error);
      ElMessage.error(error.response?.data?.detail || '删除失败');
    }
  }
};

// 批量删除
const handleBatchDelete = async () => {
  try {
    await ElMessageBox.confirm(
      `确定要删除选中的 ${selectedSessions.value.length} 个会话吗？此操作不可恢复。`,
      '确认批量删除',
      {
        confirmButtonText: '确定',
        cancelButtonText: '取消',
        type: 'warning',
      }
    );

    // 调用批量删除API
    const sessionIds = selectedSessions.value.map(session => session.session_id);
    const result = await aiChatService.batchDeleteSessions(sessionIds);
    
    if (result.success) {
      ElMessage.success(`${result.message}，共删除 ${result.deleted_count} 个会话`);
      selectedSessions.value = [];
      loadData();
    }
  } catch (error: any) {
    if (error !== 'cancel') {
      console.error('批量删除会话失败:', error);
      ElMessage.error(error.response?.data?.detail || '批量删除失败');
    }
  }
};

// 导出数据
const exportData = () => {
  ElMessage.info('导出功能开发中...');
};

// 辅助函数
const getAssistantTagType = (type: AssistantType) => {
  const typeMap = {
    customer_service: 'primary',
    news_assistant: 'success',
    trading_assistant: 'warning',
  };
  return typeMap[type] || 'info';
};

const getAssistantName = (type: AssistantType) => {
  const nameMap = {
    customer_service: '客服助手',
    news_assistant: '资讯助手',
    trading_assistant: '交易助手',
  };
  return nameMap[type] || type;
};

const getLastMessagePreview = (messages: any[]) => {
  const lastMessage = messages[messages.length - 1];
  if (lastMessage) {
    return lastMessage.content.length > 20 
      ? lastMessage.content.substring(0, 20) + '...'
      : lastMessage.content;
  }
  return '';
};

const formatDateTime = (dateTime: string) => {
  return new Date(dateTime).toLocaleString('zh-CN');
};

const extractBrowserName = (browser: string) => {
  const browserMap = {
    'Chrome': '谷歌浏览器',
    'Firefox': '火狐浏览器',
    'Safari': '苹果浏览器',
    'Edge': '微软Edge',
    'IE': 'Internet Explorer',
    'Opera': '欧朋浏览器',
    'Mobile': '移动设备',
    'Tablet': '平板设备',
    'Unknown': '未知设备',
  };
  return browserMap[browser] || browser;
};
</script>

<style scoped>
.chat-history-management {
  padding: 20px;
}

.page-header {
  display: flex;
  justify-content: space-between;
  align-items: flex-start;
  margin-bottom: 24px;
}

.header-title h1 {
  margin: 0 0 8px;
  font-size: 24px;
  color: #303133;
}

.header-title p {
  margin: 0;
  color: #606266;
  font-size: 14px;
}

.header-actions {
  display: flex;
  gap: 12px;
}

.stats-cards {
  display: grid;
  grid-template-columns: repeat(auto-fit, minmax(250px, 1fr));
  gap: 20px;
  margin-bottom: 24px;
}

.stat-card {
  background: white;
  border-radius: 12px;
  padding: 24px;
  box-shadow: 0 2px 12px rgba(0, 0, 0, 0.1);
  display: flex;
  align-items: center;
  gap: 16px;
}

.stat-icon {
  width: 48px;
  height: 48px;
  border-radius: 12px;
  display: flex;
  align-items: center;
  justify-content: center;
  color: white;
  font-size: 20px;
}

.stat-content {
  flex: 1;
}

.stat-value {
  font-size: 28px;
  font-weight: bold;
  color: #303133;
  line-height: 1;
  margin-bottom: 4px;
}

.stat-label {
  font-size: 14px;
  color: #909399;
}

.search-filters {
  margin-bottom: 24px;
}

.filter-form {
  margin: 0;
}

.sessions-list {
  margin-bottom: 24px;
}

.list-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 16px;
}

.list-header h3 {
  margin: 0;
  font-size: 18px;
  color: #303133;
}

.session-info {
  line-height: 1.5;
}

.session-id {
  font-family: monospace;
  font-size: 12px;
  color: #909399;
  margin-bottom: 4px;
}

.user-info {
  font-size: 13px;
  color: #606266;
}

.user-info .anonymous {
  color: #f56c6c;
}

.user-info .ip-info {
  margin-left: 8px;
  color: #909399;
}

.message-stats {
  text-align: center;
}

.message-count {
  font-weight: bold;
  color: #303133;
  margin-bottom: 4px;
}

.last-message {
  font-size: 12px;
  color: #909399;
  line-height: 1.3;
}

.time-info {
  font-size: 13px;
  line-height: 1.4;
}

.update-time {
  color: #909399;
  font-size: 12px;
}

.pagination-wrapper {
  margin-top: 20px;
  text-align: center;
}
</style> 