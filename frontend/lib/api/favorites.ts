/**
 * 用户收藏 API 服务
 * 连接后端 /api/users/* 端点
 */

import { apiRequest, ApiError } from './client';
import { getAccessToken } from './auth';

// ============================================
// 类型定义
// ============================================

export interface FavoriteMovie {
  id: number;
  title: string;
  poster_path: string | null;
  release_date: string | null;
  vote_average: number;
}

export interface FavoriteItem {
  id: number;
  user_id: number;
  movie_id: number;
  is_liked: boolean;
  notes: string | null;
  movie: FavoriteMovie | null;
  created_at: string;
  updated_at: string;
}

export interface FavoriteListResponse {
  favorites: FavoriteItem[];
  total_count: number;
  page: number;
  page_size: number;
  total_pages: number;
}

export interface FavoriteRequest {
  action: 'like' | 'unlike';
  tags?: string[];
  notes?: string;
}

export interface FavoriteStatus {
  is_favorited: boolean;
  is_liked: boolean;
  notes?: string | null;
  updated_at?: string;
}

// ============================================
// API 函数
// ============================================

/**
 * 获取用户收藏列表
 */
export async function getUserFavorites(
  page: number = 1,
  pageSize: number = 20,
  userId?: number
): Promise<FavoriteListResponse> {
  const token = getAccessToken();
  
  if (!token) {
    throw new Error('用户未登录');
  }

  try {
    // 从token中解析用户ID（简化处理）
    // 实际应该使用 /api/auth/me 接口获取
    const response = await apiRequest<FavoriteListResponse>(
      `/api/users/me/favorites?page=${page}&page_size=${pageSize}&user_id=${userId}`,
      {
        headers: {
          Authorization: `Bearer ${token}`,
        },
      }
    );

    return response;
  } catch (error) {
    if (error instanceof ApiError) {
      throw new Error(error.message || '获取收藏列表失败');
    }
    throw new Error('网络错误，请稍后重试');
  }
}

/**
 * 添加/取消收藏电影
 */
export async function toggleFavorite(
  movieId: number,
  action: 'like' | 'unlike',
  notes?: string
): Promise<FavoriteItem> {
  const token = getAccessToken();
  
  if (!token) {
    throw new Error('用户未登录');
  }

  try {
    const response = await apiRequest<FavoriteItem>(
      `/api/users/me/favorites/${movieId}`,
      {
        method: 'POST',
        headers: {
          Authorization: `Bearer ${token}`,
          'Content-Type': 'application/json',
        },
        body: JSON.stringify({
          action,
          notes,
        }),
      }
    );

    return response;
  } catch (error) {
    if (error instanceof ApiError) {
      throw new Error(error.message || '操作失败');
    }
    throw new Error('网络错误，请稍后重试');
  }
}

/**
 * 移除收藏
 */
export async function removeFavorite(
  movieId: number,
  userId?: number
): Promise<{ message: string }> {
  const token = getAccessToken();
  
  if (!token) {
    throw new Error('用户未登录');
  }

  try {
    const response = await apiRequest<{ message: string }>(
      `/api/users/me/favorites/${movieId}?user_id=${userId || ''}`,
      {
        method: 'DELETE',
        headers: {
          Authorization: `Bearer ${token}`,
        },
      }
    );

    return response;
  } catch (error) {
    if (error instanceof ApiError) {
      throw new Error(error.message || '移除收藏失败');
    }
    throw new Error('网络错误，请稍后重试');
  }
}

/**
 * 检查电影收藏状态
 */
export async function checkFavoriteStatus(
  movieId: number,
  userId?: number
): Promise<FavoriteStatus> {
  const token = getAccessToken();
  
  if (!token) {
    return { is_favorited: false, is_liked: false };
  }

  try {
    const response = await apiRequest<FavoriteStatus>(
      `/api/users/check-favorite/${movieId}?user_id=${userId || ''}`,
      {
        headers: {
          Authorization: `Bearer ${token}`,
        },
      }
    );

    return response;
  } catch (error) {
    // 出错时默认未收藏
    return { is_favorited: false, is_liked: false };
  }
}

/**
 * 获取用户统计信息
 */
export async function getUserStats(userId?: number) {
  const token = getAccessToken();
  
  if (!token) {
    throw new Error('用户未登录');
  }

  try {
    const response = await apiRequest<{
      user_id: number;
      watch_count: number;
      favorite_count: number;
      rating_count: number;
      search_count: number;
      activity_score: number;
      recent_activity: string | null;
      member_since: string;
    }>(
      `/api/users/me/stats?user_id=${userId || ''}`,
      {
        headers: {
          Authorization: `Bearer ${token}`,
        },
      }
    );

    return response;
  } catch (error) {
    if (error instanceof ApiError) {
      throw new Error(error.message || '获取用户统计失败');
    }
    throw new Error('网络错误，请稍后重试');
  }
}
