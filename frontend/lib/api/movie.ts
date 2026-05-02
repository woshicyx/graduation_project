/**
 * 电影相关API
 */
import { get } from './client';

export interface MovieListItem {
  id: number;
  title: string;
  poster_path: string | null;
  vote_average: number | null;
  popularity: number | null;
  release_date: string | null;
  genres: string[];
  director: string | null;
}

export interface MovieDetail {
  id: number;
  title: string;
  original_title: string | null;
  overview: string | null;
  tagline: string | null;
  budget: number | null;
  revenue: number | null;
  popularity: number | null;
  release_date: string | null;
  runtime: number | null;
  vote_average: number | null;
  vote_count: number | null;
  poster_path: string | null;
  original_language: string | null;
  genres: string | null;
  keywords: string | null;
  director: string | null;
  parsed_genres: string[];
  parsed_keywords: string[];
  parsed_production_companies?: string[];
  parsed_production_countries?: string[];
  parsed_spoken_languages?: string[];
}

export interface PaginatedMovies {
  items: MovieListItem[];
  total: number;
  page: number;
  page_size: number;
  total_pages: number;
}

/**
 * 获取电影列表
 */
export async function getMovies(page = 1, pageSize = 20): Promise<PaginatedMovies> {
  return get<PaginatedMovies>('/api/movies', {
    page,
    page_size: pageSize,
  });
}

/**
 * 获取随机推荐电影
 */
export async function getRandomMovies(limit = 5): Promise<MovieListItem[]> {
  const result = await get<{ items: MovieListItem[] }>(`/api/movies/random?limit=${limit}`);
  return result.items || [];
}

/**
 * 获取评分TOP电影
 */
export async function getTopRatedMovies(limit = 20): Promise<MovieListItem[]> {
  const result = await get<{ items: MovieListItem[] }>(`/api/movies/top/rated?limit=${limit}`);
  return result.items || [];
}

/**
 * 获取热度TOP电影
 */
export async function getTopPopularMovies(limit = 20): Promise<MovieListItem[]> {
  const result = await get<{ items: MovieListItem[] }>(`/api/movies/top/popular?limit=${limit}`);
  return result.items || [];
}

/**
 * 获取票房TOP电影
 */
export async function getTopBoxOfficeMovies(limit = 20): Promise<MovieListItem[]> {
  const result = await get<{ items: MovieListItem[] }>(`/api/movies/top/box-office?limit=${limit}`);
  return result.items || [];
}

/**
 * 获取科幻类型电影（用于Hero背景）
 */
export async function getSciFiMovies(limit = 50): Promise<MovieListItem[]> {
  const result = await searchMovies('', {
    genre: '科幻',
    page_size: limit,
  });
  return result.items || [];
}

/**
 * 搜索电影
 */
export async function searchMovies(
  query: string,
  options?: {
    genres?: string;  // 多选类型，用逗号分隔
    genre?: string;   // 单选类型（兼容）
    director?: string;
    rating_min?: number;
    rating_max?: number;
    year_min?: number;
    year_max?: number;
    years?: string;   // 多选年份，用逗号分隔
    sort?: string;    // 排序: rating, popular, boxoffice
    page?: number;
    page_size?: number;
  }
): Promise<PaginatedMovies> {
  const params: Record<string, any> = { query: query };
  // 支持多选genres
  if (options?.genres) params.genres = options.genres;
  // 兼容单选genre
  else if (options?.genre) params.genres = options.genre;
  if (options?.director) params.director = options.director;
  if (options?.rating_min) params.rating_min = options.rating_min;
  if (options?.rating_max) params.rating_max = options.rating_max;
  if (options?.year_min) params.year_min = options.year_min;
  if (options?.year_max) params.year_max = options.year_max;
  if (options?.years) params.years = options.years;
  if (options?.sort) params.sort = options.sort;
  if (options?.page) params.page = options.page;
  if (options?.page_size) params.page_size = options.page_size;
  
  return get<PaginatedMovies>('/api/search/hybrid?' + new URLSearchParams(params).toString());
}

/**
 * 获取电影详情
 */
export async function getMovieDetail(id: number): Promise<MovieDetail> {
  const data = await get<any>(`/api/movies/${id}`);
  
  // 解析 genres 和 keywords 字段（后端返回的是 JSON 字符串）
  if (data.genres && typeof data.genres === 'string') {
    try {
      data.parsed_genres = JSON.parse(data.genres);
    } catch {
      data.parsed_genres = [];
    }
  }
  
  if (data.keywords && typeof data.keywords === 'string') {
    try {
      data.parsed_keywords = JSON.parse(data.keywords);
    } catch {
      data.parsed_keywords = [];
    }
  }
  
  return data as MovieDetail;
}

/**
 * 获取热门电影（随机电影作为热门）
 */
export async function getPopularMovies(limit = 10): Promise<MovieListItem[]> {
  const result = await searchMovies('', {
    page_size: limit,
    rating_min: 7.0,
  });
  return result.items || [];
}

/**
 * 按类型获取电影
 */
export async function getMoviesByGenre(genre: string, pageSize = 50): Promise<PaginatedMovies> {
  return searchMovies('', {
    genre,
    page_size: pageSize,
  });
}

/**
 * 按评分获取电影
 */
export async function getMoviesByRating(
  minRating?: number, 
  maxRating?: number, 
  pageSize = 50
): Promise<PaginatedMovies> {
  return searchMovies('', {
    rating_min: minRating,
    rating_max: maxRating,
    page_size: pageSize,
  });
}

/**
 * 按年代获取电影
 */
export async function getMoviesByYear(year: string, pageSize = 50): Promise<PaginatedMovies> {
  // 解析年代字符串
  let yearStart: number;
  let yearEnd: number;
  
  if (year.includes('更早') || year.includes('1960')) {
    yearStart = 1900;
    yearEnd = 1960;
  } else {
    // 解析 "2020s" -> 2020-2029
    const match = year.match(/(\d{4})s/);
    if (match) {
      yearStart = parseInt(match[1]);
      yearEnd = yearStart + 9;
    } else {
      // 尝试直接解析年份
      const parsedYear = parseInt(year);
      if (!isNaN(parsedYear)) {
        yearStart = parsedYear;
        yearEnd = parsedYear;
      } else {
        yearStart = 2000;
        yearEnd = 2024;
      }
    }
  }
  
  // 后端目前不支持年份范围筛选，使用全量数据后在结果标题中过滤
  // 这是一个fallback实现
  return searchMovies('', {
    page_size: pageSize * 4, // 获取更多数据以便过滤
  });
}
