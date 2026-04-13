"use client";

import Link from "next/link";
import { useState, useEffect, useCallback } from "react";
import { searchMovies, MovieListItem } from "@/lib/api/movie";
import { recommendMovies, RecommendItem } from "@/lib/api/ai";

export default function SearchPage() {
  const [query, setQuery] = useState("");
  const [movies, setMovies] = useState<MovieListItem[]>([]);
  const [isLoading, setIsLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);
  const [searchMode, setSearchMode] = useState<'keyword' | 'ai'>('keyword');

  const handleSearch = useCallback(async () => {
    if (!query.trim()) {
      setMovies([]);
      return;
    }

    setIsLoading(true);
    setError(null);

    try {
      if (searchMode === 'ai') {
        // AI推荐模式
        const result = await recommendMovies({
          query: query,
          max_results: 20,
        });
        
        // 转换为 MovieListItem 格式（需要获取详细信息）
        // 这里暂时只显示推荐结果的基本信息
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
        // 关键词搜索模式
        const result = await searchMovies(query);
        setMovies(result.items);
      }
    } catch (err) {
      console.error("搜索失败:", err);
      setError("搜索失败，请检查后端服务是否运行");
      setMovies([]);
    } finally {
      setIsLoading(false);
    }
  }, [query, searchMode]);

  // 防抖搜索
  useEffect(() => {
    const timer = setTimeout(() => {
      if (query.trim()) {
        handleSearch();
      }
    }, 500);

    return () => clearTimeout(timer);
  }, [query, handleSearch]);

  const handleTagClick = (tag: string) => {
    setQuery(tag);
    setSearchMode('keyword');
  };

  return (
    <div className="relative min-h-screen bg-gradient-to-br from-slate-950 via-slate-950 to-slate-900">
      {/* 背景装饰 */}
      <div className="fixed inset-0 overflow-hidden">
        <div className="absolute -top-40 -right-40 h-80 w-80 rounded-full bg-emerald-500/10 blur-3xl" />
        <div className="absolute top-1/3 -left-40 h-64 w-64 rounded-full bg-blue-500/10 blur-3xl" />
      </div>

      <main className="relative z-10 flex min-h-screen flex-col px-4 pb-20 pt-4 text-slate-50 sm:px-6 lg:px-8">
        {/* 导航 */}
        <header className="mx-auto mb-8 w-full max-w-7xl">
          <div className="flex items-center justify-between">
            <Link href="/" className="flex items-center gap-3">
              <div className="h-8 w-8 rounded-lg bg-gradient-to-br from-emerald-500 to-emerald-600" />
              <h1 className="text-xl font-bold tracking-tight text-white">
                Movie<span className="text-emerald-400">AI</span>
              </h1>
            </Link>
            <div className="flex items-center gap-4">
              <Link href="/search" className="text-sm text-emerald-400">
                搜索
              </Link>
              <Link 
                href="/auth/login" 
                className="rounded-lg bg-emerald-500 px-4 py-2 text-sm font-medium text-white hover:bg-emerald-600"
              >
                登录
              </Link>
            </div>
          </div>
        </header>

        {/* 搜索区域 */}
        <div className="mx-auto mb-8 w-full max-w-3xl">
          <div className="relative">
            <svg 
              className="absolute left-4 top-1/2 h-5 w-5 -translate-y-1/2 text-slate-400" 
              fill="none" 
              stroke="currentColor" 
              viewBox="0 0 24 24"
            >
              <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M21 21l-6-6m2-5a7 7 0 11-14 0 7 7 0 0114 0z" />
            </svg>
            <input
              type="text"
              value={query}
              onChange={(e) => setQuery(e.target.value)}
              placeholder={searchMode === 'ai' ? "用自然语言描述你想要的电影..." : "搜索电影、导演、类型..."}
              className="w-full rounded-xl border border-slate-700 bg-slate-800/50 py-4 pl-12 pr-4 text-white placeholder-slate-400 backdrop-blur focus:border-emerald-500 focus:outline-none"
            />
            {isLoading && (
              <div className="absolute right-4 top-1/2 -translate-y-1/2">
                <div className="h-5 w-5 animate-spin rounded-full border-2 border-emerald-500 border-t-transparent" />
              </div>
            )}
          </div>

          {/* 搜索模式切换 */}
          <div className="mt-4 flex items-center gap-4">
            <button
              onClick={() => setSearchMode('keyword')}
              className={`rounded-lg px-4 py-2 text-sm font-medium transition-colors ${
                searchMode === 'keyword'
                  ? 'bg-emerald-500 text-white'
                  : 'bg-slate-800 text-slate-400 hover:bg-slate-700'
              }`}
            >
              关键词搜索
            </button>
            <button
              onClick={() => setSearchMode('ai')}
              className={`rounded-lg px-4 py-2 text-sm font-medium transition-colors ${
                searchMode === 'ai'
                  ? 'bg-emerald-500 text-white'
                  : 'bg-slate-800 text-slate-400 hover:bg-slate-700'
              }`}
            >
              AI 智能推荐
            </button>
          </div>

          {/* 筛选标签 */}
          <div className="mt-4 flex flex-wrap gap-2">
            {["动作", "喜剧", "科幻", "爱情", "悬疑", "动画", "恐怖", "冒险"].map((tag) => (
              <button
                key={tag}
                onClick={() => handleTagClick(tag)}
                className="rounded-full border border-slate-700 px-4 py-1.5 text-sm text-slate-400 hover:border-emerald-500 hover:text-emerald-400"
              >
                {tag}
              </button>
            ))}
          </div>
        </div>

        {/* 错误提示 */}
        {error && (
          <div className="mx-auto mb-4 w-full max-w-3xl rounded-lg bg-red-500/20 border border-red-500/50 px-4 py-3 text-red-400">
            {error}
          </div>
        )}

        {/* 搜索结果 */}
        <div className="mx-auto w-full max-w-7xl">
          <div className="mb-6">
            <h2 className="text-2xl font-bold text-white">
              {searchMode === 'ai' ? 'AI 推荐结果' : '搜索结果'}
            </h2>
            <p className="text-sm text-slate-400">
              {query ? (
                <>找到 {movies.length} 部相关电影</>
              ) : (
                "选择类型或输入关键词开始搜索"
              )}
            </p>
          </div>

          {/* 电影列表 */}
          {movies.length > 0 ? (
            <div className="grid gap-6 sm:grid-cols-2 md:grid-cols-3 lg:grid-cols-4 xl:grid-cols-5">
              {movies.map((movie) => (
                <Link 
                  key={movie.id} 
                  href={`/movies/${movie.id}`}
                  className="group rounded-xl border border-slate-800 bg-slate-900/50 overflow-hidden transition-colors hover:border-emerald-500/50"
                >
                  <div className="aspect-[2/3] bg-slate-800">
                    {movie.poster_path ? (
                      <img 
                        src={`https://image.tmdb.org/t/p/w500${movie.poster_path}`}
                        alt={movie.title}
                        className="h-full w-full object-cover"
                      />
                    ) : (
                      <div className="flex h-full w-full items-center justify-center text-slate-600">
                        <svg className="h-12 w-12" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                          <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M7 4v16M17 4v16M3 8h4m10 0h4M3 12h18M3 16h4m10 0h4M4 20h16a1 1 0 001-1V5a1 1 0 00-1-1H4a1 1 0 00-1 1v14a1 1 0 001 1z" />
                        </svg>
                      </div>
                    )}
                  </div>
                  <div className="p-4">
                    <h3 className="mb-1 truncate text-sm font-medium text-white group-hover:text-emerald-400">
                      {movie.title}
                    </h3>
                    <div className="flex flex-wrap items-center justify-between gap-2 text-xs text-slate-500">
                      <span>{movie.release_date?.split('-')[0] || '未知'}</span>
                      {movie.vote_average && (
                        <span className="flex items-center">
                          <svg className="mr-1 h-3 w-3 text-yellow-500" fill="currentColor" viewBox="0 0 20 20">
                            <path d="M9.049 2.927c.3-.921 1.603-.921 1.902 0l1.07 3.292a1 1 0 00.95.69h3.462c.969 0 1.371 1.24.588 1.81l-2.8 2.034a1 1 0 00-.364 1.118l1.07 3.292c.3.921-.755 1.688-1.54 1.118l-2.8-2.034a1 1 0 00-1.175 0l-2.8 2.034c-.784.57-1.838-.197-1.539-1.118l1.07-3.292a1 1 0 00-.364-1.118L2.98 8.72c-.783-.57-.38-1.81.588-1.81h3.461a1 1 0 00.951-.69l1.07-3.292z" />
                          </svg>
                          {movie.vote_average.toFixed(1)}
                        </span>
                      )}
                    </div>
                    {movie.genres && movie.genres.length > 0 && (
                      <div className="mt-2 flex flex-wrap gap-1">
                        {movie.genres.slice(0, 2).map((genre, i) => (
                          <span key={i} className="rounded bg-slate-700 px-1.5 py-0.5 text-xs text-slate-400">
                            {genre}
                          </span>
                        ))}
                      </div>
                    )}
                  </div>
                </Link>
              ))}
            </div>
          ) : !isLoading && query && (
            <div className="text-center text-slate-500 py-12">
              <p>未找到相关电影</p>
              <p className="mt-2 text-sm">试试其他关键词，或切换到 AI 智能推荐</p>
            </div>
          )}
        </div>

        {/* AI 助手悬浮按钮 */}
        <Link
          href="/chat"
          className="fixed bottom-6 right-6 flex h-14 w-14 items-center justify-center rounded-full bg-emerald-500 shadow-lg shadow-emerald-500/25 transition-transform hover:scale-105"
        >
          <svg className="h-6 w-6 text-white" fill="none" stroke="currentColor" viewBox="0 0 24 24">
            <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M8 10h.01M12 10h.01M16 10h.01M9 16H5a2 2 0 01-2-2V6a2 2 0 012-2h14a2 2 0 012 2v8a2 2 0 01-2 2h-5l-5 5v-5z" />
          </svg>
        </Link>
      </main>
    </div>
  );
}
