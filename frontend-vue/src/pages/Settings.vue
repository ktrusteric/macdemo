<template>
  <div class="dashboard-container">
    <!-- 页面头部 -->
    <div class="header-section">
      <h1 class="page-title">
        <el-icon class="title-icon"><Setting /></el-icon>
        个人设置
      </h1>
      <p class="page-subtitle">配置您的个人偏好设置</p>
    </div>

    <!-- 设置选项卡 -->
    <el-card class="settings-card">
      <el-tabs v-model="activeSettingTab" type="border-card" class="settings-tabs">
        <!-- 标签设置 -->
        <el-tab-pane label="标签设置" name="tags">
          <div class="settings-content">
            <!-- 加载状态 -->
            <div v-if="loading && !tags.length" class="loading-container">
              <el-skeleton animated>
                <template #template>
                  <el-skeleton-item variant="h1" />
                  <el-skeleton-item variant="text" />
                  <el-skeleton-item variant="text" />
                </template>
              </el-skeleton>
            </div>

            <!-- 错误提示 -->
            <el-alert 
              v-if="error" 
              :title="error" 
              type="error" 
              show-icon 
              class="error-alert"
              @close="error = ''"
            />

            <!-- 统计概览 -->
            <el-row :gutter="20" class="stats-section" v-if="!loading">
              <el-col :span="6">
                <el-card class="stat-card">
                  <el-statistic title="标签总数" :value="totalTagsCount" />
                  <div class="stat-icon">🏷️</div>
                </el-card>
              </el-col>
              <el-col :span="6">
                <el-card class="stat-card">
                  <el-statistic title="启用分类" :value="activeCategoriesCount" />
                  <div class="stat-icon">📂</div>
                </el-card>
              </el-col>
              <el-col :span="6">
                <el-card class="stat-card">
                  <el-statistic title="总权重" :value="totalWeight" :precision="1" />
                  <div class="stat-icon">⚖️</div>
                </el-card>
              </el-col>
              <el-col :span="6">
                <el-card class="stat-card">
                  <el-statistic title="最后更新" :value="lastUpdateTime" />
                  <div class="stat-icon">🔄</div>
                </el-card>
              </el-col>
            </el-row>

            <!-- 标签预览 -->
            <el-card class="preview-card" v-if="tags.length">
              <template #header>
                <div class="preview-header">
                  <span class="preview-title">我的标签</span>
                  <div class="action-buttons">
                    <el-tooltip content="从服务器重新加载您的标签数据" placement="top">
                      <el-button 
                        type="primary" 
                        @click="fetchTags" 
                        :loading="loading"
                      >
                        <el-icon><Refresh /></el-icon>
                        刷新标签
                      </el-button>
                    </el-tooltip>
                    <el-tooltip content="将当前修改保存到服务器" placement="top">
                      <el-button 
                        type="success" 
                        @click="saveUserTags" 
                        :loading="saving"
                        :disabled="!hasChanges"
                      >
                        <el-icon><Check /></el-icon>
                        保存更改
                      </el-button>
                    </el-tooltip>
                    <el-tooltip content="保留注册地、省份、区域和能源产品标签，清理其他标签" placement="top">
                      <el-button 
                        type="warning"
                        @click="resetToDefaults"
                      >
                        <el-icon><RefreshLeft /></el-icon>
                        重置标签
                      </el-button>
                    </el-tooltip>
                    <el-tooltip content="移除重复的标签，保持数据整洁" placement="top">
                      <el-button 
                        type="info"
                        @click="cleanDuplicates"
                      >
                        <el-icon><Delete /></el-icon>
                        清理重复
                      </el-button>
                    </el-tooltip>
                  </div>
                </div>
              </template>
              <div class="preview-content">
                <div class="all-tags-cloud">
                  <el-tag
                    v-for="tag in sortedTagsForPreview"
                    :key="`preview-${tag.category}-${tag.name}`"
                    :type="getTagTypeByCategory(tag.category)"
                    :effect="tag.source === 'preset' ? 'dark' : 'plain'"
                    class="preview-tag"
                  >
                    {{ tag.name }}
                  </el-tag>
                </div>
              </div>
            </el-card>

            <!-- 标签分类管理 -->
            <el-card class="tags-card">
              <template #header>
                <div class="tags-header">
                  <span class="tags-title">标签分类管理</span>
                </div>
              </template>

              <el-tabs v-model="activeTab" type="border-card" class="tags-tabs">
                <el-tab-pane 
                  v-for="category in tagCategories" 
                  :key="category.key" 
                  :name="category.key"
                >
                  <template #label>
                    <div class="tab-label">
                      <span>{{ category.name }}</span>
                      <el-badge 
                        :value="getTagsByCategory(category.key).length" 
                        :type="getBadgeType(category.key)"
                        :hidden="getTagsByCategory(category.key).length === 0"
                      />
                    </div>
                  </template>

                  <div class="tab-content">
                    <!-- 分类描述 -->
                    <div class="category-description">
                      <el-icon class="desc-icon"><InfoFilled /></el-icon>
                      <span>{{ category.description }}</span>
                    </div>

                    <!-- 当前标签 -->
                    <div class="current-tags-section">
                      <h4 class="section-title">当前标签</h4>
                      <div class="tags-container" v-if="getTagsByCategory(category.key).length">
                        <div
                          v-for="tag in getTagsByCategory(category.key)"
                          :key="`${tag.category}-${tag.name}`"
                          class="tag-item-wrapper"
                        >
                          <!-- 新的标签显示包装器 -->
                          <div v-if="!tag.isEditing" class="tag-display-wrapper">
                            <el-tag
                              :type="getTagTypeByCategory(category.key)"
                              :effect="tag.source === 'preset' ? 'dark' : 'plain'"
                              class="tag-item-display"
                              @click="startEditWeight(tag)"
                            >
                              <div class="tag-content">
                                <span class="tag-name">{{ tag.name }}</span>
                                <span class="tag-weight">{{ tag.weight }}x</span>
                              </div>
                            </el-tag>
                            <div class="tag-actions">
                              <el-icon class="edit-icon" @click.stop="startEditWeight(tag)" title="点击编辑权重">
                                <Edit />
                              </el-icon>
                              <el-icon class="delete-icon" @click.stop="removeTag(tag)" title="删除标签">
                                <Close />
                              </el-icon>
                            </div>
                          </div>
                          
                          <!-- 权重编辑器 -->
                          <div v-else class="tag-weight-editor">
                            <div class="editor-content">
                              <span class="editing-tag-name">{{ tag.name }}</span>
                              <el-input-number
                                v-model="tag.editingWeight"
                                :min="0.1"
                                :max="5.0"
                                :step="0.1"
                                :precision="1"
                                size="small"
                                class="weight-editor-input"
                                @keyup.enter="confirmEditWeight(tag)"
                                @keyup.esc="cancelEditWeight(tag)"
                              />
                              <div class="weight-editor-actions">
                                <el-button 
                                  type="success" 
                                  size="small"
                                  @click="confirmEditWeight(tag)"
                                >
                                  <el-icon><Check /></el-icon>
                                </el-button>
                                <el-button 
                                  type="info" 
                                  size="small"
                                  @click="cancelEditWeight(tag)"
                                >
                                  <el-icon><Close /></el-icon>
                                </el-button>
                              </div>
                            </div>
                          </div>
                        </div>
                      </div>
                      <div v-else class="empty-tags">
                        <p>暂无{{ tagCategories.find(cat => cat.key === category.key)?.name }}标签</p>
                      </div>
                    </div>

                    <!-- 预设标签 -->
                    <div class="preset-tags-section" v-if="category.key !== 'region'">
                      <h4 class="section-title">
                        预设标签
                        <div class="preset-actions">
                          <span class="preset-hint">点击添加 →</span>
                          <el-button 
                            type="primary" 
                            link 
                            @click="addAllPresetTags(category)"
                            size="small"
                          >
                            全部添加
                          </el-button>
                        </div>
                      </h4>
                      <div class="preset-tags-container">
                        <el-tag
                          v-for="presetTag in getAvailablePresetTags(category.key)"
                          :key="presetTag"
                          :type="getTagTypeByCategory(category.key)"
                          effect="plain"
                          @click="addPresetTagDirectly(category.key, presetTag)"
                          class="preset-tag-item"
                        >
                          <el-icon><Plus /></el-icon>
                          {{ presetTag }}
                        </el-tag>
                      </div>
                    </div>

                    <!-- 地域标签的特殊省份-城市选择器 -->
                    <div class="region-selector-section" v-if="category.key === 'region'">
                      <h4 class="section-title">
                        省份城市选择器
                        <div class="selector-hint">
                          <span class="selector-hint-text">选择省份和城市，自动生成地区标签</span>
                        </div>
                      </h4>
                      
                      <div class="region-selector-container">
                        <div class="region-selector-row">
                          <el-select 
                            v-model="regionSelector.selectedProvince" 
                            placeholder="选择省份" 
                            filterable 
                            @change="handleRegionProvinceChange"
                            class="province-selector"
                          >
                            <el-option 
                              v-for="province in regionProvinces" 
                              :key="province.code" 
                              :label="province.name" 
                              :value="province.code"
                            >
                              <div style="display: flex; justify-content: space-between; align-items: center;">
                                <span>{{ province.name }}</span>
                                <el-tag size="small" type="info">{{ province.city_count }}个城市</el-tag>
                              </div>
                            </el-option>
                          </el-select>
                          
                          <el-select 
                            v-model="regionSelector.selectedCity" 
                            placeholder="选择城市" 
                            filterable 
                            @change="handleRegionCityChange"
                            class="city-selector"
                            :disabled="!regionSelector.availableCities.length"
                          >
                            <el-option 
                              v-for="city in regionSelector.availableCities" 
                              :key="city" 
                              :label="city" 
                              :value="city" 
                            />
                          </el-select>
                          
                          <el-button 
                            type="success" 
                            @click="addRegionTags"
                            :disabled="!regionSelector.selectedCity"
                          >
                            <el-icon><Plus /></el-icon>
                            添加地区标签
                          </el-button>
                        </div>
                        
                        <!-- 预览将要添加的标签 -->
                        <div class="region-preview" v-if="regionSelector.previewTags.length">
                          <el-text type="info" size="small">将添加以下标签：</el-text>
                          <div class="preview-tags">
                            <el-tag 
                              v-for="tag in regionSelector.previewTags" 
                              :key="tag.name"
                              :type="tag.level === 'city' ? 'success' : tag.level === 'province' ? 'info' : 'warning'"
                              size="small"
                            >
                              {{ tag.name }} ({{ tag.level === 'city' ? '城市' : tag.level === 'province' ? '省份' : '区域' }})
                            </el-tag>
                          </div>
                        </div>
                      </div>
                    </div>
                  </div>
                </el-tab-pane>
              </el-tabs>
            </el-card>
          </div>
        </el-tab-pane>

        <!-- 收藏管理 -->
        <el-tab-pane label="收藏管理" name="favorites">
          <div class="settings-content">
            <!-- 搜索和筛选 -->
            <el-card class="search-card">
              <!-- 基础搜索行 -->
              <el-row :gutter="20" align="middle" class="search-row">
                <el-col :span="8">
                  <el-input
                    v-model="searchQuery"
                    placeholder="搜索收藏的文章标题、来源、标签..."
                    size="large"
                    clearable
                    @input="handleSearch"
                    @clear="handleSearchClear"
                    @keyup.enter="performSearch"
                  >
                    <template #prefix>
                      <el-icon><Search /></el-icon>
                    </template>
                  </el-input>
                </el-col>
                <el-col :span="3">
                  <el-button 
                    type="primary" 
                    size="large" 
                    @click="performSearch"
                    :loading="favoritesLoading"
                    style="width: 100%"
                  >
                    <el-icon><Search /></el-icon>
                    搜索
                  </el-button>
                </el-col>
                <el-col :span="3">
                  <el-button 
                    size="large" 
                    @click="resetAllFilters"
                    style="width: 100%"
                  >
                    <el-icon><Refresh /></el-icon>
                    重置
                  </el-button>
                </el-col>
                <el-col :span="3">
                  <el-button 
                    :type="showAdvancedFilters ? 'primary' : ''"
                    size="large" 
                    @click="toggleAdvancedFilters"
                    style="width: 100%"
                  >
                    <el-icon><Setting /></el-icon>
                    筛选
                  </el-button>
                </el-col>
                <el-col :span="7">
                  <div class="search-stats">
                    <span class="search-result-text">
                      <template v-if="hasActiveFilters">
                        筛选到 <strong>{{ filteredFavorites.length }}</strong> 篇文章
                      </template>
                      <template v-else-if="searchQuery">
                        搜索到 <strong>{{ filteredFavorites.length }}</strong> 篇文章
                      </template>
                      <template v-else>
                        共 <strong>{{ favorites.length }}</strong> 篇收藏
                      </template>
                    </span>
                  </div>
                </el-col>
              </el-row>

              <!-- 高级筛选面板 -->
              <el-collapse-transition>
                <div v-show="showAdvancedFilters" class="advanced-filters">
                  <el-divider content-position="left">
                    <el-icon><Setting /></el-icon>
                    高级筛选
                  </el-divider>
                  
                  <el-row :gutter="16" class="filter-row">
                    <!-- 内容类型筛选 -->
                    <el-col :span="6">
                      <div class="filter-group">
                        <label class="filter-label">内容类型</label>
                        <el-select 
                          v-model="filters.contentType" 
                          placeholder="选择内容类型"
                          clearable
                          @change="applyFilters"
                          style="width: 100%"
                        >
                          <el-option label="全部类型" value="" />
                          <el-option 
                            v-for="(count, type) in contentTypeStats" 
                            :key="type"
                            :label="`${getContentTypeLabel(type)} (${count})`"
                            :value="type"
                          >
                            <div style="display: flex; justify-content: space-between; align-items: center;">
                              <el-tag :type="getContentTypeColor(type)" size="small">
                                {{ getContentTypeLabel(type) }}
                              </el-tag>
                              <span style="color: #8492a6; font-size: 12px;">{{ count }}篇</span>
                            </div>
                          </el-option>
                        </el-select>
                      </div>
                    </el-col>

                    <!-- 能源类型筛选 -->
                    <el-col :span="6">
                      <div class="filter-group">
                        <label class="filter-label">能源类型</label>
                        <el-select 
                          v-model="filters.energyType" 
                          placeholder="选择能源类型"
                          clearable
                          filterable
                          @change="applyFilters"
                          style="width: 100%"
                        >
                          <el-option label="全部能源" value="" />
                          <el-option 
                            v-for="(count, energyType) in allEnergyTypeStats" 
                            :key="energyType"
                            :label="`${energyType} (${count})`"
                            :value="energyType"
                          >
                            <div style="display: flex; justify-content: space-between; align-items: center;">
                              <el-tag type="warning" size="small">{{ energyType }}</el-tag>
                              <span style="color: #8492a6; font-size: 12px;">{{ count }}篇</span>
                            </div>
                          </el-option>
                        </el-select>
                      </div>
                    </el-col>

                    <!-- 地区筛选 -->
                    <el-col :span="6">
                      <div class="filter-group">
                        <label class="filter-label">地区</label>
                        <el-select 
                          v-model="filters.region" 
                          placeholder="选择地区"
                          clearable
                          filterable
                          @change="applyFilters"
                          style="width: 100%"
                        >
                          <el-option label="全部地区" value="" />
                          <el-option 
                            v-for="(count, region) in allRegionStats" 
                            :key="region"
                            :label="`${region} (${count})`"
                            :value="region"
                          >
                            <div style="display: flex; justify-content: space-between; align-items: center;">
                              <el-tag type="success" size="small">{{ region }}</el-tag>
                              <span style="color: #8492a6; font-size: 12px;">{{ count }}篇</span>
                            </div>
                          </el-option>
                        </el-select>
                      </div>
                    </el-col>

                    <!-- 时间范围筛选 -->
                    <el-col :span="6">
                      <div class="filter-group">
                        <label class="filter-label">收藏时间</label>
                        <el-select 
                          v-model="filters.timeRange" 
                          placeholder="选择时间范围"
                          clearable
                          @change="applyFilters"
                          style="width: 100%"
                        >
                          <el-option label="全部时间" value="" />
                          <el-option label="最近7天" value="7days" />
                          <el-option label="最近30天" value="30days" />
                          <el-option label="最近3个月" value="3months" />
                          <el-option label="最近6个月" value="6months" />
                          <el-option label="最近1年" value="1year" />
                        </el-select>
                      </div>
                    </el-col>
                  </el-row>

                  <!-- 我的标签筛选 -->
                  <el-row class="filter-row">
                    <el-col :span="24">
                      <div class="filter-group">
                        <label class="filter-label">
                          <el-icon><InfoFilled /></el-icon>
                          按我的标签筛选
                        </label>
                        <div class="my-tags-filter">
                          <el-tag
                            v-for="tag in availableUserTags"
                            :key="tag.name"
                            :type="filters.userTags.includes(tag.name) ? getTagTypeByCategory(tag.category) : 'info'"
                            :effect="filters.userTags.includes(tag.name) ? 'dark' : 'plain'"
                            @click="toggleUserTagFilter(tag.name)"
                            class="user-tag-filter"
                          >
                            <el-icon v-if="filters.userTags.includes(tag.name)"><Check /></el-icon>
                            {{ tag.name }}
                            <span class="tag-weight">({{ tag.weight }}x)</span>
                          </el-tag>
                        </div>
                      </div>
                    </el-col>
                  </el-row>

                  <!-- 筛选结果统计 -->
                  <div class="filter-summary" v-if="hasActiveFilters">
                    <el-alert 
                      :title="`已应用 ${activeFiltersCount} 个筛选条件，找到 ${filteredFavorites.length} 篇文章`"
                      type="info" 
                      :closable="false"
                      show-icon
                    >
                      <template #default>
                        <div class="active-filters">
                          <el-tag 
                            v-if="filters.contentType"
                            type="primary" 
                            closable 
                            @close="filters.contentType = ''; applyFilters()"
                          >
                            类型: {{ getContentTypeLabel(filters.contentType) }}
                          </el-tag>
                          <el-tag 
                            v-if="filters.energyType"
                            type="warning" 
                            closable 
                            @close="filters.energyType = ''; applyFilters()"
                          >
                            能源: {{ filters.energyType }}
                          </el-tag>
                          <el-tag 
                            v-if="filters.region"
                            type="success" 
                            closable 
                            @close="filters.region = ''; applyFilters()"
                          >
                            地区: {{ filters.region }}
                          </el-tag>
                          <el-tag 
                            v-if="filters.timeRange"
                            type="info" 
                            closable 
                            @close="filters.timeRange = ''; applyFilters()"
                          >
                            时间: {{ getTimeRangeLabel(filters.timeRange) }}
                          </el-tag>
                          <el-tag 
                            v-for="userTag in filters.userTags"
                            :key="userTag"
                            type="danger" 
                            closable 
                            @close="toggleUserTagFilter(userTag)"
                          >
                            标签: {{ userTag }}
                          </el-tag>
                        </div>
                      </template>
                    </el-alert>
                  </div>
                </div>
              </el-collapse-transition>
            </el-card>

            <!-- 收藏文章列表 -->
            <el-card class="favorites-card">
              <template #header>
                <div class="card-header">
                  <span class="card-title">收藏文章</span>
                  <el-button type="primary" @click="loadFavorites" :loading="favoritesLoading">
                    <el-icon><Refresh /></el-icon>
                    刷新
                  </el-button>
                </div>
              </template>

              <div v-loading="favoritesLoading" class="favorites-list">
                <div v-if="filteredFavorites.length === 0 && !favoritesLoading" class="empty-state">
                  <el-empty :description="hasActiveFilters ? '没有找到符合条件的收藏文章' : '还没有收藏任何文章'">
                    <el-button v-if="hasActiveFilters" type="primary" @click="resetAllFilters">
                      清除筛选条件
                    </el-button>
                    <el-button v-else type="primary" @click="$router.push('/content')">
                      去发现内容
                    </el-button>
                  </el-empty>
                </div>

                <div v-else class="favorite-items">
                  <el-card 
                    v-for="item in filteredFavorites" 
                    :key="item._id"
                    class="favorite-item"
                    shadow="hover"
                  >
                    <div class="favorite-item-body">
                      <div class="favorite-main">
                        <div class="favorite-meta">
                          <el-tag 
                            :type="getContentTypeColor(item.type)" 
                            size="small"
                            class="content-type-tag"
                          >
                            {{ getContentTypeLabel(item.type) }}
                          </el-tag>
                          <span class="favorite-source">{{ item.source }}</span>
                          <span class="favorite-date">收藏于 {{ formatDate(item.favorited_at) }}</span>
                        </div>
                        <h3 class="favorite-title">
                          <a 
                            v-if="item.link" 
                            :href="item.link" 
                            target="_blank" 
                            rel="noopener noreferrer"
                            class="article-link"
                          >
                            {{ item.title }}
                            <el-icon class="external-link-icon"><TopRight /></el-icon>
                          </a>
                          <span v-else>{{ item.title }}</span>
                        </h3>
                        <p class="favorite-publish-date">发布于 {{ formatDate(item.publish_date) }}</p>
                        <div class="favorite-tags" v-if="getAllTagsFromFavorite(item).length">
                          <el-tag 
                            v-for="tag in getAllTagsFromFavorite(item).slice(0, 8)" 
                            :key="tag"
                            size="small"
                            class="favorite-tag"
                            :type="getTagColor(tag)"
                          >
                            {{ tag }}
                          </el-tag>
                          <span v-if="getAllTagsFromFavorite(item).length > 8" class="more-tags">
                            +{{ getAllTagsFromFavorite(item).length - 8 }}
                          </span>
                        </div>
                      </div>
                      <div class="favorite-actions">
                        <el-button type="danger" link @click="removeFavorite(item)">
                          <el-icon><Delete /></el-icon>
                          取消收藏
                        </el-button>
                      </div>
                    </div>
                  </el-card>
                </div>
              </div>
            </el-card>

            <!-- 收藏统计分析 -->
            <el-card class="stats-analysis-card" v-if="favorites.length > 0">
              <template #header>
                <div class="card-header">
                  <span class="card-title">收藏统计分析</span>
                </div>
              </template>

              <el-row :gutter="24">
                <!-- 内容类型统计 -->
                <el-col :span="8">
                  <div class="stats-section-item">
                    <h4 class="stats-section-title">
                      <el-icon><InfoFilled /></el-icon>
                      内容类型分布
                    </h4>
                    <div class="stats-chart">
                      <div 
                        v-for="(count, type) in contentTypeStats" 
                        :key="type"
                        class="stats-bar-item"
                      >
                        <div class="stats-bar-label">
                          <el-tag 
                            :type="getContentTypeColor(type)" 
                            size="small"
                          >
                            {{ getContentTypeLabel(type) }}
                          </el-tag>
                          <span class="stats-count">{{ count }}篇</span>
                        </div>
                        <div class="stats-bar">
                          <div 
                            class="stats-bar-fill"
                            :style="{ 
                              width: `${(count / favorites.length) * 100}%`,
                              backgroundColor: getContentTypeBarColor(type)
                            }"
                          ></div>
                        </div>
                        <span class="stats-percentage">{{ Math.round((count / favorites.length) * 100) }}%</span>
                      </div>
                    </div>
                  </div>
                </el-col>

                <!-- 能源类型统计 -->
                <el-col :span="8">
                  <div class="stats-section-item">
                    <h4 class="stats-section-title">
                      <el-icon>⚡</el-icon>
                      能源类型关注度
                    </h4>
                    <div class="stats-chart">
                      <div 
                        v-for="(count, energyType) in energyTypeStats" 
                        :key="energyType"
                        class="stats-bar-item"
                      >
                        <div class="stats-bar-label">
                          <el-tag type="warning" size="small">{{ energyType }}</el-tag>
                          <span class="stats-count">{{ count }}篇</span>
                        </div>
                        <div class="stats-bar">
                          <div 
                            class="stats-bar-fill"
                            :style="{ 
                              width: `${(count / favorites.length) * 100}%`,
                              backgroundColor: '#f39c12'
                            }"
                          ></div>
                        </div>
                        <span class="stats-percentage">{{ Math.round((count / favorites.length) * 100) }}%</span>
                      </div>
                    </div>
                  </div>
                </el-col>

                <!-- 地区统计 -->
                <el-col :span="8">
                  <div class="stats-section-item">
                    <h4 class="stats-section-title">
                      <el-icon>🌍</el-icon>
                      地区关注度
                    </h4>
                    <div class="stats-chart">
                      <div 
                        v-for="(count, region) in regionStats" 
                        :key="region"
                        class="stats-bar-item"
                      >
                        <div class="stats-bar-label">
                          <el-tag type="success" size="small">{{ region }}</el-tag>
                          <span class="stats-count">{{ count }}篇</span>
                        </div>
                        <div class="stats-bar">
                          <div 
                            class="stats-bar-fill"
                            :style="{ 
                              width: `${(count / favorites.length) * 100}%`,
                              backgroundColor: '#27ae60'
                            }"
                          ></div>
                        </div>
                        <span class="stats-percentage">{{ Math.round((count / favorites.length) * 100) }}%</span>
                      </div>
                    </div>
                  </div>
                </el-col>
              </el-row>

              <!-- 收藏趋势 -->
              <el-divider />
              <div class="stats-section-item">
                <h4 class="stats-section-title">
                  <el-icon>📈</el-icon>
                  收藏趋势分析
                </h4>
                <el-row :gutter="16" class="trend-stats">
                  <el-col :span="6">
                    <div class="trend-item">
                      <div class="trend-value">{{ recentFavoritesCount }}</div>
                      <div class="trend-label">近7天收藏</div>
                    </div>
                  </el-col>
                  <el-col :span="6">
                    <div class="trend-item">
                      <div class="trend-value">{{ monthlyFavoritesCount }}</div>
                      <div class="trend-label">近30天收藏</div>
                    </div>
                  </el-col>
                  <el-col :span="6">
                    <div class="trend-item">
                      <div class="trend-value">{{ averageFavoritesPerDay }}</div>
                      <div class="trend-label">日均收藏</div>
                    </div>
                  </el-col>
                  <el-col :span="6">
                    <div class="trend-item">
                      <div class="trend-value">{{ mostActiveDay }}</div>
                      <div class="trend-label">最活跃日期</div>
                    </div>
                  </el-col>
                </el-row>
              </div>
            </el-card>
          </div>
        </el-tab-pane>
      </el-tabs>
    </el-card>

    <!-- 页面宽度占位符 -->
    <div class="width-placeholder" aria-hidden="true"></div>
  </div>
</template>

<script setup lang="ts">
import { ref, computed, onMounted, watch, reactive } from 'vue'
import { 
  Setting, 
  Refresh, 
  Check, 
  RefreshLeft,
  Delete, 
  Edit, 
  Close, 
  Plus,
  InfoFilled,
  Search,
  TopRight
} from '@element-plus/icons-vue'
import api from '@/api/request'
import { useUserStore } from '@/store/user'
import { ElMessage, ElMessageBox } from 'element-plus'
import tagService, { type TagCategory } from '@/services/tagService'
import { favoritesAPI, type FavoriteItem, type UserBehaviorStats } from '@/api/favorites'

interface UserTag {
  category: string;
  name: string;
  weight: number;
  source: string;
  created_at: string;
  isEditing?: boolean;
  editingWeight?: number;
}

const userStore = useUserStore()

// 响应式数据
const activeSettingTab = ref('tags')
const loading = ref(false)
const saving = ref(false)
const error = ref('')
const activeTab = ref('region')
const hasChanges = ref(false)

// 标签数据
const tags = ref<UserTag[]>([])
const originalTags = ref<UserTag[]>([])

// 标签分类配置
const tagCategories = ref<TagCategory[]>([])

// 地域选择器数据
const regionProvinces = ref([])
const regionSelector = reactive({
  selectedProvince: '',
  selectedCity: '',
  availableCities: [],
  previewTags: []
})

// 收藏管理相关数据
const searchQuery = ref('')
const favorites = ref<FavoriteItem[]>([])
const favoritesLoading = ref(false)
const behaviorStats = ref<UserBehaviorStats>({
  user_id: '',
  total_favorites: 0,
  energy_type_interests: {},
  region_interests: {},
  last_activity: ''
})

// 筛选功能相关数据
const showAdvancedFilters = ref(false)
const filters = reactive({
  contentType: '',
  energyType: '',
  region: '',
  timeRange: '',
  userTags: [] as string[]
})

// 收藏管理相关计算属性
const lastActivityText = computed(() => {
  if (behaviorStats.value.last_activity) {
    return formatDate(behaviorStats.value.last_activity)
  }
  return '无'
})

// 收藏统计相关计算属性
const contentTypeStats = computed(() => {
  const stats: Record<string, number> = {}
  favorites.value.forEach(item => {
    const type = item.type || 'other'
    stats[type] = (stats[type] || 0) + 1
  })
  return stats
})

const energyTypeStats = computed(() => {
  const stats: Record<string, number> = {}
  favorites.value.forEach(item => {
    if (item.energy_type_tags && item.energy_type_tags.length > 0) {
      item.energy_type_tags.forEach(tag => {
        stats[tag] = (stats[tag] || 0) + 1
      })
    }
  })
  // 只返回前5个最常见的能源类型
  return Object.fromEntries(
    Object.entries(stats)
      .sort(([,a], [,b]) => b - a)
      .slice(0, 5)
  )
})

const regionStats = computed(() => {
  const stats: Record<string, number> = {}
  favorites.value.forEach(item => {
    if (item.region_tags && item.region_tags.length > 0) {
      item.region_tags.forEach(tag => {
        stats[tag] = (stats[tag] || 0) + 1
      })
    }
  })
  // 只返回前5个最常见的地区
  return Object.fromEntries(
    Object.entries(stats)
      .sort(([,a], [,b]) => b - a)
      .slice(0, 5)
  )
})

const recentFavoritesCount = computed(() => {
  const sevenDaysAgo = new Date()
  sevenDaysAgo.setDate(sevenDaysAgo.getDate() - 7)
  return favorites.value.filter(item => 
    new Date(item.favorited_at) >= sevenDaysAgo
  ).length
})

const monthlyFavoritesCount = computed(() => {
  const thirtyDaysAgo = new Date()
  thirtyDaysAgo.setDate(thirtyDaysAgo.getDate() - 30)
  return favorites.value.filter(item => 
    new Date(item.favorited_at) >= thirtyDaysAgo
  ).length
})

const averageFavoritesPerDay = computed(() => {
  if (favorites.value.length === 0) return '0'
  const thirtyDaysAgo = new Date()
  thirtyDaysAgo.setDate(thirtyDaysAgo.getDate() - 30)
  const recentFavorites = favorites.value.filter(item => 
    new Date(item.favorited_at) >= thirtyDaysAgo
  )
  return (recentFavorites.length / 30).toFixed(1)
})

const mostActiveDay = computed(() => {
  if (favorites.value.length === 0) return '无'
  const dayStats: Record<string, number> = {}
  favorites.value.forEach(item => {
    const day = new Date(item.favorited_at).toLocaleDateString('zh-CN')
    dayStats[day] = (dayStats[day] || 0) + 1
  })
  const mostActive = Object.entries(dayStats)
    .sort(([,a], [,b]) => b - a)[0]
  return mostActive ? mostActive[0] : '无'
})

// 筛选功能相关计算属性
const allEnergyTypeStats = computed(() => {
  const stats: Record<string, number> = {}
  favorites.value.forEach(item => {
    if (item.energy_type_tags && item.energy_type_tags.length > 0) {
      item.energy_type_tags.forEach(tag => {
        stats[tag] = (stats[tag] || 0) + 1
      })
    }
  })
  return Object.fromEntries(
    Object.entries(stats).sort(([,a], [,b]) => b - a)
  )
})

const allRegionStats = computed(() => {
  const stats: Record<string, number> = {}
  favorites.value.forEach(item => {
    if (item.region_tags && item.region_tags.length > 0) {
      item.region_tags.forEach(tag => {
        stats[tag] = (stats[tag] || 0) + 1
      })
    }
  })
  return Object.fromEntries(
    Object.entries(stats).sort(([,a], [,b]) => b - a)
  )
})

const availableUserTags = computed(() => {
  return tags.value.filter(tag => 
    tag.category !== 'basic_info' && 
    ['region', 'energy_type', 'business_field', 'policy_measure'].includes(tag.category)
  )
})

const hasActiveFilters = computed(() => {
  return !!(
    filters.contentType || 
    filters.energyType || 
    filters.region || 
    filters.timeRange || 
    filters.userTags.length > 0
  )
})

const activeFiltersCount = computed(() => {
  let count = 0
  if (filters.contentType) count++
  if (filters.energyType) count++
  if (filters.region) count++
  if (filters.timeRange) count++
  if (filters.userTags.length > 0) count += filters.userTags.length
  return count
})

const filteredFavorites = computed(() => {
  let result = [...favorites.value]
  
  // 搜索关键词筛选
  if (searchQuery.value.trim()) {
    const query = searchQuery.value.toLowerCase()
    result = result.filter(item => 
      item.title.toLowerCase().includes(query) ||
      item.source.toLowerCase().includes(query) ||
      getAllTagsFromFavorite(item).some(tag => tag.toLowerCase().includes(query))
    )
  }
  
  // 内容类型筛选
  if (filters.contentType) {
    result = result.filter(item => item.type === filters.contentType)
  }
  
  // 能源类型筛选
  if (filters.energyType) {
    result = result.filter(item => 
      item.energy_type_tags && item.energy_type_tags.includes(filters.energyType)
    )
  }
  
  // 地区筛选
  if (filters.region) {
    result = result.filter(item => 
      item.region_tags && item.region_tags.includes(filters.region)
    )
  }
  
  // 时间范围筛选
  if (filters.timeRange) {
    const now = new Date()
    let startDate = new Date()
    
    switch (filters.timeRange) {
      case '7days':
        startDate.setDate(now.getDate() - 7)
        break
      case '30days':
        startDate.setDate(now.getDate() - 30)
        break
      case '3months':
        startDate.setMonth(now.getMonth() - 3)
        break
      case '6months':
        startDate.setMonth(now.getMonth() - 6)
        break
      case '1year':
        startDate.setFullYear(now.getFullYear() - 1)
        break
    }
    
    result = result.filter(item => 
      new Date(item.favorited_at) >= startDate
    )
  }
  
  // 用户标签筛选
  if (filters.userTags.length > 0) {
    result = result.filter(item => {
      const itemTags = getAllTagsFromFavorite(item)
      return filters.userTags.some(userTag => itemTags.includes(userTag))
    })
  }
  
  return result
})

// 计算属性
const totalTagsCount = computed(() => tags.value.length)
const activeCategoriesCount = computed(() => {
  const categories = new Set(tags.value.map(tag => tag.category))
  return categories.size
})
const totalWeight = computed(() => {
  return tags.value.reduce((sum, tag) => sum + tag.weight, 0)
})
const lastUpdateTime = computed(() => {
  if (!tags.value.length) return '无'
  const dates = tags.value.map(tag => new Date(tag.created_at))
  const latest = new Date(Math.max(...dates.map(d => d.getTime())))
  return latest.toLocaleDateString('zh-CN')
})

const sortedTagsForPreview = computed(() => {
  return [...tags.value].sort((a, b) => b.weight - a.weight)
})

// 工具函数
const getTagsByCategory = (category: string) => {
  return tags.value.filter(tag => tag.category === category)
}

const getAvailablePresetTags = (category: string) => {
  const categoryConfig = tagCategories.value.find(cat => cat.key === category)
  if (!categoryConfig) return []
  
  const existingTagNames = getTagsByCategory(category).map(tag => tag.name)
  return categoryConfig.presetTags.filter(preset => !existingTagNames.includes(preset))
}

const getTagTypeByCategory = (category: string) => {
  const categoryConfig = tagCategories.value.find(cat => cat.key === category)
  return categoryConfig?.color || 'info'
}

const getBadgeType = (category: string) => {
  const count = getTagsByCategory(category).length
  if (count === 0) return 'info'
  if (count <= 2) return 'warning'
  return 'success'
}

const getTagSizeByWeight = (weight: number) => {
  if (weight >= 2.0) return 'large'
  if (weight >= 1.5) return 'default'
  return 'small'
}

// 标签操作方法
const addPresetTagDirectly = (category: string, tagName: string) => {
  if (tags.value.find(tag => tag.category === category && tag.name === tagName)) {
    ElMessage.warning('该标签已存在')
    return
  }
  
  tags.value.push({
    category,
    name: tagName,
    weight: 1.0,
    source: 'preset',
    created_at: new Date().toISOString()
  })
  
  hasChanges.value = true
  ElMessage.success(`已添加预设标签：${tagName}`)
}

const addAllPresetTags = async (category: any) => {
  const result = await ElMessageBox.confirm(
    `确定要添加所有${category.name}的预设标签吗？`,
    '批量添加确认',
    {
      confirmButtonText: '确定',
      cancelButtonText: '取消',
      type: 'info'
    }
  ).catch(() => false)
  
  if (!result) return
  
  const availableTags = getAvailablePresetTags(category.key)
  let addedCount = 0
  availableTags.forEach(tagName => {
    if (!tags.value.find(tag => tag.category === category.key && tag.name === tagName)) {
      tags.value.push({
        category: category.key,
        name: tagName,
        weight: 1.0,
        source: 'preset',
        created_at: new Date().toISOString()
      })
      addedCount++
    }
  })
  
  hasChanges.value = true
  ElMessage.success(`已添加${addedCount}个预设标签`)
}

const removeTag = async (tag: UserTag) => {
  const result = await ElMessageBox.confirm(
    `确定要删除标签"${tag.name}"吗？`,
    '删除确认',
    {
      confirmButtonText: '删除',
      cancelButtonText: '取消',
      type: 'warning'
    }
  ).catch(() => false)
  
  if (!result) return
  
  const index = tags.value.findIndex(t => t.category === tag.category && t.name === tag.name)
  if (index !== -1) {
    tags.value.splice(index, 1)
    hasChanges.value = true
    ElMessage.success(`已删除标签：${tag.name}`)
  }
}

const startEditWeight = (tag: UserTag) => {
  tag.isEditing = true
  tag.editingWeight = tag.weight
}

const confirmEditWeight = (tag: UserTag) => {
  if (tag.editingWeight !== undefined) {
    tag.weight = tag.editingWeight
    hasChanges.value = true
  }
  tag.isEditing = false
  tag.editingWeight = undefined
  ElMessage.success(`已更新标签权重：${tag.name}`)
}

const cancelEditWeight = (tag: UserTag) => {
  tag.isEditing = false
  tag.editingWeight = undefined
}

const resetToDefaults = async () => {
  const result = await ElMessageBox.confirm(
    '确定要重置标签吗？这将保留注册地、省份、区域和能源产品标签，清理其他标签。',
    '重置确认',
    {
      confirmButtonText: '重置',
      cancelButtonText: '取消',
      type: 'warning'
    }
  ).catch(() => false)
  
  if (!result) return
  
  const preserveCategories = ['region', 'energy_type']
  tags.value = tags.value.filter(tag => preserveCategories.includes(tag.category))
  hasChanges.value = true
  ElMessage.success('已重置标签')
}

const cleanDuplicates = () => {
  const seen = new Set()
  const cleaned = tags.value.filter(tag => {
    const key = `${tag.category}-${tag.name}`
    if (seen.has(key)) {
      return false
    }
    seen.add(key)
    return true
  })
  
  const duplicateCount = tags.value.length - cleaned.length
  if (duplicateCount > 0) {
    tags.value = cleaned
    hasChanges.value = true
    ElMessage.success(`已清理${duplicateCount}个重复标签`)
  } else {
    ElMessage.info('没有发现重复标签')
  }
}

const fetchTags = async () => {
  try {
    loading.value = true
    error.value = ''
    
    const userId = userStore.currentUser?.demo_user_id || userStore.currentUser?.id
    if (!userId) {
      throw new Error('请先登录')
    }
    
    console.log('🏷️ 获取用户标签 - userId:', userId)
    const response = await api.get(`/users/${userId}/tags`)
    
    if (response.data?.data?.tags) {
      // 处理标签数据并去重
      let rawTags = response.data.data.tags
      
      // 映射标签分类（处理后端可能返回的城市、省份等标签）
      rawTags = rawTags.map(tag => {
        if (['city', 'province'].includes(tag.category)) {
          return { ...tag, category: 'region' }
        }
        return tag
      })
      
      // 过滤掉基础信息标签
      rawTags = rawTags.filter(tag => tag.category !== 'basic_info')
      
      tags.value = rawTags || []
      originalTags.value = JSON.parse(JSON.stringify(tags.value))
      hasChanges.value = false
      
      console.log('✅ 标签加载成功，数量:', tags.value.length)
      ElMessage.success(`成功加载${tags.value.length}个标签`)
    } else {
      tags.value = []
      originalTags.value = []
      ElMessage.info('暂无标签，请添加您感兴趣的标签')
    }
  } catch (err: any) {
    console.error('❌ 获取标签失败:', err)
    error.value = err.response?.data?.message || err.message || '获取标签失败'
    ElMessage.error(error.value)
  } finally {
    loading.value = false
  }
}

const saveUserTags = async () => {
  if (!hasChanges.value) {
    ElMessage.info('没有更改需要保存')
    return
  }
  
  try {
    saving.value = true
    
    const userId = userStore.currentUser?.demo_user_id || userStore.currentUser?.id
    if (!userId) {
      throw new Error('请先登录')
    }
    
    const tagsData = {
      tags: tags.value.map(tag => ({
        category: tag.category,
        name: tag.name,
        weight: tag.weight || 1.0,
        source: tag.source || 'manual',
        created_at: tag.created_at || new Date().toISOString()
      }))
    }
    
    console.log('💾 保存用户标签:', {
      总数: tagsData.tags.length
    })
    
    await api.put(`/users/${userId}/tags`, tagsData)
    
    originalTags.value = JSON.parse(JSON.stringify(tags.value))
    hasChanges.value = false
    ElMessage.success(`✅ 成功保存 ${tags.value.length} 个标签`)
  } catch (err: any) {
    console.error('❌ 保存标签失败:', err)
    
    let errorMessage = '保存失败'
    if (err.response?.status === 400) {
      errorMessage = `验证失败：${err.response.data?.detail?.message || '标签验证失败'}`
    } else if (err.response?.status === 500) {
      errorMessage = '服务器内部错误，请稍后重试'
    } else {
      errorMessage = err.response?.data?.message || err.message || '保存失败'
    }
    
    ElMessage.error(errorMessage)
  } finally {
    saving.value = false
  }
}

// 初始化数据
onMounted(async () => {
  try {
    tagCategories.value = await tagService.getTagCategories()
    await loadProvincesWithCities()
    await fetchTags()
    
    // 如果当前是收藏管理页签，则加载收藏数据
    if (activeSettingTab.value === 'favorites') {
      await loadFavorites()
    }
  } catch (err) {
    console.error('初始化失败:', err)
    error.value = '初始化失败，请刷新页面重试'
  }
})

// 监听页签切换，自动加载对应数据
watch(activeSettingTab, async (newTab) => {
  if (newTab === 'favorites' && favorites.value.length === 0) {
    await loadFavorites()
  }
})

// 地域选择器相关函数
const loadProvincesWithCities = async () => {
  try {
    console.log('🌍 开始加载省份城市数据...')
    const data = await tagService.getProvincesWithCities()
    regionProvinces.value = data.provinces
    
    console.log('✅ 省份城市数据加载成功', {
      provinces: data.total_provinces,
      cities: data.total_cities,
      provincesData: regionProvinces.value.slice(0, 3)
    })
  } catch (error) {
    console.error('❌ 加载省份城市数据失败:', error)
    ElMessage.error('加载省份城市数据失败')
    
    // 提供备用数据
    regionProvinces.value = [
      {
        code: 'SC',
        name: '四川省',
        cities: ['成都', '绵阳', '德阳', '南充', '宜宾'],
        city_count: 5
      },
      {
        code: 'AH', 
        name: '安徽省',
        cities: ['合肥', '芜湖', '蚌埠', '淮南', '马鞍山'],
        city_count: 5
      }
    ]
    console.log('🔄 使用备用省份城市数据')
  }
}

const handleRegionProvinceChange = (provinceCode: string) => {
  console.log('🏛️ 省份选择变化:', provinceCode)
  
  // 清空城市选择
  regionSelector.selectedCity = ''
  regionSelector.previewTags = []
  
  // 更新可选城市列表
  const selectedProvince = regionProvinces.value.find(p => p.code === provinceCode)
  if (selectedProvince) {
    regionSelector.availableCities = selectedProvince.cities || []
    console.log(`✅ 省份选择成功: ${selectedProvince.name}, ${regionSelector.availableCities.length}个城市`, regionSelector.availableCities)
  } else {
    regionSelector.availableCities = []
    console.log('❌ 未找到对应省份数据')
  }
}

const handleRegionCityChange = async (cityValue: string) => {
  if (!cityValue) {
    regionSelector.previewTags = []
    return
  }
  
  try {
    // 调用后端API获取城市的完整区域信息
    const data = await tagService.getCitiesDetails()
    const citiesDetails = data.cities
    
    const cityDetail = citiesDetails.find(c => c.city === cityValue)
    if (cityDetail) {
      // 生成预览标签
      regionSelector.previewTags = []
      
      // 城市标签
      regionSelector.previewTags.push({
        name: cityDetail.city,
        level: 'city',
        weight: 2.5
      })
      
      // 省份标签
      if (cityDetail.province) {
        regionSelector.previewTags.push({
          name: cityDetail.province,
          level: 'province',
          weight: 2.0
        })
      }
      
      // 区域标签
      if (cityDetail.region) {
        regionSelector.previewTags.push({
          name: cityDetail.region,
          level: 'region',
          weight: 1.5
        })
      }
      
      console.log('🏙️ 城市选择完成:', cityDetail)
      console.log('📝 预览标签:', regionSelector.previewTags)
    }
  } catch (error) {
    console.error('❌ 获取城市详情失败:', error)
    ElMessage.error('获取城市详情失败')
  }
}

const addRegionTags = async () => {
  if (!regionSelector.selectedCity || !regionSelector.previewTags.length) {
    ElMessage.warning('请先选择城市')
    return
  }
  
  try {
    let addedCount = 0
    
    // 添加预览中的标签
    for (const previewTag of regionSelector.previewTags) {
      // 检查标签是否已存在
      const existingTag = tags.value.find(tag => 
        tag.category === 'region' && tag.name === previewTag.name
      )
      
      if (!existingTag) {
        tags.value.push({
          category: 'region',
          name: previewTag.name,
          weight: previewTag.weight,
          source: previewTag.level === 'city' ? 'preset' : 'region_auto',
          created_at: new Date().toISOString()
        })
        addedCount++
      }
    }
    
    if (addedCount > 0) {
      hasChanges.value = true
      ElMessage.success(`成功添加${addedCount}个地区标签`)
      
      // 清空选择器
      regionSelector.selectedProvince = ''
      regionSelector.selectedCity = ''
      regionSelector.availableCities = []
      regionSelector.previewTags = []
    } else {
      ElMessage.info('所选地区标签已存在，无需添加')
    }
    
  } catch (error) {
    console.error('❌ 添加地区标签失败:', error)
    ElMessage.error('添加地区标签失败')
  }
}

// 监听标签变化
watch(tags, () => {
  const currentTagsStr = JSON.stringify(tags.value)
  const originalTagsStr = JSON.stringify(originalTags.value)
  hasChanges.value = currentTagsStr !== originalTagsStr
}, { deep: true })

// 收藏管理相关函数
const loadFavorites = async () => {
  try {
    favoritesLoading.value = true
    error.value = ''
    
    const userId = userStore.currentUser?.demo_user_id || userStore.currentUser?.id
    if (!userId) {
      throw new Error('请先登录')
    }
    
    console.log('💖 获取用户收藏 - userId:', userId)
    const favoritesList = await favoritesAPI.getFavoritesList(50)
    const stats = await favoritesAPI.getUserBehaviorStats()
    
    favorites.value = favoritesList
    Object.assign(behaviorStats.value, stats)
    
    console.log('✅ 收藏加载成功，数量:', favorites.value.length)
    ElMessage.success(`成功加载${favorites.value.length}个收藏`)
  } catch (err: any) {
    console.error('❌ 获取收藏失败:', err)
    error.value = err.response?.data?.message || err.message || '获取收藏失败'
    ElMessage.error(error.value)
  } finally {
    favoritesLoading.value = false
  }
}

const removeFavorite = async (item: FavoriteItem) => {
  const result = await ElMessageBox.confirm(
    `确定要取消收藏"${item.title}"吗？`,
    '取消收藏确认',
    {
      confirmButtonText: '取消收藏',
      cancelButtonText: '取消',
      type: 'warning'
    }
  ).catch(() => false)
  
  if (!result) return
  
  try {
    await favoritesAPI.removeFavorite(item.content_id)
    
    favorites.value = favorites.value.filter(i => i._id !== item._id)
    ElMessage.success(`已取消收藏：${item.title}`)
  } catch (err: any) {
    console.error('❌ 取消收藏失败:', err)
    error.value = err.response?.data?.message || err.message || '取消收藏失败'
    ElMessage.error(error.value)
  }
}

const handleSearch = () => {
  // 实现搜索逻辑
  if (searchQuery.value.trim()) {
    performSearch()
  }
}

const handleSearchClear = () => {
  searchQuery.value = ''
  loadFavorites()
}

const performSearch = async () => {
  if (!searchQuery.value.trim()) {
    loadFavorites()
    return
  }
  
  try {
    favoritesLoading.value = true
    const results = await favoritesAPI.searchFavorites(searchQuery.value.trim(), 50)
    favorites.value = results
    ElMessage.success(`搜索到${results.length}篇文章`)
  } catch (err: any) {
    console.error('❌ 搜索失败:', err)
    ElMessage.error('搜索失败，请重试')
  } finally {
    favoritesLoading.value = false
  }
}

const resetAllFilters = () => {
  searchQuery.value = ''
  filters.contentType = ''
  filters.energyType = ''
  filters.region = ''
  filters.timeRange = ''
  filters.userTags = []
  loadFavorites()
}

const getContentTypeColor = (type: string) => {
  switch (type) {
    case 'policy': return 'success'
    case 'news': return 'primary'
    case 'price': return 'warning'
    case 'announcement': return 'danger'
    default: return 'info'
  }
}

const getContentTypeBarColor = (type: string) => {
  switch (type) {
    case 'policy': return '#67c23a'
    case 'news': return '#409eff'
    case 'price': return '#e6a23c'
    case 'announcement': return '#f56c6c'
    default: return '#909399'
  }
}

const getContentTypeLabel = (type: string) => {
  switch (type) {
    case 'policy': return '政策'
    case 'news': return '资讯'
    case 'price': return '调价'
    case 'announcement': return '公告'
    default: return '其他'
  }
}

const getAllTagsFromFavorite = (item: FavoriteItem): string[] => {
  return [
    ...(item.energy_type_tags || []),
    ...(item.region_tags || [])
  ]
}

const getTagColor = (tag: string) => {
  if (tag.includes('天然气') || tag.includes('原油')) return 'warning'
  if (tag.includes('政策') || tag.includes('法规')) return 'success'
  if (tag.includes('公告') || tag.includes('调价')) return 'danger'
  return 'info'
}

const formatDate = (dateString: string) => {
  return new Date(dateString).toLocaleDateString('zh-CN')
}

// 筛选功能相关函数
const toggleAdvancedFilters = () => {
  showAdvancedFilters.value = !showAdvancedFilters.value
}

const applyFilters = () => {
  // 筛选逻辑已在 filteredFavorites 计算属性中实现
  // 这里可以添加额外的逻辑，比如记录筛选行为
  console.log('🔍 应用筛选条件:', {
    contentType: filters.contentType,
    energyType: filters.energyType,
    region: filters.region,
    timeRange: filters.timeRange,
    userTags: filters.userTags,
    resultCount: filteredFavorites.value.length
  })
}

const toggleUserTagFilter = (tagName: string) => {
  const index = filters.userTags.indexOf(tagName)
  if (index > -1) {
    filters.userTags.splice(index, 1)
  } else {
    filters.userTags.push(tagName)
  }
  applyFilters()
}

const getTimeRangeLabel = (timeRange: string) => {
  switch (timeRange) {
    case '7days': return '最近7天'
    case '30days': return '最近30天'
    case '3months': return '最近3个月'
    case '6months': return '最近6个月'
    case '1year': return '最近1年'
    default: return '全部时间'
  }
}
</script>

<style scoped>
.dashboard-container {
  min-height: 100vh;
  max-width: 1280px;
  margin: 0 auto;
}

/* 页面头部 */
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

/* 设置卡片 */
.settings-card {
  border-radius: 12px;
  box-shadow: 0 2px 12px rgba(0,0,0,0.08);
  margin-bottom: 24px;
}

.settings-tabs {
  border: none;
}

.settings-content {
  padding: 0;
}

/* 加载和错误状态 */
.loading-container {
  padding: 40px;
}

.error-alert {
  margin-bottom: 24px;
}

/* 统计卡片 */
.stats-section {
  margin-bottom: 24px;
}

.stat-card {
  position: relative;
  border-radius: 12px;
  overflow: hidden;
  transition: all 0.3s;
  cursor: pointer;
  background: white;
  border: 1px solid #ebeef5;
}

.stat-card:hover {
  transform: translateY(-4px);
  box-shadow: 0 8px 25px rgba(0,0,0,0.15);
}

.stat-icon {
  position: absolute;
  right: 16px;
  top: 50%;
  transform: translateY(-50%);
  font-size: 32px;
  opacity: 0.3;
  color: #909399;
}

/* 标签预览卡片 */
.preview-card {
  margin-bottom: 24px;
  border-radius: 12px;
  border: none;
  box-shadow: 0 2px 12px rgba(0,0,0,0.08);
}

.preview-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  padding: 0;
}

.preview-title {
  font-size: 18px;
  font-weight: bold;
  color: #303133;
}

.action-buttons {
  display: flex;
  gap: 12px;
}

.action-buttons .el-button {
  border-radius: 8px;
}

.preview-content {
  padding: 16px 0;
}

.all-tags-cloud {
  display: flex;
  flex-wrap: wrap;
  gap: 8px;
  align-items: center;
}

.preview-tag {
  margin: 0;
  border-radius: 6px;
  font-weight: 500;
  transition: all 0.3s;
  height: 32px;
  line-height: 32px;
  padding: 0 12px;
  font-size: 14px;
  display: inline-flex;
  align-items: center;
  box-sizing: border-box;
}

.preview-tag:hover {
  transform: scale(1.05);
}

/* 标签管理卡片 */
.tags-card {
  border-radius: 12px;
  border: none;
  box-shadow: 0 2px 12px rgba(0,0,0,0.08);
}

.tags-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  padding: 0;
}

.tags-title {
  font-size: 18px;
  font-weight: bold;
  color: #303133;
}

.tags-tabs {
  border: none;
}

.tab-label {
  display: flex;
  align-items: center;
  gap: 8px;
}

.tab-content {
  padding: 20px 0;
}

/* 分类描述 */
.category-description {
  display: flex;
  align-items: center;
  gap: 8px;
  padding: 16px;
  background: linear-gradient(135deg, #f8fafc, #f1f5f9);
  border-radius: 8px;
  margin-bottom: 24px;
  border: 1px solid #e2e8f0;
  color: #64748b;
  font-size: 14px;
}

.desc-icon {
  color: #3b82f6;
  font-size: 16px;
}

/* 当前标签部分 */
.current-tags-section {
  margin-bottom: 32px;
}

.section-title {
  font-size: 16px;
  font-weight: bold;
  color: #303133;
  margin: 0 0 16px 0;
  display: flex;
  justify-content: space-between;
  align-items: center;
}

.tags-container {
  display: flex;
  flex-wrap: wrap;
  gap: 12px;
  align-items: flex-start;
}

.tag-item-wrapper {
  position: relative;
}

/* 新的标签显示包装器 */
.tag-display-wrapper {
  display: inline-flex;
  align-items: center;
  gap: 8px;
  background: white;
  border-radius: 8px;
  padding: 4px;
  border: 2px solid transparent;
  transition: all 0.3s;
}

.tag-display-wrapper:hover {
  border-color: #409eff;
  box-shadow: 0 4px 12px rgba(64, 158, 255, 0.3);
  transform: translateY(-2px);
}

.tag-item-display {
  margin: 0;
  border-radius: 6px;
  font-weight: 500;
  cursor: pointer;
  transition: all 0.3s;
  border: none !important;
}

.tag-item-display:hover {
  transform: scale(1.02);
}

.tag-content {
  display: flex;
  align-items: center;
  gap: 6px;
}

.tag-name {
  font-weight: 500;
}

.tag-weight {
  font-size: 12px;
  font-weight: bold;
  opacity: 0.8;
}

/* 标签操作按钮 */
.tag-actions {
  display: flex;
  align-items: center;
  gap: 4px;
}

.edit-icon,
.delete-icon {
  width: 16px;
  height: 16px;
  padding: 2px;
  border-radius: 4px;
  cursor: pointer;
  transition: all 0.3s;
  font-size: 12px;
}

.edit-icon {
  color: #409eff;
  background: rgba(64, 158, 255, 0.1);
}

.edit-icon:hover {
  background: rgba(64, 158, 255, 0.2);
  transform: scale(1.1);
}

.delete-icon {
  color: #f56c6c;
  background: rgba(245, 108, 108, 0.1);
}

.delete-icon:hover {
  background: rgba(245, 108, 108, 0.2);
  transform: scale(1.1);
}

/* 权重编辑器 */
.tag-weight-editor {
  display: inline-flex;
  align-items: center;
  background: white;
  border: 2px solid #409eff;
  border-radius: 6px;
  padding: 8px 12px;
  box-shadow: 0 4px 12px rgba(64, 158, 255, 0.3);
}

.editor-content {
  display: flex;
  align-items: center;
  gap: 8px;
}

.editing-tag-name {
  font-weight: 500;
  color: #303133;
  white-space: nowrap;
}

.weight-editor-input {
  width: 80px;
}

.weight-editor-actions {
  display: flex;
  gap: 4px;
  margin-left: 8px;
}

.weight-editor-actions .el-button {
  padding: 4px 8px;
  border-radius: 4px;
}

/* 空标签状态 */
.empty-tags {
  text-align: center;
  padding: 32px;
  color: #909399;
  background: #fafafa;
  border-radius: 8px;
  border: 2px dashed #dcdfe6;
}

.empty-tags p {
  margin: 0;
  font-size: 14px;
}

/* 预设标签部分 */
.preset-tags-section {
  border-top: 1px solid #ebeef5;
  padding-top: 24px;
}

.preset-actions {
  display: flex;
  align-items: center;
  gap: 12px;
  font-size: 14px;
}

.preset-hint {
  color: #909399;
  font-weight: normal;
}

.preset-tags-container {
  display: flex;
  flex-wrap: wrap;
  gap: 8px;
  align-items: center;
}

.preset-tag-item {
  margin: 0;
  border-radius: 6px;
  font-weight: 500;
  cursor: pointer;
  transition: all 0.3s;
  border: 2px solid transparent;
  display: flex;
  align-items: center;
  gap: 4px;
}

.preset-tag-item:hover {
  border-color: currentColor;
  transform: translateY(-2px);
  box-shadow: 0 4px 12px rgba(0,0,0,0.15);
}

.preset-tag-item .el-icon {
  font-size: 12px;
}

/* 内容卡片 */
.content-card {
  border-radius: 12px;
  box-shadow: 0 2px 12px rgba(0,0,0,0.08);
  text-align: center;
  padding: 40px;
}

.content-card h3 {
  margin: 0 0 16px 0;
  color: #303133;
}

.content-card p {
  margin: 0;
  color: #666;
}

/* 地域选择器样式 */
.region-selector-section {
  margin-bottom: 32px;
  padding: 20px;
  background: #f0f9ff;
  border: 2px dashed #3b82f6;
  border-radius: 12px;
}

.selector-hint {
  display: flex;
  align-items: center;
  gap: 8px;
}

.selector-hint-text {
  font-size: 12px;
  color: #3b82f6;
  font-weight: normal;
}

.region-selector-container {
  margin-top: 16px;
}

.region-selector-row {
  display: flex;
  gap: 12px;
  align-items: center;
  margin-bottom: 16px;
}

.province-selector {
  flex: 1;
  min-width: 160px;
}

.city-selector {
  flex: 1;
  min-width: 160px;
}

.region-preview {
  padding: 12px;
  background: white;
  border-radius: 8px;
  border: 1px solid #e5e7eb;
}

.preview-tags {
  display: flex;
  flex-wrap: wrap;
  gap: 8px;
  margin-top: 8px;
}

.preview-tags .el-tag {
  margin: 0;
}

/* 响应式设计 */
@media (max-width: 1200px) {
  .dashboard-container {
    max-width: 1024px;
  }
}

@media (max-width: 768px) {
  .dashboard-container {
    max-width: 100%;
    margin: 0 16px;
  }
  
  .page-title {
    font-size: 28px;
  }
  
  .title-icon {
    font-size: 32px;
  }
  
  .stats-section .el-col {
    margin-bottom: 16px;
  }
  
  .action-buttons {
    flex-direction: column;
    gap: 8px;
  }
  
  .action-buttons .el-button {
    width: 100%;
  }
  
  .tags-container {
    gap: 8px;
  }
  
  .preset-tags-container {
    gap: 6px;
  }
  
  .editor-content {
    flex-direction: column;
    align-items: flex-start;
    gap: 8px;
  }
  
  .weight-editor-actions {
    margin-left: 0;
    margin-top: 8px;
  }
}

/* 页面宽度占位符 */
.width-placeholder {
  width: 1280px;
  min-width: 1280px;
  height: 1px;
  visibility: hidden;
  pointer-events: none;
  position: relative;
  margin: 0 auto;
}

/* 收藏管理样式 */
.search-card {
  margin-bottom: 24px;
  border-radius: 12px;
  box-shadow: 0 2px 12px rgba(0,0,0,0.08);
  background: white;
}

.search-stats {
  display: flex;
  align-items: center;
  justify-content: flex-end;
  height: 100%;
}

.search-result-text {
  font-size: 14px;
  color: #606266;
}

.search-result-text strong {
  color: #1890ff;
  font-weight: bold;
}

.favorites-card {
  border-radius: 12px;
  background: white;
  border: none;
  box-shadow: 0 2px 12px rgba(0,0,0,0.08);
  margin-bottom: 24px;
}

.card-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  position: relative;
  padding: 0;
}

.card-title {
  font-size: 18px;
  font-weight: bold;
  color: #303133;
  position: absolute;
  left: 50%;
  transform: translateX(-50%);
  margin: 0;
}

.favorites-list {
  min-height: 400px;
}

.favorite-items {
  display: flex;
  flex-direction: column;
  gap: 16px;
}

.favorite-item {
  cursor: pointer;
  transition: all 0.3s;
  border-radius: 8px;
  background: white;
  border: 1px solid #ebeef5;
  overflow: hidden;
}

.favorite-item:hover {
  transform: translateY(-2px);
  box-shadow: 0 8px 25px rgba(0,0,0,0.15);
}

.favorite-item-body {
  display: flex;
  justify-content: space-between;
  align-items: flex-start;
  padding: 20px;
  gap: 16px;
}

.favorite-main {
  flex: 1;
}

.favorite-meta {
  display: flex;
  align-items: center;
  gap: 12px;
  margin-bottom: 12px;
}

.content-type-tag {
  font-weight: bold;
  border-radius: 6px;
}

.favorite-source {
  font-size: 12px;
  color: #909399;
}

.favorite-date {
  font-size: 12px;
  color: #909399;
}

.favorite-title {
  margin: 0 0 8px 0;
  font-size: 16px;
  font-weight: bold;
  color: #303133;
  line-height: 1.4;
}

.article-link {
  color: #409eff;
  text-decoration: none;
  display: inline-flex;
  align-items: center;
  gap: 4px;
}

.article-link:hover {
  color: #66b1ff;
}

.external-link-icon {
  font-size: 12px;
}

.favorite-publish-date {
  margin: 0 0 12px 0;
  font-size: 12px;
  color: #909399;
}

.favorite-tags {
  display: flex;
  flex-wrap: wrap;
  gap: 6px;
  align-items: center;
}

.favorite-tag {
  margin: 0;
  border-radius: 4px;
}

.more-tags {
  font-size: 12px;
  color: #909399;
  background: #f5f7fa;
  padding: 2px 6px;
  border-radius: 4px;
}

.favorite-actions {
  display: flex;
  flex-direction: column;
  gap: 8px;
}

.empty-state {
  text-align: center;
  padding: 60px 20px;
}

/* Element Plus 样式重写 */
:deep(.el-statistic__head) {
  color: #606266;
  margin-bottom: 8px;
}

:deep(.el-statistic__content) {
  color: #303133;
  font-weight: bold;
}

:deep(.el-tabs__header) {
  margin: 0 0 20px 0;
}

:deep(.el-tabs__nav-wrap::after) {
  display: none;
}

:deep(.el-tabs__item) {
  padding: 0 20px;
  font-weight: 500;
}

:deep(.el-tabs__item.is-active) {
  color: #409eff;
  font-weight: bold;
}

:deep(.el-badge__content) {
  border: none;
  font-weight: bold;
  font-size: 10px;
  padding: 0 4px;
  min-width: 16px;
  height: 16px;
  line-height: 16px;
}

/* 收藏统计分析样式 */
.stats-analysis-card {
  border-radius: 12px;
  background: white;
  border: none;
  box-shadow: 0 2px 12px rgba(0,0,0,0.08);
  margin-bottom: 24px;
}

.stats-section-item {
  padding: 16px;
  background: #fafbfc;
  border-radius: 8px;
  border: 1px solid #ebeef5;
}

.stats-section-title {
  display: flex;
  align-items: center;
  gap: 8px;
  font-size: 16px;
  font-weight: bold;
  color: #303133;
  margin: 0 0 16px 0;
}

.stats-chart {
  display: flex;
  flex-direction: column;
  gap: 12px;
}

.stats-bar-item {
  display: flex;
  flex-direction: column;
  gap: 4px;
}

.stats-bar-label {
  display: flex;
  justify-content: space-between;
  align-items: center;
  font-size: 12px;
}

.stats-count {
  color: #606266;
  font-weight: 500;
}

.stats-bar {
  height: 8px;
  background: #f5f7fa;
  border-radius: 4px;
  overflow: hidden;
  position: relative;
}

.stats-bar-fill {
  height: 100%;
  border-radius: 4px;
  transition: width 0.3s ease;
}

.stats-percentage {
  font-size: 11px;
  color: #909399;
  text-align: right;
}

.trend-stats {
  margin-top: 16px;
}

.trend-item {
  text-align: center;
  padding: 16px;
  background: white;
  border-radius: 8px;
  border: 1px solid #ebeef5;
  transition: all 0.3s;
}

.trend-item:hover {
  transform: translateY(-2px);
  box-shadow: 0 4px 12px rgba(0,0,0,0.1);
}

.trend-value {
  font-size: 24px;
  font-weight: bold;
  color: #409eff;
  margin-bottom: 8px;
}

.trend-label {
  font-size: 12px;
  color: #606266;
}

/* 高级筛选样式 */
.search-row {
  margin-bottom: 0;
}

.advanced-filters {
  margin-top: 20px;
  padding-top: 20px;
}

.filter-row {
  margin-bottom: 16px;
}

.filter-group {
  margin-bottom: 16px;
}

.filter-label {
  display: flex;
  align-items: center;
  gap: 4px;
  font-size: 14px;
  font-weight: 500;
  color: #303133;
  margin-bottom: 8px;
}

.my-tags-filter {
  display: flex;
  flex-wrap: wrap;
  gap: 8px;
  align-items: center;
  padding: 12px;
  background: #f8f9fa;
  border-radius: 8px;
  border: 1px solid #e9ecef;
  min-height: 60px;
}

.user-tag-filter {
  cursor: pointer;
  transition: all 0.3s;
  margin: 0;
  border-radius: 6px;
  display: inline-flex;
  align-items: center;
  gap: 4px;
}

.user-tag-filter:hover {
  transform: translateY(-2px);
  box-shadow: 0 4px 12px rgba(0,0,0,0.15);
}

.user-tag-filter .tag-weight {
  font-size: 11px;
  opacity: 0.7;
  margin-left: 2px;
}

.filter-summary {
  margin-top: 16px;
}

.active-filters {
  display: flex;
  flex-wrap: wrap;
  gap: 8px;
  margin-top: 8px;
}

.active-filters .el-tag {
  margin: 0;
}
</style> 