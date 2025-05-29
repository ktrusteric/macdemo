import React, { useState } from 'react';
import { Card, Row, Col, Button, Badge, Divider, List, Tag } from 'antd';
import { 
  CustomerServiceOutlined, 
  FileSearchOutlined, 
  TransactionOutlined,
  MessageOutlined,
  StarOutlined,
  UsergroupAddOutlined,
  RobotOutlined
} from '@ant-design/icons';
import { useSelector } from 'react-redux';
import type { RootState } from '../../store';

interface AIAssistant {
  id: string;
  token: string;
  name: string;
  description: string;
  icon: React.ReactNode;
  color: string;
  bgColor: string;
  features: string[];
  usage: number;
  rating: number;
  knowledgeBase: string;
}

const AIAssistants: React.FC = () => {
  const { user } = useSelector((state: RootState) => state.auth);
  const [loadingAssistant, setLoadingAssistant] = useState<string | null>(null);

  const assistants: AIAssistant[] = [
    {
      id: '9714d9bc-31ca-40b5-a720-4329f5fc4af7',
      token: 'e0dc8833077b48669a04ad4a70a7ebe2',
      name: '客服助手',
      description: '专业的客户服务支持，解答账户问题、功能咨询、技术支持等',
      icon: <CustomerServiceOutlined />,
      color: '#1890ff',
      bgColor: '#e6f7ff',
      features: ['账户问题', '功能咨询', '技术支持', '操作指导'],
      usage: 156,
      rating: 4.8,
      knowledgeBase: '客服支持知识库'
    },
    {
      id: '158ab70e-2996-4cce-9822-6f8195a7cfa5',
      token: '9bc6008decb94efeaee65dd076aab5e8',
      name: '资讯助手',
      description: '实时分析行业动态，提供市场洞察和政策解读',
      icon: <FileSearchOutlined />,
      color: '#52c41a',
      bgColor: '#f6ffed',
      features: ['市场快讯', '政策解读', '行业分析', '趋势预测'],
      usage: 248,
      rating: 4.9,
      knowledgeBase: '行业资讯知识库'
    },
    {
      id: '1e72acc1-43a8-4cda-8d54-f409c9c5d5ed',
      token: '18703d14357040c88f32ae5e4122c2d6',
      name: '交易助手',
      description: '智能交易分析，提供策略建议和风险评估',
      icon: <TransactionOutlined />,
      color: '#fa8c16',
      bgColor: '#fff7e6',
      features: ['策略建议', '风险评估', '交易分析', '市场机会'],
      usage: 189,
      rating: 4.7,
      knowledgeBase: '交易策略知识库'
    }
  ];

  const launchAssistant = async (assistant: AIAssistant) => {
    setLoadingAssistant(assistant.id);
    
    try {
      // 动态加载智能助手脚本
      await loadAssistantScript(assistant);
    } catch (error) {
      console.error('Failed to launch assistant:', error);
    } finally {
      setLoadingAssistant(null);
    }
  };

  const loadAssistantScript = (assistant: AIAssistant): Promise<void> => {
    return new Promise((resolve, reject) => {
      // 检查是否已经加载过脚本
      if (typeof window.WiseBotInit !== 'undefined') {
        initializeBot(assistant);
        resolve();
        return;
      }

      // 创建并加载脚本
      const script = document.createElement('script');
      script.src = 'https://ai.wiseocean.cn/bot/robot.js';
      script.onload = () => {
        requestAnimationFrame(() => {
          initializeBot(assistant);
          resolve();
        });
      };
      script.onerror = () => {
        reject(new Error('Failed to load AI assistant script'));
      };
      
      document.body.appendChild(script);
    });
  };

  const initializeBot = (assistant: AIAssistant) => {
    const botConfig = {
      id: assistant.id,
      token: assistant.token,
      size: 'normal',
      theme: 'dark',
      host: 'https://ai.wiseocean.cn',
      userContext: {
        userId: user?.id,
        username: user?.username,
        role: user?.role
      }
    };

    // 调用智能助手初始化
    if (window.WiseBotInit) {
      window.WiseBotInit(botConfig);
    }
  };

  return (
    <div>
      <div className="flex items-center justify-between mb-6">
        <h2 className="text-2xl font-bold">AI智能助手</h2>
        <div className="text-gray-500">
          选择合适的助手开始对话
        </div>
      </div>

      <div className="mb-6 p-4 bg-blue-50 rounded-lg">
        <div className="flex items-center mb-2">
          <RobotOutlined className="text-blue-500 mr-2" />
          <span className="font-semibold">智能助手介绍</span>
        </div>
        <p className="text-gray-600 text-sm">
          我们的AI助手采用先进的自然语言处理技术，每个助手都拥有专业的知识库，
          能够根据您的用户标签和历史对话提供个性化的专业建议。
        </p>
      </div>
      
      <Row gutter={[16, 16]}>
        {assistants.map((assistant) => (
          <Col span={8} key={assistant.id}>
            <Card
              hoverable
              className="h-full"
              style={{ borderColor: assistant.color }}
              cover={
                <div 
                  className="h-32 flex items-center justify-center text-6xl"
                  style={{ backgroundColor: assistant.bgColor, color: assistant.color }}
                >
                  {assistant.icon}
                </div>
              }
              actions={[
                <Button 
                  type="primary" 
                  style={{ backgroundColor: assistant.color, borderColor: assistant.color }}
                  loading={loadingAssistant === assistant.id}
                  onClick={() => launchAssistant(assistant)}
                  icon={<MessageOutlined />}
                >
                  开始对话
                </Button>
              ]}
            >
              <Card.Meta
                title={
                  <div className="flex items-center justify-between">
                    <span>{assistant.name}</span>
                    <Badge count={assistant.usage} style={{ backgroundColor: assistant.color }} />
                  </div>
                }
                description={
                  <div className="space-y-3">
                    <p className="text-gray-600">{assistant.description}</p>
                    
                    <Divider className="my-3" />
                    
                    <div>
                      <div className="font-semibold mb-2 text-gray-700">核心功能：</div>
                      <div className="flex flex-wrap gap-1">
                        {assistant.features.map((feature, index) => (
                          <Tag 
                            key={index} 
                            color={assistant.color}
                            className="mb-1"
                          >
                            {feature}
                          </Tag>
                        ))}
                      </div>
                    </div>
                    
                    <div className="flex items-center justify-between text-sm text-gray-500">
                      <span>
                        <StarOutlined style={{ color: '#faad14' }} /> {assistant.rating}
                      </span>
                      <span>
                        <UsergroupAddOutlined /> {assistant.usage}次对话
                      </span>
                    </div>
                    
                    <div className="text-xs text-gray-400">
                      知识库：{assistant.knowledgeBase}
                    </div>
                  </div>
                }
              />
            </Card>
          </Col>
        ))}
      </Row>

      <div className="mt-8">
        <Card title="使用提示" size="small">
          <List
            size="small"
            dataSource={[
              '点击"开始对话"按钮启动相应的智能助手',
              '助手会根据您的用户标签提供个性化建议',
              '支持多轮对话，助手具有上下文记忆能力',
              '不同助手拥有专业知识库，请选择合适的助手咨询'
            ]}
            renderItem={(item, index) => (
              <List.Item>
                <span className="text-blue-500 font-bold mr-2">{index + 1}.</span>
                {item}
              </List.Item>
            )}
          />
        </Card>
      </div>
    </div>
  );
};

// 扩展Window类型以支持WiseBotInit
declare global {
  interface Window {
    WiseBotInit: (config: any) => void;
  }
}

export default AIAssistants; 