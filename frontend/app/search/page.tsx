"use client";

import { useState, useEffect } from "react";
import { useSearchParams, useRouter } from "next/navigation";
import { Input } from "@/components/ui/input";
import { Button } from "@/components/ui/button";
import { Card, CardContent } from "@/components/ui/card";
import { Badge } from "@/components/ui/badge";
import { 
  Search, 
  Filter, 
  Star, 
  Calendar, 
  ChevronLeft,
  Bookmark,
  BookmarkCheck
} from "lucide-react";
import Link from "next/link";
import { useUser } from "@/components/user-auth-context";
import { useQuery } from "@tanstack/react-query";

interface Movie {
  id: number;
  title: string;
  poster_path: string | null;
  release_date: string | null;
  vote_average: number | null;
  vote_count: number;
  overview: string | null;
  genres: string[];
  is_favorited?: boolean;
}

async function searchMovies(query: string, filters?: any): Promise<Movie[]> {
  try {
    const params = new URLSearchParams({ q: query });
    if (filters?.genre) params.append("genre", filters.genre);
    if (filters?.year) params.append("year", filters.year);
    
    const response = await fetch(`http://localhost:8000/api/search/movies?${params}`);
    if (!response.ok) throw new Error("搜索失败");
    
    const data = await response.json();
    return data.movies || [];
  } catch (error) {
    console.error("搜索出错:", error);
    return [];
  }
}

async function checkFavoriteStatus(movieId: number, userId?: number) {
  if (!userId) return { is_favorited: false };
  
  try {
    const response = await fetch(`http://localhost:8000/api/users/check-favorite/${movieId}?user_id=${userId}`);
    if (!response.ok) throw new Error("检查收藏状态失败");
    
    return await response.json();
  } catch (error) {
    console.error("检查收藏状态出错:", error);
    return { is_favorited: false };
  }
}

export default function SearchPage() {
  const searchParams = useSearchParams();
  const router = useRouter();
  const { user, isLoading: userLoading } = useUser();
  
  const [searchQuery, setSearchQuery] = useState(searchParams.get("q") || "");
  const [isSearching, setIsSearching] = useState(false);
  const [movies, setMovies] = useState<Movie[]>([]);
  const [filters, setFilters] = useState({
    genre: searchParams.get("genre") || "",
    year: searchParams.get("year") || "",
  });

  // 搜索查询
  const { data: searchResults, isLoading } = useQuery({
    queryKey: ["search", searchQuery, filters],
    queryFn: () => searchMovies(searchQuery, filters),
    enabled: !!searchQuery && searchQuery.length >= 2,
  });

  // 处理搜索
  const handleSearch = (e: React.FormEvent) => {
    e.preventDefault();
    if (!searchQuery.trim()) return;
    
    // 更新URL参数
    const params = new URLSearchParams();
    params.set("q", searchQuery);
    if (filters.genre) params.set("genre", filters.genre);
    if (filters.year) params.set("year", filters.year);
    
    router.push(`/search?${params.toString()}`);
  };

  // 处理收藏
  const handleFavorite = async (movieId: number) => {
    if (!user) {
      router.push("/auth/login");
      return;
    }

    try {
      const movie = movies.find(m => m.id === movieId);
      const isFavorited = movie?.is_favorited;
      
      const method = isFavorited ? "DELETE" : "POST";
      const url = `http://localhost:8000/api/users/me/favorites/${movieId}?user_id=${user.id}`;
      
      const response = await fetch(url, {
        method,
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({
          action: isFavorited ? "dislike" : "like",
          notes: "",
          tags: []
        })
      });

      if (response.ok) {
        // 更新本地状态
        setMovies(prev => prev.map(movie => 
          movie.id === movieId 
            ? { ...movie, is_favorited: !movie.is_favorited }
            : movie
        ));
      }
    } catch (error) {
      console.error("收藏操作失败:", error);
    }
  };

  // 记录搜索历史
  useEffect(() => {
    if (searchQuery && movies.length > 0 && !userLoading) {
      const recordHistory = async () => {
        try {
          const params = new URLSearchParams();
          params.set("query", searchQuery);
          params.set("search_type", "keyword");
          params.set("result_count", movies.length.toString());
          params.set("result_ids", movies.slice(0, 10).map(m => m.id).join(","));
          
          if (user) params.set("user_id", user.id.toString());
          
          await fetch(`http://localhost:8000/api/users/me/search-history?${params}`, {
            method: "POST"
          });
        } catch (error) {
          // 静默失败
        }
      };
      
      recordHistory();
    }
  }, [searchQuery, movies, user, userLoading]);

  // 记录浏览历史
  const handleMovieClick = (movieId: number) => {
    if (user) {
      // 记录浏览历史
      fetch(`http://localhost:8000/api/users/me/watch-history/${movieId}?user_id=${user.id}`, {
        method: "POST"
      }).catch(console.error);
    }
    
    // 导航到电影详情页
    router.push(`/movies/${movieId}`);
  };

  return (
    <div className="min-h-screen bg-gradient-to-b from-gray-50 to-white">
      <div className="container mx-auto px-4 py-8">
        {/* 头部 */}
        <div className="mb-8">
          <Link href="/" className="inline-flex items-center text-gray-600 hover:text-gray-900 mb-6">
            <ChevronLeft className="w-4 h-4 mr-1" />
            返回首页
          </Link>
          
          <h1 className="text-3xl font-bold text-gray-900 mb-2">电影搜索</h1>
          <p className="text-gray-600">在4,803部电影中查找您感兴趣的内容</p>
        </div>

        {/* 搜索框 */}
        <form onSubmit={handleSearch} className="mb-8">
          <div className="relative">
            <Search className="absolute left-4 top-1/2 transform -translate-y-1/2 text-gray-400 w-5 h-5" />
            <Input
              type="text"
              placeholder="输入电影名称、演员、导演或关键词..."
              className="pl-12 pr-32 py-6 text-lg"
              value={searchQuery}
              onChange={(e) => setSearchQuery(e.target.value)}
            />
            <div className="absolute right-2 top-1/2 transform -translate-y-1/2">
              <Button type="submit" size="lg" disabled={isLoading || !searchQuery.trim()}>
                {isLoading ? "搜索中..." : "搜索"}
              </Button>
            </div>
          </div>
        </form>

        {/* 筛选条件 */}
        <div className="mb-8 p-4 bg-white rounded-lg border shadow-sm">
          <div className="flex items-center gap-4 mb-4">
            <Filter className="w-5 h-5 text-gray-500" />
            <span className="font-medium text-gray-700">筛选条件</span>
          </div>
          
          <div className="flex gap-4">
            <select 
              className="px-4 py-2 border rounded-md"
              value={filters.genre}
              onChange={(e) => setFilters(prev => ({ ...prev, genre: e.target.value }))}
            >
              <option value="">全部类型</option>
              <option value="Action">动作</option>
              <option value="Comedy">喜剧</option>
              <option value="Drama">剧情</option>
              <option value="Horror">恐怖</option>
              <option value="Sci-Fi">科幻</option>
            </select>
            
            <select 
              className="px-4 py-2 border rounded-md"
              value={filters.year}
              onChange={(e) => setFilters(prev => ({ ...prev, year: e.target.value }))}
            >
              <option value="">全部年份</option>
              <option value="2023">2023</option>
              <option value="2022">2022</option>
              <option value="2021">2021</option>
              <option value="2020">2020</option>
              <option value="2019">2019</option>
            </select>
            
            <Button
              variant="outline"
              onClick={() => setFilters({ genre: "", year: "" })}
            >
              重置
            </Button>
          </div>
        </div>

        {/* 搜索结果 */}
        <div className="space-y-4">
          <div className="flex items-center justify-between">
            <div className="text-gray-700">
              {isLoading ? (
                "正在搜索..."
              ) : searchResults && searchResults.length > 0 ? (
                `找到 ${searchResults.length} 部电影`
              ) : searchQuery ? (
                "未找到相关电影"
              ) : (
                "请输入搜索词"
              )}
            </div>
          </div>

          {isLoading && (
            <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6">
              {[1, 2, 3, 4, 5, 6].map(i => (
                <Card key={i} className="animate-pulse">
                  <CardContent className="p-0">
                    <div className="h-48 bg-gray-200 rounded-t-lg"></div>
                    <div className="p-4">
                      <div className="h-6 bg-gray-200 rounded mb-2"></div>
                      <div className="h-4 bg-gray-200 rounded mb-4"></div>
                      <div className="flex gap-2">
                        <div className="h-6 w-16 bg-gray-200 rounded"></div>
                        <div className="h-6 w-16 bg-gray-200 rounded"></div>
                      </div>
                    </div>
                  </CardContent>
                </Card>
              ))}
            </div>
          )}

          {!isLoading && searchResults && searchResults.length > 0 && (
            <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6">
              {searchResults.map(movie => (
                <Card key={movie.id} className="hover:shadow-lg transition-shadow duration-300">
                  <CardContent className="p-0">
                    {/* 电影海报 */}
                    <div 
                      className="h-48 bg-gray-100 rounded-t-lg relative cursor-pointer"
                      onClick={() => handleMovieClick(movie.id)}
                    >
                      {movie.poster_path ? (
                        <img
                          src={`https://image.tmdb.org/t/p/w500${movie.poster_path}`}
                          alt={movie.title}
                          className="w-full h-full object-cover rounded-t-lg"
                        />
                      ) : (
                        <div className="w-full h-full flex items-center justify-center text-gray-400">
                          暂无海报
                        </div>
                      )}
                      
                      {/* 收藏按钮 */}
                      <button
                        onClick={(e) => {
                          e.stopPropagation();
                          handleFavorite(movie.id);
                        }}
                        className="absolute top-3 right-3 p-2 bg-white/90 backdrop-blur-sm rounded-full hover:bg-white transition-colors"
                      >
                        {movie.is_favorited ? (
                          <BookmarkCheck className="w-5 h-5 text-emerald-600" />
                        ) : (
                          <Bookmark className="w-5 h-5 text-gray-600" />
                        )}
                      </button>
                      
                      {/* 评分 */}
                      {movie.vote_average && movie.vote_average > 0 && (
                        <div className="absolute bottom-3 left-3 px-2 py-1 bg-black/70 text-white text-sm rounded-md backdrop-blur-sm flex items-center gap-1">
                          <Star className="w-3 h-3 fill-yellow-400 text-yellow-400" />
                          {movie.vote_average.toFixed(1)}
                        </div>
                      )}
                    </div>

                    {/* 电影信息 */}
                    <div className="p-4">
                      <h3 
                        className="font-bold text-lg mb-2 line-clamp-1 cursor-pointer hover:text-emerald-600 transition-colors"
                        onClick={() => handleMovieClick(movie.id)}
                      >
                        {movie.title}
                      </h3>
                      
                      <div className="flex items-center text-gray-500 text-sm mb-3">
                        {movie.release_date && (
                          <>
                            <Calendar className="w-4 h-4 mr-1" />
                            {new Date(movie.release_date).getFullYear()}
                          </>
                        )}
                      </div>
                      
                      <p className="text-gray-600 text-sm line-clamp-2 mb-4">
                        {movie.overview || "暂无简介"}
                      </p>
                      
                      <div className="flex flex-wrap gap-2">
                        {movie.genres?.slice(0, 3).map((genre, index) => (
                          <Badge key={index} variant="secondary" className="text-xs">
                            {genre}
                          </Badge>
                        ))}
                      </div>
                    </div>
                  </CardContent>
                </Card>
              ))}
            </div>
          )}

          {!isLoading && searchQuery && searchResults && searchResults.length === 0 && (
            <div className="text-center py-12">
              <div className="text-gray-400 mb-4">📽️</div>
              <h3 className="text-lg font-medium text-gray-700 mb-2">未找到相关电影</h3>
              <p className="text-gray-500 mb-4">
                未找到与 "{searchQuery}" 相关的电影，请尝试其他关键词。
              </p>
              <Button variant="outline" onClick={() => setSearchQuery("")}>
                清空搜索
              </Button>
            </div>
          )}

          {!isLoading && !searchQuery && (
            <div className="text-center py-12">
              <div className="text-gray-400 mb-4">🔍</div>
              <h3 className="text-lg font-medium text-gray-700 mb-2">开始搜索</h3>
              <p className="text-gray-500">
                在搜索框中输入关键词，查找您感兴趣的电影
              </p>
            </div>
          )}
        </div>
      </div>
    </div>
  );
}