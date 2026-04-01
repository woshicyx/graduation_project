/**
 * 电影相关API
 */

import { get, PaginatedResponse } from './client';

// 数据库中的电影数据类型
export interface DatabaseMovie {
  id: number;
  title: string;
  original_title: string;
  overview: string;
  tagline: string;
  budget: number;
  revenue: number;
  popularity: number;
  release_date: string;
  runtime: number;
  vote_average: number;
  vote_count: number;
  poster_path: string;
  homepage: string;
  status: string;
  original_language: string;
  genres: string; // JSON字符串
  keywords: string; // JSON字符串
  production_companies: string; // JSON字符串
  production_countries: string; // JSON字符串
  spoken_languages: string; // JSON字符串
  director: string;
  created_at: string;
  updated_at: string;
}

// 前端使用的电影数据类型
export interface Movie {
  id: string;
  title: string;
  director: string;
  genres: string[];
  rating: number;
  boxOffice: number;
  releaseDate: string;
  posterUrl: string;
  popularity: number;
  synopsis: string;
}

// 搜索参数
export interface MovieSearchParams {
  q?: string;
  director?: string;
  genre?: string;
  rating_min?: number;
  rating_max?: number;
  box_office_min?: number;
  box_office_max?: number;
  release_date_from?: string;
  release_date_to?: string;
  page?: number;
  page_size?: number;
}

// 榜单参数
export interface TopMoviesParams {
  limit?: number;
}

/**
 * 将数据库电影数据转换为前端电影数据
 */
export function transformDatabaseMovie(dbMovie: DatabaseMovie): Movie {
  // 解析genres字段（JSON字符串）
  let genres: string[] = [];
  try {
    const parsedGenres = JSON.parse(dbMovie.genres || '[]');
    if (Array.isArray(parsedGenres)) {
      genres = parsedGenres;
    } else if (typeof parsedGenres === 'string') {
      genres = [parsedGenres];
    }
  } catch {
    genres = [];
  }

  // 构建海报URL（如果没有poster_path，使用默认图片）
  let posterUrl = dbMovie.poster_path 
    ? `https://image.tmdb.org/t/p/w500${dbMovie.poster_path}`
    : '/placeholder-poster.jpg';

  return {
    id: dbMovie.id.toString(),
    title: dbMovie.title || dbMovie.original_title || '未知电影',
    director: dbMovie.director || '未知导演',
    genres,
    rating: dbMovie.vote_average || 0,
    boxOffice: dbMovie.revenue || 0,
    releaseDate: dbMovie.release_date || '未知日期',
    posterUrl,
    popularity: dbMovie.popularity || 0,
    synopsis: dbMovie.overview || dbMovie.tagline || '暂无简介',
  };
}

/**
 * 获取电影列表/搜索
 */
export async function getMovies(params?: MovieSearchParams): Promise<PaginatedResponse<Movie>> {
  try {
    const response = await get<PaginatedResponse<DatabaseMovie>>('/api/movies', params);
    
    return {
      ...response,
      items: response.items.map(transformDatabaseMovie),
    };
  } catch (error) {
    console.error('获取电影列表失败:', error);
    throw error;
  }
}

/**
 * 获取票房最高电影
 */
export async function getTopBoxOffice(params?: TopMoviesParams): Promise<PaginatedResponse<Movie>> {
  try {
    const response = await get<PaginatedResponse<DatabaseMovie>>('/api/movies/top-box-office', params);
    
    return {
      ...response,
      items: response.items.map(transformDatabaseMovie),
    };
  } catch (error) {
    console.error('获取票房最高电影失败:', error);
    throw error;
  }
}

/**
 * 获取评分最高电影
 */
export async function getTopRated(params?: TopMoviesParams): Promise<PaginatedResponse<Movie>> {
  try {
    const response = await get<PaginatedResponse<DatabaseMovie>>('/api/movies/top-rated', params);
    
    return {
      ...response,
      items: response.items.map(transformDatabaseMovie),
    };
  } catch (error) {
    console.error('获取评分最高电影失败:', error);
    throw error;
  }
}

/**
 * 获取随机推荐电影
 */
export async function getRandomMovies(limit: number = 5): Promise<Movie[]> {
  try {
    // 注意：后端需要实现 /api/movies/random 接口
    const response = await get<PaginatedResponse<DatabaseMovie>>('/api/movies/random', { limit });
    
    return response.items.map(transformDatabaseMovie);
  } catch (error) {
    console.error('获取随机电影失败:', error);
    // 如果接口未实现，返回空数组
    return [];
  }
}

/**
 * 获取电影详情
 */
export async function getMovieDetail(movieId: string): Promise<Movie> {
  try {
    const response = await get<DatabaseMovie>(`/api/movies/${movieId}`);
    return transformDatabaseMovie(response);
  } catch (error) {
    console.error(`获取电影详情失败 (ID: ${movieId}):`, error);
    throw error;
  }
}

/**
 * 获取电影统计信息
 */
export async function getMovieStats(): Promise<{
  total: number;
  averageRating: number;
  totalBoxOffice: number;
  genres: Record<string, number>;
}> {
  try {
    // 注意：后端需要实现 /api/movies/stats/summary 接口
    return await get('/api/movies/stats/summary');
  } catch (error) {
    console.error('获取电影统计失败:', error);
    // 返回默认统计信息
    return {
      total: 0,
      averageRating: 0,
      totalBoxOffice: 0,
      genres: {},
    };
  }
}

/**
 * 搜索建议
 */
export async function getSearchSuggestions(query: string, limit: number = 5): Promise<Movie[]> {
  try {
    const response = await get<PaginatedResponse<DatabaseMovie>>('/api/movies', {
      q: query,
      page_size: limit,
    });
    
    return response.items.map(transformDatabaseMovie);
  } catch (error) {
    console.error('获取搜索建议失败:', error);
    return [];
  }
}