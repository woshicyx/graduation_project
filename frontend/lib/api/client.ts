/**
 * API客户端配置
 */

const API_BASE_URL = process.env.NEXT_PUBLIC_API_URL || 'http://localhost:8000';

export interface ApiResponse<T> {
  data: T;
  message?: string;
  success: boolean;
}

export interface PaginatedResponse<T> {
  items: T[];
  total: number;
  page: number;
  page_size: number;
  total_pages: number;
}

export class ApiError extends Error {
  constructor(
    public status: number,
    public message: string,
    public details?: any
  ) {
    super(message);
    this.name = 'ApiError';
  }
}

/**
 * 统一的API请求函数
 */
export async function apiRequest<T>(
  endpoint: string,
  options: RequestInit = {}
): Promise<T> {
  const url = `${API_BASE_URL}${endpoint}`;
  
  const defaultHeaders = {
    'Content-Type': 'application/json',
    'Accept': 'application/json',
  };

  const config: RequestInit = {
    ...options,
    headers: {
      ...defaultHeaders,
      ...options.headers,
    },
  };

  try {
    const response = await fetch(url, config);
    
    if (!response.ok) {
      let errorMessage = `HTTP ${response.status}: ${response.statusText}`;
      try {
        const errorData = await response.json();
        errorMessage = errorData.detail || errorData.message || errorMessage;
      } catch {
        // 如果响应不是JSON，使用默认错误信息
      }
      throw new ApiError(response.status, errorMessage);
    }

    // 处理204 No Content响应
    if (response.status === 204) {
      return {} as T;
    }

    const data = await response.json();
    return data;
  } catch (error) {
    if (error instanceof ApiError) {
      throw error;
    }
    throw new ApiError(0, '网络请求失败，请检查网络连接');
  }
}

/**
 * GET请求
 */
export async function get<T>(endpoint: string, params?: Record<string, any>): Promise<T> {
  const queryString = params ? `?${new URLSearchParams(params).toString()}` : '';
  return apiRequest<T>(`${endpoint}${queryString}`, {
    method: 'GET',
  });
}

/**
 * POST请求
 */
export async function post<T>(endpoint: string, data?: any): Promise<T> {
  return apiRequest<T>(endpoint, {
    method: 'POST',
    body: data ? JSON.stringify(data) : undefined,
  });
}

/**
 * PUT请求
 */
export async function put<T>(endpoint: string, data?: any): Promise<T> {
  return apiRequest<T>(endpoint, {
    method: 'PUT',
    body: data ? JSON.stringify(data) : undefined,
  });
}

/**
 * DELETE请求
 */
export async function del<T>(endpoint: string): Promise<T> {
  return apiRequest<T>(endpoint, {
    method: 'DELETE',
  });
}

/**
 * 创建带取消功能的请求
 */
export function createCancellableRequest() {
  const controller = new AbortController();
  
  return {
    signal: controller.signal,
    cancel: () => controller.abort(),
  };
}

/**
 * 设置请求超时
 */
export function withTimeout<T>(
  promise: Promise<T>,
  timeoutMs: number = 10000
): Promise<T> {
  return Promise.race([
    promise,
    new Promise<never>((_, reject) => {
      setTimeout(() => reject(new ApiError(408, '请求超时')), timeoutMs);
    }),
  ]);
}