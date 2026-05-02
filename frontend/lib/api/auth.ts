/**
 * 用户认证 API 服务
 * 连接后端 /api/auth/* 端点
 */

import { apiRequest, ApiError } from './client';

// ============================================
// 类型定义
// ============================================

export interface User {
  id: number;
  username: string;
  email: string;
  role: string;
  is_active: boolean;
  is_verified: boolean;
  created_at: string;
  updated_at: string;
}

export interface RegisterRequest {
  username: string;
  email: string;
  password: string;
  confirm_password: string;
}

export interface LoginRequest {
  identifier: string; // 支持用户名或邮箱
  password: string;
}

export interface TokenResponse {
  access_token: string;
  refresh_token?: string;
  token_type: string;
  expires_in: number;
  user: User;
}

export interface AuthState {
  user: User | null;
  accessToken: string | null;
  isAuthenticated: boolean;
  isLoading: boolean;
}

// ============================================
// API 函数
// ============================================

/**
 * 用户注册
 */
export async function register(data: RegisterRequest): Promise<User> {
  try {
    const response = await apiRequest<{
      id: number;
      username: string;
      email: string;
      role: string;
      is_active: boolean;
      is_verified: boolean;
      created_at: string;
      updated_at: string;
    }>('/api/auth/register', {
      method: 'POST',
      body: JSON.stringify(data),
    });

    return response as User;
  } catch (error) {
    if (error instanceof ApiError) {
      // 解析后端返回的错误信息
      throw new Error(error.message || '注册失败');
    }
    throw new Error('网络错误，请稍后重试');
  }
}

/**
 * 用户登录
 */
export async function login(data: LoginRequest): Promise<TokenResponse> {
  try {
    const response = await apiRequest<TokenResponse>('/api/auth/login', {
      method: 'POST',
      body: JSON.stringify(data),
    });

    return response;
  } catch (error) {
    if (error instanceof ApiError) {
      throw new Error(error.message || '登录失败');
    }
    throw new Error('网络错误，请稍后重试');
  }
}

/**
 * 用户登出
 */
export async function logout(): Promise<void> {
  try {
    await apiRequest<{ message: string }>('/api/auth/logout', {
      method: 'POST',
    });
  } catch (error) {
    // 即使API调用失败，也清理本地状态
    console.warn('登出API调用失败，将清理本地状态');
  }
}

/**
 * 获取当前用户信息
 */
export async function getCurrentUser(token: string): Promise<User> {
  try {
    const response = await apiRequest<User>('/api/auth/me', {
      headers: {
        Authorization: `Bearer ${token}`,
      },
    });

    return response;
  } catch (error) {
    if (error instanceof ApiError) {
      throw new Error(error.message || '获取用户信息失败');
    }
    throw new Error('网络错误，请稍后重试');
  }
}

// ============================================
// Token 管理
// ============================================

const TOKEN_KEY = 'movieai_access_token';
const REFRESH_TOKEN_KEY = 'movieai_refresh_token';
const USER_KEY = 'movieai_user';

/**
 * 保存 Token 到 localStorage
 */
export function saveTokens(accessToken: string, refreshToken?: string): void {
  if (typeof window === 'undefined') return;
  
  localStorage.setItem(TOKEN_KEY, accessToken);
  if (refreshToken) {
    localStorage.setItem(REFRESH_TOKEN_KEY, refreshToken);
  }
}

/**
 * 获取 Access Token
 */
export function getAccessToken(): string | null {
  if (typeof window === 'undefined') return null;
  return localStorage.getItem(TOKEN_KEY);
}

/**
 * 获取 Refresh Token
 */
export function getRefreshToken(): string | null {
  if (typeof window === 'undefined') return null;
  return localStorage.getItem(REFRESH_TOKEN_KEY);
}

/**
 * 清除所有 Token
 */
export function clearTokens(): void {
  if (typeof window === 'undefined') return;
  localStorage.removeItem(TOKEN_KEY);
  localStorage.removeItem(REFRESH_TOKEN_KEY);
}

/**
 * 保存用户信息到 localStorage
 */
export function saveUser(user: User): void {
  if (typeof window === 'undefined') return;
  localStorage.setItem(USER_KEY, JSON.stringify(user));
}

/**
 * 获取本地存储的用户信息
 */
export function getStoredUser(): User | null {
  if (typeof window === 'undefined') return null;
  const userStr = localStorage.getItem(USER_KEY);
  if (!userStr) return null;
  
  try {
    return JSON.parse(userStr) as User;
  } catch {
    return null;
  }
}

/**
 * 清除用户信息
 */
export function clearUser(): void {
  if (typeof window === 'undefined') return;
  localStorage.removeItem(USER_KEY);
}

/**
 * 清除所有认证信息
 */
export function clearAuth(): void {
  clearTokens();
  clearUser();
}

// ============================================
// 表单验证辅助函数
// ============================================

export function validateEmail(email: string): string | null {
  if (!email) {
    return '邮箱地址不能为空';
  }
  
  const emailRegex = /^[^\s@]+@[^\s@]+\.[^\s@]+$/;
  if (!emailRegex.test(email)) {
    return '请输入有效的邮箱地址';
  }
  
  return null;
}

export function validatePassword(password: string): string | null {
  if (!password) {
    return '密码不能为空';
  }
  
  if (password.length < 6) {
    return '密码长度至少为6位';
  }
  
  return null;
}

export function validateUsername(username: string): string | null {
  if (!username) {
    return '用户名不能为空';
  }
  
  if (username.length < 3) {
    return '用户名长度至少为3位';
  }
  
  if (username.length > 20) {
    return '用户名长度不能超过20位';
  }
  
  // 只允许字母、数字、下划线
  const usernameRegex = /^[a-zA-Z0-9_]+$/;
  if (!usernameRegex.test(username)) {
    return '用户名只能包含字母、数字和下划线';
  }
  
  return null;
}

export function validatePasswordMatch(password: string, confirmPassword: string): string | null {
  if (password !== confirmPassword) {
    return '两次输入的密码不一致';
  }
  return null;
}

// ============================================
// 导出完整认证状态
// ============================================

export function getAuthState(): AuthState {
  const token = getAccessToken();
  const user = getStoredUser();
  
  return {
    user,
    accessToken: token,
    isAuthenticated: !!token && !!user,
    isLoading: false,
  };
}
