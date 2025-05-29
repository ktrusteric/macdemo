import React, { useState, useEffect } from 'react';
import { Card, Row, Col, Statistic, List, Tag, Spin, Alert, Button, Select, Switch } from 'antd';
import { 
  FileTextOutlined, 
  TagsOutlined, 
  RobotOutlined, 
  RiseOutlined,
  DollarOutlined,
  UserOutlined,
  FireOutlined,
  ClockCircleOutlined,
  ExperimentOutlined
} from '@ant-design/icons';
import { useSelector, useDispatch } from 'react-redux';
import { contentService } from '../../services/contentService';
import { userService } from '../../services/userService';
import { recommendationService } from '../../services/recommendationService';
import { 
  setCurrentUserId, 
  fetchUserTags, 
  syncUserIdFromAuth, 
  setDemoUser, 
  enableDemoMode,
  disableDemoMode 
} from '../../store/slices/userSlice';
import type { RootState } from '../../store';

interface DashboardStats {
  todayContent: number;
  userTags: number;
  aiChats: number;
  weeklyGrowth: number;
}

interface PriceData {
  name: string;
  price: number;
  change: number;
  changePercent: number;
}

interface RecommendedContent {
  id: string;
  title: string;
  type: string;
  publishTime: string;
  tags: string[];
}

interface UserTagInfo {
  category: string;
  name: string;
  weight: number;
}

const Dashboard: React.FC = () => {
  const dispatch = useDispatch();
  const { user, isAuthenticated } = useSelector((state: RootState) => state.auth);
  const { currentUserId, isDemoMode } = useSelector((state: RootState) => state.user);
  
  const [loading, setLoading] = useState(true);
  const [stats, setStats] = useState<DashboardStats>({
    todayContent: 0,
    userTags: 0,
    aiChats: 0,
    weeklyGrowth: 0
  });
  const [priceData, setPriceData] = useState<PriceData[]>([]);
  const [recommendations, setRecommendations] = useState<RecommendedContent[]>([]);
  const [userTags, setUserTags] = useState<UserTagInfo[]>([]);
  const [error, setError] = useState<string | null>(null);

  // 演示用户选项
  const demoUsers = [
    { value: 'user001', label: '张先生 (上海) - 新能源投资者' },
    { value: 'user002', label: '李女士 (北京) - 传统能源企业主' },
    { value: 'user003', label: '王先生 (深圳) - 节能减排顾问' },
    { value: 'user004', label: '陈女士 (广州) - 电力系统工程师' },
    { value: 'user005', label: '刘先生 (成都) - 能源政策研究员' },
  ];

  useEffect(() => {
    initializeUser();
  }, [isAuthenticated, user, dispatch]);

  // 关键修复：当currentUserId变化时，重新加载所有数据
  useEffect(() => {
    if (currentUserId) {
      console.log('🔄 用户ID变化，重新加载数据:', currentUserId, '演示模式:', isDemoMode);
      loadDashboardData();
    }
  }, [currentUserId, isDemoMode]); // 添加isDemoMode依赖

  const initializeUser = () => {
    if (isAuthenticated && user?.id) {
      // 认证用户：同步用户ID
      dispatch(syncUserIdFromAuth(user.id));
    } else {
      // 未认证：启用演示模式，默认用户user001
      dispatch(enableDemoMode());
    }
  };

  const handleDemoModeChange = (enabled: boolean) => {
    if (enabled) {
      dispatch(enableDemoMode());
    } else {
      dispatch(disableDemoMode());
    }
  };

  const handleDemoUserChange = (demoUserId: string) => {
    console.log('🎭 切换演示用户:', demoUserId);
    dispatch(setDemoUser(demoUserId));
    // 强制清空当前数据，显示加载状态
    setUserTags([]);
    setRecommendations([]);
    setLoading(true);
  };

  const loadDashboardData = async () => {
    if (!currentUserId) {
      console.warn('没有可用的用户ID');
      setLoading(false);
      return;
    }
    
    setLoading(true);
    setError(null);
    
    try {
      console.log('📊 Dashboard加载数据，用户ID:', currentUserId, '演示模式:', isDemoMode);
      
      // 清空之前的数据
      setUserTags([]);
      setRecommendations([]);
      
      const [todayContent, userTagsData] = await Promise.allSettled([
        loadContentStats(),
        loadUserTags(currentUserId)
      ]);

      const contentCount = todayContent.status === 'fulfilled' 
        ? todayContent.value 
        : Math.floor(Math.random() * 50) + 20;

      const tagsCount = userTagsData.status === 'fulfilled' && userTagsData.value
        ? userTagsData.value.length
        : 0;

      setStats({
        todayContent: contentCount,
        userTags: tagsCount,
        aiChats: Math.floor(Math.random() * 20) + 10,
        weeklyGrowth: +(Math.random() * 10 + 5).toFixed(1)
      });

      // 加载推荐内容（在标签加载完成后）
      await loadRecommendations(currentUserId);
      loadMockPriceData();

    } catch (error: any) {
      console.error('Dashboard loading error:', error);
      
      setError('数据加载失败，请检查网络连接或稍后重试');
      
      setStats({
        todayContent: 25,
        userTags: 0,
        aiChats: 15,
        weeklyGrowth: 8.5
      });
      
      setUserTags([]);
      setRecommendations([]);
      loadMockPriceData();
    } finally {
      setLoading(false);
    }
  };

  const loadContentStats = async () => {
    try {
      const response = await contentService.getContentList();
      const today = new Date().toISOString().split('T')[0];
      const todayContent = response.items.filter((item: any) => 
        item.publish_time?.startsWith(today)
      ).length;
      return todayContent || Math.floor(Math.random() * 50) + 20;
    } catch (error) {
      return Math.floor(Math.random() * 50) + 20;
    }
  };

  const loadUserTags = async (userId: string) => {
    if (!userId) {
      console.warn('用户ID为空，无法加载标签');
      return [];
    }

    try {
      console.log('🏷️ Dashboard开始加载用户标签，用户ID:', userId, '演示模式:', isDemoMode);
      
      // 根据是否为演示模式使用不同的API
      let userTagsResponse;
      if (isDemoMode && userId.startsWith('user')) {
        console.log('📱 使用演示用户API加载标签');
        userTagsResponse = await userService.getUserTags(userId);
      } else {
        console.log('👤 使用普通用户API加载标签');
        userTagsResponse = await userService.getUserTags(userId);
      }
      
      console.log('📥 用户标签响应:', userTagsResponse);
      
      if (userTagsResponse && userTagsResponse.tags) {
        const tagList = userTagsResponse.tags.map((tag: any) => ({
          category: tag.category,
          name: tag.name,
          weight: tag.weight
        }));
        console.log('✅ 标签解析成功:', tagList);
        setUserTags(tagList);
        return tagList;
      } else {
        console.log('⚠️ 用户无标签数据');
        setUserTags([]);
        return [];
      }
    } catch (error) {
      console.error('❌ 用户标签加载失败:', error);
      setUserTags([]);
      return [];
    }
  };

  const loadRecommendations = async (userId: string) => {
    try {
      console.log('🎯 Dashboard开始加载推荐内容，用户ID:', userId, '演示模式:', isDemoMode);
      
      // 确保使用正确的用户ID格式
      const effectiveUserId = isDemoMode && userId.startsWith('user') ? userId : userId;
      
      const recs = await recommendationService.getRecommendations(effectiveUserId);
      console.log('📊 Dashboard获取到推荐数据:', recs);
      
      if (recs && recs.length > 0) {
        const formattedRecs = recs.slice(0, 6).map((item: any) => ({
          id: item.id,
          title: item.title,
          type: item.type,
          publishTime: item.publish_time || item.publishTime || new Date().toISOString(),
          tags: Array.isArray(item.tags) ? item.tags.slice(0, 3) : []
        }));
        console.log('✅ Dashboard格式化推荐内容:', formattedRecs);
        setRecommendations(formattedRecs);
      } else {
        console.log('⚠️ 推荐数据为空，为用户', effectiveUserId);
        setRecommendations([]);
      }
    } catch (error) {
      console.error('❌ 推荐内容加载失败:', error);
      setRecommendations([]);
    }
  };

  const loadMockPriceData = () => {
    const mockPrices: PriceData[] = [
      {
        name: '天然气期货',
        price: 4.25,
        change: 0.15,
        changePercent: 3.66
      },
      {
        name: 'LNG现货价格',
        price: 850,
        change: -25,
        changePercent: -2.86
      },
      {
        name: '原油WTI',
        price: 78.32,
        change: 1.24,
        changePercent: 1.61
      },
      {
        name: '煤炭指数',
        price: 156.8,
        change: -2.4,
        changePercent: -1.51
      }
    ];
    setPriceData(mockPrices);
  };

  const getTagColor = (category: string) => {
    const colorMap: { [key: string]: string } = {
      'region': 'blue',
      'energy_type': 'green', 
      'business_field': 'orange',
      'basic_info': 'purple',
      'beneficiary': 'cyan',
      'policy_measure': 'red',
      'importance': 'gold',
      'city': 'blue',
      'province': 'geekblue'
    };
    return colorMap[category] || 'default';
  };

  const getCategoryName = (category: string) => {
    const categoryNames: { [key: string]: string } = {
      'region': '地区',
      'energy_type': '能源类型',
      'business_field': '业务领域',
      'basic_info': '基本信息',
      'beneficiary': '受益方',
      'policy_measure': '政策措施',
      'importance': '重要性',
      'city': '城市',
      'province': '省份'
    };
    return categoryNames[category] || '未知类别';
  };

  // 获取当前显示用户信息
  const getCurrentUserInfo = () => {
    if (isDemoMode && currentUserId) {
      const demoUser = demoUsers.find(u => u.value === currentUserId);
      return demoUser ? demoUser.label.split(' - ')[0] : currentUserId;
    }
    
    return user?.username || '用户';
  };

  if (loading) {
    return (
      <div className="flex justify-center items-center h-64">
        <Spin size="large" spinning={true}>
          <div className="text-center py-8">
            <div className="text-gray-500">正在加载数据...</div>
            {currentUserId && (
              <div className="text-sm text-gray-400 mt-2">
                当前用户: {getCurrentUserInfo()}
              </div>
            )}
          </div>
        </Spin>
      </div>
    );
  }

  return (
    <div>
      <div className="flex items-center justify-between mb-6">
        <h2 className="text-2xl font-bold">仪表盘</h2>
        <div className="flex items-center gap-4">
          {/* 演示模式控制 */}
          <div className="flex items-center gap-2">
            <ExperimentOutlined />
            <span className="text-sm text-gray-600">演示模式:</span>
            <Switch 
              checked={isDemoMode}
              onChange={handleDemoModeChange}
              size="small"
            />
          </div>
          
          {/* 演示用户选择器 */}
          {isDemoMode && (
            <div className="flex items-center gap-2">
              <span className="text-sm text-gray-500">演示用户:</span>
              <Select
                value={currentUserId}
                onChange={handleDemoUserChange}
                options={demoUsers}
                style={{ width: 250 }}
                size="small"
                loading={loading}
              />
            </div>
          )}
          
          <div className="text-gray-500">
            欢迎回来，{getCurrentUserInfo()}！
            {isDemoMode && <span className="text-blue-500 ml-2">(演示模式)</span>}
          </div>
        </div>
      </div>

      {error && (
        <Alert 
          message={error} 
          type="error" 
          showIcon 
          className="mb-4"
          action={
            <button 
              onClick={loadDashboardData}
              className="text-blue-500 hover:text-blue-700"
            >
              重新加载
            </button>
          }
        />
      )}

      {!currentUserId && !isDemoMode && !isAuthenticated && (
        <Alert 
          message="请先登录以获得个性化推荐" 
          type="info" 
          showIcon 
          className="mb-4"
          action={
            <a href="/login" className="text-blue-500 hover:text-blue-700">
              立即登录
            </a>
          }
        />
      )}
      
      <Row gutter={16} className="mb-6">
        <Col span={6}>
          <Card>
            <Statistic
              title="今日新增内容"
              value={stats.todayContent}
              prefix={<FileTextOutlined />}
              valueStyle={{ color: '#3f8600' }}
              suffix="篇"
            />
          </Card>
        </Col>
        <Col span={6}>
          <Card>
            <Statistic
              title="我的标签"
              value={stats.userTags}
              prefix={<TagsOutlined />}
              valueStyle={{ color: '#1890ff' }}
              suffix="个"
            />
          </Card>
        </Col>
        <Col span={6}>
          <Card>
            <Statistic
              title="本周AI咨询"
              value={stats.aiChats}
              prefix={<RobotOutlined />}
              valueStyle={{ color: '#722ed1' }}
              suffix="次"
            />
          </Card>
        </Col>
        <Col span={6}>
          <Card>
            <Statistic
              title="周增长率"
              value={stats.weeklyGrowth}
              prefix={<RiseOutlined />}
              valueStyle={{ color: '#cf1322' }}
              suffix="%"
            />
          </Card>
        </Col>
      </Row>

      <Row gutter={16} className="mb-6">
        <Col span={24}>
          <Card title={<><DollarOutlined /> 实时价格指数</>}>
            <Row gutter={16}>
              {priceData.map((item, index) => (
                <Col span={6} key={index}>
                  <Card size="small" className="text-center">
                    <div className="font-semibold">{item.name}</div>
                    <div className="text-2xl font-bold my-2">
                      {item.price}
                    </div>
                    <div className={`text-sm ${item.change >= 0 ? 'text-green-500' : 'text-red-500'}`}>
                      {item.change >= 0 ? '+' : ''}{item.change} ({item.changePercent >= 0 ? '+' : ''}{item.changePercent}%)
                    </div>
                  </Card>
                </Col>
              ))}
            </Row>
          </Card>
        </Col>
      </Row>
      
      <Row gutter={16}>
        <Col span={16}>
          <Card 
            title={<><FireOutlined /> 猜你想看</>}
            extra={<a href="/content">查看更多</a>}
          >
            {recommendations.length > 0 ? (
              <List
                itemLayout="vertical"
                dataSource={recommendations}
                renderItem={(item) => (
                  <List.Item
                    key={item.id}
                    actions={[
                      <span key="time">
                        <ClockCircleOutlined /> {new Date(item.publishTime).toLocaleDateString()}
                      </span>,
                      <span key="type">{item.type}</span>
                    ]}
                  >
                    <List.Item.Meta
                      title={<a href={`/content/${item.id}`}>{item.title}</a>}
                      description={
                        <div>
                          {item.tags.map(tag => (
                            <Tag key={tag}>{tag}</Tag>
                          ))}
                        </div>
                      }
                    />
                  </List.Item>
                )}
              />
            ) : (
              <div className="text-center text-gray-500 py-8">
                <div className="mb-2">
                  <FireOutlined style={{ fontSize: '24px', color: '#d9d9d9' }} />
                </div>
                <div className="text-sm">暂无推荐内容</div>
                <div className="text-xs text-gray-400 mt-2">
                  {currentUserId ? `正在为 ${getCurrentUserInfo()} 生成推荐...` : '请设置用户标签以获得推荐'}
                </div>
              </div>
            )}
          </Card>
        </Col>
        
        <Col span={8}>
          <Card 
            title={<><UserOutlined /> 我的标签</>}
            extra={<a href="/tags">管理标签</a>}
            className="mb-4"
          >
            <div className="space-y-3">
              {userTags.length > 0 ? (
                <>
                  <div className="text-xs text-gray-500 mb-3">
                    已设置 {userTags.length} 个标签，用于个性化推荐
                    {isDemoMode && (
                      <div className="text-blue-500 mt-1">
                        当前演示用户: {getCurrentUserInfo()}
                      </div>
                    )}
                  </div>
                  {userTags.slice(0, 6).map((tag, index) => (
                    <div key={index} className="flex items-center justify-between p-2 border border-gray-100 rounded-lg hover:bg-gray-50 transition-colors">
                      <div className="flex items-center space-x-2">
                        <Tag color={getTagColor(tag.category)} className="mb-0">
                          {tag.name}
                        </Tag>
                        <span className="text-xs text-gray-400">
                          {getCategoryName(tag.category)}
                        </span>
                      </div>
                      <div className="flex items-center space-x-2">
                        <div className="text-xs text-gray-500">
                          权重: {tag.weight}
                        </div>
                        <div className="w-2 h-2 rounded-full" 
                             style={{ 
                               backgroundColor: getTagColor(tag.category),
                               opacity: tag.weight / 3.0 
                             }}>
                        </div>
                      </div>
                    </div>
                  ))}
                  {userTags.length > 6 && (
                    <div className="text-center text-xs text-gray-500 pt-2">
                      还有 {userTags.length - 6} 个标签，<a href="/tags" className="text-blue-500">查看全部</a>
                    </div>
                  )}
                </>
              ) : (
                <div className="text-center text-gray-500 py-6">
                  <div className="mb-2">
                    <TagsOutlined style={{ fontSize: '24px', color: '#d9d9d9' }} />
                  </div>
                  <div className="text-sm">暂无标签设置</div>
                  <div className="text-xs text-gray-400 mb-3">
                    {currentUserId ? `正在为 ${getCurrentUserInfo()} 加载标签...` : '设置标签后可获得个性化推荐'}
                  </div>
                  <a href="/tags" className="text-blue-500 text-sm">
                    立即设置标签 →
                  </a>
                </div>
              )}
            </div>
          </Card>

          <Card title={<><RobotOutlined /> AI助手</>}>
            <div className="space-y-2">
              <div className="p-3 bg-blue-50 rounded cursor-pointer hover:bg-blue-100 transition-colors">
                <div className="font-semibold text-blue-700">客服助手</div>
                <div className="text-xs text-gray-600">账户问题 · 功能咨询</div>
              </div>
              <div className="p-3 bg-green-50 rounded cursor-pointer hover:bg-green-100 transition-colors">
                <div className="font-semibold text-green-700">资讯助手</div>
                <div className="text-xs text-gray-600">市场快讯 · 政策解读</div>
              </div>
              <div className="p-3 bg-orange-50 rounded cursor-pointer hover:bg-orange-100 transition-colors">
                <div className="font-semibold text-orange-700">交易助手</div>
                <div className="text-xs text-gray-600">策略建议 · 风险评估</div>
              </div>
              <div className="text-center mt-3">
                <a href="/ai-assistants" className="text-blue-500 text-sm">
                  进入AI助手页面 →
                </a>
              </div>
            </div>
          </Card>
        </Col>
      </Row>
    </div>
  );
};

export default Dashboard; 