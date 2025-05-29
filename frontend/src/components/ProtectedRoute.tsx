import React from 'react';
import { Navigate, useLocation } from 'react-router-dom';
import { useSelector } from 'react-redux';
import type { RootState } from '../store';

interface ProtectedRouteProps {
  children: React.ReactNode;
  requireAuth?: boolean; // 是否必须登录，默认false（允许演示模式）
}

const ProtectedRoute: React.FC<ProtectedRouteProps> = ({ 
  children, 
  requireAuth = false 
}) => {
  const location = useLocation();
  const { isAuthenticated } = useSelector((state: RootState) => state.auth);
  const { isDemoMode } = useSelector((state: RootState) => state.user);

  // 如果需要强制认证且用户未登录，跳转到登录页
  if (requireAuth && !isAuthenticated) {
    return <Navigate 
      to="/login" 
      state={{ from: location }} 
      replace 
    />;
  }

  // 如果不需要强制认证，检查是否有认证或演示模式
  if (!requireAuth && !isAuthenticated && !isDemoMode) {
    // 可以选择跳转到登录页，或者启用演示模式
    // 这里我们跳转到登录页，但提供演示模式选项
    return <Navigate 
      to="/login" 
      state={{ from: location, allowDemo: true }} 
      replace 
    />;
  }

  return <>{children}</>;
};

export default ProtectedRoute; 