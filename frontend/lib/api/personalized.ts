/**
 * 个性化推荐 API - "猜你喜欢"
 */
import { get } from './client';
import { MovieListItem } from './movie';

export interface PersonalizedItem {
  movie_id: number;
  title: string;
  poster_path: string | null;
  vote_average: number;
  release_date: string | null;
  genres: string[];
  relevance_score: number;
  reason?: string;
}

export interface PersonalizedResponse {
  query: string;
  items: PersonalizedItem[];
  total_time_ms: number;
}

/**
 * 获取个性化推荐（"猜你喜欢"）
 * 已登录用户返回基于收藏历史的推荐
 * 游客返回热门推荐
 */
export async function getPersonalizedRecommendations(limit = 10): Promise<MovieListItem[]> {
  try {
    const response = await get<PersonalizedResponse>(`/api/personalized/for-you?limit=${limit}`);
    
    return response.items.map((item: PersonalizedItem) => ({
      id: item.movie_id,
      title: item.title,
      poster_path: item.poster_path || null,
      vote_average: item.vote_average || item.relevance_score * 10,
      popularity: item.relevance_score * 100,
      release_date: item.release_date || null,
      genres: item.genres || [],
      director: null,
    }));
  } catch (error) {
    console.error("获取个性化推荐失败:", error);
    return [];
  }
}
