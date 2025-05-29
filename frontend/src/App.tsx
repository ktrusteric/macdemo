import { BrowserRouter as Router, Routes, Route, Navigate } from 'react-router-dom';
import { Provider } from 'react-redux';
import { ConfigProvider } from 'antd';
import zhCN from 'antd/locale/zh_CN';
import { store } from './store';
import MainLayout from './components/Layout/MainLayout';
import Dashboard from './pages/Dashboard';
import TestComponent from './components/TestComponent';
import TestPage from './TestPage';
import TestTagsPage from './pages/TestTagsPage';
import TagsManagement from './pages/TagsManagement';
import ContentList from './pages/ContentList';
import AIAssistants from './pages/AIAssistants';
import Settings from './pages/Settings';
import Register from './components/Auth/Register';
import RegisterSimple from './components/Auth/RegisterSimple';
import Login from './components/Auth/Login';
import UnauthorizedPage from './pages/UnauthorizedPage';
import NotFoundPage from './pages/NotFoundPage';
import ResearchReports from './pages/ResearchReports';
import PrivateRoute from './components/Auth/PrivateRoute';
import './App.css';

function App() {
  return (
    <Provider store={store}>
      <ConfigProvider locale={zhCN}>
        <Router>
          <Routes>
            {/* 公共路由 - 不需要MainLayout */}
            <Route path="/register" element={<Register />} />
            <Route path="/register-simple" element={<RegisterSimple />} />
            <Route path="/login" element={<Login />} />
            <Route path="/unauthorized" element={<UnauthorizedPage />} />
            <Route path="/not-found" element={<NotFoundPage />} />
            
            {/* 🔧 测试路由 - 简单的测试页面 */}
            <Route path="/test" element={<TestComponent />} />
            <Route path="/test-page" element={<TestPage />} />
            <Route path="/test-tags" element={<TestTagsPage />} />
            
            {/* 受保护路由 - 使用MainLayout */}
            <Route path="/" element={
              <PrivateRoute>
                <MainLayout>
                  <Dashboard />
                </MainLayout>
              </PrivateRoute>
            } />
            
            <Route path="/tags" element={
              <PrivateRoute>
                <MainLayout>
                  <TagsManagement />
                </MainLayout>
              </PrivateRoute>
            } />
            
            <Route path="/content" element={
              <PrivateRoute>
                <MainLayout>
                  <ContentList />
                </MainLayout>
              </PrivateRoute>
            } />
            
            <Route path="/ai-assistants" element={
              <PrivateRoute>
                <MainLayout>
                  <AIAssistants />
                </MainLayout>
              </PrivateRoute>
            } />
            
            <Route path="/settings" element={
              <PrivateRoute>
                <MainLayout>
                  <Settings />
                </MainLayout>
              </PrivateRoute>
            } />
            
            {/* 需要特定权限的路由 */}
            <Route path="/research" element={
              <PrivateRoute requiredFeature="research_reports">
                <MainLayout>
                  <ResearchReports />
                </MainLayout>
              </PrivateRoute>
            } />
            
            {/* 重定向与404 */}
            <Route path="*" element={<Navigate to="/not-found" replace />} />
          </Routes>
        </Router>
      </ConfigProvider>
    </Provider>
  );
}

export default App;