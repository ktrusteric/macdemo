import React, { useState, useEffect } from 'react';
import { 
  Card, 
  Tag, 
  Button, 
  Slider, 
  Space, 
  Modal, 
  Form, 
  Input, 
  Select, 
  message,
  Tabs,
  Tooltip,
  Badge,
  Spin,
  Alert,
  Typography
} from 'antd';
import { 
  PlusOutlined, 
  EditOutlined, 
  DeleteOutlined, 
  SaveOutlined,
  ReloadOutlined,
  InfoCircleOutlined,
  TagsOutlined
} from '@ant-design/icons';

const { Title } = Typography;

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

const TestTagsPage: React.FC = () => {
  const [userTags, setUserTags] = useState<UserTag[]>([]);
  const [loading, setLoading] = useState(false);
  const [saving, setSaving] = useState(false);
  const [isModalVisible, setIsModalVisible] = useState(false);
  const [editingTag, setEditingTag] = useState<UserTag | null>(null);
  const [form] = Form.useForm();
  const [activeTab, setActiveTab] = useState('city');
  
  // 测试用户ID
  const testUserId = 'test_user_123';

  // 9大类标签配置
  const tagCategories: TagCategory[] = [
    {
      key: 'city',
      name: '🏙️ 城市标签',
      description: '您所在城市的相关内容和政策',
      color: 'blue',
      presetTags: ['上海', '北京', '深圳', '广州', '杭州', '成都', '长沙', '武汉', '南京', '苏州', '天津', '重庆']
    },
    {
      key: 'province',
      name: '📍 省份标签',
      description: '省级行政区域的政策和发展动态',
      color: 'green',
      presetTags: ['上海市', '北京市', '广东省', '浙江省', '四川省', '湖南省', '湖北省', '江苏省', '天津市', '重庆市']
    },
    {
      key: 'region',
      name: '🗺️ 区域标签', 
      description: '大区域范围的宏观政策和发展趋势',
      color: 'orange',
      presetTags: ['华东地区', '华南地区', '华北地区', '华中地区', '西南地区', '西北地区', '东北地区']
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
    },
    {
      key: 'basic_info',
      name: '📄 基础信息标签',
      description: '内容类型和基础属性',
      color: 'lime',
      presetTags: ['政策法规', '行业资讯', '交易公告', '研报分析', '价格变动', '科技创新']
    }
  ];

  useEffect(() => {
    loadUserTags();
  }, []);

  const loadUserTags = async () => {
    setLoading(true);
    try {
      const response = await fetch(`/api/v1/users/${testUserId}/tags`);
      if (response.ok) {
        const data = await response.json();
        setUserTags(data.data.tags || []);
        message.success('标签加载成功');
      } else if (response.status === 404) {
        // 用户暂无标签，显示默认状态
        setUserTags([]);
        message.info('暂无标签，请添加您感兴趣的标签');
      } else {
        throw new Error(`HTTP ${response.status}`);
      }
    } catch (error: any) {
      console.error('Failed to load user tags:', error);
      message.error('标签加载失败，使用默认配置');
      // 设置一些默认标签用于测试
      setUserTags([
        {
          category: 'city',
          name: '上海',
          weight: 2.0,
          source: 'preset',
          created_at: new Date().toISOString()
        },
        {
          category: 'energy_type',
          name: '天然气',
          weight: 1.5,
          source: 'preset',
          created_at: new Date().toISOString()
        }
      ]);
    } finally {
      setLoading(false);
    }
  };

  const saveUserTags = async () => {
    setSaving(true);
    try {
      const response = await fetch(`/api/v1/users/${testUserId}/tags`, {
        method: 'PUT',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify({ tags: userTags }),
      });

      if (response.ok) {
        const data = await response.json();
        message.success('标签保存成功！');
        console.log('保存结果:', data);
      } else {
        throw new Error(`HTTP ${response.status}`);
      }
    } catch (error) {
      console.error('Failed to save user tags:', error);
      message.error('标签保存失败');
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
    
    const newTag: UserTag = {
      category,
      name: tagName,
      weight: 1.0,
      source: 'preset',
      created_at: new Date().toISOString()
    };
    
    setUserTags([...userTags, newTag]);
    message.success(`已添加标签: ${tagName}`);
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
    message.success(`已删除标签: ${tagName}`);
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
          message.warning('该标签已存在');
          return;
        }
        
        const newTag: UserTag = {
          ...values,
          source: 'manual',
          created_at: new Date().toISOString()
        };
        
        setUserTags([...userTags, newTag]);
        message.success('标签添加成功');
      }
      
      setIsModalVisible(false);
      form.resetFields();
    });
  };

  const getUserTagsByCategory = (category: string) => {
    return userTags.filter(tag => tag.category === category);
  };

  const getCategoryStats = () => {
    const stats = tagCategories.map(category => ({
      ...category,
      count: getUserTagsByCategory(category.key).length
    }));
    return stats;
  };

  const renderCategoryTags = (category: TagCategory) => {
    const categoryTags = getUserTagsByCategory(category.key);
    const availablePresets = category.presetTags.filter(preset => 
      !categoryTags.find(tag => tag.name === preset)
    );

    return (
      <div className="space-y-4">
        {/* 现有标签 */}
        <div>
          <div className="flex items-center justify-between mb-3">
            <h4 className="font-semibold">我的{category.name}</h4>
            <Button 
              type="dashed" 
              size="small"
              icon={<PlusOutlined />}
              onClick={() => openAddTagModal(category.key)}
            >
              添加自定义标签
            </Button>
          </div>
          
          {categoryTags.length > 0 ? (
            <div className="space-y-3">
              {categoryTags.map((tag) => (
                <Card key={`${tag.category}-${tag.name}`} size="small" className="border-l-4" 
                      style={{ borderLeftColor: getCategoryColor(category.color) }}>
                  <div className="flex items-center justify-between">
                    <div className="flex-1">
                      <div className="flex items-center space-x-2">
                        <Tag color={category.color}>{tag.name}</Tag>
                        <span className="text-xs text-gray-500">
                          {tag.source === 'preset' ? '预置' : '自定义'}
                        </span>
                      </div>
                      <div className="mt-2">
                        <span className="text-sm text-gray-600 mr-2">权重:</span>
                        <Slider
                          className="flex-1"
                          style={{ width: '200px' }}
                          min={0}
                          max={2}
                          step={0.1}
                          value={tag.weight}
                          onChange={(value) => updateTagWeight(tag.category, tag.name, value)}
                        />
                        <span className="ml-2 text-sm font-medium">{tag.weight}</span>
                      </div>
                    </div>
                    <div className="flex space-x-1">
                      <Button
                        type="text"
                        size="small"
                        icon={<EditOutlined />}
                        onClick={() => openEditTagModal(tag)}
                      />
                      <Button
                        type="text"
                        size="small"
                        danger
                        icon={<DeleteOutlined />}
                        onClick={() => removeTag(tag.category, tag.name)}
                      />
                    </div>
                  </div>
                </Card>
              ))}
            </div>
          ) : (
            <div className="text-center py-8 text-gray-500">
              暂无{category.name}，请添加或选择预置标签
            </div>
          )}
        </div>

        {/* 预置标签 */}
        {availablePresets.length > 0 && (
          <div>
            <h4 className="font-semibold mb-3">预置{category.name}</h4>
            <div className="flex flex-wrap gap-2">
              {availablePresets.map(preset => (
                <Button
                  key={preset}
                  size="small"
                  type="dashed"
                  onClick={() => addPresetTag(category.key, preset)}
                >
                  <PlusOutlined /> {preset}
                </Button>
              ))}
            </div>
          </div>
        )}
      </div>
    );
  };

  const getCategoryColor = (color: string): string => {
    const colorMap: { [key: string]: string } = {
      'blue': '#1890ff',
      'green': '#52c41a',
      'orange': '#fa8c16',
      'cyan': '#13c2c2',
      'red': '#f5222d',
      'gold': '#fadb14',
      'purple': '#722ed1',
      'magenta': '#eb2f96',
      'lime': '#a0d911'
    };
    return colorMap[color] || '#1890ff';
  };

  if (loading) {
    return (
      <div className="flex justify-center items-center h-64">
        <Spin size="large" tip="正在加载标签数据..." />
      </div>
    );
  }

  return (
    <div style={{ padding: '24px', maxWidth: '1200px', margin: '0 auto' }}>
      <div className="flex items-center justify-between mb-6">
        <Title level={2}>🏷️ 标签管理测试页面</Title>
        <Space>
          <Button 
            icon={<ReloadOutlined />} 
            onClick={loadUserTags}
            loading={loading}
          >
            刷新
          </Button>
          <Button 
            type="primary" 
            icon={<SaveOutlined />}
            loading={saving}
            onClick={saveUserTags}
          >
            保存标签
          </Button>
        </Space>
      </div>

      <Alert
        className="mb-4"
        message="测试说明"
        description={`正在为测试用户 ${testUserId} 管理标签。您可以添加、编辑、删除标签，并调整权重。点击"保存标签"按钮将数据提交到后端API。`}
        type="info"
        showIcon
        icon={<InfoCircleOutlined />}
      />

      {/* 标签统计概览 */}
      <Card className="mb-6" title="📊 标签分布统计">
        <div className="grid grid-cols-3 md:grid-cols-9 gap-4">
          {getCategoryStats().map(stat => (
            <div key={stat.key} className="text-center">
              <Badge count={stat.count} color={getCategoryColor(stat.color)}>
                <div className="p-3 bg-gray-50 rounded hover:bg-gray-100 transition-colors cursor-pointer"
                     onClick={() => setActiveTab(stat.key)}>
                  <TagsOutlined 
                    style={{ 
                      fontSize: '20px', 
                      color: getCategoryColor(stat.color) 
                    }} 
                  />
                  <div className="mt-1 text-xs font-medium">{stat.name.replace(/[🏙️📍🗺️⚡🏢👥📋⭐📄]/g, '').trim()}</div>
                </div>
              </Badge>
            </div>
          ))}
        </div>
      </Card>

      {/* 标签分类管理 */}
      <Card>
        <Tabs 
          activeKey={activeTab}
          onChange={setActiveTab}
          type="card"
          items={tagCategories.map(category => ({
            key: category.key,
            label: (
              <Badge count={getUserTagsByCategory(category.key).length} size="small">
                <span>{category.name}</span>
              </Badge>
            ),
            children: (
              <div>
                <div className="mb-4 p-3 bg-gray-50 rounded">
                  <Tooltip title={category.description}>
                    <InfoCircleOutlined className="mr-2 text-gray-500" />
                  </Tooltip>
                  <span className="text-gray-600">{category.description}</span>
                </div>
                {renderCategoryTags(category)}
              </div>
            )
          }))}
        />
      </Card>

      {/* 添加/编辑标签弹窗 */}
      <Modal
        title={editingTag ? '编辑标签' : '添加标签'}
        open={isModalVisible}
        onOk={handleTagSubmit}
        onCancel={() => setIsModalVisible(false)}
      >
        <Form form={form} layout="vertical">
          <Form.Item
            name="category"
            label="标签分类"
            rules={[{ required: true, message: '请选择标签分类' }]}
          >
            <Select>
              {tagCategories.map(category => (
                <Select.Option key={category.key} value={category.key}>
                  {category.name}
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
            rules={[{ required: true, message: '请设置标签权重' }]}
          >
            <Slider min={0} max={2} step={0.1} marks={{ 0: '0', 1: '1', 2: '2' }} />
          </Form.Item>
        </Form>
      </Modal>
    </div>
  );
};

export default TestTagsPage; 