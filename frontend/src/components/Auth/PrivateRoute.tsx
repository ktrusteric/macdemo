import React from 'react';
import { Navigate, useLocation } from 'react-router-dom';
import { useSelector } from 'react-redux';
import type { RootState } from '../../store';

interface PrivateRouteProps {
  children: React.ReactNode;
  requiredFeature?: string;
  requireAuth?: boolean; // 是否强制需要认证（默认false，允许演示模式）
}

const PrivateRoute: React.FC<PrivateRouteProps> = ({ 
  children, 
  requiredFeature,
  requireAuth = false
}) => {
  const location = useLocation();
  const { user, isAuthenticated } = useSelector((state: RootState) => state.auth);
  const { isDemoMode, currentUserId } = useSelector((state: RootState) => state.user);

  // 如果强制需要认证且用户未登录，跳转到登录页
  if (requireAuth && !isAuthenticated) {
    console.log('需要强制认证，用户未登录，跳转到登录页');
    return <Navigate 
      to="/login" 
      state={{ from: location }} 
      replace 
    />;
  }

  // 如果不强制认证，检查是否有认证或演示模式
  if (!requireAuth && !isAuthenticated && !isDemoMode) {
    console.log('用户未认证且未启用演示模式，跳转到登录页');
    return <Navigate 
      to="/login" 
      state={{ from: location, allowDemo: true }} 
      replace 
    />;
  }

  // 在演示模式下，跳过权限检查
  if (isDemoMode) {
    console.log('演示模式下访问:', location.pathname, '当前演示用户:', currentUserId);
    return <>{children}</>;
  }

  // 对于认证用户，检查特定功能权限
  if (isAuthenticated && requiredFeature && user?.access_features && !user.access_features.includes(requiredFeature)) {
    console.log(`用户缺少权限: ${requiredFeature}`);
    return <Navigate to="/unauthorized" replace />;
  }

  return <>{children}</>;
};

export default PrivateRoute;