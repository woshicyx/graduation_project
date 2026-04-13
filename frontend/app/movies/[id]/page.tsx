"use client";

import Link from "next/link";
import { useState, useEffect } from "react";
import { getMovieDetail, MovieDetail } from "@/lib/api/movie";
import { useAuth } from "@/contexts/AuthContext";
import { addWatchHistory } from "@/lib/api/history";
import FavoriteButton from "@/components/favorite-button";

interface MoviePageProps {
  params: Promise<{ id: string }>;
}

export default function MovieDetailPage({ params }: MoviePageProps) {
  const { user, isAuthenticated } = useAuth();
  const [movie, setMovie] = useState<MovieDetail | null>(null);
  const [isLoading, setIsLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);
  const [movieId, setMovieId] = useState<number | null>(null);

  useEffect(() => {
    params.then((p) => {
      setMovieId(parseInt(p.id, 10));
    });
  }, [params]);

  // 加载电影详情
  useEffect(() => {
    if (!movieId) return;

    setIsLoading(true);
    setError(null);

    getMovieDetail(movieId)
      .then((data) => {
        setMovie(data);
        setIsLoading(false);
      })
      .catch((err) => {
        console.error("获取电影详情失败:", err);
        setError("无法加载电影详情，请检查后端服务是否运行");
        setIsLoading(false);
      });
  }, [movieId]);

  // 记录浏览历史
  useEffect(() => {
    if (!movieId || !isAuthenticated || !user) return;

    addWatchHistory(movieId, user.id)
      .catch((err) => {
        console.error("记录浏览历史失败:", err);
      });
  }, [movieId, isAuthenticated, user]);

  if (isLoading) {
    return (
      <div className="relative min-h-screen bg-gradient-to-br from-slate-950 via-slate-950 to-slate-900">
        <div className="fixed inset-0 overflow-hidden">
          <div className="absolute -top-40 -right-40 h-80 w-80 rounded-full bg-emerald-500/10 blur-3xl" />
          <div className="absolute bottom-40 left-1/4 h-96 w-96 rounded-full bg-blue-500/10 blur-3xl" />
        </div>
        <div className="relative z-10 flex min-h-screen items-center justify-center">
          <div className="h-8 w-8 animate-spin rounded-full border-2 border-emerald-500 border-t-transparent" />
        </div>
      </div>
    );
  }

  if (error || !movie) {
    return (
      <div className="relative min-h-screen bg-gradient-to-br from-slate-950 via-slate-950 to-slate-900">
        <div className="fixed inset-0 overflow-hidden">
          <div className="absolute -top-40 -right-40 h-80 w-80 rounded-full bg-emerald-500/10 blur-3xl" />
          <div className="absolute bottom-40 left-1/4 h-96 w-96 rounded-full bg-blue-500/10 blur-3xl" />
        </div>
        <header className="relative z-10 border-b border-slate-800 bg-slate-950/80 backdrop-blur">
          <div className="mx-auto flex h-16 max-w-7xl items-center px-4">
            <Link href="/" className="flex items-center gap-3">
              <div className="h-8 w-8 rounded-lg bg-gradient-to-br from-emerald-500 to-emerald-600" />
              <h1 className="text-xl font-bold tracking-tight text-white">
                Movie<span className="text-emerald-400">AI</span>
              </h1>
            </Link>
          </div>
        </header>
        <div className="relative z-10 flex min-h-[calc(100vh-64px)] flex-col items-center justify-center px-4">
          <p className="text-red-400">{error || "电影不存在"}</p>
          <Link 
            href="/search"
            className="mt-4 rounded-lg bg-emerald-500 px-4 py-2 text-white hover:bg-emerald-600"
          >
            返回搜索
          </Link>
        </div>
      </div>
    );
  }

  return (
    <div className="relative min-h-screen bg-gradient-to-br from-slate-950 via-slate-950 to-slate-900">
      {/* 背景装饰 */}
      <div className="fixed inset-0 overflow-hidden">
        <div className="absolute -top-40 -right-40 h-80 w-80 rounded-full bg-emerald-500/10 blur-3xl" />
        <div className="absolute bottom-40 left-1/4 h-96 w-96 rounded-full bg-blue-500/10 blur-3xl" />
      </div>

      {/* 导航 */}
      <header className="relative z-10 border-b border-slate-800 bg-slate-950/80 backdrop-blur">
        <div className="mx-auto flex h-16 max-w-7xl items-center justify-between px-4">
          <Link href="/" className="flex items-center gap-3">
            <div className="h-8 w-8 rounded-lg bg-gradient-to-br from-emerald-500 to-emerald-600" />
            <h1 className="text-xl font-bold tracking-tight text-white">
              Movie<span className="text-emerald-400">AI</span>
            </h1>
          </Link>
          <div className="flex items-center gap-4">
            <Link href="/search" className="text-sm text-slate-300 hover:text-emerald-400">
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

      {/* 电影详情内容 */}
      <main className="relative z-10 mx-auto max-w-7xl px-4 py-8">
        {/* 面包屑导航 */}
        <div className="mb-6 flex items-center gap-2 text-sm text-slate-500">
          <Link href="/" className="hover:text-emerald-400">首页</Link>
          <span>/</span>
          <Link href="/search" className="hover:text-emerald-400">搜索</Link>
          <span>/</span>
          <span className="text-slate-400">{movie.title}</span>
        </div>

        {/* 电影信息区域 */}
        <div className="grid gap-8 lg:grid-cols-3">
          {/* 海报 */}
          <div className="lg:col-span-1">
            <div className="sticky top-8">
              <div className="aspect-[2/3] overflow-hidden rounded-2xl border border-slate-800 bg-slate-800">
                {movie.poster_path ? (
                  <img 
                    src={`https://image.tmdb.org/t/p/w500${movie.poster_path}`}
                    alt={movie.title}
                    className="h-full w-full object-cover"
                  />
                ) : (
                  <div className="flex h-full w-full items-center justify-center">
                    <svg className="h-16 w-16 text-slate-600" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                      <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M7 4v16M17 4v16M3 8h4m10 0h4M3 12h18M3 16h4m10 0h4M4 20h16a1 1 0 001-1V5a1 1 0 00-1-1H4a1 1 0 00-1 1v14a1 1 0 001 1z" />
                    </svg>
                  </div>
                )}
              </div>
              
              {/* 收藏按钮 - 集成 FavoriteButton */}
              <div className="mt-4 flex items-center gap-3">
                <FavoriteButton 
                  movieId={movieId!} 
                  size="lg" 
                  showText={true}
                  className="flex-1"
                />
              </div>
            </div>
          </div>

          {/* 电影详情 */}
          <div className="lg:col-span-2 space-y-6">
            {/* 标题区域 */}
            <div>
              <h1 className="text-3xl font-bold text-white">{movie.title}</h1>
              {movie.original_title && movie.original_title !== movie.title && (
                <p className="mt-1 text-slate-400">{movie.original_title}</p>
              )}
              {movie.tagline && (
                <p className="mt-2 italic text-emerald-400">{movie.tagline}</p>
              )}
            </div>

            {/* 基本信息 */}
            <div className="flex flex-wrap gap-4 text-sm text-slate-400">
              {movie.vote_average && (
                <span className="flex items-center gap-1">
                  <svg className="h-4 w-4 text-yellow-500" fill="currentColor" viewBox="0 0 20 20">
                    <path d="M9.049 2.927c.3-.921 1.603-.921 1.902 0l1.07 3.292a1 1 0 00.95.69h3.462c.969 0 1.371 1.24.588 1.81l-2.8 2.034a1 1 0 00-.364 1.118l1.07 3.292c.3.921-.755 1.688-1.54 1.118l-2.8-2.034a1 1 0 00-1.175 0l-2.8 2.034c-.784.57-1.838-.197-1.539-1.118l1.07-3.292a1 1 0 00-.364-1.118L2.98 8.72c-.783-.57-.38-1.81.588-1.81h3.461a1 1 0 00.951-.69l1.07-3.292z" />
                  </svg>
                  {movie.vote_average.toFixed(1)} ({movie.vote_count || 0} 人评分)
                </span>
              )}
              {movie.release_date && (
                <span>{movie.release_date.split('-')[0]}</span>
              )}
              {movie.runtime && (
                <span>{movie.runtime} 分钟</span>
              )}
              {movie.original_language && (
                <span className="uppercase">{movie.original_language}</span>
              )}
            </div>

            {/* 类型标签 */}
            {movie.parsed_genres && movie.parsed_genres.length > 0 && (
              <div className="flex flex-wrap gap-2">
                {movie.parsed_genres.map((genre, i) => (
                  <span key={i} className="rounded-full bg-emerald-500/20 border border-emerald-500/50 px-3 py-1 text-sm text-emerald-400">
                    {genre}
                  </span>
                ))}
              </div>
            )}

            {/* 剧情简介 */}
            {movie.overview && (
              <div className="rounded-xl border border-slate-800 bg-slate-900/50 p-6">
                <h2 className="mb-3 text-lg font-semibold text-white">剧情简介</h2>
                <p className="text-sm leading-relaxed text-slate-400">
                  {movie.overview}
                </p>
              </div>
            )}

            {/* 导演 */}
            {movie.director && (
              <div className="rounded-xl border border-slate-800 bg-slate-900/50 p-6">
                <h2 className="mb-3 text-lg font-semibold text-white">导演</h2>
                <p className="text-sm text-slate-400">{movie.director}</p>
              </div>
            )}

            {/* 关键词 */}
            {movie.parsed_keywords && movie.parsed_keywords.length > 0 && (
              <div className="rounded-xl border border-slate-800 bg-slate-900/50 p-6">
                <h2 className="mb-3 text-lg font-semibold text-white">关键词</h2>
                <div className="flex flex-wrap gap-2">
                  {movie.parsed_keywords.slice(0, 10).map((keyword, i) => (
                    <span key={i} className="rounded bg-slate-700 px-2 py-1 text-xs text-slate-400">
                      {keyword}
                    </span>
                  ))}
                </div>
              </div>
            )}

            {/* 制作信息 */}
            {(movie.budget || movie.revenue) && (
              <div className="rounded-xl border border-slate-800 bg-slate-900/50 p-6">
                <h2 className="mb-3 text-lg font-semibold text-white">制作信息</h2>
                <div className="grid grid-cols-2 gap-4 text-sm">
                  {movie.budget && movie.budget > 0 && (
                    <div>
                      <span className="text-slate-500">预算</span>
                      <p className="text-white">${movie.budget.toLocaleString()}</p>
                    </div>
                  )}
                  {movie.revenue && movie.revenue > 0 && (
                    <div>
                      <span className="text-slate-500">票房</span>
                      <p className="text-white">${movie.revenue.toLocaleString()}</p>
                    </div>
                  )}
                </div>
              </div>
            )}
          </div>
        </div>
      </main>

      {/* AI 助手悬浮按钮 */}
      <Link
        href="/chat"
        className="fixed bottom-6 right-6 flex h-14 w-14 items-center justify-center rounded-full bg-emerald-500 shadow-lg shadow-emerald-500/25 transition-transform hover:scale-105"
      >
        <svg className="h-6 w-6 text-white" fill="none" stroke="currentColor" viewBox="0 0 24 24">
          <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M8 10h.01M12 10h.01M16 10h.01M9 16H5a2 2 0 01-2-2V6a2 2 0 012-2h14a2 2 0 012 2v8a2 2 0 01-2 2h-5l-5 5v-5z" />
        </svg>
      </Link>
    </div>
  );
}
