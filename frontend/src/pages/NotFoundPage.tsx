// src/pages/NotFoundPage.tsx
import React from 'react';
import { Result, Button } from 'antd';
import { Link } from 'react-router-dom';

const NotFoundPage: React.FC = () => {
  return (
    <div className="flex justify-center items-center min-h-screen">
      <Result
        status="404"
        title="页面不存在"
        subTitle="抱歉，您访问的页面不存在。"
        extra={
          <Button type="primary">
            <Link to="/">返回首页</Link>
          </Button>
        }
      />
    </div>
  );
};

export default NotFoundPage;