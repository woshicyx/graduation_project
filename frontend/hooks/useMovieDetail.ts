/**
 * 电影详情相关Hooks
 */

import { useQuery, useMutation, useQueryClient } from '@tanstack/react-query';
import { getMovieDetail, Movie } from '@/lib/api/movies';
import { 
  getReviews, 
  getReviewStats, 
  createReview, 
  voteReview, 
  Review, 
  ReviewStats,
  ReviewFilters,
  CreateReviewRequest
} from '@/lib/api/reviews';

/**
 * 获取电影详情
 */
export function useMovieDetail(movieId: string) {
  return useQuery({
    queryKey: ['movie', movieId],
    queryFn: () => getMovieDetail(movieId),
    enabled: !!movieId,
    staleTime: 5 * 60 * 1000, // 5分钟
  });
}

/**
 * 获取电影影评列表
 */
export function useMovieReviews(movieId: string, filters: ReviewFilters = {}) {
  return useQuery({
    queryKey: ['movie-reviews', movieId, filters],
    queryFn: () => getReviews({ ...filters, movie_id: parseInt(movieId) }),
    enabled: !!movieId,
    staleTime: 2 * 60 * 1000, // 2分钟
  });
}

/**
 * 获取电影影评统计
 */
export function useMovieReviewStats(movieId: string) {
  return useQuery({
    queryKey: ['movie-review-stats', movieId],
    queryFn: () => getReviewStats(parseInt(movieId)),
    enabled: !!movieId,
    staleTime: 5 * 60 * 1000, // 5分钟
  });
}

/**
 * 创建影评
 */
export function useCreateReview() {
  const queryClient = useQueryClient();
  
  return useMutation({
    mutationFn: (reviewData: CreateReviewRequest) => createReview(reviewData),
    onSuccess: (data, variables) => {
      // 使相关查询失效
      queryClient.invalidateQueries({ 
        queryKey: ['movie-reviews', variables.movie_id.toString()] 
      });
      queryClient.invalidateQueries({ 
        queryKey: ['movie-review-stats', variables.movie_id.toString()] 
      });
    },
  });
}

/**
 * 投票影评
 */
export function useVoteReview() {
  const queryClient = useQueryClient();
  
  return useMutation({
    mutationFn: ({ reviewId, helpful }: { reviewId: number; helpful: boolean }) => 
      voteReview(reviewId, helpful),
    onSuccess: (data) => {
      // 使相关查询失效
      queryClient.invalidateQueries({ 
        queryKey: ['movie-reviews', data.movie_id.toString()] 
      });
    },
  });
}

/**
 * 格式化票房显示
 */
export function formatBoxOffice(boxOffice: number): string {
  if (boxOffice === 0) return '未知';
  
  if (boxOffice >= 1_000_000_000) {
    return `$${(boxOffice / 1_000_000_000).toFixed(1)}B`;
  } else if (boxOffice >= 1_000_000) {
    return `$${(boxOffice / 1_000_000).toFixed(1)}M`;
  } else if (boxOffice >= 1_000) {
    return `$${(boxOffice / 1_000).toFixed(1)}K`;
  }
  return `$${boxOffice}`;
}

/**
 * 格式化时长显示
 */
export function formatRuntime(runtime: number): string {
  if (!runtime || runtime === 0) return '未知';
  
  const hours = Math.floor(runtime / 60);
  const minutes = runtime % 60;
  
  if (hours === 0) {
    return `${minutes}分钟`;
  }
  return `${hours}小时${minutes}分钟`;
}

/**
 * 格式化评分显示
 */
export function formatRating(rating: number): string {
  return rating.toFixed(1);
}

/**
 * 获取评分颜色
 */
export function getRatingColor(rating: number): string {
  if (rating >= 8) return 'text-green-600';
  if (rating >= 6) return 'text-yellow-600';
  return 'text-red-600';
}

/**
 * 获取评分背景颜色
 */
export function getRatingBgColor(rating: number): string {
  if (rating >= 8) return 'bg-green-100';
  if (rating >= 6) return 'bg-yellow-100';
  return 'bg-red-100';
}

/**
 * 解析JSON字符串数组
 */
export function parseJsonArray<T>(jsonString: string): T[] {
  try {
    const parsed = JSON.parse(jsonString || '[]');
    return Array.isArray(parsed) ? parsed : [];
  } catch {
    return [];
  }
}

/**
 * 获取相似电影（基于类型）
 */
export function getSimilarMovies(movie: Movie, allMovies: Movie[], limit: number = 5): Movie[] {
  if (!movie || !allMovies.length) return [];
  
  const movieGenres = movie.genres;
  if (!movieGenres.length) return [];
  
  // 计算相似度分数
  const scoredMovies = allMovies
    .filter(m => m.id !== movie.id) // 排除当前电影
    .map(otherMovie => {
      const otherGenres = otherMovie.genres;
      const commonGenres = movieGenres.filter(genre => 
        otherGenres.includes(genre)
      ).length;
      
      // 相似度分数 = 共同类型数量 + 评分相似度（0-1）
      const ratingSimilarity = 1 - Math.abs(movie.rating - otherMovie.rating) / 10;
      const score = commonGenres * 2 + ratingSimilarity;
      
      return { movie: otherMovie, score };
    })
    .sort((a, b) => b.score - a.score) // 按分数降序排序
    .slice(0, limit)
    .map(item => item.movie);
  
  return scoredMovies;
}