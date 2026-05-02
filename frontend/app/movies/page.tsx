"use client";

import Link from "next/link";
import { useState, useEffect, useCallback, useRef } from "react";
import { useSearchParams } from "next/navigation";
import { searchMovies, MovieListItem, PaginatedMovies } from "@/lib/api/movie";
import { Sparkles, Play, Loader2, Clapperboard, Star } from "lucide-react";

// 排序选项
const SORT_OPTIONS = [
  { label: "综合排序", value: "" },
  { label: "评分最高", value: "rating" },
  { label: "最受欢迎", value: "popular" },
  { label: "票房最高", value: "boxoffice" },
];

// 电影类型标签（使用英文，与数据库genres字段匹配）
const GENRE_TAGS = [
  "全部", "Action", "Comedy", "Drama", "Science Fiction", "Romance", "Thriller", "Horror", 
  "Crime", "Animation", "Adventure", "Fantasy", "Documentary", "Family"
];

// 评分标签
const RATING_TAGS = [
  { label: "全部评分", value: 0 },
  { label: "9分+", value: 9 },
  { label: "8分+", value: 8 },
  { label: "7分+", value: 7 },
  { label: "6分+", value: 6 },
];

// 年份标签
const YEAR_TAGS = [
  { label: "全部年代", value: 0 },
  { label: "2020后", value: 2020 },
  { label: "2010后", value: 2010 },
  { label: "2000后", value: 2000 },
  { label: "90年代", value: 1990 },
  { label: "更早", value: 1980 },
];

export default function MoviesPage() {
  const searchParams = useSearchParams();
  const [movies, setMovies] = useState<MovieListItem[]>([]);
  const [isLoading, setIsLoading] = useState(true);
  const [isLoadingMore, setIsLoadingMore] = useState(false);
  const [error, setError] = useState<string | null>(null);
  
  // 分页
  const [page, setPage] = useState(1);
  const [totalPages, setTotalPages] = useState(1);
  const [total, setTotal] = useState(0);
  
  // 筛选 - 单选模式（同一维度只能选一个，不同维度可混合）
  const [selectedGenre, setSelectedGenre] = useState<string | null>(null);
  const [selectedRating, setSelectedRating] = useState<number | null>(null);
  const [selectedYear, setSelectedYear] = useState<number | null>(null);
  const [selectedSort, setSelectedSort] = useState(searchParams.get("sort") || "");
  
  // 加载锁
  const loadingRef = useRef(false);
  
  // 用于虚化背景的电影海报（取前8张）
  const backgroundMovies = movies.slice(0, 8);

  // 单选切换函数
  const handleGenreSelect = (genre: string | null) => {
    setSelectedGenre(prev => prev === genre ? null : genre);
  };

  const handleRatingSelect = (rating: number | null) => {
    if (rating === 0 || rating === null) {
      setSelectedRating(null);
    } else {
      setSelectedRating(prev => prev === rating ? null : rating);
    }
  };

  const handleYearSelect = (year: number | null) => {
    if (year === 0 || year === null) {
      setSelectedYear(null);
    } else {
      setSelectedYear(prev => prev === year ? null : year);
    }
  };

  // 加载电影列表
  const loadMovies = useCallback(async (pageNum: number, append = false) => {
    if (loadingRef.current) return;
    loadingRef.current = true;
    
    if (append) {
      setIsLoadingMore(true);
    } else {
      setIsLoading(true);
    }
    setError(null);

    try {
      // 构建筛选参数
      const options: any = {
        page: pageNum,
        page_size: 24,
      };
      
      // 类型筛选（单选）
      if (selectedGenre) {
        options.genres = selectedGenre;
      }
      
      // 评分筛选（单选，取最低评分）
      if (selectedRating !== null && selectedRating > 0) {
        options.rating_min = selectedRating;
      }
      
      // 年份筛选（单选）
      if (selectedYear !== null && selectedYear > 0) {
        if (selectedYear === 1980) {
          // "更早" 表示1980年之前
          options.year_max = 1979;
        } else {
          // 其他按年代筛选
          const yearStart = selectedYear;
          options.year_min = yearStart;
          if (selectedYear === 1990) {
            options.year_max = 1999;
          }
        }
      }
      
      // 排序
      if (selectedSort) {
        options.sort = selectedSort;
      }
      
      // 调用后端筛选API
      const result = await searchMovies('*', options);
      
      if (append) {
        setMovies(prev => [...prev, ...result.items]);
      } else {
        setMovies(result.items);
      }
      setTotalPages(result.total_pages);
      setTotal(result.total);
      setPage(pageNum);
    } catch (err) {
      console.error("加载电影失败:", err);
      setError("加载失败，请检查后端服务是否运行");
    } finally {
      setIsLoading(false);
      setIsLoadingMore(false);
      loadingRef.current = false;
    }
  }, [selectedGenre, selectedRating, selectedYear, selectedSort]);

  // 初始加载
  useEffect(() => {
    loadMovies(1);
  }, [loadMovies]);

  // 筛选变化时重新加载
  useEffect(() => {
    loadMovies(1);
  }, [selectedGenre, selectedRating, selectedYear, selectedSort, loadMovies]);

  // 加载更多
  const handleLoadMore = () => {
    if (page < totalPages && !isLoadingMore) {
      loadMovies(page + 1, true);
    }
  };

  // 滚动到底部检测
  useEffect(() => {
    const handleScroll = () => {
      if (
        window.innerHeight + window.scrollY >= document.body.offsetHeight - 500 &&
        page < totalPages &&
        !isLoadingMore &&
        !isLoading
      ) {
        handleLoadMore();
      }
    };

    window.addEventListener('scroll', handleScroll);
    return () => window.removeEventListener('scroll', handleScroll);
  }, [page, totalPages, isLoadingMore, isLoading]);

  return (
    <div className="relative min-h-screen bg-[#0a0a0f] overflow-hidden">
      {/* 虚化电影海报背景层 - Netflix风格 */}
      <div className="fixed inset-0 overflow-hidden pointer-events-none z-0">
        {/* 海报网格背景 - 提高透明度确保可见 */}
        <div 
          className="absolute inset-0 grid gap-1 opacity-40"
          style={{
            gridTemplateColumns: 'repeat(8, 1fr)',
            gridTemplateRows: 'repeat(4, 1fr)',
            transform: 'scale(1.1)',
            transformOrigin: 'center center',
            filter: 'blur(3px) saturate(0.7)',
          }}
        >
          {[...backgroundMovies, ...backgroundMovies, ...backgroundMovies].slice(0, 32).map((movie, index) => (
            <div
              key={`movie-bg-${movie.id}-${index}`}
              className="relative overflow-hidden"
              style={{
                aspectRatio: '2/3',
                opacity: 0.6 + (Math.sin(index * 1.3) * 0.2),
              }}
            >
              {movie.poster_path ? (
                <img
                  src={`https://image.tmdb.org/t/p/w300${movie.poster_path}`}
                  alt=""
                  className="w-full h-full object-cover"
                />
              ) : (
                // 无海报时的渐变背景
                <div className="w-full h-full bg-gradient-to-br from-gray-800 to-gray-900" />
              )}
            </div>
          ))}
        </div>
        
        {/* 渐变遮罩确保内容可读 - 调整遮罩强度 */}
        <div className="absolute inset-0 bg-gradient-to-b from-[#0a0a0f] via-[#0a0a0f]/60 to-[#0a0a0f]" />
        
        {/* 顶部光晕 */}
        <div className="absolute -top-20 -right-20 h-60 w-60 rounded-full bg-red-600/15 blur-3xl" />
        <div className="absolute top-1/4 -left-20 h-48 w-48 rounded-full bg-purple-500/10 blur-3xl" />
        
        {/* 底部光晕 */}
        <div className="absolute bottom-0 left-0 right-0 h-32 bg-gradient-to-t from-[#0a0a0f] to-transparent" />
      </div>

      <main className="relative z-10 flex min-h-screen flex-col px-4 pb-20">
        {/* 导航 */}
        <header className="mx-auto mb-6 w-full max-w-7xl pt-4">
          <div className="flex items-center justify-between">
            <Link href="/" className="flex items-center gap-3">
              <div className="flex h-10 w-10 items-center justify-center rounded-xl bg-gradient-to-br from-red-600 to-red-700">
                <Clapperboard className="h-5 w-5 text-white" />
              </div>
              <span className="text-xl font-bold tracking-tight text-white">
                Movie<span className="text-red-500">AI</span>
              </span>
            </Link>
            <div className="flex items-center gap-4">
              <Link href="/" className="text-sm text-white/70 hover:text-white">
                首页
              </Link>
              <Link href="/movies" className="text-sm text-white font-medium">
                电影
              </Link>
              <Link href="/profile" className="text-sm text-white/70 hover:text-white">
                个人中心
              </Link>
            </div>
          </div>
        </header>

        {/* 页面标题 */}
        <div className="mx-auto mb-6 w-full max-w-7xl">
          <h1 className="text-3xl font-bold text-white">电影库</h1>
          <p className="mt-1 text-sm text-white/50">
            共 {total.toLocaleString()} 部电影
          </p>
        </div>

        {/* 筛选区域 */}
        <div className="mx-auto mb-6 w-full max-w-7xl">
          {/* 排序选项 */}
          <div className="mb-4">
            <h3 className="mb-2 text-sm text-white/50">排序</h3>
            <div className="flex flex-wrap gap-2">
              {SORT_OPTIONS.map((option) => (
                <button
                  key={option.value}
                  onClick={() => setSelectedSort(option.value)}
                  className={`rounded-full px-4 py-1.5 text-sm transition-all ${
                    selectedSort === option.value
                      ? 'bg-gradient-to-r from-purple-500 to-pink-500 text-white'
                      : 'bg-white/5 text-white/50 hover:bg-white/10 hover:text-white border border-white/10'
                  }`}
                >
                  {option.label}
                </button>
              ))}
            </div>
          </div>

          {/* 类型筛选 */}
          <div className="mb-4">
            <h3 className="mb-2 text-sm text-white/50">类型</h3>
            <div className="flex flex-wrap gap-2">
              {GENRE_TAGS.filter(g => g === "全部" || g === selectedGenre || !selectedGenre).map((genre) => {
                const isActive = genre === "全部" ? !selectedGenre : selectedGenre === genre;
                return (
                  <button
                    key={genre}
                    onClick={() => handleGenreSelect(genre === "全部" ? null : genre)}
                    className={`rounded-full px-4 py-1.5 text-sm transition-all ${
                      isActive
                        ? 'bg-gradient-to-r from-red-600 to-red-700 text-white'
                        : 'bg-white/5 text-white/50 hover:bg-white/10 hover:text-white border border-white/10'
                    }`}
                  >
                    {genre}
                  </button>
                );
              })}
            </div>
          </div>

          {/* 评分筛选 */}
          <div className="mb-4">
            <h3 className="mb-2 text-sm text-white/50">评分</h3>
            <div className="flex flex-wrap gap-2">
              {RATING_TAGS.map((tag) => {
                const isActive = tag.value === 0 ? !selectedRating : selectedRating === tag.value;
                return (
                  <button
                    key={tag.value}
                    onClick={() => handleRatingSelect(tag.value)}
                    className={`rounded-full px-4 py-1.5 text-sm transition-all ${
                      isActive
                        ? 'bg-gradient-to-r from-yellow-500 to-orange-500 text-black font-medium'
                        : 'bg-white/5 text-white/50 hover:bg-white/10 hover:text-white border border-white/10'
                    }`}
                  >
                    {tag.label}
                  </button>
                );
              })}
            </div>
          </div>

          {/* 年份筛选 */}
          <div>
            <h3 className="mb-2 text-sm text-white/50">年代</h3>
            <div className="flex flex-wrap gap-2">
              {YEAR_TAGS.map((tag) => {
                const isActive = tag.value === 0 ? !selectedYear : selectedYear === tag.value;
                return (
                  <button
                    key={tag.value}
                    onClick={() => handleYearSelect(tag.value)}
                    className={`rounded-full px-4 py-1.5 text-sm transition-all ${
                      isActive
                        ? 'bg-gradient-to-r from-emerald-500 to-teal-500 text-white'
                        : 'bg-white/5 text-white/50 hover:bg-white/10 hover:text-white border border-white/10'
                    }`}
                  >
                    {tag.label}
                  </button>
                );
              })}
            </div>
          </div>
        </div>

        {/* 错误提示 */}
        {error && (
          <div className="mx-auto mb-4 w-full max-w-7xl rounded-lg bg-red-500/20 border border-red-500/30 px-4 py-3 text-red-300">
            {error}
          </div>
        )}

        {/* 电影网格 */}
        <div className="mx-auto w-full max-w-7xl">
          {isLoading ? (
            // 加载骨架屏
            <div className="grid gap-4 sm:grid-cols-2 md:grid-cols-3 lg:grid-cols-4 xl:grid-cols-6">
              {Array.from({ length: 24 }).map((_, i) => (
                <div key={i} className="rounded-xl border border-white/5 bg-white/3 p-2 animate-pulse">
                  <div className="aspect-[2/3] rounded-lg bg-white/5" />
                  <div className="mt-2 h-4 w-3/4 rounded bg-white/5" />
                  <div className="mt-1 h-3 w-1/2 rounded bg-white/5" />
                </div>
              ))}
            </div>
          ) : movies.length > 0 ? (
            <>
              <div className="grid gap-4 sm:grid-cols-2 md:grid-cols-3 lg:grid-cols-4 xl:grid-cols-6">
                {movies.map((movie) => (
                  <Link 
                    key={movie.id} 
                    href={`/movies/${movie.id}`}
                    className="group relative rounded-xl border border-white/10 bg-white/5 overflow-hidden transition-all hover:border-red-500/50 hover:bg-white/10 hover:scale-105"
                  >
                    <div className="aspect-[2/3] relative">
                      {movie.poster_path ? (
                        <img 
                          src={`https://image.tmdb.org/t/p/w500${movie.poster_path}`}
                          alt={movie.title}
                          className="h-full w-full object-cover transition-transform duration-300 group-hover:scale-110"
                          loading="lazy"
                        />
                      ) : (
                        <div className="flex h-full w-full items-center justify-center bg-white/10">
                          <Clapperboard className="h-12 w-12 text-white/30" />
                        </div>
                      )}
                      {/* 悬停遮罩 */}
                      <div className="absolute inset-0 bg-gradient-to-t from-black/80 via-black/20 to-transparent opacity-0 group-hover:opacity-100 transition-opacity" />
                      {/* 评分 */}
                      {movie.vote_average && movie.vote_average > 0 && (
                        <div className="absolute top-2 right-2 flex items-center gap-1 rounded-full bg-black/60 px-2 py-1 backdrop-blur">
                          <Star className="h-3 w-3 fill-yellow-400 text-yellow-400" />
                          <span className="text-xs font-medium text-white">
                            {movie.vote_average.toFixed(1)}
                          </span>
                        </div>
                      )}
                      {/* 悬停播放图标 */}
                      <div className="absolute inset-0 flex items-center justify-center opacity-0 group-hover:opacity-100 transition-opacity">
                        <div className="h-12 w-12 rounded-full bg-red-600/90 backdrop-blur flex items-center justify-center shadow-lg">
                          <Play className="h-6 w-6 text-white ml-1" />
                        </div>
                      </div>
                    </div>
                    <div className="p-3">
                      <h3 className="mb-1 truncate text-sm font-medium text-white group-hover:text-red-400 transition-colors">
                        {movie.title}
                      </h3>
                      <div className="flex items-center justify-between text-xs text-white/50">
                        <span>{movie.release_date?.split('-')[0] || '未知'}</span>
                        {movie.genres && movie.genres.length > 0 && (
                          <span className="text-red-400/70 truncate max-w-[50%]">{movie.genres[0]}</span>
                        )}
                      </div>
                    </div>
                  </Link>
                ))}
              </div>

              {/* 加载更多提示 */}
              {isLoadingMore && (
                <div className="mt-8 flex items-center justify-center">
                  <Loader2 className="h-6 w-6 animate-spin text-red-500" />
                  <span className="ml-2 text-white/50">加载更多...</span>
                </div>
              )}

              {/* 到底提示 */}
              {!isLoadingMore && page >= totalPages && movies.length > 0 && (
                <div className="mt-8 text-center text-white/30">
                  已加载全部 {movies.length} 部电影
                </div>
              )}
            </>
          ) : (
            <div className="text-center text-white/50 py-20">
              <div className="mx-auto mb-4 h-16 w-16 rounded-full bg-white/5 flex items-center justify-center">
                <Clapperboard className="h-8 w-8 text-white/30" />
              </div>
              <p>暂无符合条件的电影</p>
              <p className="mt-2 text-sm text-white/30">试试调整筛选条件</p>
            </div>
          )}
        </div>

        {/* AI 助手悬浮按钮 */}
        <Link
          href="/chat"
          className="fixed bottom-6 right-6 flex h-14 w-14 items-center justify-center rounded-full bg-gradient-to-r from-red-600 to-red-700 shadow-lg shadow-red-500/25 transition-all hover:scale-105 hover:shadow-red-500/50"
        >
          <Sparkles className="h-6 w-6 text-white" />
        </Link>
      </main>
    </div>
  );
}
