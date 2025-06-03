/**
 * 统一标签配置服务
 * 负责从API获取所有标签配置，避免前端多处硬编码
 */

import api from '@/api/request'

export interface TagOptions {
  energy_type_tags: string[]
  basic_info_tags: string[]
  business_field_tags: string[]
  beneficiary_tags: string[]
  policy_measure_tags: string[]
  importance_tags: string[]
  content_type_map: Record<string, string>
  region_tags: {
    cities: string[]
    cities_by_region: Record<string, string[]>
    provinces: string[]
    regions: string[]
    total_cities: number
    total_provinces: number
    total_regions: number
  }
}

export interface TagCategory {
  key: string
  name: string
  description: string
  color: string
  presetTags: string[]
}

class TagService {
  private static instance: TagService
  private cachedTagOptions: TagOptions | null = null
  private cacheTimestamp: number = 0
  private readonly CACHE_DURATION = 5 * 60 * 1000 // 5分钟缓存

  static getInstance(): TagService {
    if (!TagService.instance) {
      TagService.instance = new TagService()
    }
    return TagService.instance
  }

  /**
   * 获取所有标签选项（带缓存）
   */
  async getTagOptions(forceRefresh: boolean = false): Promise<TagOptions> {
    const now = Date.now()
    
    // 检查缓存是否有效
    if (!forceRefresh && 
        this.cachedTagOptions && 
        (now - this.cacheTimestamp) < this.CACHE_DURATION) {
      console.log('🏷️ 使用缓存的标签配置')
      return this.cachedTagOptions
    }

    try {
      console.log('🌐 从API获取标签配置...')
      const response = await api.get('/users/tag-options')
      const tagOptions = response.data

      // 更新缓存
      this.cachedTagOptions = tagOptions
      this.cacheTimestamp = now

      console.log('✅ 标签配置获取成功:', {
        energy_types: tagOptions.energy_type_tags?.length || 0,
        basic_info: tagOptions.basic_info_tags?.length || 0,
        business_fields: tagOptions.business_field_tags?.length || 0,
        beneficiaries: tagOptions.beneficiary_tags?.length || 0,
        policy_measures: tagOptions.policy_measure_tags?.length || 0,
        importance: tagOptions.importance_tags?.length || 0,
        cities: tagOptions.region_tags?.total_cities || 0
      })

      return tagOptions
    } catch (error) {
      console.error('❌ 获取标签配置失败:', error)
      
      // 如果有缓存，返回缓存的数据
      if (this.cachedTagOptions) {
        console.warn('⚠️ 使用过期的缓存标签配置')
        return this.cachedTagOptions
      }

      // API失败且无缓存时，抛出错误让调用方处理
      throw new Error('无法获取标签配置，请检查网络连接或联系管理员')
    }
  }

  /**
   * 获取标签分类配置（供TagsManagement.vue等使用）
   */
  async getTagCategories(): Promise<TagCategory[]> {
    const tagOptions = await this.getTagOptions()

    return [
      {
        key: 'basic_info',
        name: '📄 基础信息',
        description: '内容类型和基础属性标签',
        color: 'primary',
        presetTags: tagOptions.basic_info_tags || []
      },
      {
        key: 'region',
        name: '🗺️ 地域标签',
        description: '地理区域相关标签（请使用下方的省份城市选择器添加）',
        color: 'success',
        presetTags: [] // 地域标签使用选择器，不用预设标签
      },
      {
        key: 'energy_type',
        name: '⚡ 能源品种',
        description: '能源类型和细分品种标签',
        color: 'warning',
        presetTags: tagOptions.energy_type_tags || []
      },
      {
        key: 'business_field',
        name: '🏢 业务领域',
        description: '业务类型和关注主题标签',
        color: 'info',
        presetTags: tagOptions.business_field_tags || []
      },
      {
        key: 'beneficiary',
        name: '👥 受益主体',
        description: '涉及的主体类型标签',
        color: 'danger',
        presetTags: tagOptions.beneficiary_tags || []
      },
      {
        key: 'policy_measure',
        name: '📋 政策措施',
        description: '政策措施和关键举措标签',
        color: 'success',
        presetTags: tagOptions.policy_measure_tags || []
      },
      {
        key: 'importance',
        name: '⭐ 重要性',
        description: '内容重要程度和影响范围标签',
        color: 'warning',
        presetTags: tagOptions.importance_tags || []
      }
    ]
  }

  /**
   * 获取Admin页面的预设标签（供AdminArticles.vue使用）
   */
  async getAdminPresetTags(): Promise<{
    energy_types: string[]
    regions: string[]
    basic_info: string[]
    business_fields: string[]
    beneficiaries: string[]
    policy_measures: string[]
    importance: string[]
  }> {
    const tagOptions = await this.getTagOptions()

    // 合并所有地区标签（城市、省份、地区）
    const allRegionTags: string[] = []
    if (tagOptions.region_tags) {
      allRegionTags.push(
        ...tagOptions.region_tags.cities,
        ...tagOptions.region_tags.provinces,
        ...tagOptions.region_tags.regions
      )
    }

    return {
      energy_types: tagOptions.energy_type_tags || [],
      regions: [...new Set(allRegionTags)].sort(), // 去重并排序
      basic_info: tagOptions.basic_info_tags || [],
      business_fields: tagOptions.business_field_tags || [],
      beneficiaries: tagOptions.beneficiary_tags || [],
      policy_measures: tagOptions.policy_measure_tags || [],
      importance: tagOptions.importance_tags || []
    }
  }

  /**
   * 获取省份城市数据（供地区选择器使用）
   */
  async getProvincesWithCities(): Promise<any> {
    try {
      const response = await api.get('/users/provinces-with-cities')
      return response.data
    } catch (error) {
      console.error('❌ 获取省份城市数据失败:', error)
      throw error
    }
  }

  /**
   * 获取城市详情数据
   */
  async getCitiesDetails(): Promise<any> {
    try {
      const response = await api.get('/users/cities-details')
      return response.data
    } catch (error) {
      console.error('❌ 获取城市详情失败:', error)
      throw error
    }
  }

  /**
   * 获取内容类型显示名称
   */
  async getContentTypeDisplayName(type: string): Promise<string> {
    const tagOptions = await this.getTagOptions()
    return tagOptions.content_type_map[type] || type
  }

  /**
   * 获取所有内容类型映射
   */
  async getContentTypeMap(): Promise<Record<string, string>> {
    const tagOptions = await this.getTagOptions()
    return tagOptions.content_type_map || {}
  }

  /**
   * 清除缓存（用于强制刷新）
   */
  clearCache(): void {
    this.cachedTagOptions = null
    this.cacheTimestamp = 0
    console.log('🗑️ 标签配置缓存已清除')
  }
}

// 导出单例实例
export const tagService = TagService.getInstance()
export default tagService 