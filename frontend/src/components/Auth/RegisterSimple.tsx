import React, { useState } from 'react';
import { Form, Input, Button, Card, Select, Alert } from 'antd';
import { UserOutlined, LockOutlined, MailOutlined } from '@ant-design/icons';
import { Link } from 'react-router-dom';

const RegisterSimple: React.FC = () => {
  const [form] = Form.useForm();
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);
  const [success, setSuccess] = useState(false);

  // 简化的城市列表（用于测试）
  const cities = [
    '上海', '北京', '深圳', '广州', '杭州', '成都', 
    '长沙', '武汉', '南京', '苏州', '天津', '重庆'
  ];
  
  // 完整的能源类型列表
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

  const onFinish = async (values: any) => {
    setLoading(true);
    setError(null);
    
    try {
      console.log('提交的表单数据:', values);
      
      // 模拟API调用延迟
      await new Promise(resolve => setTimeout(resolve, 1000));
      
      // 显示成功消息
      setSuccess(true);
      setError(null);
      
      // 重置表单
      form.resetFields();
      
    } catch (error) {
      console.error('注册错误:', error);
      setError('注册失败，请重试');
    } finally {
      setLoading(false);
    }
  };

  return (
    <div className="flex justify-center items-center min-h-screen bg-gray-50 p-4">
      <Card 
        title="📝 注册新账户 (测试版)" 
        className="w-full max-w-md shadow-lg"
        extra={<Link to="/login">已有账户？登录</Link>}
      >
        {error && <Alert message={error} type="error" showIcon className="mb-4" />}
        {success && <Alert message="🎉 注册成功！表单数据已记录到控制台" type="success" showIcon className="mb-4" />}
        {loading && <Alert message="⏳ 正在处理注册..." type="info" showIcon className="mb-4" />}
        
        <Form
          form={form}
          name="register"
          layout="vertical"
          onFinish={onFinish}
          initialValues={{ 
            energy_types: ['天然气'],
            register_city: '上海'
          }}
        >
          <Form.Item
            name="email"
            label="📧 邮箱"
            rules={[
              { required: true, message: '请输入邮箱地址' },
              { type: 'email', message: '请输入有效的邮箱地址' }
            ]}
          >
            <Input prefix={<MailOutlined />} placeholder="邮箱地址" />
          </Form.Item>
          
          <Form.Item
            name="username"
            label="👤 用户名"
            rules={[{ required: true, message: '请输入用户名' }]}
          >
            <Input prefix={<UserOutlined />} placeholder="用户名" />
          </Form.Item>
          
          <Form.Item
            name="password"
            label="🔒 密码"
            rules={[
              { required: true, message: '请输入密码' },
              { min: 6, message: '密码长度至少为6位' }
            ]}
          >
            <Input.Password prefix={<LockOutlined />} placeholder="密码" />
          </Form.Item>
          
          <Form.Item
            name="register_city"
            label="🏙️ 注册城市"
            rules={[{ required: true, message: '请选择您的注册城市' }]}
          >
            <Select placeholder="选择注册城市">
              {cities.map(city => (
                <Select.Option key={city} value={city}>
                  {city}
                </Select.Option>
              ))}
            </Select>
          </Form.Item>
          
          <Form.Item
            name="energy_types"
            label="⚡ 关注能源品种"
            tooltip="选择您感兴趣的能源类型"
          >
            <Select 
              mode="multiple" 
              placeholder="选择关注能源品种"
              maxTagCount={3}
            >
              {energyTypes.map(energyType => (
                <Select.Option key={energyType.value} value={energyType.value}>
                  {energyType.label}
                </Select.Option>
              ))}
            </Select>
          </Form.Item>
          
          <Form.Item>
            <Button 
              type="primary" 
              htmlType="submit" 
              loading={loading}
              className="w-full"
            >
              🚀 注册
            </Button>
          </Form.Item>
          
          <div className="text-xs text-gray-500 text-center">
            📊 支持 {cities.length} 个城市 | ⚡ {energyTypes.length} 种能源类型
          </div>
        </Form>
      </Card>
    </div>
  );
};

export default RegisterSimple; 