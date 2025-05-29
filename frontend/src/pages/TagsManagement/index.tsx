import React, { useState, useEffect } from 'react';
import {
  Card,
  Row,
  Col,
  Tag,
  Button,
  Form,
  Input,
  Select,
  Modal,
  message,
  Tabs,
  Badge,
  Spin,
  Alert,
  Slider,
  Space
} from 'antd';
import { 
  PlusOutlined, 
  EditOutlined, 
  DeleteOutlined, 
  SaveOutlined,
  ReloadOutlined,
  TagsOutlined,
  CheckOutlined
} from '@ant-design/icons';
import { useSelector } from 'react-redux';
import { userService } from '../../services/userService';
import type { RootState } from '../../store';

interface UserTag {
  category: string;
  name: string;
  weight: number;
  source: string;
  created_at: string;
}

interface TagCategory {
  key: string;
  name: string;
  description: string;
  color: string;
  presetTags: string[];
}

interface City {
  value: string;
  label: string;
  province?: string;
  region?: string;
}

interface CitiesDetailsResponse {
  cities: Array<{
    city: string;
    province: string;
    region: string;
    province_code: string;
    region_code: string;
  }>;
  total: number;
}

// 城市到省份和地区的映射关系（作为备用）
const cityMapping: { [key: string]: { province: string; region: string } } = {
  '上海': { province: '上海市', region: '华东地区' },
  '北京': { province: '北京市', region: '华北地区' },
  '深圳': { province: '广东省', region: '华南地区' },
  '广州': { province: '广东省', region: '华南地区' },
  '杭州': { province: '浙江省', region: '华东地区' },
  '成都': { province: '四川省', region: '西南地区' },
  '长沙': { province: '湖南省', region: '华中地区' },
  '武汉': { province: '湖北省', region: '华中地区' },
  '南京': { province: '江苏省', region: '华东地区' },
  '苏州': { province: '江苏省', region: '华东地区' },
  '天津': { province: '天津市', region: '华北地区' },
  '重庆': { province: '重庆市', region: '西南地区' },
  '西安': { province: '陕西省', region: '西北地区' },
  '郑州': { province: '河南省', region: '华中地区' },
  '沈阳': { province: '辽宁省', region: '东北地区' },
  '大连': { province: '辽宁省', region: '东北地区' },
  '青岛': { province: '山东省', region: '华东地区' },
  '济南': { province: '山东省', region: '华东地区' }
};

const TagsManagement: React.FC = () => {
  const { user } = useSelector((state: RootState) => state.auth);
  const { currentUserId } = useSelector((state: RootState) => state.user);
  const [userTags, setUserTags] = useState<UserTag[]>([]);
  const [loading, setLoading] = useState(true);
  const [saving, setSaving] = useState(false);
  const [isModalVisible, setIsModalVisible] = useState(false);
  const [editingTag, setEditingTag] = useState<UserTag | null>(null);
  const [form] = Form.useForm();
  const [activeTab, setActiveTab] = useState('city');
  const [error, setError] = useState<string | null>(null);
  const [connectionTest, setConnectionTest] = useState<boolean | null>(null);
  const [cities, setCities] = useState<City[]>([]);
  const [citiesLoading, setCitiesLoading] = useState(false);

  // 简化的6大类标签配置（去掉省份和地区）
  const tagCategories: TagCategory[] = [
    {
      key: 'city',
      name: '🏙️ 城市标签',
      description: '选择城市后自动生成省份和地区标签',
      color: 'blue',
      presetTags: cities.map(city => city.value) // 使用动态城市列表
    },
    {
      key: 'energy_type',
      name: '⚡ 能源品种标签',
      description: '能源类型和细分品种',
      color: 'cyan',
      presetTags: ['原油', '管道天然气(PNG)', '天然气', '液化天然气(LNG)', '液化石油气(LPG)', '汽油', '柴油', '沥青', '石油焦', '生物柴油', '电力', '煤炭']
    },
    {
      key: 'business_field',
      name: '🏢 业务领域标签',
      description: '业务类型和关注主题',
      color: 'purple',
      presetTags: ['市场动态', '价格变化', '交易信息', '科技创新', '政策解读', '国际合作', '投资支持']
    },
    {
      key: 'beneficiary',
      name: '👥 受益主体标签',
      description: '涉及的主体类型',
      color: 'red',
      presetTags: ['能源企业', '政府机构', '交易方', '民营企业', '国有企业', '外资企业']
    },
    {
      key: 'policy_measure',
      name: '📋 关键措施标签',
      description: '政策措施和关键举措',
      color: 'gold',
      presetTags: ['市场监管', '技术合作', '竞价规则', '投资支持', '市场准入', '创新投融资', '风险管控']
    },
    {
      key: 'importance',
      name: '⭐ 重要性标签',
      description: '内容重要程度和影响范围',
      color: 'magenta',
      presetTags: ['国家级', '权威发布', '重要政策', '行业影响', '常规公告', '国际影响']
    }
  ];

  useEffect(() => {
    // 先加载城市列表
    loadCities();
    
    const effectiveUserId = currentUserId || user?.id;
    if (effectiveUserId) {
      loadUserTags(effectiveUserId);
    } else {
      console.warn('用户未登录或用户ID不存在');
      setLoading(false);
      setError('用户未登录，无法加载标签数据');
    }
  }, [currentUserId, user]);

  const loadCities = async () => {
    setCitiesLoading(true);
    try {
      // 使用城市详情API获取完整的城市信息
      const response = await fetch('/api/v1/users/cities-details');
      if (response.ok) {
        const data: CitiesDetailsResponse = await response.json();
        
        // 将城市列表转换为带有省份和区域信息的格式
        const cityOptions: City[] = data.cities.map(cityData => ({
          value: cityData.city,
          label: cityData.city,
          province: cityData.province,
          region: cityData.region
        }));
        
        setCities(cityOptions);
        console.log('✅ 城市列表加载成功，数量:', cityOptions.length);
      } else {
        throw new Error(`HTTP ${response.status}`);
      }
    } catch (error) {
      console.error('加载城市列表失败:', error);
      
      // 使用备用城市列表
      const fallbackCities: City[] = Object.keys(cityMapping).map(cityName => ({
        value: cityName,
        label: cityName,
        province: cityMapping[cityName].province,
        region: cityMapping[cityName].region
      }));
      setCities(fallbackCities);
      console.log('🔄 使用备用城市列表，数量:', fallbackCities.length);
    } finally {
      setCitiesLoading(false);
    }
  };

  const loadUserTags = async (userId: string) => {
    if (!userId) {
      setError('用户信息无效');
      setLoading(false);
      return;
    }
    
    setLoading(true);
    setError(null);
    console.log('🏷️ 标签管理页面开始加载用户标签，用户ID:', userId);
    
    try {
      // 优先尝试演示用户API
      let response;
      try {
        console.log('尝试使用演示用户API...');
        response = await userService.getDemoUserTags(userId);
        if (response && response.tags) {
          console.log('✅ 演示用户标签加载成功:', response.tags.length);
        } else {
          throw new Error('演示用户API返回空数据');
        }
      } catch (demoError) {
        console.log('演示用户API失败，尝试常规API...');
        response = await userService.getUserTags(userId);
      }
      
      console.log('📥 用户标签响应:', response);
      
      if (response && response.tags) {
        setUserTags(response.tags);
        console.log('✅ 标签加载成功，数量:', response.tags.length);
        setConnectionTest(true);
        
        if (response.tags.length === 0) {
          message.info('暂无标签，请选择感兴趣的标签类型');
        } else {
          message.success(`成功加载 ${response.tags.length} 个标签`);
        }
      } else {
        console.log('⚠️ 响应为空或格式错误');
        setUserTags([]);
        setConnectionTest(true);
        message.info('未找到用户标签，请添加标签');
      }
    } catch (error: any) {
      console.error('❌ 加载用户标签失败:', error);
      setConnectionTest(false);
      
      // 详细的错误处理
      if (error.code === 'ECONNABORTED') {
        setError('网络连接超时，请检查网络连接');
        message.error('网络连接超时');
      } else if (error.message?.includes('ECONNREFUSED')) {
        setError('无法连接到后端服务，请确认服务已启动');
        message.error('后端服务连接失败');
      } else if (error.response?.status === 404) {
        setError('用户标签不存在，可能是首次使用');
        message.info('首次使用，请选择您感兴趣的标签');
        setUserTags([]); // 设置为空数组而不是默认标签
      } else if (error.response?.status === 401) {
        setError('认证失败，请重新登录');
        message.error('认证失败，请重新登录');
      } else {
        setError(`加载失败: ${error.message || '未知错误'}`);
        message.error('标签加载失败');
      }
      
      // 只有在连接错误时才设置空数组
      setUserTags([]);
    } finally {
      setLoading(false);
    }
  };

  const saveUserTags = async () => {
    const effectiveUserId = currentUserId || user?.id;
    if (!effectiveUserId) {
      message.error('用户信息无效，无法保存标签');
      return;
    }
    
    if (userTags.length === 0) {
      message.warning('请至少选择一个标签');
      return;
    }
    
    setSaving(true);
    console.log('💾 开始保存用户标签:', userTags);
    
    try {
      const response = await userService.updateUserTags(effectiveUserId, userTags);
      console.log('✅ 标签保存成功:', response);
      message.success(`成功保存 ${userTags.length} 个标签`);
      
      // 刷新标签数据确保同步
      await loadUserTags(effectiveUserId);
    } catch (error: any) {
      console.error('❌ 标签保存失败:', error);
      if (error.response?.status === 401) {
        message.error('认证失败，请重新登录');
      } else {
        message.error(`保存失败: ${error.message || '未知错误'}`);
      }
    } finally {
      setSaving(false);
    }
  };

  const addPresetTag = (category: string, tagName: string) => {
    const existingTag = userTags.find(tag => 
      tag.category === category && tag.name === tagName
    );
    
    if (existingTag) {
      message.warning('该标签已存在');
      return;
    }

    let newTags: UserTag[] = [];

    // 添加主标签
    const newTag: UserTag = {
      category,
      name: tagName,
      weight: 1.0,
      source: 'preset',
      created_at: new Date().toISOString()
    };
    newTags.push(newTag);

    // 如果是城市标签，自动添加对应的省份和地区标签
    if (category === 'city') {
      // 优先从动态加载的城市列表中查找
      const cityData = cities.find(city => city.value === tagName);
      let province = '';
      let region = '';
      
      if (cityData) {
        province = cityData.province || '';
        region = cityData.region || '';
      } else if (cityMapping[tagName]) {
        // 备用：从静态映射中查找
        province = cityMapping[tagName].province;
        region = cityMapping[tagName].region;
      }
      
      if (province && region) {
        // 检查省份标签是否已存在
        const existingProvinceTag = userTags.find(tag => 
          tag.category === 'province' && tag.name === province
        );
        if (!existingProvinceTag) {
          newTags.push({
            category: 'province',
            name: province,
            weight: 1.0,
            source: 'auto',
            created_at: new Date().toISOString()
          });
        }

        // 检查地区标签是否已存在
        const existingRegionTag = userTags.find(tag => 
          tag.category === 'region' && tag.name === region
        );
        if (!existingRegionTag) {
          newTags.push({
            category: 'region',
            name: region,
            weight: 1.0,
            source: 'auto',
            created_at: new Date().toISOString()
          });
        }
      }
    }

    setUserTags([...userTags, ...newTags]);
    
    // 显示添加的标签信息
    if (newTags.length === 1) {
      message.success(`添加标签: ${tagName}`);
    } else {
      const addedNames = newTags.map(t => t.name).join('、');
      message.success(`添加标签: ${addedNames}`);
    }
  };

  const updateTagWeight = (category: string, tagName: string, weight: number) => {
    setUserTags(userTags.map(tag =>
      tag.category === category && tag.name === tagName
        ? { ...tag, weight }
        : tag
    ));
  };

  const removeTag = (category: string, tagName: string) => {
    setUserTags(userTags.filter(tag => 
      !(tag.category === category && tag.name === tagName)
    ));
    message.success(`移除标签: ${tagName}`);
  };

  const openAddTagModal = (category?: string) => {
    setEditingTag(null);
    form.resetFields();
    if (category) {
      form.setFieldsValue({ category });
    }
    setIsModalVisible(true);
  };

  const openEditTagModal = (tag: UserTag) => {
    setEditingTag(tag);
    form.setFieldsValue({
      category: tag.category,
      name: tag.name,
      weight: tag.weight
    });
    setIsModalVisible(true);
  };

  const handleTagSubmit = () => {
    form.validateFields().then(values => {
      if (editingTag) {
        // 编辑现有标签
        setUserTags(userTags.map(tag =>
          tag.category === editingTag.category && tag.name === editingTag.name
            ? { ...tag, ...values }
            : tag
        ));
        message.success('标签更新成功');
      } else {
        // 添加新标签
        const existingTag = userTags.find(tag => 
          tag.category === values.category && tag.name === values.name
        );
        
        if (existingTag) {
          message.error('该标签已存在');
          return;
        }

        const newTag: UserTag = {
          category: values.category,
          name: values.name,
          weight: values.weight || 1.0,
          source: 'manual',
          created_at: new Date().toISOString()
        };
        
        setUserTags([...userTags, newTag]);
        message.success('标签添加成功');
      }
      setIsModalVisible(false);
    });
  };

  const getUserTagsByCategory = (category: string) => {
    return userTags.filter(tag => tag.category === category);
  };

  const getCategoryStats = () => {
    // 基本标签分类统计
    const basicStats = tagCategories.map(category => ({
      ...category,
      count: getUserTagsByCategory(category.key).length
    }));

    // 添加省份和地区标签的统计（这些是自动生成的）
    const additionalStats = [
      {
        key: 'province',
        name: '📍 省份标签',
        description: '自动生成的省份标签',
        color: 'green',
        presetTags: [],
        count: getUserTagsByCategory('province').length
      },
      {
        key: 'region',
        name: '🗺️ 区域标签',
        description: '自动生成的区域标签',
        color: 'orange',
        presetTags: [],
        count: getUserTagsByCategory('region').length
      }
    ];

    return [...basicStats, ...additionalStats];
  };

  // 渲染标签类别内容
  const renderCategoryTags = (category: TagCategory) => {
    const userCategoryTags = getUserTagsByCategory(category.key);
    
    return (
      <div className="space-y-4">
        {/* 类别描述 */}
        <div className="bg-gray-50 p-4 rounded-lg">
          <div className="flex items-center justify-between mb-2">
            <h3 className="font-semibold text-lg">{category.name}</h3>
            <Badge count={userCategoryTags.length} showZero />
          </div>
          <p className="text-gray-600 text-sm">{category.description}</p>
        </div>

        {/* 用户已选标签 */}
        {userCategoryTags.length > 0 && (
          <Card title="已选标签" size="small">
            <div className="space-y-3">
              {userCategoryTags.map((tag, index) => (
                <div key={index} className="flex items-center justify-between p-3 border rounded-lg">
                  <div className="flex items-center space-x-3">
                    <Tag color={category.color}>{tag.name}</Tag>
                    <span className="text-xs text-gray-500">
                      来源: {tag.source === 'preset' ? '预设' : tag.source === 'manual' ? '手动' : '自动'}
                    </span>
                  </div>
                  <div className="flex items-center space-x-3">
                    <div className="flex items-center space-x-2" style={{ minWidth: '120px' }}>
                      <span className="text-xs">权重:</span>
                      <Slider
                        min={0}
                        max={3}
                        step={0.1}
                        value={tag.weight}
                        onChange={(value) => updateTagWeight(tag.category, tag.name, value)}
                        style={{ flex: 1 }}
                      />
                      <span className="text-xs w-8">{tag.weight}</span>
                    </div>
                    <Space>
                      <Button
                        size="small"
                        icon={<EditOutlined />}
                        onClick={() => openEditTagModal(tag)}
                      />
                      <Button
                        size="small"
                        danger
                        icon={<DeleteOutlined />}
                        onClick={() => removeTag(tag.category, tag.name)}
                      />
                    </Space>
                  </div>
                </div>
              ))}
            </div>
          </Card>
        )}

        {/* 预设标签选择 */}
        <Card title="预设标签" size="small">
          <div className="space-y-2">
            <div className="text-xs text-gray-500 mb-3">
              {category.key === 'city' 
                ? '使用下拉框选择城市，自动生成省份和地区标签' 
                : '点击下方标签快速添加到您的标签库'
              }
            </div>
            
            {/* 城市标签使用下拉框选择 */}
            {category.key === 'city' ? (
              <Select
                placeholder={citiesLoading ? "正在加载城市列表..." : "选择城市"}
                style={{ width: '100%' }}
                showSearch
                size="large"
                loading={citiesLoading}
                filterOption={(input, option) => {
                  const label = option?.children || '';
                  return String(label).toLowerCase().includes(input.toLowerCase());
                }}
                onChange={(cityValue: string) => {
                  if (cityValue) {
                    const isSelected = userCategoryTags.some(tag => tag.name === cityValue);
                    if (isSelected) {
                      removeTag(category.key, cityValue);
                    } else {
                      addPresetTag(category.key, cityValue);
                    }
                  }
                }}
                value={undefined} // 选择后清空
                notFoundContent={citiesLoading ? "加载中..." : "未找到匹配的城市"}
              >
                {cities.map(city => {
                  const isSelected = userCategoryTags.some(tag => tag.name === city.value);
                  return (
                    <Select.Option key={city.value} value={city.value}>
                      <div className="flex justify-between items-center">
                        <span>
                          {isSelected ? <CheckOutlined className="mr-2 text-green-500" /> : null}
                          🏙️ {city.value}
                        </span>
                        <div className="text-xs text-gray-500">
                          {city.province} · {city.region}
                        </div>
                      </div>
                    </Select.Option>
                  );
                })}
              </Select>
            ) : (
              /* 其他标签使用原来的标签点击方式 */
              <div className="flex flex-wrap gap-2">
                {category.presetTags.map(tagName => {
                  const isSelected = userCategoryTags.some(tag => tag.name === tagName);
                  return (
                    <Tag
                      key={tagName}
                      color={isSelected ? category.color : 'default'}
                      style={{ cursor: 'pointer' }}
                      icon={isSelected ? <CheckOutlined /> : <PlusOutlined />}
                      onClick={() => {
                        if (isSelected) {
                          removeTag(category.key, tagName);
                        } else {
                          addPresetTag(category.key, tagName);
                        }
                      }}
                    >
                      {tagName}
                    </Tag>
                  );
                })}
              </div>
            )}
          </div>
        </Card>

        {/* 自定义标签添加 */}
        <Card title="自定义标签" size="small">
          <Button
            type="dashed"
            icon={<PlusOutlined />}
            onClick={() => openAddTagModal(category.key)}
            block
          >
            添加自定义{category.name.replace(/[🏙️📍🗺️⚡🏢👥📋⭐📄]/g, '').replace('标签', '')}
          </Button>
        </Card>
      </div>
    );
  };

  if (loading) {
    return (
      <div className="flex justify-center items-center min-h-96">
        <Spin size="large">
          <div className="text-center py-8">
            <div className="text-gray-500">正在加载标签数据...</div>
            <div className="text-xs text-gray-400 mt-2">
              用户ID: {currentUserId || user?.id || '未获取'}
            </div>
          </div>
        </Spin>
      </div>
    );
  }

  // 如果有连接错误，显示错误页面
  if (connectionTest === false) {
    return (
      <div className="max-w-4xl mx-auto p-6">
        <Alert
          message="连接失败"
          description={
            <div>
              <p>{error}</p>
              <div className="mt-4 space-y-2 text-sm">
                <div>🔍 <strong>检查项目:</strong></div>
                <div>1. 后端服务是否启动 (端口 8001)</div>
                <div>2. MongoDB 是否运行</div>
                <div>3. 网络连接是否正常</div>
                <div className="mt-3">
                  <strong>调试信息:</strong><br/>
                  API 地址: http://localhost:8001/api/v1<br/>
                  用户ID: {currentUserId || user?.id || '未获取'}
                </div>
              </div>
            </div>
          }
          type="error"
          showIcon
          action={
            <Button type="primary" onClick={() => loadUserTags(currentUserId || user?.id || '')}>
              重新连接
            </Button>
          }
        />
      </div>
    );
  }

  return (
    <div className="max-w-6xl mx-auto p-6">
      {/* 页面头部 */}
      <div className="flex items-center justify-between mb-6">
        <div>
          <h2 className="text-2xl font-bold flex items-center">
            <TagsOutlined className="mr-2" />
            标签管理
          </h2>
          <p className="text-gray-500 mt-1">
            管理您的兴趣标签，获得个性化内容推荐
          </p>
        </div>
        <div className="flex space-x-2">
          <Button
            icon={<ReloadOutlined />}
            onClick={() => loadUserTags(currentUserId || user?.id || '')}
            loading={loading}
          >
            刷新
          </Button>
          <Button
            type="primary"
            icon={<SaveOutlined />}
            onClick={saveUserTags}
            loading={saving}
            disabled={userTags.length === 0}
          >
            保存标签 ({userTags.length})
          </Button>
        </div>
      </div>

      {/* 错误提示 */}
      {error && (
        <Alert 
          message={error} 
          type="warning" 
          showIcon 
          className="mb-4"
          action={
            <Button size="small" onClick={() => loadUserTags(currentUserId || user?.id || '')}>
              重试
            </Button>
          }
        />
      )}

      {/* 连接状态指示 */}
      <div className="mb-4 p-3 bg-gray-50 rounded-lg">
        <div className="flex items-center justify-between text-sm">
          <div className="flex items-center space-x-4">
            <span>连接状态: {connectionTest ? '✅ 正常' : '❌ 异常'}</span>
            <span>用户: {user?.username || '未知'}</span>
            <span>用户ID: {currentUserId || user?.id || '未获取'}</span>
          </div>
          <div>
            标签总数: <Badge count={userTags.length} showZero />
          </div>
        </div>
      </div>

      {/* 标签统计概览 */}
      <Row gutter={16} className="mb-6">
        {getCategoryStats().map(cat => (
          <Col span={8} key={cat.key} className="mb-4">
            <Card size="small" className="text-center">
              <div className="font-semibold">{cat.name}</div>
              <div className="text-2xl font-bold text-blue-600">{cat.count}</div>
              <div className="text-xs text-gray-500">个标签</div>
            </Card>
          </Col>
        ))}
      </Row>

      {/* 标签分类选项卡 */}
      <Card>
        <Tabs 
          activeKey={activeTab}
          onChange={setActiveTab}
          items={[
            // 基本标签选项卡
            ...tagCategories.map(category => ({
              key: category.key,
              label: (
                <div className="flex items-center">
                  {category.name}
                  <Badge 
                    count={getUserTagsByCategory(category.key).length} 
                    size="small" 
                    style={{ marginLeft: 8 }}
                  />
                </div>
              ),
              children: renderCategoryTags(category)
            })),
            // 省份标签选项卡（只读）
            {
              key: 'province',
              label: (
                <div className="flex items-center">
                  📍 省份标签
                  <Badge 
                    count={getUserTagsByCategory('province').length} 
                    size="small" 
                    style={{ marginLeft: 8 }}
                  />
                </div>
              ),
              children: (
                <div className="space-y-4">
                  <div className="bg-gray-50 p-4 rounded-lg">
                    <h3 className="font-semibold text-lg">📍 省份标签</h3>
                    <p className="text-gray-600 text-sm">这些标签根据您选择的城市自动生成</p>
                  </div>
                  {getUserTagsByCategory('province').length > 0 && (
                    <Card title="省份标签" size="small">
                      <div className="flex flex-wrap gap-2">
                        {getUserTagsByCategory('province').map((tag, index) => (
                          <Tag key={index} color="green">
                            {tag.name}
                            <span className="ml-2 text-xs">(权重: {tag.weight})</span>
                          </Tag>
                        ))}
                      </div>
                    </Card>
                  )}
                  {getUserTagsByCategory('province').length === 0 && (
                    <Card size="small">
                      <div className="text-center text-gray-500 py-4">
                        暂无省份标签，请先选择城市标签
                      </div>
                    </Card>
                  )}
                </div>
              )
            },
            // 区域标签选项卡（只读）
            {
              key: 'region',
              label: (
                <div className="flex items-center">
                  🗺️ 区域标签
                  <Badge 
                    count={getUserTagsByCategory('region').length} 
                    size="small" 
                    style={{ marginLeft: 8 }}
                  />
                </div>
              ),
              children: (
                <div className="space-y-4">
                  <div className="bg-gray-50 p-4 rounded-lg">
                    <h3 className="font-semibold text-lg">🗺️ 区域标签</h3>
                    <p className="text-gray-600 text-sm">这些标签根据您选择的城市自动生成</p>
                  </div>
                  {getUserTagsByCategory('region').length > 0 && (
                    <Card title="区域标签" size="small">
                      <div className="flex flex-wrap gap-2">
                        {getUserTagsByCategory('region').map((tag, index) => (
                          <Tag key={index} color="orange">
                            {tag.name}
                            <span className="ml-2 text-xs">(权重: {tag.weight})</span>
                          </Tag>
                        ))}
                      </div>
                    </Card>
                  )}
                  {getUserTagsByCategory('region').length === 0 && (
                    <Card size="small">
                      <div className="text-center text-gray-500 py-4">
                        暂无区域标签，请先选择城市标签
                      </div>
                    </Card>
                  )}
                </div>
              )
            }
          ]}
        />
      </Card>

      {/* 添加/编辑标签模态框 */}
      <Modal
        title={editingTag ? '编辑标签' : '添加自定义标签'}
        open={isModalVisible}
        onOk={handleTagSubmit}
        onCancel={() => setIsModalVisible(false)}
        okText="确定"
        cancelText="取消"
      >
        <Form form={form} layout="vertical">
          <Form.Item
            name="category"
            label="标签分类"
            rules={[{ required: true, message: '请选择标签分类' }]}
          >
            <Select placeholder="选择分类">
              {tagCategories.map(cat => (
                <Select.Option key={cat.key} value={cat.key}>
                  {cat.name}
                </Select.Option>
              ))}
            </Select>
          </Form.Item>
          
          <Form.Item
            name="name"
            label="标签名称"
            rules={[{ required: true, message: '请输入标签名称' }]}
          >
            <Input placeholder="请输入标签名称" />
          </Form.Item>
          
          <Form.Item
            name="weight"
            label="权重"
            initialValue={1.0}
          >
            <Slider min={0} max={3} step={0.1} />
          </Form.Item>
        </Form>
      </Modal>
    </div>
  );
};

export default TagsManagement; 