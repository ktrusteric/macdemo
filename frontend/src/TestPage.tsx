import React from 'react';

const TestPage: React.FC = () => {
  return (
    <div style={{ 
      padding: '20px', 
      textAlign: 'center',
      fontFamily: 'Arial, sans-serif',
      backgroundColor: '#f0f2f5',
      minHeight: '100vh',
      display: 'flex',
      alignItems: 'center',
      justifyContent: 'center'
    }}>
      <div style={{
        backgroundColor: 'white',
        padding: '40px',
        borderRadius: '8px',
        boxShadow: '0 2px 8px rgba(0,0,0,0.1)',
        maxWidth: '600px',
        width: '100%'
      }}>
        <h1 style={{ color: '#1890ff', marginBottom: '20px' }}>
          🔧 React 测试页面
        </h1>
        
        <div style={{ marginBottom: '20px' }}>
          <p>✅ React 组件正常渲染</p>
          <p>✅ TypeScript 编译正常</p>
          <p>✅ Vite 开发服务器运行中</p>
        </div>
        
        <div style={{ 
          backgroundColor: '#f6ffed', 
          border: '1px solid #b7eb8f',
          padding: '15px',
          borderRadius: '4px',
          marginBottom: '20px'
        }}>
          <h3>🏙️ 城市测试</h3>
          <p>支持的城市: 上海、北京、深圳、广州等</p>
        </div>

        <div style={{ 
          backgroundColor: '#fff2e8', 
          border: '1px solid #ffbb96',
          padding: '15px',
          borderRadius: '4px',
          marginBottom: '20px'
        }}>
          <h3>⚡ 能源类型测试</h3>
          <p>能源品种: 原油、天然气、液化天然气(LNG)、液化石油气(LPG)等</p>
        </div>

        <div style={{ 
          backgroundColor: '#f0f5ff', 
          border: '1px solid #91d5ff',
          padding: '15px',
          borderRadius: '4px'
        }}>
          <h3>🗺️ 区域映射测试</h3>
          <p>上海 → 华东地区 → 上海市</p>
          <p>北京 → 华北地区 → 北京市</p>
          <p>深圳 → 华南地区 → 广东省</p>
        </div>

        <div style={{ marginTop: '30px', fontSize: '14px', color: '#666' }}>
          <p>🌐 当前URL: {window.location.href}</p>
          <p>⏰ 加载时间: {new Date().toLocaleString()}</p>
        </div>
      </div>
    </div>
  );
};

export default TestPage; 