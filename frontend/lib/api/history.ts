/**
 * 用户浏览历史 API 服务
 * 连接后端 /api/users/* 端点
 */

import { apiRequest, ApiError } from './client';
import { getAccessToken } from './auth';

// ============================================
// 类型定义
// ============================================

export interface HistoryMovie {
  id: number;
  title: string;
  poster_path: string | null;
  release_date: string | null;
  vote_average: number | null;
}

export interface WatchHistoryItem {
  id: number;
  user_id: number;
  movie_id: number;
  movie: HistoryMovie | null;
  watch_duration: number;
  progress: number;
  interaction_score: number;
  created_at: string;
}

// ============================================
// API 函数
// ============================================

/**
 * 获取用户浏览历史
 */
export async function getWatchHistory(
  limit: number = 50,
  userId?: number
): Promise<WatchHistoryItem[]> {
  const token = getAccessToken();
  
  if (!token) {
    throw new Error('用户未登录');
  }

  try {
    const response = await apiRequest<WatchHistoryItem[]>(
      `/api/users/me/watch-history?limit=${limit}&user_id=${userId || ''}`,
      {
        headers: {
          Authorization: `Bearer ${token}`,
        },
      }
    );

    return response;
  } catch (error) {
    if (error instanceof ApiError) {
      throw new Error(error.message || '获取浏览历史失败');
    }
    throw new Error('网络错误，请稍后重试');
  }
}

/**
 * 记录浏览历史
 */
export async function addWatchHistory(
  movieId: number,
  userId?: number,
  watchDuration?: number,
  progress?: number
): Promise<{ message: string }> {
  const token = getAccessToken();
  
  if (!token) {
    throw new Error('用户未登录');
  }

  try {
    const params = new URLSearchParams();
    if (userId) params.append('user_id', userId.toString());
    if (watchDuration) params.append('watch_duration', watchDuration.toString());
    if (progress !== undefined) params.append('progress', progress.toString());

    const response = await apiRequest<{ message: string }>(
      `/api/users/me/watch-history/${movieId}?${params.toString()}`,
      {
        method: 'POST',
        headers: {
          Authorization: `Bearer ${token}`,
        },
      }
    );

    return response;
  } catch (error) {
    if (error instanceof ApiError) {
      throw new Error(error.message || '记录浏览历史失败');
    }
    throw new Error('网络错误，请稍后重试');
  }
}

/**
 * 记录搜索历史（从搜索结果点击进入详情页）
 */
export async function addSearchHistory(
  movieId: number,
  query?: string,
  userId?: number
): Promise<{ message: string }> {
  const token = getAccessToken();
  
  if (!token) {
    throw new Error('用户未登录');
  }

  try {
    const params = new URLSearchParams();
    if (userId) params.append('user_id', userId.toString());
    if (query) params.append('query', query);

    const response = await apiRequest<{ message: string }>(
      `/api/users/me/search-history/${movieId}?${params.toString()}`,
      {
        method: 'POST',
        headers: {
          Authorization: `Bearer ${token}`,
        },
      }
    );

    return response;
  } catch (error) {
    if (error instanceof ApiError) {
      throw new Error(error.message || '记录搜索历史失败');
    }
    throw new Error('网络错误，请稍后重试');
  }
}

/**
 * 获取浏览历史统计
 */
export async function getWatchStats(userId?: number) {
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
      throw new Error(error.message || '获取统计失败');
    }
    throw new Error('网络错误，请稍后重试');
  }
}
