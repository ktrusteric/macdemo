// src/pages/ResearchReports.tsx
import React from 'react';
import { Card, List, Typography, Tag, Space } from 'antd';

const { Title } = Typography;

const ResearchReports: React.FC = () => {
  const reports = [
    {
      id: '1',
      title: '2023年天然气市场分析',
      author: '能源研究院',
      date: '2023-12-15',
      tags: ['天然气', '市场分析']
    },
    {
      id: '2',
      title: 'LNG贸易新格局研究',
      author: '国际能源研究所',
      date: '2023-11-30',
      tags: ['LNG', '国际贸易']
    }
  ];

  return (
    <div className="p-6">
      <Title level={2}>研究报告</Title>
      <List
        grid={{ gutter: 16, column: 3 }}
        dataSource={reports}
        renderItem={item => (
          <List.Item>
            <Card title={item.title}>
              <p>作者: {item.author}</p>
              <p>日期: {item.date}</p>
              <Space>
                {item.tags.map(tag => (
                  <Tag key={tag} color="blue">{tag}</Tag>
                ))}
              </Space>
            </Card>
          </List.Item>
        )}
      />
    </div>
  );
};

export default ResearchReports;