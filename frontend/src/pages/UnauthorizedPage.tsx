// src/pages/UnauthorizedPage.tsx
import React from 'react';
import { Result, Button } from 'antd';
import { Link } from 'react-router-dom';

const UnauthorizedPage: React.FC = () => {
  return (
    <div className="flex justify-center items-center min-h-screen">
      <Result
        status="403"
        title="无权访问"
        subTitle="很抱歉，您没有权限访问此页面。需要升级为付费用户才能查看高级内容。"
        extra={[
          <Button type="primary" key="dashboard">
            <Link to="/">返回首页</Link>
          </Button>,
          <Button key="upgrade">
            <Link to="/settings">升级账户</Link>
          </Button>
        ]}
      />
    </div>
  );
};

export default UnauthorizedPage;