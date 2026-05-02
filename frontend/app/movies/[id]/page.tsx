"use client";

import Link from "next/link";
import Image from "next/image";
import { useState, useEffect } from "react";
import { useRouter } from "next/navigation";
import { getMovieDetail, MovieDetail } from "@/lib/api/movie";
import { useAuth } from "@/contexts/AuthContext";
import { addWatchHistory } from "@/lib/api/history";
import FavoriteButton from "@/components/favorite-button";
import { Sparkles, Play, Clock, Calendar, Star, User, Heart } from "lucide-react";

interface MoviePageProps {
  params: Promise<{ id: string }>;
}

export default function MovieDetailPage({ params }: MoviePageProps) {
  const router = useRouter();
  const { user, isAuthenticated } = useAuth();
  const [movie, setMovie] = useState<MovieDetail | null>(null);
  const [isLoading, setIsLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);
  const [movieId, setMovieId] = useState<number | null>(null);

  useEffect(() => {
    // Next.js 14 App Router params handling
    const resolveParams = async () => {
      const resolved = await params;
      if (resolved?.id) {
        setMovieId(parseInt(resolved.id, 10));
      }
    };
    resolveParams();
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
      <div className="relative min-h-screen bg-[#0a0a0f]">
        <div className="fixed inset-0 overflow-hidden pointer-events-none">
          <div className="absolute -top-40 -right-40 h-80 w-80 rounded-full bg-red-500/10 blur-3xl" />
          <div className="absolute bottom-40 left-1/4 h-96 w-96 rounded-full bg-purple-500/5 blur-3xl" />
        </div>
        <div className="relative z-10 flex min-h-screen items-center justify-center">
          <div className="h-8 w-8 animate-spin rounded-full border-2 border-red-500 border-t-transparent" />
        </div>
      </div>
    );
  }

  if (error || !movie) {
    return (
      <div className="relative min-h-screen bg-[#0a0a0f]">
        <div className="fixed inset-0 overflow-hidden pointer-events-none">
          <div className="absolute -top-40 -right-40 h-80 w-80 rounded-full bg-red-500/10 blur-3xl" />
          <div className="absolute bottom-40 left-1/4 h-96 w-96 rounded-full bg-purple-500/5 blur-3xl" />
        </div>
        <header className="relative z-10 border-b border-white/5 bg-[#0a0a0f]/80 backdrop-blur">
          <div className="mx-auto flex h-16 max-w-7xl items-center px-4">
            <Link href="/" className="flex items-center gap-3">
              <div className="flex h-10 w-10 items-center justify-center rounded-xl bg-gradient-to-br from-red-600 to-red-700">
                <Sparkles className="h-5 w-5 text-white" />
              </div>
              <span className="text-xl font-bold tracking-tight text-white">
                Movie<span className="text-red-500">AI</span>
              </span>
            </Link>
          </div>
        </header>
        <div className="relative z-10 flex min-h-[calc(100vh-64px)] flex-col items-center justify-center px-4">
          <p className="text-red-400">{error || "电影不存在"}</p>
          <Link 
            href="/search"
            className="mt-4 rounded-lg bg-gradient-to-r from-red-600 to-red-700 px-4 py-2 text-white hover:from-red-500 hover:to-red-600"
          >
            返回搜索
          </Link>
        </div>
      </div>
    );
  }

  return (
    <div className="relative min-h-screen bg-[#0a0a0f]">
      {/* 背景装饰 */}
      <div className="fixed inset-0 overflow-hidden pointer-events-none">
        <div className="absolute -top-40 -right-40 h-80 w-80 rounded-full bg-red-500/10 blur-3xl" />
        <div className="absolute bottom-40 left-1/4 h-96 w-96 rounded-full bg-purple-500/5 blur-3xl" />
      </div>

      {/* 导航 */}
      <header className="relative z-10 border-b border-white/5 bg-[#0a0a0f]/80 backdrop-blur">
        <div className="mx-auto flex h-16 max-w-7xl items-center justify-between px-4">
          <Link href="/" className="flex items-center gap-3">
            <div className="flex h-10 w-10 items-center justify-center rounded-xl bg-gradient-to-br from-red-600 to-red-700">
              <Sparkles className="h-5 w-5 text-white" />
            </div>
            <span className="text-xl font-bold tracking-tight text-white">
              Movie<span className="text-red-500">AI</span>
            </span>
          </Link>
          <div className="flex items-center gap-4">
            <Link href="/chat" className="text-sm text-white/70 hover:text-white">
              AI助手
            </Link>
            <Link href="/search" className="text-sm text-white/70 hover:text-white">
              搜索
            </Link>
            <Link 
              href="/auth/login" 
              className="rounded-lg bg-gradient-to-r from-red-600 to-red-700 px-4 py-2 text-sm font-medium text-white hover:from-red-500 hover:to-red-600"
            >
              登录
            </Link>
          </div>
        </div>
      </header>

      {/* 电影详情内容 */}
      <main className="relative z-10 mx-auto max-w-7xl px-4 py-8">
        {/* 面包屑导航 */}
        <div className="mb-6 flex items-center gap-2 text-sm text-white/50">
          <Link href="/" className="hover:text-white">首页</Link>
          <span>/</span>
          <Link href="/search" className="hover:text-white">搜索</Link>
          <span>/</span>
          <span className="text-white/70">{movie.title}</span>
        </div>

        {/* 电影信息区域 */}
        <div className="grid gap-8 lg:grid-cols-3">
          {/* 海报 */}
          <div className="lg:col-span-1">
            <div className="sticky top-8">
              <div className="aspect-[2/3] relative overflow-hidden rounded-2xl border border-white/10 bg-white/5">
                {movie.poster_path ? (
                  <Image 
                    src={`https://image.tmdb.org/t/p/w500${movie.poster_path}`}
                    alt={movie.title}
                    fill
                    className="object-cover"
                    sizes="(max-width: 1024px) 100vw, 33vw"
                    priority
                  />
                ) : (
                  <div className="flex h-full w-full items-center justify-center">
                    <Play className="h-16 w-16 text-white/30" />
                  </div>
                )}
                {/* 评分 */}
                {movie.vote_average && movie.vote_average > 0 && (
                  <div className="absolute top-3 left-3 flex items-center gap-1 rounded-full bg-black/60 px-3 py-1.5 backdrop-blur">
                    <Star className="h-4 w-4 text-yellow-400 fill-yellow-400" />
                    <span className="text-sm font-medium text-white">
                      {movie.vote_average.toFixed(1)}
                    </span>
                  </div>
                )}
              </div>
              
              {/* 操作按钮 */}
              <div className="mt-4 flex gap-3">
                <button
                  onClick={() => {
                    if (!isAuthenticated) {
                      router.push('/auth/login');
                      return;
                    }
                    addWatchHistory(movieId!, user?.id).catch(console.error);
                  }}
                  className="flex flex-1 items-center justify-center gap-2 rounded-xl bg-gradient-to-r from-red-600 to-red-700 px-6 py-3 text-sm font-medium text-white shadow-lg shadow-red-600/30 hover:from-red-500 hover:to-red-600 transition-all"
                >
                  <Play className="h-5 w-5 fill-current" />
                  观看
                </button>
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
                <p className="mt-1 text-white/50">{movie.original_title}</p>
              )}
              {movie.tagline && (
                <p className="mt-3 italic text-red-400">{movie.tagline}</p>
              )}
            </div>

            {/* 基本信息 */}
            <div className="flex flex-wrap gap-4 text-sm text-white/50">
              {movie.vote_average && (
                <span className="flex items-center gap-1.5 rounded-full bg-white/10 px-3 py-1">
                  <Star className="h-4 w-4 text-yellow-400 fill-yellow-400" />
                  <span className="text-white">{movie.vote_average.toFixed(1)}</span>
                  <span className="text-white/50">({movie.vote_count || 0} 人评分)</span>
                </span>
              )}
              {movie.release_date && (
                <span className="flex items-center gap-1.5">
                  <Calendar className="h-4 w-4" />
                  {movie.release_date.split('-')[0]}
                </span>
              )}
              {movie.runtime && (
                <span className="flex items-center gap-1.5">
                  <Clock className="h-4 w-4" />
                  {movie.runtime} 分钟
                </span>
              )}
              {movie.original_language && (
                <span className="uppercase">{movie.original_language}</span>
              )}
            </div>

            {/* 类型标签 */}
            {movie.parsed_genres && movie.parsed_genres.length > 0 && (
              <div className="flex flex-wrap gap-2">
                {movie.parsed_genres.map((genre, i) => (
                  <span key={i} className="rounded-full border border-red-500/30 bg-red-500/10 px-3 py-1 text-sm text-red-400">
                    {genre}
                  </span>
                ))}
              </div>
            )}

            {/* 剧情简介 */}
            {movie.overview && (
              <div className="rounded-xl border border-white/10 bg-white/5 p-6 backdrop-blur">
                <h2 className="mb-3 flex items-center gap-2 text-lg font-semibold text-white">
                  <Play className="h-5 w-5 text-red-400" />
                  剧情简介
                </h2>
                <p className="text-sm leading-relaxed text-white/70">
                  {movie.overview}
                </p>
              </div>
            )}

            {/* 导演 */}
            {movie.director && (
              <div className="rounded-xl border border-white/10 bg-white/5 p-6 backdrop-blur">
                <h2 className="mb-3 flex items-center gap-2 text-lg font-semibold text-white">
                  <User className="h-5 w-5 text-red-400" />
                  导演
                </h2>
                <p className="text-sm text-white/70">{movie.director}</p>
              </div>
            )}

            {/* 关键词 */}
            {movie.parsed_keywords && movie.parsed_keywords.length > 0 && (
              <div className="rounded-xl border border-white/10 bg-white/5 p-6 backdrop-blur">
                <h2 className="mb-3 text-lg font-semibold text-white">关键词</h2>
                <div className="flex flex-wrap gap-2">
                  {movie.parsed_keywords.slice(0, 10).map((keyword, i) => (
                    <span key={i} className="rounded-full bg-white/10 px-2.5 py-1 text-xs text-white/60">
                      {keyword}
                    </span>
                  ))}
                </div>
              </div>
            )}

            {/* 制作信息 */}
            {(movie.budget || movie.revenue) && (
              <div className="rounded-xl border border-white/10 bg-white/5 p-6 backdrop-blur">
                <h2 className="mb-3 text-lg font-semibold text-white">制作信息</h2>
                <div className="grid grid-cols-2 gap-4 text-sm">
                  {movie.budget && movie.budget > 0 && (
                    <div>
                      <span className="text-white/50">预算</span>
                      <p className="text-white">${movie.budget.toLocaleString()}</p>
                    </div>
                  )}
                  {movie.revenue && movie.revenue > 0 && (
                    <div>
                      <span className="text-white/50">票房</span>
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
        className="fixed bottom-6 right-6 flex h-14 w-14 items-center justify-center rounded-full bg-gradient-to-r from-red-600 to-red-700 shadow-lg shadow-red-500/25 transition-all hover:scale-105"
      >
        <Sparkles className="h-6 w-6 text-white" />
      </Link>
    </div>
  );
}
