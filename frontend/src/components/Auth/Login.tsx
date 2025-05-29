import React, { useState, useEffect } from 'react';
import { Form, Input, Button, Card, Alert, Divider } from 'antd';
import { MailOutlined, LockOutlined, ExperimentOutlined, InfoCircleOutlined } from '@ant-design/icons';
import { Link, useNavigate, useLocation } from 'react-router-dom';
import { useDispatch } from 'react-redux';
import { loginUser } from '../../store/slices/authSlice';
import { enableDemoMode } from '../../store/slices/userSlice';
import { testConnection, diagnoseNetwork } from '../../services/api';
import type { AppDispatch } from '../../store';

const Login: React.FC = () => {
  const [form] = Form.useForm();
  const navigate = useNavigate();
  const location = useLocation();
  const dispatch = useDispatch<AppDispatch>();
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);
  const [networkStatus, setNetworkStatus] = useState<'testing' | 'success' | 'failed' | null>(null);
  const [diagnosisResults, setDiagnosisResults] = useState<any>(null);
  const [showDiagnosis, setShowDiagnosis] = useState(false);

  // 获取重定向信息
  const from = (location.state as any)?.from?.pathname || '/';
  const allowDemo = (location.state as any)?.allowDemo || false;

  useEffect(() => {
    // 组件加载时测试网络连接
    testNetworkConnection();
  }, []);

  const testNetworkConnection = async () => {
    setNetworkStatus('testing');
    try {
      const isConnected = await testConnection();
      setNetworkStatus(isConnected ? 'success' : 'failed');
      
      // 如果连接失败，自动运行详细诊断
      if (!isConnected) {
        const diagnosis = await diagnoseNetwork();
        setDiagnosisResults(diagnosis);
        setShowDiagnosis(true);
      }
    } catch (error) {
      console.error('网络测试失败:', error);
      setNetworkStatus('failed');
      const diagnosis = await diagnoseNetwork();
      setDiagnosisResults(diagnosis);
      setShowDiagnosis(true);
    }
  };

  const onFinish = async (values: any) => {
    setLoading(true);
    setError(null);
    
    try {
      console.log('🔐 正在登录:', values);
      const resultAction = await dispatch(loginUser({
        email: values.email,
        password: values.password
      }));
      
      if (loginUser.fulfilled.match(resultAction)) {
        console.log('✅ 登录成功');
        navigate(from, { replace: true });
      } else {
        // 获取具体的错误信息
        const errorMessage = resultAction.payload as string || '登录失败，请稍后重试';
        console.log('❌ 登录失败:', errorMessage);
        setError(errorMessage);
      }
    } catch (err: any) {
      console.error('❌ 登录错误:', err);
      
      // 根据错误类型显示具体错误信息
      let errorMessage = '登录失败，请稍后重试';
      
      if (err.code === 'ECONNABORTED' || err.message?.includes('超时')) {
        errorMessage = `网络连接超时，请检查网络连接后重试`;
      } else if (err.code === 'ECONNREFUSED') {
        errorMessage = '无法连接到服务器，请检查后端服务是否运行';
      } else if (err.response?.status === 401) {
        errorMessage = '邮箱或密码错误，请检查后重试';
      } else if (err.response?.status === 500) {
        errorMessage = '服务器内部错误，请稍后重试';
      } else if (err.response?.status === 422) {
        errorMessage = '请求数据格式错误，请检查输入';
      } else if (err.response?.status >= 400 && err.response?.status < 500) {
        errorMessage = `客户端错误 (${err.response.status})：${err.response?.data?.message || '请求失败'}`;
      } else if (err.response?.status >= 500) {
        errorMessage = `服务器错误 (${err.response.status})，请稍后重试`;
      } else if (err.message) {
        errorMessage = err.message;
      }
      
      setError(errorMessage);
    } finally {
      setLoading(false);
    }
  };

  const handleDemoMode = () => {
    console.log('🎭 启用演示模式');
    dispatch(enableDemoMode());
    navigate(from, { replace: true });
  };

  const handleQuickLogin = (email: string) => {
    form.setFieldsValue({ email, password: 'demo123' });
  };

  return (
    <div className="flex justify-center items-center min-h-screen bg-gray-50">
      <Card 
        title="用户登录" 
        className="w-full max-w-md shadow-lg"
        extra={<Link to="/register">创建新账户</Link>}
      >
        {error && <Alert message={error} type="error" showIcon className="mb-4" />}
        
        {from !== '/' && (
          <Alert 
            message={`访问 ${from} 需要登录或使用演示模式`} 
            type="info" 
            showIcon 
            className="mb-4" 
          />
        )}
        
        <Form
          form={form}
          name="login"
          layout="vertical"
          onFinish={onFinish}
          initialValues={{
            email: 'zhang@newenergy.com',
            password: 'demo123'
          }}
        >
          <Form.Item
            name="email"
            rules={[
              { required: true, message: '请输入邮箱地址' },
              { type: 'email', message: '请输入有效的邮箱地址' }
            ]}
          >
            <Input prefix={<MailOutlined />} placeholder="邮箱地址" />
          </Form.Item>
          
          <Form.Item
            name="password"
            rules={[{ required: true, message: '请输入密码' }]}
          >
            <Input.Password prefix={<LockOutlined />} placeholder="密码" />
          </Form.Item>
          
          <Form.Item>
            <Button 
              type="primary" 
              htmlType="submit" 
              loading={loading}
              className="w-full"
            >
              {loading ? '登录中...' : '登录'}
            </Button>
          </Form.Item>
          
          <div className="flex justify-between">
            <Link to="/forgot-password">忘记密码？</Link>
          </div>
        </Form>
        
        <Divider>或者</Divider>
        
        <Button 
          type="dashed" 
          icon={<ExperimentOutlined />}
          onClick={handleDemoMode}
          className="w-full mb-4"
          size="large"
        >
          进入演示模式（无需登录）
        </Button>
        
        <div className="mt-4 p-3 bg-blue-50 rounded text-sm">
          <strong>演示用户账户：</strong>
          <div className="text-xs text-gray-600 mb-2">点击快速填充登录信息</div>
          <div className="grid grid-cols-1 gap-2">
            <div 
              className="bg-white p-2 rounded border cursor-pointer hover:bg-gray-50 transition-colors"
              onClick={() => handleQuickLogin('zhang@newenergy.com')}
            >
              <strong>张先生</strong> (新能源投资者)<br/>
              <span className="text-xs text-gray-500">zhang@newenergy.com</span>
            </div>
            <div 
              className="bg-white p-2 rounded border cursor-pointer hover:bg-gray-50 transition-colors"
              onClick={() => handleQuickLogin('li@traditional.com')}
            >
              <strong>李女士</strong> (传统能源企业主)<br/>
              <span className="text-xs text-gray-500">li@traditional.com</span>
            </div>
            <div 
              className="bg-white p-2 rounded border cursor-pointer hover:bg-gray-50 transition-colors"
              onClick={() => handleQuickLogin('wang@carbon.com')}
            >
              <strong>王先生</strong> (节能减排顾问)<br/>
              <span className="text-xs text-gray-500">wang@carbon.com</span>
            </div>
            <div 
              className="bg-white p-2 rounded border cursor-pointer hover:bg-gray-50 transition-colors"
              onClick={() => handleQuickLogin('chen@power.com')}
            >
              <strong>陈女士</strong> (电力系统工程师)<br/>
              <span className="text-xs text-gray-500">chen@power.com</span>
            </div>
            <div 
              className="bg-white p-2 rounded border cursor-pointer hover:bg-gray-50 transition-colors"
              onClick={() => handleQuickLogin('liu@policy.com')}
            >
              <strong>刘先生</strong> (能源政策研究员)<br/>
              <span className="text-xs text-gray-500">liu@policy.com</span>
            </div>
          </div>
        </div>
        
        <div className="mt-2 p-2 bg-gray-50 rounded text-xs text-gray-600">
          <strong>使用说明：</strong><br/>
          • 登录模式：使用真实账户，完整功能<br/>
          • 演示模式：无需注册，体验所有功能<br/>
          • 所有演示账户密码均为：demo123
        </div>
        
        <div className="mt-2 p-2 bg-blue-50 rounded text-xs">
          <div className="flex items-center justify-between">
            <div>
              <strong>网络状态：</strong>
              {networkStatus === 'testing' && <span className="text-yellow-600">🔄 正在测试...</span>}
              {networkStatus === 'success' && <span className="text-green-600">✅ 连接正常</span>}
              {networkStatus === 'failed' && <span className="text-red-600">❌ 连接失败</span>}
            </div>
            <Button 
              size="small" 
              type="text" 
              icon={<InfoCircleOutlined />}
              onClick={testNetworkConnection}
              loading={networkStatus === 'testing'}
            >
              重新测试
            </Button>
          </div>
          <div className="text-xs text-gray-500 mt-1">
            API地址: {window.location.hostname === 'localhost' ? 'http://localhost:8001' : `http://${window.location.hostname}:8001`}
          </div>
          
          {showDiagnosis && diagnosisResults && (
            <div className="mt-2 p-2 bg-white rounded border">
              <div className="font-semibold text-xs mb-1">网络诊断结果:</div>
              <div className="space-y-1">
                <div className="flex justify-between">
                  <span>localhost:8001</span>
                  <span className={diagnosisResults.localhost ? 'text-green-600' : 'text-red-600'}>
                    {diagnosisResults.localhost ? '✅' : '❌'}
                  </span>
                </div>
                <div className="flex justify-between">
                  <span>127.0.0.1:8001</span>
                  <span className={diagnosisResults.ip ? 'text-green-600' : 'text-red-600'}>
                    {diagnosisResults.ip ? '✅' : '❌'}
                  </span>
                </div>
                <div className="flex justify-between">
                  <span>当前API端点</span>
                  <span className={diagnosisResults.apiEndpoint ? 'text-green-600' : 'text-red-600'}>
                    {diagnosisResults.apiEndpoint ? '✅' : '❌'}
                  </span>
                </div>
              </div>
              
              {!diagnosisResults.localhost && !diagnosisResults.ip && (
                <div className="mt-2 p-1 bg-red-50 rounded text-red-700 text-xs">
                  💡 建议：后端服务可能未启动，请检查 http://localhost:8001 是否可访问
                </div>
              )}
              
              <button 
                className="text-blue-500 text-xs mt-1" 
                onClick={() => setShowDiagnosis(false)}
              >
                隐藏诊断
              </button>
            </div>
          )}
        </div>
      </Card>
    </div>
  );
};

export default Login;