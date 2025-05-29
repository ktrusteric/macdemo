// src/components/Auth/Register.tsx
import React, { useState, useEffect } from 'react';
import { Form, Input, Button, Card, Select, Alert, Spin, Tooltip, Badge, Tag, Divider } from 'antd';
import { UserOutlined, LockOutlined, MailOutlined, EnvironmentOutlined, CheckCircleOutlined, InfoCircleOutlined, TagsOutlined } from '@ant-design/icons';
import { Link, useNavigate } from 'react-router-dom';

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

// 能源类型列表（包含您要求的完整能源类型）
const energyTypes = [
  { value: '原油', label: '原油' },
  { value: '管道天然气(PNG)', label: '管道天然气(PNG)' },
  { value: '天然气', label: '天然气' },
  { value: '液化天然气(LNG)', label: '液化天然气(LNG)' },
  { value: '液化石油气(LPG)', label: '液化石油气(LPG)' },
  { value: '汽油', label: '汽油' },
  { value: '柴油', label: '柴油' },
  { value: '沥青', label: '沥青' },
  { value: '石油焦', label: '石油焦' },
  { value: '生物柴油', label: '生物柴油' },
  { value: '电力', label: '电力' },
  { value: '煤炭', label: '煤炭' },
];

const Register: React.FC = () => {
  const [form] = Form.useForm();
  const navigate = useNavigate();
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);
  const [cities, setCities] = useState<City[]>([]);
  const [citiesLoading, setCitiesLoading] = useState(false);
  const [selectedCity, setSelectedCity] = useState<string>('');
  const [regionInfo, setRegionInfo] = useState<{ province: string; region: string } | null>(null);

  // 加载城市列表
  useEffect(() => {
    loadCities();
  }, []);

  const loadCities = async () => {
    setCitiesLoading(true);
    try {
      // 使用新的cities-details API获取完整的城市信息
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
      } else {
        throw new Error(`HTTP ${response.status}`);
      }
    } catch (error) {
      console.error('加载城市列表失败:', error);
      setError('加载城市列表失败，请刷新页面重试');
      
      // 使用本地城市列表作为备选（从之前的硬编码映射）
      const fallbackCities = [
        { value: '上海', label: '上海', province: '上海市', region: '华东地区' },
        { value: '北京', label: '北京', province: '北京市', region: '华北地区' },
        { value: '深圳', label: '深圳', province: '广东省', region: '华南地区' },
        { value: '广州', label: '广州', province: '广东省', region: '华南地区' },
        { value: '杭州', label: '杭州', province: '浙江省', region: '华东地区' },
        { value: '成都', label: '成都', province: '四川省', region: '西南地区' },
        { value: '长沙', label: '长沙', province: '湖南省', region: '华中地区' },
        { value: '武汉', label: '武汉', province: '湖北省', region: '华中地区' },
        { value: '南京', label: '南京', province: '江苏省', region: '华东地区' },
        { value: '苏州', label: '苏州', province: '江苏省', region: '华东地区' },
        { value: '天津', label: '天津', province: '天津市', region: '华北地区' },
        { value: '重庆', label: '重庆', province: '重庆市', region: '西南地区' },
      ];
      setCities(fallbackCities);
    } finally {
      setCitiesLoading(false);
    }
  };

  // 处理城市选择
  const handleCityChange = (cityValue: string) => {
    setSelectedCity(cityValue);
    const city = cities.find(c => c.value === cityValue);
    if (city) {
      setRegionInfo({
        province: city.province || '未知省份',
        region: city.region || '未知地区'
      });
    }
  };

  const onFinish = async (values: any) => {
    setLoading(true);
    setError(null);
    
    try {
      const response = await fetch('/api/v1/users/register', {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify(values),
      });
      
      if (response.ok) {
        const result = await response.json();
        console.log('注册成功:', result);
        // 注册成功后跳转到登录页面
        navigate('/login', { 
          state: { message: '注册成功！请登录您的账户。' }
        });
      } else {
        const errorData = await response.json();
        throw new Error(errorData.detail || '注册失败');
      }
    } catch (error) {
      console.error('注册错误:', error);
      setError(error instanceof Error ? error.message : '注册失败，请重试');
    } finally {
      setLoading(false);
    }
  };

  return (
    <div className="min-h-screen bg-gradient-to-br from-blue-50 to-green-50 flex items-center justify-center p-4">
      <Card 
        title={
          <div className="text-center">
            <h2 className="text-xl font-bold text-blue-600 mb-2">
              🏭 能源交易系统注册
            </h2>
            <div className="text-sm text-gray-500">
              支持 <Badge count={cities.length} color="blue" /> 个城市 | 
              <Badge count={energyTypes.length} color="green" /> 种能源类型
            </div>
          </div>
        }
        className="w-full max-w-md shadow-lg border-0"
        extra={<Link to="/login" className="text-blue-500">已有账户？登录</Link>}
      >
        {error && (
          <Alert 
            message="注册失败" 
            description={error} 
            type="error" 
            showIcon 
            className="mb-4" 
          />
        )}
        
        <Form
          form={form}
          name="register"
          layout="vertical"
          onFinish={onFinish}
          initialValues={{ 
            energy_types: ['天然气'],
            register_city: ''
          }}
        >
          <Form.Item
            name="email"
            label="📧 邮箱地址"
            rules={[
              { required: true, message: '请输入邮箱地址' },
              { type: 'email', message: '请输入有效的邮箱地址' }
            ]}
          >
            <Input 
              prefix={<MailOutlined />} 
              placeholder="your@email.com" 
              size="large"
            />
          </Form.Item>
          
          <Form.Item
            name="username"
            label="👤 用户名"
            rules={[
              { required: true, message: '请输入用户名' },
              { min: 3, message: '用户名至少3个字符' }
            ]}
          >
            <Input 
              prefix={<UserOutlined />} 
              placeholder="请输入用户名" 
              size="large"
            />
          </Form.Item>
          
          <Form.Item
            name="password"
            label="🔒 密码"
            rules={[
              { required: true, message: '请输入密码' },
              { min: 6, message: '密码长度至少为6位' }
            ]}
          >
            <Input.Password 
              prefix={<LockOutlined />} 
              placeholder="请输入密码" 
              size="large"
            />
          </Form.Item>
          
          <Form.Item
            name="register_city"
            label={
              <div className="flex items-center">
                <EnvironmentOutlined className="mr-1" />
                <span>🏙️ 注册城市</span>
                {citiesLoading && <Spin size="small" className="ml-2" />}
              </div>
            }
            rules={[{ required: true, message: '请选择您的注册城市' }]}
          >
            <Select 
              placeholder={citiesLoading ? "正在加载城市列表..." : "选择您的城市"}
              loading={citiesLoading}
              size="large"
              showSearch
              filterOption={(input, option) => {
                const label = option?.children || option?.label || '';
                return String(label).toLowerCase().includes(input.toLowerCase());
              }}
              onChange={handleCityChange}
            >
              {cities.map(city => (
                <Select.Option key={city.value} value={city.value} label={city.label}>
                  <div className="flex justify-between items-center">
                    <span>🏙️ {city.label}</span>
                    <div className="text-xs text-gray-500">
                      {city.province} · {city.region}
                    </div>
                  </div>
                </Select.Option>
              ))}
            </Select>
          </Form.Item>

          {/* 显示选中城市的省份和区域信息以及标签预览 */}
          {regionInfo && selectedCity && (
            <div className="mb-4 space-y-4">
              {/* 地区信息确认 */}
              <div className="p-4 bg-blue-50 rounded-lg border border-blue-200">
                <div className="flex items-center text-sm mb-3">
                  <CheckCircleOutlined className="text-green-500 mr-2" />
                  <span className="font-medium">地区信息确认:</span>
                </div>
                <div className="space-y-2">
                  <div className="flex items-center">
                    <Tag color="blue">🏙️ 城市</Tag>
                    <span className="font-medium">{selectedCity}</span>
                  </div>
                  <div className="flex items-center">
                    <Tag color="green">📍 省份</Tag>
                    <span className="font-medium">{regionInfo.province}</span>
                  </div>
                  <div className="flex items-center">
                    <Tag color="orange">🗺️ 区域</Tag>
                    <span className="font-medium">{regionInfo.region}</span>
                  </div>
                </div>
              </div>

              {/* 标签生成预览 */}
              <div className="p-4 bg-gradient-to-r from-green-50 to-blue-50 rounded-lg border border-green-200">
                <div className="flex items-center text-sm mb-3">
                  <TagsOutlined className="text-blue-500 mr-2" />
                  <span className="font-medium text-blue-700">将自动生成的地域标签:</span>
                  <Tooltip title="系统将根据您的注册城市自动生成三层地域标签，权重越高的标签在内容推荐中影响越大">
                    <InfoCircleOutlined className="text-gray-400 ml-2" />
                  </Tooltip>
                </div>
                <div className="space-y-3">
                  <div className="flex items-center justify-between bg-white rounded-lg p-3 border border-blue-100">
                    <div className="flex items-center">
                      <Tag color="processing">🏙️ 城市标签</Tag>
                      <span className="font-medium">{selectedCity}</span>
                    </div>
                    <div className="flex items-center">
                      <span className="text-xs text-gray-500 mr-2">权重</span>
                      <Badge count="2.5" style={{ backgroundColor: '#52c41a' }} />
                      <Tooltip title="最高权重，您明确选择的城市">
                        <InfoCircleOutlined className="text-gray-400 ml-1" />
                      </Tooltip>
                    </div>
                  </div>
                  
                  <div className="flex items-center justify-between bg-white rounded-lg p-3 border border-green-100">
                    <div className="flex items-center">
                      <Tag color="success">📍 省份标签</Tag>
                      <span className="font-medium">{regionInfo.province}</span>
                    </div>
                    <div className="flex items-center">
                      <span className="text-xs text-gray-500 mr-2">权重</span>
                      <Badge count="2.0" style={{ backgroundColor: '#1890ff' }} />
                      <Tooltip title="高权重，根据城市自动生成">
                        <InfoCircleOutlined className="text-gray-400 ml-1" />
                      </Tooltip>
                    </div>
                  </div>
                  
                  <div className="flex items-center justify-between bg-white rounded-lg p-3 border border-orange-100">
                    <div className="flex items-center">
                      <Tag color="warning">🗺️ 区域标签</Tag>
                      <span className="font-medium">{regionInfo.region}</span>
                    </div>
                    <div className="flex items-center">
                      <span className="text-xs text-gray-500 mr-2">权重</span>
                      <Badge count="1.5" style={{ backgroundColor: '#fa8c16' }} />
                      <Tooltip title="中权重，更大范围的区域标签">
                        <InfoCircleOutlined className="text-gray-400 ml-1" />
                      </Tooltip>
                    </div>
                  </div>
                </div>
                
                <Divider style={{ margin: '12px 0' }} />
                
                <div className="text-xs text-gray-600 bg-yellow-50 p-3 rounded border-l-4 border-yellow-400">
                  <strong>💡 标签说明:</strong>
                  <ul className="mt-1 space-y-1">
                    <li>• <strong>城市标签</strong>: 优先推荐您所在城市的相关内容</li>
                    <li>• <strong>省份标签</strong>: 推荐省内其他城市的相关政策和信息</li>
                    <li>• <strong>区域标签</strong>: 推荐整个地理区域的宏观政策和发展动态</li>
                    <li>• 注册成功后，您可以在"标签管理"页面查看和调整这些标签</li>
                  </ul>
                </div>
              </div>
            </div>
          )}
          
          <Form.Item
            name="energy_types"
            label="⚡ 关注能源品种"
            tooltip="选择您感兴趣的能源类型，系统将为您推荐相关内容"
            rules={[{ required: true, message: '请至少选择一种能源类型' }]}
          >
            <Select 
              mode="multiple" 
              placeholder="选择关注的能源品种"
              maxTagCount={3}
              size="large"
              showSearch
              filterOption={(input, option) => {
                const label = option?.children || option?.label || '';
                return String(label).toLowerCase().includes(input.toLowerCase());
              }}
            >
              {energyTypes.map(energyType => (
                <Select.Option key={energyType.value} value={energyType.value}>
                  ⚡ {energyType.label}
                </Select.Option>
              ))}
            </Select>
          </Form.Item>
          
          <Form.Item className="mb-0">
            <Button 
              type="primary" 
              htmlType="submit" 
              loading={loading}
              size="large"
              className="w-full bg-blue-600 hover:bg-blue-700"
            >
              {loading ? '🔄 注册中...' : '🚀 立即注册'}
            </Button>
          </Form.Item>
          
          <div className="text-center mt-4 text-xs text-gray-500">
            📋 注册即表示您同意我们的用户协议和隐私政策
          </div>
        </Form>
      </Card>
    </div>
  );
};

export default Register;