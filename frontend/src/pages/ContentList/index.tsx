import React, { useState, useEffect, useCallback, useRef } from 'react';
import { 
  Card, 
  List, 
  Tag, 
  Select, 
  Input, 
  Button, 
  Space, 
  Spin, 
  Alert, 
  Avatar,
  Row,
  Col,
  Checkbox,
  Typography,
  Empty,
  Tooltip,
  Badge,
  Pagination
} from 'antd';
import { 
  SearchOutlined, 
  FilterOutlined, 
  ClockCircleOutlined,
  EyeOutlined,
  FireOutlined,
  SortAscendingOutlined,
  ReloadOutlined
} from '@ant-design/icons';
import { useSelector } from 'react-redux';
import { contentService } from '../../services/contentService';
import type { ContentListParams, Content, UserBehavior } from '../../services/contentService';
import type { RootState } from '../../store';

const { Search } = Input;
const { Option } = Select;
const { Text, Title } = Typography;
const { Group: CheckboxGroup } = Checkbox;

const ContentList: React.FC = () => {
  const { user } = useSelector((state: RootState) => state.auth);
  const [content, setContent] = useState<Content[]>([]);
  const [loading, setLoading] = useState(false);
  const [currentPage, setCurrentPage] = useState(1);
  const [totalCount, setTotalCount] = useState(0);
  const [availableTags, setAvailableTags] = useState<string[]>([]);
  const [filterVisible, setFilterVisible] = useState(false);
  const [error, setError] = useState<string | null>(null);
  
  // 筛选和排序参数
  const [params, setParams] = useState<ContentListParams>({
    page: 1,
    page_size: 10,
    sort_by: 'latest'
  });

  const listRef = useRef<HTMLDivElement>(null);

  useEffect(() => {
    loadAvailableTags();
    loadContentList();
  }, []);

  // 当参数变化时重新加载
  useEffect(() => {
    loadContentList();
  }, [params]);

  const loadAvailableTags = async () => {
    try {
      const tags = await contentService.getAvailableTags();
      setAvailableTags(tags);
    } catch (error) {
      console.error('Failed to load available tags:', error);
    }
  };

  const loadContentList = async () => {
    setLoading(true);
    setError(null);

    try {
      // 根据排序方式选择API
      let response;
      if (params.sort_by === 'relevance' && user) {
        response = await contentService.getPersonalizedContent(user.id, params);
      } else {
        response = await contentService.getContentList(params);
      }

      setContent(response.items);
      setTotalCount(response.total);
      setCurrentPage(response.page);
    } catch (error) {
      console.error('Failed to load content:', error);
      setError('内容加载失败，请重试');
    } finally {
      setLoading(false);
    }
  };

  const handleSearch = (value: string) => {
    setParams(prev => ({ ...prev, search_keyword: value, page: 1 }));
  };

  const handleSortChange = (sortBy: 'latest' | 'relevance' | 'popularity') => {
    setParams(prev => ({ ...prev, sort_by: sortBy, page: 1 }));
  };

  const handleTagFilterChange = (tags: string[]) => {
    setParams(prev => ({ ...prev, tag_filters: tags, page: 1 }));
  };

  const handleContentTypeChange = (type: string) => {
    setParams(prev => ({ ...prev, content_type: type, page: 1 }));
  };

  const handlePageChange = (page: number, pageSize?: number) => {
    setParams(prev => ({ 
      ...prev, 
      page, 
      page_size: pageSize || prev.page_size 
    }));
  };

  const recordBehavior = useCallback(async (action: 'view' | 'click', contentId: string, duration?: number) => {
    if (!user) return;
    
    const behavior: UserBehavior = {
      user_id: user.id,
      action,
      content_id: contentId,
      timestamp: new Date().toISOString(),
      duration
    };
    
    await contentService.recordUserBehavior(behavior);
  }, [user]);

  const handleContentClick = (contentItem: Content) => {
    recordBehavior('click', contentItem.id);
    // 这里可以添加路由跳转逻辑
    window.open(`/content/${contentItem.id}`, '_blank');
  };

  const getContentTypeColor = (type: string) => {
    const colorMap: { [key: string]: string } = {
      '政策法规': 'red',
      '行业资讯': 'blue',
      '交易公告': 'green',
      '研报分析': 'orange',
      '价格变动': 'purple',
      '科技创新': 'cyan'
    };
    return colorMap[type] || 'default';
  };

  const renderFilterPanel = () => (
    <Card 
      size="small" 
      title="筛选条件" 
      className="mb-4"
      style={{ display: filterVisible ? 'block' : 'none' }}
    >
      <Row gutter={16}>
        <Col span={8}>
          <div className="mb-3">
            <Text strong>内容类型</Text>
            <Select
              placeholder="选择内容类型"
              allowClear
              style={{ width: '100%', marginTop: 8 }}
              onChange={handleContentTypeChange}
              value={params.content_type}
            >
              <Option value="政策法规">政策法规</Option>
              <Option value="行业资讯">行业资讯</Option>
              <Option value="交易公告">交易公告</Option>
              <Option value="研报分析">研报分析</Option>
              <Option value="价格变动">价格变动</Option>
              <Option value="科技创新">科技创新</Option>
            </Select>
          </div>
        </Col>
        <Col span={16}>
          <div className="mb-3">
            <Text strong>标签筛选</Text>
            <CheckboxGroup
              options={availableTags.slice(0, 12).map(tag => ({ label: tag, value: tag }))}
              value={params.tag_filters}
              onChange={handleTagFilterChange}
              style={{ marginTop: 8 }}
            />
          </div>
        </Col>
      </Row>
    </Card>
  );

  return (
    <div>
      <div className="flex items-center justify-between mb-6">
        <Title level={2} className="mb-0">信息资讯</Title>
        <Space>
          <Badge count={totalCount} overflowCount={9999}>
            <Text type="secondary">共 {totalCount} 条内容</Text>
          </Badge>
        </Space>
      </div>

      {/* 搜索和控制栏 */}
      <Card className="mb-4">
        <Row gutter={16} align="middle">
          <Col flex="auto">
            <Search
              placeholder="搜索内容标题、关键词..."
              allowClear
              enterButton={<SearchOutlined />}
              size="large"
              onSearch={handleSearch}
            />
          </Col>
          <Col>
            <Space>
              <Select
                value={params.sort_by}
                onChange={handleSortChange}
                style={{ width: 120 }}
                suffixIcon={<SortAscendingOutlined />}
              >
                <Option value="latest">最新发布</Option>
                <Option value="relevance">个性化推荐</Option>
                <Option value="popularity">热门内容</Option>
              </Select>
              
              <Button
                icon={<FilterOutlined />}
                onClick={() => setFilterVisible(!filterVisible)}
                type={filterVisible ? 'primary' : 'default'}
              >
                筛选
              </Button>
              
              <Button
                icon={<ReloadOutlined />}
                onClick={() => loadContentList()}
                loading={loading}
              >
                刷新
              </Button>
            </Space>
          </Col>
        </Row>
      </Card>

      {/* 筛选面板 */}
      {renderFilterPanel()}

      {/* 错误提示 */}
      {error && (
        <Alert
          message={error}
          type="error"
          showIcon
          className="mb-4"
          action={
            <Button size="small" onClick={() => loadContentList()}>
              重试
            </Button>
          }
        />
      )}

      {/* 内容列表 */}
      <div ref={listRef}>
        <List
          dataSource={content}
          locale={{
            emptyText: (
              <Empty 
                description="暂无内容"
                image={Empty.PRESENTED_IMAGE_SIMPLE}
              />
            )
          }}
          renderItem={(item) => (
            <List.Item
              key={item.id}
              className="cursor-pointer hover:shadow-md transition-shadow"
              onClick={() => handleContentClick(item)}
              actions={[
                <Space key="metadata">
                  <Tooltip title="发布时间">
                    <span>
                      <ClockCircleOutlined /> {new Date(item.publish_time).toLocaleDateString()}
                    </span>
                  </Tooltip>
                  {item.view_count && (
                    <Tooltip title="浏览次数">
                      <span>
                        <EyeOutlined /> {item.view_count}
                      </span>
                    </Tooltip>
                  )}
                  {item.relevance_score && (
                    <Tooltip title="相关性评分">
                      <span>
                        <FireOutlined /> {Math.round(item.relevance_score * 100)}%
                      </span>
                    </Tooltip>
                  )}
                </Space>
              ]}
            >
              <List.Item.Meta
                avatar={
                  <Avatar 
                    style={{ backgroundColor: getContentTypeColor(item.type) }}
                    icon={item.type.charAt(0)}
                  />
                }
                title={
                  <div className="flex items-center justify-between">
                    <span className="font-semibold hover:text-blue-600">
                      {item.title}
                    </span>
                    <Tag color={getContentTypeColor(item.type)}>
                      {item.type}
                    </Tag>
                  </div>
                }
                description={
                  <div className="space-y-2">
                    <div className="text-gray-600 line-clamp-2">
                      {item.content.substring(0, 150)}...
                    </div>
                    <div className="flex flex-wrap gap-1">
                      {item.tags.slice(0, 5).map((tag, index) => (
                        <Tag key={index}>
                          {tag.name}
                        </Tag>
                      ))}
                      {item.tags.length > 5 && (
                        <Tag color="default">
                          +{item.tags.length - 5}
                        </Tag>
                      )}
                    </div>
                  </div>
                }
              />
            </List.Item>
          )}
        />
      </div>

      {/* 加载状态 */}
      {loading && (
        <div className="text-center py-8">
          <Spin size="large" spinning={true}>
            <div className="py-4">
              <div className="text-gray-500">加载中...</div>
            </div>
          </Spin>
        </div>
      )}

      {/* 分页 */}
      <div className="text-center py-4">
        <Pagination
          current={currentPage}
          total={totalCount}
          pageSize={params.page_size}
          onChange={handlePageChange}
        />
      </div>
    </div>
  );
};

export default ContentList; 