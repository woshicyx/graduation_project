import { useQuery, useInfiniteQuery, useMutation, useQueryClient } from '@tanstack/react-query';
import { 
  getMovies, 
  getTopBoxOffice, 
  getTopRated, 
  getRandomMovies, 
  getMovieDetail,
  getMovieStats,
  getSearchSuggestions,
  type Movie,
  type MovieSearchParams,
  type TopMoviesParams
} from '@/lib/api/movies';

// Query keys
export const movieKeys = {
  all: ['movies'] as const,
  lists: () => [...movieKeys.all, 'list'] as const,
  list: (params: MovieSearchParams) => [...movieKeys.lists(), params] as const,
  details: () => [...movieKeys.all, 'detail'] as const,
  detail: (id: string) => [...movieKeys.details(), id] as const,
  topBoxOffice: (params?: TopMoviesParams) => [...movieKeys.all, 'top-box-office', params] as const,
  topRated: (params?: TopMoviesParams) => [...movieKeys.all, 'top-rated', params] as const,
  random: (limit?: number) => [...movieKeys.all, 'random', limit] as const,
  stats: () => [...movieKeys.all, 'stats'] as const,
  searchSuggestions: (query: string, limit?: number) => [...movieKeys.all, 'suggestions', query, limit] as const,
};

/**
 * 获取电影列表/搜索
 */
export function useMovies(params?: MovieSearchParams) {
  return useQuery({
    queryKey: movieKeys.list(params || {}),
    queryFn: () => getMovies(params),
    staleTime: 5 * 60 * 1000, // 5分钟
    gcTime: 10 * 60 * 1000, // 10分钟
  });
}

/**
 * 无限滚动获取电影列表
 */
export function useInfiniteMovies(params?: Omit<MovieSearchParams, 'page'>) {
  return useInfiniteQuery({
    queryKey: movieKeys.list(params || {}),
    queryFn: ({ pageParam = 1 }) => 
      getMovies({ ...params, page: pageParam }),
    initialPageParam: 1,
    getNextPageParam: (lastPage) => {
      if (lastPage.page < lastPage.total_pages) {
        return lastPage.page + 1;
      }
      return undefined;
    },
    staleTime: 5 * 60 * 1000,
    gcTime: 10 * 60 * 1000,
  });
}

/**
 * 获取票房最高电影
 */
export function useTopBoxOffice(params?: TopMoviesParams) {
  return useQuery({
    queryKey: movieKeys.topBoxOffice(params),
    queryFn: () => getTopBoxOffice(params),
    staleTime: 10 * 60 * 1000, // 10分钟
    gcTime: 15 * 60 * 1000, // 15分钟
  });
}

/**
 * 获取评分最高电影
 */
export function useTopRated(params?: TopMoviesParams) {
  return useQuery({
    queryKey: movieKeys.topRated(params),
    queryFn: () => getTopRated(params),
    staleTime: 10 * 60 * 1000,
    gcTime: 15 * 60 * 1000,
  });
}

/**
 * 获取随机推荐电影
 */
export function useRandomMovies(limit: number = 5) {
  return useQuery({
    queryKey: movieKeys.random(limit),
    queryFn: () => getRandomMovies(limit),
    staleTime: 2 * 60 * 1000, // 2分钟
    gcTime: 5 * 60 * 1000,
  });
}

/**
 * 获取电影详情
 */
export function useMovieDetail(movieId: string) {
  return useQuery({
    queryKey: movieKeys.detail(movieId),
    queryFn: () => getMovieDetail(movieId),
    enabled: !!movieId,
    staleTime: 10 * 60 * 1000,
    gcTime: 15 * 60 * 1000,
  });
}

/**
 * 获取电影统计信息
 */
export function useMovieStats() {
  return useQuery({
    queryKey: movieKeys.stats(),
    queryFn: getMovieStats,
    staleTime: 30 * 60 * 1000, // 30分钟
    gcTime: 60 * 60 * 1000, // 60分钟
  });
}

/**
 * 获取搜索建议
 */
export function useSearchSuggestions(query: string, limit: number = 5) {
  return useQuery({
    queryKey: movieKeys.searchSuggestions(query, limit),
    queryFn: () => getSearchSuggestions(query, limit),
    enabled: query.length >= 2, // 至少2个字符才触发搜索
    staleTime: 1 * 60 * 1000, // 1分钟
    gcTime: 2 * 60 * 1000,
  });
}

/**
 * 预加载电影详情
 */
export function usePrefetchMovieDetail() {
  const queryClient = useQueryClient();
  
  return (movieId: string) => {
    queryClient.prefetchQuery({
      queryKey: movieKeys.detail(movieId),
      queryFn: () => getMovieDetail(movieId),
    });
  };
}

/**
 * 预加载电影列表
 */
export function usePrefetchMovies() {
  const queryClient = useQueryClient();
  
  return (params?: MovieSearchParams) => {
    queryClient.prefetchQuery({
      queryKey: movieKeys.list(params || {}),
      queryFn: () => getMovies(params),
    });
  };
}