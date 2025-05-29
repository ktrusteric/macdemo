import React from 'react';
import { Layout, Menu, theme } from 'antd';
import {
  DashboardOutlined,
  TagsOutlined,
  FileTextOutlined,
  RobotOutlined,
  SettingOutlined,
} from '@ant-design/icons';
import { useNavigate } from 'react-router-dom';
import { useAppSelector, useAppDispatch } from '../../store/hooks';
import { setActiveMenu, setSidebarOpen } from '../../store/slices/uiSlice';

const { Header, Sider, Content } = Layout;

interface MainLayoutProps {
  children: React.ReactNode;
}

const MainLayout: React.FC<MainLayoutProps> = ({ children }) => {
  const navigate = useNavigate();
  const dispatch = useAppDispatch();
  const { sidebarOpen, activeMenu } = useAppSelector((state) => state.ui);
  const {
    token: { colorBgContainer },
  } = theme.useToken();

  const menuItems = [
    {
      key: 'dashboard',
      icon: <DashboardOutlined />,
      label: '仪表盘',
      onClick: () => {
        dispatch(setActiveMenu('dashboard'));
        navigate('/');
      },
    },
    {
      key: 'tags',
      icon: <TagsOutlined />,
      label: '标签管理',
      onClick: () => {
        dispatch(setActiveMenu('tags'));
        navigate('/tags');
      },
    },
    {
      key: 'content',
      icon: <FileTextOutlined />,
      label: '信息资讯',
      onClick: () => {
        dispatch(setActiveMenu('content'));
        navigate('/content');
      },
    },
    {
      key: 'ai-assistants',
      icon: <RobotOutlined />,
      label: 'A I 助手',
      onClick: () => {
        dispatch(setActiveMenu('ai-assistants'));
        navigate('/ai-assistants');
      },
    },
    {
      key: 'settings',
      icon: <SettingOutlined />,
      label: '个性设置',
      onClick: () => {
        dispatch(setActiveMenu('settings'));
        navigate('/settings');
      },
    },
  ];

  return (
    <Layout style={{ minHeight: '100vh' }}>
      <Sider
        collapsible
        collapsed={!sidebarOpen}
        onCollapse={(collapsed) => dispatch(setSidebarOpen(!collapsed))}
        theme="dark"
      >
        <div className="flex items-center justify-center h-16 text-white text-lg font-bold">
          能源信息系统
        </div>
        <Menu
          theme="dark"
          mode="inline"
          selectedKeys={[activeMenu]}
          items={menuItems}
        />
      </Sider>
      <Layout>
        <Header style={{ padding: 0, background: colorBgContainer }}>
          <div className="px-6 py-4">
            <h1 className="text-xl font-semibold">能源信息服务平台</h1>
          </div>
        </Header>
        <Content
          style={{
            margin: '24px 16px',
            padding: 24,
            minHeight: 280,
            background: colorBgContainer,
          }}
        >
          {children}
        </Content>
      </Layout>
    </Layout>
  );
};

export default MainLayout; 