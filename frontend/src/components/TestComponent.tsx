import React from 'react';
import { Card, Button } from 'antd';
import { Link } from 'react-router-dom';

const TestComponent: React.FC = () => {
  return (
    <div className="flex justify-center items-center min-h-screen bg-gray-50">
      <Card title="前端测试页面" className="w-full max-w-md">
        <p>如果您看到这个页面，说明前端应用正在正常运行。</p>
        <div className="space-y-2 mt-4">
          <Button type="primary" block>
            <Link to="/register">前往注册页面</Link>
          </Button>
          <Button block>
            <Link to="/login">前往登录页面</Link>
          </Button>
        </div>
        <div className="mt-4 text-sm text-gray-600">
          <p>API Base URL: {import.meta.env.VITE_API_BASE_URL}</p>
          <p>环境: {import.meta.env.MODE}</p>
        </div>
      </Card>
    </div>
  );
};

export default TestComponent; 