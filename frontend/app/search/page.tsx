"use client";

import Link from "next/link";
import { useState, useEffect, useCallback } from "react";
import { searchMovies, getMoviesByGenre, getMoviesByRating, getMoviesByYear, getMovies, MovieListItem } from "@/lib/api/movie";
import { recommendMovies, RecommendItem } from "@/lib/api/ai";
import { Sparkles, Search, Loader2 } from "lucide-react";
import MovieWallBackground from "@/components/MovieWallBackground";
import MovieCard from "@/components/MovieCard";

export default function SearchPage() {
  const [query, setQuery] = useState("");
  const [movies, setMovies] = useState<MovieListItem[]>([]);
  const [isLoading, setIsLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);
  const [searchMode, setSearchMode] = useState<'keyword' | 'ai'>('keyword');
  const [isSearching, setIsSearching] = useState(false);
  
  // 筛选状态
  const [selectedGenre, setSelectedGenre] = useState<string | null>(null);
  const [selectedRating, setSelectedRating] = useState<{min?: number, max?: number} | null>(null);
  const [selectedYear, setSelectedYear] = useState<string | null>(null);

  const handleSearch = useCallback(async () => {
    setIsLoading(true);
    setIsSearching(true);
    setError(null);

    try {
      if (searchMode === 'ai') {
        const result = await recommendMovies({
          query: query || "推荐好看的电影",
          max_results: 20,
        });
        
        setMovies(result.items.map((item: RecommendItem) => ({
          id: item.movie_id,
          title: item.title,
          poster_path: null,
          vote_average: item.relevance_score * 10,
          popularity: item.relevance_score * 100,
          release_date: null,
          genres: [],
          director: null,
        })));
      } else {
        // 如果有筛选条件，使用筛选API
        if (selectedGenre || selectedRating || selectedYear) {
          // 使用 searchMovies API，支持多种筛选条件组合
          const genreEn = selectedGenre ? (genreMap[selectedGenre] || selectedGenre) : undefined;
          const yearRange = selectedYear ? yearMap[selectedYear] : undefined;
          
          const result = await searchMovies("", {
            genre: genreEn,
            rating_min: selectedRating?.min,
            rating_max: selectedRating?.max,
            year_min: yearRange?.min,
            year_max: yearRange?.max,
            page_size: 50,
          });
          setMovies(result.items);
        } else if (query.trim()) {
          const result = await searchMovies(query);
          setMovies(result.items);
        } else {
          // 无筛选条件时显示全部电影 - 使用 getMovies API
          const result = await getMovies(1, 50);
          setMovies(result.items);
        }
      }
    } catch (err) {
      console.error("搜索失败:", err);
      setError("搜索失败，请检查后端服务是否运行");
      setMovies([]);
    } finally {
      setIsLoading(false);
      setIsSearching(false);
    }
  }, [query, searchMode, selectedGenre, selectedRating, selectedYear]);

  // 防抖搜索
  useEffect(() => {
    const timer = setTimeout(() => {
      handleSearch();
    }, 500);

    return () => clearTimeout(timer);
  }, [query, searchMode, selectedGenre, selectedRating, selectedYear, handleSearch]);

  // 清除所有筛选
  const clearFilters = () => {
    setSelectedGenre(null);
    setSelectedRating(null);
    setSelectedYear(null);
    setQuery("");
  };

  // 类型映射：中文->英文（用于API请求）
  const genreMap: Record<string, string> = {
    "动作": "Action",
    "喜剧": "Comedy",
    "科幻": "Science Fiction",
    "爱情": "Romance",
    "悬疑": "Mystery",
    "动画": "Animation",
    "恐怖": "Horror",
    "冒险": "Adventure",
    "奇幻": "Fantasy",
    "惊悚": "Thriller",
    "战争": "War",
    "纪录": "Documentary",
    "家庭": "Family",
    "剧情": "Drama",
    "Music": "Music",
    "Western": "Western",
    "History": "History",
    "Science Fiction": "Science Fiction",
    "TV Movie": "TV Movie",
  };

  // 年代映射：标签->年份范围
  const yearMap: Record<string, {min: number, max: number}> = {
    "2020s": { min: 2020, max: 2029 },
    "2010s": { min: 2010, max: 2019 },
    "2000s": { min: 2000, max: 2009 },
    "1990s": { min: 1990, max: 1999 },
    "1980s": { min: 1980, max: 1989 },
    "1970s": { min: 1970, max: 1979 },
    "1960s": { min: 1960, max: 1969 },
    "更早": { min: 1900, max: 1959 },
  };

  // 类型标签点击（同一维度只选一个，但不同维度可多选）
  const handleGenreClick = (genre: string) => {
    if (genre === '全部') {
      setSelectedGenre(null);
    } else {
      // 同一维度选一个：选新标签替换旧标签
      setSelectedGenre(selectedGenre === genre ? null : genre);
    }
    setQuery("");
    setSearchMode('keyword');
  };

  // 评分标签点击（同一维度只选一个，但不同维度可多选）
  const handleRatingClick = (min?: number, max?: number) => {
    // 检查是否已选中当前评分
    const isSame = selectedRating?.min === min && selectedRating?.max === max;
    setSelectedRating(isSame ? null : { min, max });
    setQuery("");
    setSearchMode('keyword');
  };

  // 年代标签点击（同一维度只选一个，但不同维度可多选）
  const handleYearClick = (year: string) => {
    // 同一维度选一个：选新标签替换旧标签
    setSelectedYear(selectedYear === year ? null : year);
    setQuery("");
    setSearchMode('keyword');
  };

  // 获取有海报的电影用于背景（从已有电影中筛选）
  const backgroundPosters = movies.filter(m => m.poster_path).slice(0, 10);

  return (
    <div className="relative min-h-screen bg-[#0a0a0f] overflow-hidden">
      {/* 使用可复用的电影墙背景组件 */}
      <MovieWallBackground darkness="heavy" />

      <main className="relative z-10 flex min-h-screen flex-col px-4 pb-20 pt-4">
        {/* 导航 */}
        <header className="mx-auto mb-8 w-full max-w-7xl">
          <div className="flex items-center justify-between">
            <Link href="/" className="flex items-center gap-3">
              <div className="flex h-10 w-10 items-center justify-center rounded-xl bg-gradient-to-br from-red-600 to-red-700">
                <Sparkles className="h-5 w-5 text-white" />
              </div>
              <span className="text-xl font-bold tracking-tight text-white">
                Movie<span className="text-red-500">AI</span>
              </span>
            </Link>
            <div className="flex items-center gap-4">
              <Link href="/profile" className="text-sm text-white/70 hover:text-white">
                个人中心
              </Link>
              <Link 
                href="/auth/login" 
                className="rounded-lg bg-gradient-to-r from-red-600 to-rose-600 px-4 py-2 text-sm font-bold text-white shadow-lg shadow-red-900/50 hover:brightness-110 active:scale-95 transition-all"
              >
                登录
              </Link>
            </div>
          </div>
        </header>

        {/* 搜索区域 */}
        <div className="mx-auto mb-8 w-full max-w-3xl">
          <div className="relative">
            <Search className="absolute left-4 top-1/2 h-5 w-5 -translate-y-1/2 text-white/40" />
            <input
              type="text"
              value={query}
              onChange={(e) => setQuery(e.target.value)}
              placeholder={searchMode === 'ai' ? "用自然语言描述你想要的电影..." : "搜索电影、导演、类型..."}
              className="w-full rounded-xl border border-white/10 bg-white/5 py-4 pl-12 pr-4 text-white placeholder-white/30 backdrop-blur focus:border-red-500/50 focus:outline-none focus:ring-2 focus:ring-red-500/20 transition-all"
            />
            {isLoading && (
              <div className="absolute right-4 top-1/2 -translate-y-1/2">
                <Loader2 className="h-5 w-5 animate-spin text-red-500" />
              </div>
            )}
          </div>

          {/* 搜索模式切换 */}
          <div className="mt-4 flex items-center gap-4">
            <button
              onClick={() => setSearchMode('keyword')}
              className={`rounded-lg px-4 py-2 text-sm font-bold transition-colors shadow-lg ${
                searchMode === 'keyword'
                  ? 'bg-gradient-to-r from-red-600 to-rose-600 text-white shadow-red-900/50 hover:brightness-110 active:scale-95'
                  : 'bg-white/5 text-white/50 hover:bg-white/10 hover:text-white'
              }`}
            >
              关键词搜索
            </button>
            <button
              onClick={() => setSearchMode('ai')}
              className={`rounded-lg px-4 py-2 text-sm font-bold transition-colors shadow-lg flex items-center gap-2 ${
                searchMode === 'ai'
                  ? 'bg-gradient-to-r from-purple-600 to-purple-700 text-white shadow-purple-900/50 hover:brightness-110 active:scale-95'
                  : 'bg-white/5 text-white/50 hover:bg-white/10 hover:text-white'
              }`}
            >
              <Sparkles className="h-4 w-4" />
              AI 智能推荐
            </button>
          </div>

          {/* 类型筛选标签 */}
          <div className="mt-4">
            <div className="mb-2 flex items-center justify-between">
              <span className="text-xs text-white/40">类型</span>
              {(selectedGenre || selectedRating || selectedYear) && (
                <button 
                  onClick={clearFilters}
                  className="text-xs text-red-400 hover:text-red-300"
                >
                  清除筛选
                </button>
              )}
            </div>
            <div className="flex flex-wrap gap-2">
              {["全部", "动作", "喜剧", "科幻", "爱情", "悬疑", "动画", "恐怖", "冒险", "奇幻", "惊悚", "战争", "纪录", "家庭", "剧情", "Romance", "Music", "Western", "History", "Mystery", "Science Fiction", "TV Movie"].map((tag) => (
                <button
                  key={tag}
                  onClick={() => handleGenreClick(tag === '全部' ? '全部' : tag)}
                  className={`rounded-full border px-3 py-1 text-xs transition-all ${
                    (tag === '全部' && !selectedGenre) || selectedGenre === tag
                      ? 'border-red-500 bg-red-500/20 text-white'
                      : 'border-white/10 bg-white/5 text-white/50 hover:border-red-500/50 hover:text-white'
                  }`}
                >
                  {tag}
                </button>
              ))}
            </div>
          </div>

          {/* 评分筛选标签 */}
          <div className="mt-4">
            <div className="mb-2 text-xs text-white/40">评分</div>
            <div className="flex flex-wrap gap-2">
              {[
                { label: "9+", min: 9 },
                { label: "8-9分", min: 8, max: 9 },
                { label: "7-8分", min: 7, max: 8 },
                { label: "6-7分", min: 6, max: 7 },
                { label: "6分以下", max: 6 }
              ].map((item) => (
                <button
                  key={item.label}
                  onClick={() => handleRatingClick(item.min, item.max)}
                  className={`rounded-full border px-3 py-1 text-xs transition-all ${
                    selectedRating?.min === item.min && selectedRating?.max === item.max
                      ? 'border-yellow-500 bg-yellow-500/20 text-yellow-400'
                      : 'border-white/10 bg-white/5 text-white/50 hover:border-yellow-500/50 hover:text-yellow-400'
                  }`}
                >
                  {item.label}
                </button>
              ))}
            </div>
          </div>

          {/* 年代筛选标签 */}
          <div className="mt-4">
            <div className="mb-2 text-xs text-white/40">年代</div>
            <div className="flex flex-wrap gap-2">
              {["2020s", "2010s", "2000s", "1990s", "1980s", "1970s", "1960s", "更早"].map((decade) => (
                <button
                  key={decade}
                  onClick={() => handleYearClick(decade)}
                  className={`rounded-full border px-3 py-1 text-xs transition-all ${
                    selectedYear === decade
                      ? 'border-emerald-500 bg-emerald-500/20 text-emerald-400'
                      : 'border-white/10 bg-white/5 text-white/50 hover:border-emerald-500/50 hover:text-emerald-400'
                  }`}
                >
                  {decade}
                </button>
              ))}
            </div>
          </div>
        </div>

        {/* 错误提示 */}
        {error && (
          <div className="mx-auto mb-4 w-full max-w-3xl rounded-lg bg-red-500/20 border border-red-500/30 px-4 py-3 text-red-300">
            {error}
          </div>
        )}

        {/* 搜索结果 */}
        <div className="mx-auto w-full max-w-7xl">
          <div className="mb-6">
            <h2 className="text-2xl font-bold text-white">
              {searchMode === 'ai' ? 'AI 推荐结果' : '搜索结果'}
            </h2>
            <p className="text-sm text-white/50">
              {query ? (
                <>找到 {movies.length} 部相关电影</>
              ) : (
                "选择类型或输入关键词开始搜索"
              )}
            </p>
          </div>

          {/* 电影列表 - 使用MovieCard组件 */}
          {movies.length > 0 ? (
            <div className="grid gap-6 sm:grid-cols-2 md:grid-cols-3 lg:grid-cols-4 xl:grid-cols-5">
              {movies.map((movie) => (
                <MovieCard key={movie.id} movie={movie} />
              ))}
            </div>
          ) : !isLoading && query && (
            <div className="text-center text-white/50 py-12">
              <div className="mx-auto mb-4 h-16 w-16 rounded-full bg-white/5 flex items-center justify-center">
                <Search className="h-8 w-8 text-white/30" />
              </div>
              <p>未找到相关电影</p>
              <p className="mt-2 text-sm text-white/30">试试其他关键词，或切换到 AI 智能推荐</p>
            </div>
          )}
        </div>

        {/* AI 助手悬浮按钮 */}
        <Link
          href="/chat"
          className="fixed bottom-6 right-6 flex h-14 w-14 items-center justify-center rounded-full bg-gradient-to-r from-red-600 to-rose-600 shadow-lg shadow-red-900/50 transition-all hover:scale-110 hover:shadow-red-600/50 hover:brightness-110 active:scale-95"
        >
          <Sparkles className="h-6 w-6 text-white" />
        </Link>
      </main>
    </div>
  );
}
