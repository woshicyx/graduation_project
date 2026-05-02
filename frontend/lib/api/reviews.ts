/**
 * 影评相关API
 */

import { get, post, PaginatedResponse } from './client';

// 影评数据类型
export interface Review {
  id: number;
  movie_id: number;
  rating: number;
  title: string;
  content: string;
  author: string;
  helpful_count: number;
  not_helpful_count: number;
  created_at: string;
  updated_at: string;
  movie_title?: string;
  movie_poster_url?: string;
}

// 影评统计信息
export interface ReviewStats {
  movie_id: number;
  total_reviews: number;
  average_rating: number;
  rating_distribution: Record<string, number>;
  recent_reviews_count: number;
}

// 创建影评请求
export interface CreateReviewRequest {
  movie_id: number;
  rating: number;
  title: string;
  content: string;
  author?: string;
}

// 影评筛选参数
export interface ReviewFilters {
  movie_id?: number;
  min_rating?: number;
  max_rating?: number;
  author?: string;
  sort_by?: 'newest' | 'most_helpful' | 'highest_rating' | 'lowest_rating';
  page?: number;
  page_size?: number;
}

// 投票请求
export interface VoteReviewRequest {
  helpful: boolean;
}

/**
 * 获取影评列表
 */
export async function getReviews(filters: ReviewFilters = {}): Promise<PaginatedResponse<Review>> {
  try {
    const params = {
      movie_id: filters.movie_id,
      min_rating: filters.min_rating,
      max_rating: filters.max_rating,
      author: filters.author,
      sort_by: filters.sort_by || 'newest',
      page: filters.page || 1,
      page_size: filters.page_size || 20,
    };

    return await get<PaginatedResponse<Review>>('/api/reviews', params);
  } catch (error) {
    console.error('获取影评列表失败:', error);
    throw error;
  }
}

/**
 * 获取影评详情
 */
export async function getReviewDetail(reviewId: number): Promise<Review> {
  try {
    return await get<Review>(`/api/reviews/${reviewId}`);
  } catch (error) {
    console.error(`获取影评详情失败 (ID: ${reviewId}):`, error);
    throw error;
  }
}

/**
 * 创建影评
 */
export async function createReview(reviewData: CreateReviewRequest): Promise<Review> {
  try {
    const data = {
      ...reviewData,
      author: reviewData.author || '匿名用户',
      helpful_count: 0,
      not_helpful_count: 0,
    };

    return await post<Review>('/api/reviews', data);
  } catch (error) {
    console.error('创建影评失败:', error);
    throw error;
  }
}

/**
 * 获取影评统计信息
 */
export async function getReviewStats(movieId: number): Promise<ReviewStats> {
  try {
    return await get<ReviewStats>(`/api/reviews/stats/${movieId}`);
  } catch (error) {
    console.error(`获取影评统计失败 (电影ID: ${movieId}):`, error);
    // 返回默认统计信息
    return {
      movie_id: movieId,
      total_reviews: 0,
      average_rating: 0,
      rating_distribution: {},
      recent_reviews_count: 0,
    };
  }
}

/**
 * 为影评投票
 */
export async function voteReview(reviewId: number, helpful: boolean): Promise<Review> {
  try {
    return await post<Review>(`/api/reviews/${reviewId}/vote`, { helpful });
  } catch (error) {
    console.error(`投票影评失败 (ID: ${reviewId}):`, error);
    throw error;
  }
}

/**
 * 格式化评分显示
 */
export function formatRating(rating: number): string {
  return rating.toFixed(1);
}

/**
 * 格式化日期显示
 */
export function formatReviewDate(dateString: string): string {
  const date = new Date(dateString);
  const now = new Date();
  const diffMs = now.getTime() - date.getTime();
  const diffDays = Math.floor(diffMs / (1000 * 60 * 60 * 24));

  if (diffDays === 0) {
    return '今天';
  } else if (diffDays === 1) {
    return '昨天';
  } else if (diffDays < 7) {
    return `${diffDays}天前`;
  } else if (diffDays < 30) {
    const weeks = Math.floor(diffDays / 7);
    return `${weeks}周前`;
  } else {
    return date.toLocaleDateString('zh-CN', {
      year: 'numeric',
      month: 'long',
      day: 'numeric',
    });
  }
}

/**
 * 计算影评有用率
 */
export function calculateHelpfulRate(review: Review): number {
  const totalVotes = review.helpful_count + review.not_helpful_count;
  if (totalVotes === 0) return 0;
  return Math.round((review.helpful_count / totalVotes) * 100);
}