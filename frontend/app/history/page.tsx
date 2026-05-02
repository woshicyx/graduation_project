"use client";

import { useState, useEffect, useCallback } from "react";
import Link from "next/link";
import { useRouter } from "next/navigation";
import { Clock, Loader2, Trash2, Star, Calendar, Play, TrendingUp } from "lucide-react";
import { useAuth } from "@/contexts/AuthContext";
import { getWatchHistory, WatchHistoryItem } from "@/lib/api/history";
import FavoriteButton from "@/components/favorite-button";

export default function HistoryPage() {
  const router = useRouter();
  const { user, isAuthenticated, isLoading: authLoading } = useAuth();
  
  const [history, setHistory] = useState<WatchHistoryItem[]>([]);
  const [isLoading, setIsLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);

  // 获取浏览历史
  const fetchHistory = useCallback(async () => {
    if (!user) return;
    
    setIsLoading(true);
    setError(null);

    try {
      const data = await getWatchHistory(50, user.id);
      setHistory(data);
    } catch (err) {
      console.error("获取浏览历史失败:", err);
      setError("无法加载浏览历史");
    } finally {
      setIsLoading(false);
    }
  }, [user]);

  useEffect(() => {
    if (!authLoading && !isAuthenticated) {
      router.push("/auth/login");
      return;
    }
    
    if (isAuthenticated && user) {
      fetchHistory();
    }
  }, [authLoading, isAuthenticated, user, fetchHistory, router]);

  // 加载状态
  if (authLoading || (isLoading && history.length === 0)) {
    return (
      <div className="relative min-h-screen bg-[#0a0a0f]">
        <div className="fixed inset-0 overflow-hidden pointer-events-none">
          <div className="absolute -top-1/2 -right-1/4 h-[800px] w-[800px] rounded-full bg-red-600/5 blur-[120px]" />
          <div className="absolute -top-1/3 left-1/4 h-[600px] w-[600px] rounded-full bg-orange-500/5 blur-[100px]" />
        </div>
        <div className="relative z-10 flex min-h-screen items-center justify-center">
          <Loader2 className="h-8 w-8 animate-spin text-red-500" />
        </div>
      </div>
    );
  }

  // 按日期分组
  const groupedHistory = history.reduce((groups, item) => {
    const date = new Date(item.created_at).toLocaleDateString('zh-CN', {
      year: 'numeric',
      month: 'long',
      day: 'numeric'
    });
    if (!groups[date]) {
      groups[date] = [];
    }
    groups[date].push(item);
    return groups;
  }, {} as Record<string, WatchHistoryItem[]>);

  return (
    <div className="relative min-h-screen bg-[#0a0a0f]">
      {/* 背景装饰 */}
      <div className="fixed inset-0 overflow-hidden pointer-events-none">
        <div className="absolute -top-1/2 -right-1/4 h-[800px] w-[800px] rounded-full bg-red-600/5 blur-[120px]" />
        <div className="absolute -top-1/3 left-1/4 h-[600px] w-[600px] rounded-full bg-orange-500/5 blur-[100px]" />
      </div>

      {/* 导航 */}
      <header className="relative z-10 border-b border-white/10 bg-black/50 backdrop-blur-md">
        <div className="mx-auto flex h-16 max-w-7xl items-center justify-between px-4">
          <Link href="/" className="flex items-center gap-3">
            <div className="flex h-10 w-10 items-center justify-center rounded-xl bg-gradient-to-br from-red-600 to-red-700">
              <svg className="h-5 w-5 text-white" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M7 4v16M17 4v16M3 8h4m10 0h4M3 12h18M3 16h4m10 0h4M4 20h16a1 1 0 001-1V5a1 1 0 00-1-1H4a1 1 0 00-1 1v14a1 1 0 001 1z" />
              </svg>
            </div>
            <span className="text-xl font-bold tracking-tight text-white">
              Movie<span className="text-red-500">AI</span>
            </span>
          </Link>
          <div className="flex items-center gap-4">
            <Link href="/search" className="text-sm text-white/70 hover:text-white">
              搜索
            </Link>
            <div className="h-8 w-px bg-white/10" />
            <span className="text-sm text-white/50">
              {user?.username}
            </span>
          </div>
        </div>
      </header>

      {/* 内容 */}
      <main className="relative z-10 mx-auto max-w-7xl px-4 py-8">
        {/* 标题 */}
        <div className="mb-8">
          <h1 className="text-3xl font-bold text-white">浏览历史</h1>
          <p className="mt-2 text-sm text-white/50">
            共 {history.length} 条浏览记录
          </p>
        </div>

        {/* 错误提示 */}
        {error && (
          <div className="mb-6 rounded-xl border border-red-500/30 bg-red-500/10 p-4">
            <p className="text-sm text-red-400">{error}</p>
          </div>
        )}

        {/* 历史列表 */}
        {history.length > 0 ? (
          <div className="space-y-8">
            {Object.entries(groupedHistory).map(([date, items]) => (
              <div key={date}>
                <h2 className="mb-4 flex items-center gap-2 text-sm font-medium text-white/50">
                  <Clock className="h-4 w-4" />
                  {date}
                </h2>
                <div className="grid gap-4 sm:grid-cols-2 lg:grid-cols-3 xl:grid-cols-4">
                  {items.map((item) => (
                    <div
                      key={item.id}
                      className="group relative overflow-hidden rounded-2xl border border-white/5 bg-white/5 transition-all hover:border-white/10 hover:bg-white/10"
                    >
                      {/* 海报 */}
                      <Link href={`/movies/${item.movie_id}`} className="block">
                        <div className="aspect-[2/3] overflow-hidden">
                          {item.movie?.poster_path ? (
                            <img
                              src={`https://image.tmdb.org/t/p/w500${item.movie.poster_path}`}
                              alt={item.movie?.title || "电影"}
                              className="h-full w-full object-cover transition-transform duration-300 group-hover:scale-105"
                            />
                          ) : (
                            <div className="flex h-full w-full items-center justify-center bg-white/5">
                              <svg className="h-16 w-16 text-white/20" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                                <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M7 4v16M17 4v16M3 8h4m10 0h4M3 12h18M3 16h4m10 0h4M4 20h16a1 1 0 001-1V5a1 1 0 00-1-1H4a1 1 0 00-1 1v14a1 1 0 001 1z" />
                              </svg>
                            </div>
                          )}
                        </div>
                      </Link>

                      {/* 进度条 */}
                      {item.progress > 0 && (
                        <div className="absolute bottom-0 left-0 right-0 h-1 bg-white/10">
                          <div 
                            className="h-full bg-red-500 transition-all"
                            style={{ width: `${Math.min(item.progress, 100)}%` }}
                          />
                        </div>
                      )}

                      {/* 信息 */}
                      <div className="p-4">
                        <Link href={`/movies/${item.movie_id}`}>
                          <h3 className="line-clamp-1 text-sm font-medium text-white hover:text-red-400">
                            {item.movie?.title || "未知电影"}
                          </h3>
                        </Link>
                        
                        <div className="mt-2 flex items-center gap-3 text-xs text-white/50">
                          {item.movie?.vote_average && (
                            <span className="flex items-center gap-1">
                              <Star className="h-3 w-3 text-yellow-500" />
                              {item.movie.vote_average.toFixed(1)}
                            </span>
                          )}
                          {item.movie?.release_date && (
                            <span className="flex items-center gap-1">
                              <Calendar className="h-3 w-3" />
                              {item.movie.release_date.split('-')[0]}
                            </span>
                          )}
                          {item.watch_duration > 0 && (
                            <span className="flex items-center gap-1">
                              <Play className="h-3 w-3" />
                              {Math.floor(item.watch_duration / 60)}分钟
                            </span>
                          )}
                        </div>

                        {/* 操作按钮 */}
                        <div className="mt-4 flex items-center justify-between">
                          <FavoriteButton 
                            movieId={item.movie_id} 
                            size="sm" 
                            showText={true}
                          />
                          <button
                            onClick={() => {
                              setHistory(prev => prev.filter(h => h.id !== item.id));
                            }}
                            className="flex items-center gap-1 text-xs text-white/40 hover:text-red-400"
                          >
                            <Trash2 className="h-4 w-4" />
                            删除
                          </button>
                        </div>
                      </div>

                      {/* 互动分数 */}
                      {item.interaction_score > 0 && (
                        <div className="absolute left-2 top-2">
                          <div className="flex items-center gap-1 rounded-full bg-black/50 px-2 py-1 backdrop-blur">
                            <TrendingUp className="h-3 w-3 text-green-500" />
                            <span className="text-xs text-white/70">
                              {Math.round(item.interaction_score * 100)}%
                            </span>
                          </div>
                        </div>
                      )}
                    </div>
                  ))}
                </div>
              </div>
            ))}
          </div>
        ) : (
          /* 空状态 */
          <div className="flex flex-col items-center justify-center py-20">
            <div className="flex h-20 w-20 items-center justify-center rounded-full bg-white/5">
              <Clock className="h-10 w-10 text-white/20" />
            </div>
            <h3 className="mt-4 text-lg font-medium text-white">暂无浏览记录</h3>
            <p className="mt-2 text-sm text-white/50">
              开始探索喜欢的电影吧
            </p>
            <Link
              href="/search"
              className="mt-6 rounded-xl bg-gradient-to-r from-red-600 to-red-700 px-6 py-3 text-sm font-medium text-white shadow-lg shadow-red-600/30"
            >
              浏览电影
            </Link>
          </div>
        )}
      </main>
    </div>
  );
}
