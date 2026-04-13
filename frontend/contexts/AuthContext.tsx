"use client";

import React, { createContext, useContext, useState, useEffect, useCallback, ReactNode } from 'react';
import { 
  User, 
  LoginRequest, 
  RegisterRequest,
  login as apiLogin,
  register as apiRegister,
  logout as apiLogout,
  saveTokens,
  saveUser,
  getAccessToken,
  getStoredUser,
  clearAuth,
} from '@/lib/api/auth';

// ============================================
// 类型定义
// ============================================

interface AuthContextType {
  // 状态
  user: User | null;
  isAuthenticated: boolean;
  isLoading: boolean;
  error: string | null;
  
  // 方法
  login: (data: LoginRequest) => Promise<void>;
  register: (data: RegisterRequest) => Promise<void>;
  logout: () => Promise<void>;
  clearError: () => void;
}

interface AuthProviderProps {
  children: ReactNode;
}

// ============================================
// Context 创建
// ============================================

const AuthContext = createContext<AuthContextType | undefined>(undefined);

// ============================================
// Provider 组件
// ============================================

export function AuthProvider({ children }: AuthProviderProps) {
  const [user, setUser] = useState<User | null>(null);
  const [isLoading, setIsLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);

  // 初始化：从 localStorage 恢复登录状态
  useEffect(() => {
    const initializeAuth = () => {
      try {
        const token = getAccessToken();
        const storedUser = getStoredUser();
        
        if (token && storedUser) {
          setUser(storedUser);
        }
      } catch (err) {
        console.error('初始化认证状态失败:', err);
      } finally {
        setIsLoading(false);
      }
    };

    initializeAuth();
  }, []);

  // 登录方法
  const login = useCallback(async (data: LoginRequest) => {
    setIsLoading(true);
    setError(null);

    try {
      const response = await apiLogin(data);
      
      // 保存 Token 和用户信息
      saveTokens(response.access_token, response.refresh_token);
      saveUser(response.user);
      
      // 更新状态
      setUser(response.user);
    } catch (err) {
      const message = err instanceof Error ? err.message : '登录失败';
      setError(message);
      throw err;
    } finally {
      setIsLoading(false);
    }
  }, []);

  // 注册方法
  const register = useCallback(async (data: RegisterRequest) => {
    setIsLoading(true);
    setError(null);

    try {
      const newUser = await apiRegister(data);
      
      // 注册成功后自动登录
      await login({
        identifier: data.username, // 用户名
        password: data.password,
      });
    } catch (err) {
      const message = err instanceof Error ? err.message : '注册失败';
      setError(message);
      throw err;
    } finally {
      setIsLoading(false);
    }
  }, [login]);

  // 登出方法
  const logout = useCallback(async () => {
    setIsLoading(true);
    
    try {
      await apiLogout();
    } catch (err) {
      console.warn('登出 API 调用失败:', err);
    } finally {
      // 无论 API 是否成功，都清理本地状态
      clearAuth();
      setUser(null);
      setIsLoading(false);
    }
  }, []);

  // 清除错误
  const clearError = useCallback(() => {
    setError(null);
  }, []);

  // Context 值
  const value: AuthContextType = {
    user,
    isAuthenticated: !!user,
    isLoading,
    error,
    login,
    register,
    logout,
    clearError,
  };

  return (
    <AuthContext.Provider value={value}>
      {children}
    </AuthContext.Provider>
  );
}

// ============================================
// Hook
// ============================================

export function useAuth(): AuthContextType {
  const context = useContext(AuthContext);
  
  if (context === undefined) {
    throw new Error('useAuth must be used within an AuthProvider');
  }
  
  return context;
}

// ============================================
// Protected Route 组件
// ============================================

interface ProtectedRouteProps {
  children: ReactNode;
  fallback?: ReactNode;
}

export function ProtectedRoute({ children, fallback }: ProtectedRouteProps) {
  const { isAuthenticated, isLoading } = useAuth();

  // 加载中
  if (isLoading) {
    return (
      <div className="flex h-screen items-center justify-center bg-[#0a0a0f]">
        <div className="h-8 w-8 animate-spin rounded-full border-2 border-red-500 border-t-transparent" />
      </div>
    );
  }

  // 未认证且有 fallback
  if (!isAuthenticated && fallback) {
    return <>{fallback}</>;
  }

  // 未认证 - 重定向到登录页
  if (!isAuthenticated) {
    if (typeof window !== 'undefined') {
      window.location.href = '/auth/login';
    }
    return null;
  }

  // 已认证
  return <>{children}</>;
}

export default AuthContext;
