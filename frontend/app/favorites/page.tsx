"use client";

import { useState, useEffect, useCallback } from "react";
import Link from "next/link";
import { useRouter } from "next/navigation";
import { Heart, Loader2, Trash2, Star, Calendar } from "lucide-react";
import { useAuth } from "@/contexts/AuthContext";
import { getUserFavorites, removeFavorite, FavoriteItem } from "@/lib/api/favorites";
import FavoriteButton from "@/components/favorite-button";

export default function FavoritesPage() {
  const router = useRouter();
  const { user, isAuthenticated, isLoading: authLoading } = useAuth();
  
  const [favorites, setFavorites] = useState<FavoriteItem[]>([]);
  const [isLoading, setIsLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);
  const [page, setPage] = useState(1);
  const [totalPages, setTotalPages] = useState(1);
  const [totalCount, setTotalCount] = useState(0);

  // 获取收藏列表
  const fetchFavorites = useCallback(async (pageNum: number = 1) => {
    if (!user) return;
    
    setIsLoading(true);
    setError(null);

    try {
      const response = await getUserFavorites(pageNum, 20, user.id);
      setFavorites(response.favorites);
      setTotalPages(response.total_pages);
      setTotalCount(response.total_count);
      setPage(pageNum);
    } catch (err) {
      console.error("获取收藏列表失败:", err);
      setError("无法加载收藏列表");
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
      fetchFavorites(1);
    }
  }, [authLoading, isAuthenticated, user, fetchFavorites, router]);

  // 移除收藏
  const handleRemove = async (movieId: number) => {
    if (!user) return;
    
    try {
      await removeFavorite(movieId, user.id);
      // 移除成功后刷新列表
      setFavorites(prev => prev.filter(f => f.movie_id !== movieId));
      setTotalCount(prev => prev - 1);
    } catch (err) {
      console.error("移除收藏失败:", err);
    }
  };

  // 加载状态
  if (authLoading || (isLoading && favorites.length === 0)) {
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
          <h1 className="text-3xl font-bold text-white">我的收藏</h1>
          <p className="mt-2 text-sm text-white/50">
            共 {totalCount} 部收藏电影
          </p>
        </div>

        {/* 错误提示 */}
        {error && (
          <div className="mb-6 rounded-xl border border-red-500/30 bg-red-500/10 p-4">
            <p className="text-sm text-red-400">{error}</p>
          </div>
        )}

        {/* 收藏列表 */}
        {favorites.length > 0 ? (
          <>
            <div className="grid gap-4 sm:grid-cols-2 lg:grid-cols-3 xl:grid-cols-4">
              {favorites.map((favorite) => (
                <div
                  key={favorite.id}
                  className="group relative overflow-hidden rounded-2xl border border-white/5 bg-white/5 transition-all hover:border-white/10 hover:bg-white/10"
                >
                  {/* 海报 */}
                  <Link href={`/movies/${favorite.movie_id}`} className="block">
                    <div className="aspect-[2/3] overflow-hidden">
                      {favorite.movie?.poster_path ? (
                        <img
                          src={`https://image.tmdb.org/t/p/w500${favorite.movie.poster_path}`}
                          alt={favorite.movie?.title || "电影"}
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

                  {/* 信息 */}
                  <div className="p-4">
                    <Link href={`/movies/${favorite.movie_id}`}>
                      <h3 className="line-clamp-1 text-sm font-medium text-white hover:text-red-400">
                        {favorite.movie?.title || "未知电影"}
                      </h3>
                    </Link>
                    
                    <div className="mt-2 flex items-center gap-3 text-xs text-white/50">
                      {favorite.movie?.vote_average && (
                        <span className="flex items-center gap-1">
                          <Star className="h-3 w-3 text-yellow-500" />
                          {favorite.movie.vote_average.toFixed(1)}
                        </span>
                      )}
                      {favorite.movie?.release_date && (
                        <span className="flex items-center gap-1">
                          <Calendar className="h-3 w-3" />
                          {favorite.movie.release_date.split('-')[0]}
                        </span>
                      )}
                    </div>

                    {/* 操作按钮 */}
                    <div className="mt-4 flex items-center justify-between">
                      <FavoriteButton 
                        movieId={favorite.movie_id} 
                        size="sm" 
                        showText={true}
                      />
                      <button
                        onClick={() => handleRemove(favorite.movie_id)}
                        className="flex items-center gap-1 text-xs text-white/40 hover:text-red-400"
                      >
                        <Trash2 className="h-4 w-4" />
                        移除
                      </button>
                    </div>
                  </div>

                  {/* 收藏时间 */}
                  <div className="absolute right-2 top-2">
                    <div className="flex items-center gap-1 rounded-full bg-black/50 px-2 py-1 backdrop-blur">
                      <Heart className="h-3 w-3 fill-red-500 text-red-500" />
                    </div>
                  </div>
                </div>
              ))}
            </div>

            {/* 分页 */}
            {totalPages > 1 && (
              <div className="mt-8 flex items-center justify-center gap-2">
                <button
                  onClick={() => fetchFavorites(page - 1)}
                  disabled={page <= 1}
                  className="rounded-lg border border-white/10 px-4 py-2 text-sm text-white/70 hover:bg-white/5 disabled:opacity-50"
                >
                  上一页
                </button>
                <span className="text-sm text-white/50">
                  第 {page} / {totalPages} 页
                </span>
                <button
                  onClick={() => fetchFavorites(page + 1)}
                  disabled={page >= totalPages}
                  className="rounded-lg border border-white/10 px-4 py-2 text-sm text-white/70 hover:bg-white/5 disabled:opacity-50"
                >
                  下一页
                </button>
              </div>
            )}
          </>
        ) : (
          /* 空状态 */
          <div className="flex flex-col items-center justify-center py-20">
            <div className="flex h-20 w-20 items-center justify-center rounded-full bg-white/5">
              <Heart className="h-10 w-10 text-white/20" />
            </div>
            <h3 className="mt-4 text-lg font-medium text-white">暂无收藏</h3>
            <p className="mt-2 text-sm text-white/50">
              去发现喜欢的电影吧
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
