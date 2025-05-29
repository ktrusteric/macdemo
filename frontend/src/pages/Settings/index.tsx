import React, { useState, useEffect } from 'react';
import { Card, Form, Switch, Button, Select, Space, Divider, message, Spin } from 'antd';
import { LogoutOutlined, UserSwitchOutlined } from '@ant-design/icons';
import { useDispatch, useSelector } from 'react-redux';
import { useNavigate } from 'react-router-dom';
import { logout } from '../../store/slices/authSlice';
import { setCurrentUserId } from '../../store/slices/userSlice';
import type { RootState } from '../../store';

const { Option } = Select;

interface DemoUser {
  id: string;
  demo_user_id: string;
  username: string;
  email: string;
  description: string;
  register_city: string;
}

// 默认演示用户数据（与后端energyTypes保持一致）
const DEFAULT_DEMO_USERS: DemoUser[] = [
  { 
    id: 'user001', 
    demo_user_id: 'user001',
    username: '张先生', 
    email: 'zhang@newenergy.com',
    description: '新能源投资者 - 关注电力、生物柴油、天然气',
    register_city: '上海'
  },
  { 
    id: 'user002', 
    demo_user_id: 'user002',
    username: '李女士', 
    email: 'li@traditional.com',
    description: '传统能源企业主 - 原油、天然气、LNG、煤炭专家',
    register_city: '北京'
  },
  { 
    id: 'user003', 
    demo_user_id: 'user003',
    username: '王先生', 
    email: 'wang@carbon.com',
    description: '节能减排顾问 - 专注电力、生物柴油、天然气',
    register_city: '深圳'
  },
  { 
    id: 'user004', 
    demo_user_id: 'user004',
    username: '陈女士', 
    email: 'chen@power.com',
    description: '电力系统工程师 - 电力、煤炭、天然气技术专家',
    register_city: '广州'
  },
  { 
    id: 'user005', 
    demo_user_id: 'user005',
    username: '刘先生', 
    email: 'liu@policy.com',
    description: '能源政策研究员 - 原油、天然气、电力、煤炭分析',
    register_city: '成都'
  }
];

const Settings: React.FC = () => {
  const dispatch = useDispatch();
  const navigate = useNavigate();
  const { user } = useSelector((state: RootState) => state.auth);
  const { currentUserId } = useSelector((state: RootState) => state.user);
  
  const [demoUsers, setDemoUsers] = useState<DemoUser[]>([]);
  const [loading, setLoading] = useState(false);

  // 获取演示用户列表
  const fetchDemoUsers = async () => {
    try {
      setLoading(true);
      const response = await fetch('/api/v1/users/demo-users');
      if (response.ok) {
        const data = await response.json();
        console.log('获取到的演示用户数据:', data);
        setDemoUsers(data.users || []);
      } else {
        console.error('API响应失败:', response.status, response.statusText);
        // 如果API失败，使用默认数据
        setDemoUsers(DEFAULT_DEMO_USERS);
      }
    } catch (error) {
      console.error('获取演示用户列表时出错:', error);
      message.error('获取演示用户列表失败，使用默认数据');
      // 使用默认数据作为后备
      setDemoUsers(DEFAULT_DEMO_USERS);
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    fetchDemoUsers();
  }, []);

  const handleLogout = () => {
    dispatch(logout());
    message.success('已成功登出');
    navigate('/login');
  };

  const handleUserSwitch = async (userId: string) => {
    try {
      // 更新Redux store中的当前用户ID
      dispatch(setCurrentUserId(userId));
      
      const selectedUser = demoUsers.find(u => u.demo_user_id === userId);
      if (selectedUser) {
        message.success(`已切换到: ${selectedUser.username}`);
        
        // 可以在这里调用API预加载用户标签数据
        try {
          const tagsResponse = await fetch(`/api/v1/users/demo-users/${userId}/tags`);
          if (tagsResponse.ok) {
            const tagsData = await tagsResponse.json();
            console.log('用户标签已预加载:', tagsData);
          }
        } catch (error) {
          console.log('预加载标签数据失败，将在标签页面重新加载');
        }
      }
    } catch (error) {
      console.error('用户切换失败:', error);
      message.error('用户切换失败');
    }
  };

  const getCurrentUserInfo = () => {
    if (user) {
      return {
        username: user.username,
        email: user.email,
        userId: currentUserId
      };
    }
    
    // 如果没有认证用户，显示当前选中的演示用户信息
    const currentDemo = demoUsers.find(u => u.demo_user_id === currentUserId);
    if (currentDemo) {
      return {
        username: currentDemo.username,
        email: currentDemo.email,
        userId: currentUserId
      };
    }
    
    return {
      username: '未知用户',
      email: '未知邮箱',
      userId: currentUserId || 'user001'
    };
  };

  const userInfo = getCurrentUserInfo();

  return (
    <div>
      <h2 className="text-2xl font-bold mb-6">设置</h2>
      
      {/* 个性设置区域 */}
      <Card title="个性设置" className="mb-6">
        <div className="space-y-4">
          {/* 当前用户信息 */}
          <div>
            <h4 className="text-lg font-medium mb-2">当前用户</h4>
            <div className="p-3 bg-gray-50 rounded-md">
              <p><strong>用户名:</strong> {userInfo.username}</p>
              <p><strong>邮箱:</strong> {userInfo.email}</p>
              <p><strong>用户ID:</strong> {userInfo.userId}</p>
            </div>
          </div>

          <Divider />

          {/* 用户切换功能 */}
          <div>
            <h4 className="text-lg font-medium mb-3 flex items-center">
              <UserSwitchOutlined className="mr-2" />
              演示用户切换
            </h4>
            <p className="text-gray-600 mb-3">切换不同用户以查看不同的个性化标签:</p>
            <Spin spinning={loading}>
              <Select
                value={currentUserId}
                onChange={handleUserSwitch}
                style={{ width: '100%' }}
                placeholder="选择演示用户"
              >
                {demoUsers.map(user => (
                  <Option key={user.demo_user_id} value={user.demo_user_id}>
                    <div>
                      <div className="font-medium">{user.username} ({user.register_city})</div>
                      <div className="text-sm text-gray-500">{user.description}</div>
                    </div>
                  </Option>
                ))}
              </Select>
            </Spin>
          </div>

          <Divider />

          {/* 登出功能 */}
          <div>
            <h4 className="text-lg font-medium mb-3 flex items-center">
              <LogoutOutlined className="mr-2" />
              账户管理
            </h4>
            <Space>
              <Button 
                type="primary" 
                danger 
                icon={<LogoutOutlined />}
                onClick={handleLogout}
              >
                登出账户
              </Button>
              <span className="text-gray-500">退出当前账户，返回登录页面</span>
            </Space>
          </div>
        </div>
      </Card>
      
      {/* 系统设置区域 */}
      <Card title="系统设置">
        <Form
          labelCol={{ span: 6 }}
          wrapperCol={{ span: 18 }}
          style={{ maxWidth: 600 }}
        >
          <Form.Item label="深色模式" name="darkMode">
            <Switch />
          </Form.Item>
          
          <Form.Item label="推送通知" name="notifications">
            <Switch defaultChecked />
          </Form.Item>
          
          <Form.Item label="自动刷新" name="autoRefresh">
            <Switch defaultChecked />
          </Form.Item>
          
          <Form.Item wrapperCol={{ offset: 6, span: 18 }}>
            <Button type="primary">保存设置</Button>
          </Form.Item>
        </Form>
      </Card>
    </div>
  );
};

export default Settings; 