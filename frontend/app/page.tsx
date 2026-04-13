"use client";

import Link from "next/link";
import { useState, useEffect } from "react";
import { motion } from "framer-motion";
import { getRandomMovies, getTopRatedMovies, getTopPopularMovies, getTopBoxOfficeMovies, MovieListItem } from "@/lib/api/movie";
import { 
  Search, 
  Sparkles, 
  BookMarked, 
  TrendingUp,
  Play,
  ChevronRight,
  Star,
  Flame,
  Clapperboard,
  Tv2,
  Clock,
  Award,
  Wand2,
  DollarSign,
  TrendingUp as TrendingUpIcon
} from "lucide-react";

export default function Home() {
  const [aiRecommendMovies, setAiRecommendMovies] = useState<MovieListItem[]>([]);
  const [topRatedMovies, setTopRatedMovies] = useState<MovieListItem[]>([]);
  const [topPopularMovies, setTopPopularMovies] = useState<MovieListItem[]>([]);
  const [topBoxOfficeMovies, setTopBoxOfficeMovies] = useState<MovieListItem[]>([]);
  const [isLoading, setIsLoading] = useState(true);

  useEffect(() => {
    // 并行获取四种类型的电影
    Promise.all([
      getRandomMovies(5).catch(() => []),
      getTopRatedMovies(8).catch(() => []),
      getTopPopularMovies(8).catch(() => []),
      getTopBoxOfficeMovies(8).catch(() => [])
    ])
      .then(([aiRecommend, topRated, topPopular, topBoxOffice]) => {
        setAiRecommendMovies(aiRecommend);
        setTopRatedMovies(topRated);
        setTopPopularMovies(topPopular);
        setTopBoxOfficeMovies(topBoxOffice);
        setIsLoading(false);
      })
      .catch((err) => {
        console.error("获取电影数据失败:", err);
        setIsLoading(false);
      });
  }, []);

  return (
    <div className="relative min-h-screen overflow-hidden bg-[#0a0a0f]">
      {/* 背景装饰 - 暗黑电影风格 */}
      <div className="fixed inset-0 overflow-hidden pointer-events-none">
        {/* 顶部渐变光晕 */}
        <div className="absolute -top-1/2 -right-1/4 h-[800px] w-[800px] rounded-full bg-red-600/5 blur-[120px]" />
        <div className="absolute -top-1/3 left-1/4 h-[600px] w-[600px] rounded-full bg-orange-500/5 blur-[100px]" />
        
        {/* 底部渐变 */}
        <div className="absolute bottom-0 left-0 right-0 h-1/2 bg-gradient-to-t from-[#0a0a0f] via-[#0a0a0f]/50 to-transparent" />
        
        {/* 噪点纹理 */}
        <div className="absolute inset-0 opacity-[0.015]" 
          style={{ 
            backgroundImage: `url("data:image/svg+xml,%3Csvg viewBox='0 0 400 400' xmlns='http://www.w3.org/2000/svg'%3E%3Cfilter id='noiseFilter'%3E%3CfeTurbulence type='fractalNoise' baseFrequency='0.9' numOctaves='3' stitchTiles='stitch'/%3E%3C/filter%3E%3Crect width='100%25' height='100%25' filter='url(%23noiseFilter)'/%3E%3C/svg%3E")` 
          }} 
        />
      </div>

      <main className="relative z-10 flex min-h-screen flex-col">
        {/* 导航栏 - 暗黑电影风格 */}
        <header className="sticky top-0 z-50 border-b border-white/5 bg-[#0a0a0f]/80 backdrop-blur-xl">
          <div className="mx-auto max-w-7xl px-4 sm:px-6 lg:px-8">
            <div className="flex h-16 items-center justify-between">
              {/* Logo */}
              <Link href="/" className="flex items-center gap-3 group">
                <div className="relative">
                  <div className="flex h-10 w-10 items-center justify-center rounded-lg bg-gradient-to-br from-red-600 to-red-700 shadow-lg shadow-red-600/30">
                    <Clapperboard className="h-5 w-5 text-white" />
                  </div>
                  <div className="absolute -inset-1 rounded-lg bg-gradient-to-br from-red-600 to-red-700 opacity-0 blur transition-opacity duration-300 group-hover:opacity-50" />
                </div>
                <div className="flex items-baseline gap-1">
                  <span className="text-xl font-bold tracking-tight text-white">
                    Movie
                  </span>
                  <span className="text-xl font-bold tracking-tight text-red-500">
                    AI
                  </span>
                </div>
              </Link>

              {/* 导航链接 */}
              <nav className="hidden md:flex items-center gap-8">
                <Link href="/" className="text-sm font-medium text-white hover:text-red-400 transition-colors">
                  首页
                </Link>
                <Link href="/search" className="text-sm font-medium text-white/70 hover:text-red-400 transition-colors">
                  电影
                </Link>
                <Link href="/search" className="text-sm font-medium text-white/70 hover:text-red-400 transition-colors">
                  剧集
                </Link>
                <Link href="/search" className="text-sm font-medium text-white/70 hover:text-red-400 transition-colors">
                  我的列表
                </Link>
              </nav>

              {/* 右侧操作 */}
              <div className="flex items-center gap-4">
                <Link 
                  href="/search"
                  className="flex items-center gap-2 rounded-full bg-white/5 px-4 py-2 text-sm text-white/70 border border-white/10 hover:bg-white/10 hover:text-white transition-all"
                >
                  <Search className="h-4 w-4" />
                  <span className="hidden sm:inline">搜索电影...</span>
                </Link>
                <Link 
                  href="/auth/login" 
                  className="rounded-lg bg-gradient-to-r from-red-600 to-red-700 px-5 py-2 text-sm font-medium text-white shadow-lg shadow-red-600/30 hover:from-red-500 hover:to-red-600 transition-all"
                >
                  登录
                </Link>
              </div>
            </div>
          </div>
        </header>

        {/* 主要内容区域 */}
        <div className="flex-1">
          {/* 英雄区域 - 搜索 */}
          <section className="relative py-20 sm:py-28 lg:py-36">
            <div className="mx-auto max-w-7xl px-4 sm:px-6 lg:px-8">
              <motion.div 
                initial={{ opacity: 0, y: 20 }}
                animate={{ opacity: 1, y: 0 }}
                transition={{ duration: 0.6 }}
                className="text-center"
              >
                {/* 标签 */}
                <div className="inline-flex items-center gap-2 rounded-full border border-red-500/30 bg-red-500/10 px-4 py-1.5 mb-6">
                  <Sparkles className="h-3.5 w-3.5 text-red-400" />
                  <span className="text-xs font-medium text-red-300">AI 驱动的智能推荐</span>
                </div>

                {/* 主标题 */}
                <h1 className="text-4xl font-bold tracking-tight sm:text-5xl lg:text-6xl">
                  <span className="text-white">发现你的</span>
                  <br />
                  <span className="bg-gradient-to-r from-red-500 via-orange-400 to-yellow-400 bg-clip-text text-transparent">
                    下一部电影
                  </span>
                </h1>

                {/* 副标题 */}
                <p className="mx-auto mt-6 max-w-2xl text-lg text-white/60">
                  基于先进的 AI 技术，为你推荐最适合的电影和剧集
                </p>

                {/* 搜索框 */}
                <div className="mt-10 mx-auto max-w-2xl">
                  <Link href="/search">
                    <div className="group relative flex items-center rounded-2xl border border-white/10 bg-white/5 p-2 backdrop-blur-xl transition-all hover:border-red-500/50 hover:bg-white/[0.07]">
                      <div className="flex h-12 w-12 items-center justify-center rounded-xl bg-gradient-to-br from-red-600 to-red-700">
                        <Search className="h-5 w-5 text-white" />
                      </div>
                      <div className="ml-4 flex-1 text-left">
                        <p className="text-sm font-medium text-white/90 group-hover:text-white">
                          搜索电影、导演、类型...
                        </p>
                        <p className="text-xs text-white/40">
                          试试 "科幻电影" 或 "诺兰导演"
                        </p>
                      </div>
                      <div className="flex items-center gap-2">
                        <span className="hidden sm:inline-flex items-center gap-1 rounded-full bg-white/10 px-3 py-1 text-xs text-white/60">
                          <Star className="h-3 w-3" />
                          AI 推荐
                        </span>
                        <div className="flex h-10 w-10 items-center justify-center rounded-xl bg-white/10 text-white/60 group-hover:bg-red-600 group-hover:text-white transition-colors">
                          <ChevronRight className="h-5 w-5" />
                        </div>
                      </div>
                    </div>
                  </Link>
                </div>

                {/* 统计信息 */}
                <div className="mt-12 flex flex-wrap items-center justify-center gap-8">
                  <div className="text-center">
                    <div className="text-2xl font-bold text-white">4,800+</div>
                    <div className="text-sm text-white/50">电影资源</div>
                  </div>
                  <div className="h-8 w-px bg-white/10" />
                  <div className="text-center">
                    <div className="text-2xl font-bold text-white">AI</div>
                    <div className="text-sm text-white/50">智能推荐</div>
                  </div>
                  <div className="h-8 w-px bg-white/10" />
                  <div className="text-center">
                    <div className="text-2xl font-bold text-white">24/7</div>
                    <div className="text-sm text-white/50">随时发现</div>
                  </div>
                </div>
              </motion.div>
            </div>
          </section>

          {/* 功能介绍 */}
          <section className="py-16 border-t border-white/5">
            <div className="mx-auto max-w-7xl px-4 sm:px-6 lg:px-8">
              <div className="grid gap-6 md:grid-cols-3">
                {/* 智能搜索 */}
                <motion.div 
                  initial={{ opacity: 0, y: 20 }}
                  whileInView={{ opacity: 1, y: 0 }}
                  viewport={{ once: true }}
                  transition={{ delay: 0.1 }}
                  className="group relative rounded-2xl border border-white/5 bg-gradient-to-b from-white/[0.05] to-transparent p-8 backdrop-blur-sm transition-all hover:border-red-500/30 hover:bg-white/[0.08]"
                >
                  <div className="absolute inset-0 rounded-2xl bg-gradient-to-b from-red-500/5 to-transparent opacity-0 transition-opacity group-hover:opacity-100" />
                  <div className="relative">
                    <div className="flex h-14 w-14 items-center justify-center rounded-2xl bg-gradient-to-br from-red-500/20 to-red-600/10 border border-red-500/20">
                      <Search className="h-7 w-7 text-red-400" />
                    </div>
                    <h3 className="mt-6 text-xl font-semibold text-white">智能搜索</h3>
                    <p className="mt-3 text-sm text-white/50 leading-relaxed">
                      支持多维度搜索：电影名、类型、导演、演员、评分，找你想看的一切
                    </p>
                    <div className="mt-6 flex flex-wrap gap-2">
                      <span className="rounded-full bg-white/5 px-3 py-1 text-xs text-white/40">类型筛选</span>
                      <span className="rounded-full bg-white/5 px-3 py-1 text-xs text-white/40">评分排序</span>
                      <span className="rounded-full bg-white/5 px-3 py-1 text-xs text-white/40">年代筛选</span>
                    </div>
                  </div>
                </motion.div>

                {/* AI 推荐 */}
                <motion.div 
                  initial={{ opacity: 0, y: 20 }}
                  whileInView={{ opacity: 1, y: 0 }}
                  viewport={{ once: true }}
                  transition={{ delay: 0.2 }}
                  className="group relative rounded-2xl border border-white/5 bg-gradient-to-b from-white/[0.05] to-transparent p-8 backdrop-blur-sm transition-all hover:border-orange-500/30 hover:bg-white/[0.08]"
                >
                  <div className="absolute inset-0 rounded-2xl bg-gradient-to-b from-orange-500/5 to-transparent opacity-0 transition-opacity group-hover:opacity-100" />
                  <div className="relative">
                    <div className="flex h-14 w-14 items-center justify-center rounded-2xl bg-gradient-to-br from-orange-500/20 to-orange-600/10 border border-orange-500/20">
                      <Sparkles className="h-7 w-7 text-orange-400" />
                    </div>
                    <h3 className="mt-6 text-xl font-semibold text-white">AI 推荐</h3>
                    <p className="mt-3 text-sm text-white/50 leading-relaxed">
                      基于 RAG 技术的智能推荐系统，深入理解你的观影偏好
                    </p>
                    <div className="mt-6 flex flex-wrap gap-2">
                      <span className="rounded-full bg-white/5 px-3 py-1 text-xs text-white/40">个性化</span>
                      <span className="rounded-full bg-white/5 px-3 py-1 text-xs text-white/40">深度理解</span>
                      <span className="rounded-full bg-white/5 px-3 py-1 text-xs text-white/40">精准匹配</span>
                    </div>
                  </div>
                </motion.div>

                {/* 收藏管理 */}
                <motion.div 
                  initial={{ opacity: 0, y: 20 }}
                  whileInView={{ opacity: 1, y: 0 }}
                  viewport={{ once: true }}
                  transition={{ delay: 0.3 }}
                  className="group relative rounded-2xl border border-white/5 bg-gradient-to-b from-white/[0.05] to-transparent p-8 backdrop-blur-sm transition-all hover:border-yellow-500/30 hover:bg-white/[0.08]"
                >
                  <div className="absolute inset-0 rounded-2xl bg-gradient-to-b from-yellow-500/5 to-transparent opacity-0 transition-opacity group-hover:opacity-100" />
                  <div className="relative">
                    <div className="flex h-14 w-14 items-center justify-center rounded-2xl bg-gradient-to-br from-yellow-500/20 to-yellow-600/10 border border-yellow-500/20">
                      <BookMarked className="h-7 w-7 text-yellow-400" />
                    </div>
                    <h3 className="mt-6 text-xl font-semibold text-white">收藏管理</h3>
                    <p className="mt-3 text-sm text-white/50 leading-relaxed">
                      登录后创建个人片单，收藏喜欢的电影，记录观影历史
                    </p>
                    <div className="mt-6 flex flex-wrap gap-2">
                      <span className="rounded-full bg-white/5 px-3 py-1 text-xs text-white/40">片单</span>
                      <span className="rounded-full bg-white/5 px-3 py-1 text-xs text-white/40">历史</span>
                      <span className="rounded-full bg-white/5 px-3 py-1 text-xs text-white/40">评论</span>
                    </div>
                  </div>
                </motion.div>
              </div>
            </div>
          </section>

          {/* AI 精选推荐 */}
          {aiRecommendMovies.length > 0 && (
            <section className="py-16 border-t border-white/5">
              <div className="mx-auto max-w-7xl px-4 sm:px-6 lg:px-8">
                <motion.div 
                  initial={{ opacity: 0, y: 20 }}
                  whileInView={{ opacity: 1, y: 0 }}
                  viewport={{ once: true }}
                  className="mb-10 flex items-center justify-between"
                >
                  <div className="flex items-center gap-4">
                    <div className="flex h-12 w-12 items-center justify-center rounded-xl bg-gradient-to-br from-purple-500/20 to-purple-600/10 border border-purple-500/20">
                      <Wand2 className="h-6 w-6 text-purple-400" />
                    </div>
                    <div>
                      <h2 className="text-2xl font-bold text-white">AI 精选</h2>
                      <p className="text-sm text-white/50">为你智能推荐的独特影片</p>
                    </div>
                  </div>
                  <Link 
                    href="/search" 
                    className="flex items-center gap-2 text-sm font-medium text-purple-400 hover:text-purple-300 transition-colors"
                  >
                    查看全部
                    <ChevronRight className="h-4 w-4" />
                  </Link>
                </motion.div>

                <div className="grid gap-5 sm:grid-cols-2 md:grid-cols-3 lg:grid-cols-5">
                  {aiRecommendMovies.map((movie, index) => (
                    <motion.div
                      key={movie.id}
                      initial={{ opacity: 0, y: 20 }}
                      whileInView={{ opacity: 1, y: 0 }}
                      viewport={{ once: true }}
                      transition={{ delay: index * 0.05 }}
                    >
                      <Link 
                        href={`/movies/${movie.id}`}
                        className="group block"
                      >
                        <div className="relative overflow-hidden rounded-xl border border-purple-500/20 bg-gradient-to-b from-purple-500/5 to-transparent transition-all duration-300 group-hover:border-purple-500/50 group-hover:shadow-lg group-hover:shadow-purple-500/10">
                          <div className="relative aspect-[2/3] overflow-hidden">
                            {movie.poster_path ? (
                              <img 
                                src={`https://image.tmdb.org/t/p/w500${movie.poster_path}`}
                                alt={movie.title}
                                className="h-full w-full object-cover transition-transform duration-500 group-hover:scale-105"
                              />
                            ) : (
                              <div className="flex h-full w-full items-center justify-center bg-white/5">
                                <Clapperboard className="h-12 w-12 text-white/20" />
                              </div>
                            )}
                            <div className="absolute inset-0 bg-gradient-to-t from-black/80 via-black/20 to-transparent opacity-0 transition-opacity duration-300 group-hover:opacity-100" />
                            <div className="absolute top-3 left-3">
                              <div className="flex items-center gap-1 rounded-full bg-purple-500/90 px-2.5 py-1 text-xs font-bold text-white">
                                <Wand2 className="h-3 w-3" />
                                AI
                              </div>
                            </div>
                            {movie.vote_average && (
                              <div className="absolute top-3 right-3">
                                <div className="flex items-center gap-1 rounded-full bg-black/60 backdrop-blur-sm px-2.5 py-1 text-xs font-bold text-white">
                                  <Star className="h-3 w-3 fill-current text-yellow-400" />
                                  {movie.vote_average.toFixed(1)}
                                </div>
                              </div>
                            )}
                          </div>
                          <div className="p-3">
                            <h3 className="text-sm font-medium text-white truncate group-hover:text-purple-300 transition-colors">
                              {movie.title}
                            </h3>
                            <p className="mt-1 text-xs text-white/50">
                              {movie.release_date?.split('-')[0] || '未知'}
                            </p>
                          </div>
                        </div>
                      </Link>
                    </motion.div>
                  ))}
                </div>
              </div>
            </section>
          )}

          {/* 高分电影 */}
          {topRatedMovies.length > 0 && (
            <section className="py-16 border-t border-white/5">
              <div className="mx-auto max-w-7xl px-4 sm:px-6 lg:px-8">
                <motion.div 
                  initial={{ opacity: 0, y: 20 }}
                  whileInView={{ opacity: 1, y: 0 }}
                  viewport={{ once: true }}
                  className="mb-10 flex items-center justify-between"
                >
                  <div className="flex items-center gap-4">
                    <div className="flex h-12 w-12 items-center justify-center rounded-xl bg-gradient-to-br from-yellow-500/20 to-yellow-600/10 border border-yellow-500/20">
                      <Award className="h-6 w-6 text-yellow-400" />
                    </div>
                    <div>
                      <h2 className="text-2xl font-bold text-white">高分佳作</h2>
                      <p className="text-sm text-white/50">豆瓣高分电影精选</p>
                    </div>
                  </div>
                  <Link 
                    href="/search" 
                    className="flex items-center gap-2 text-sm font-medium text-yellow-400 hover:text-yellow-300 transition-colors"
                  >
                    查看全部
                    <ChevronRight className="h-4 w-4" />
                  </Link>
                </motion.div>

                <div className="grid gap-5 sm:grid-cols-2 md:grid-cols-3 lg:grid-cols-4">
                  {topRatedMovies.map((movie, index) => (
                    <motion.div
                      key={movie.id}
                      initial={{ opacity: 0, y: 20 }}
                      whileInView={{ opacity: 1, y: 0 }}
                      viewport={{ once: true }}
                      transition={{ delay: index * 0.05 }}
                    >
                      <Link 
                        href={`/movies/${movie.id}`}
                        className="group block"
                      >
                        <div className="relative overflow-hidden rounded-xl border border-yellow-500/20 bg-gradient-to-b from-yellow-500/5 to-transparent transition-all duration-300 group-hover:border-yellow-500/50 group-hover:shadow-lg group-hover:shadow-yellow-500/10">
                          <div className="relative aspect-[2/3] overflow-hidden">
                            {movie.poster_path ? (
                              <img 
                                src={`https://image.tmdb.org/t/p/w500${movie.poster_path}`}
                                alt={movie.title}
                                className="h-full w-full object-cover transition-transform duration-500 group-hover:scale-105"
                              />
                            ) : (
                              <div className="flex h-full w-full items-center justify-center bg-white/5">
                                <Clapperboard className="h-12 w-12 text-white/20" />
                              </div>
                            )}
                            <div className="absolute inset-0 bg-gradient-to-t from-black/80 via-black/20 to-transparent opacity-0 transition-opacity duration-300 group-hover:opacity-100" />
                            <div className="absolute top-3 left-3">
                              <div className="flex items-center gap-1 rounded-full bg-yellow-500/90 px-2.5 py-1 text-xs font-bold text-black">
                                <Award className="h-3 w-3" />
                                高分
                              </div>
                            </div>
                            {movie.vote_average && (
                              <div className="absolute top-3 right-3">
                                <div className="flex items-center gap-1 rounded-full bg-black/60 backdrop-blur-sm px-2.5 py-1 text-xs font-bold text-white">
                                  <Star className="h-3 w-3 fill-current text-yellow-400" />
                                  {movie.vote_average.toFixed(1)}
                                </div>
                              </div>
                            )}
                          </div>
                          <div className="p-3">
                            <h3 className="text-sm font-medium text-white truncate group-hover:text-yellow-300 transition-colors">
                              {movie.title}
                            </h3>
                            <p className="mt-1 text-xs text-white/50">
                              {movie.release_date?.split('-')[0] || '未知'}
                            </p>
                          </div>
                        </div>
                      </Link>
                    </motion.div>
                  ))}
                </div>
              </div>
            </section>
          )}

          {/* 热门电影 */}
          <section className="py-16 border-t border-white/5">
            <div className="mx-auto max-w-7xl px-4 sm:px-6 lg:px-8">
              <motion.div 
                initial={{ opacity: 0, y: 20 }}
                whileInView={{ opacity: 1, y: 0 }}
                viewport={{ once: true }}
                className="mb-10 flex items-center justify-between"
              >
                <div className="flex items-center gap-4">
                  <div className="flex h-12 w-12 items-center justify-center rounded-xl bg-gradient-to-br from-red-500/20 to-red-600/10 border border-red-500/20">
                    <Flame className="h-6 w-6 text-red-400" />
                  </div>
                  <div>
                    <h2 className="text-2xl font-bold text-white">热门电影</h2>
                    <p className="text-sm text-white/50">根据评分和人气统计的热门榜单</p>
                  </div>
                </div>
                <Link 
                  href="/search" 
                  className="flex items-center gap-2 text-sm font-medium text-red-400 hover:text-red-300 transition-colors"
                >
                  查看全部
                  <ChevronRight className="h-4 w-4" />
                </Link>
              </motion.div>

              {isLoading ? (
                <div className="grid gap-4 sm:grid-cols-2 md:grid-cols-3 lg:grid-cols-4">
                  {[1, 2, 3, 4].map((i) => (
                    <div key={i} className="group rounded-xl border border-white/5 bg-white/[0.03] p-3 animate-pulse">
                      <div className="aspect-[2/3] rounded-lg bg-white/5" />
                      <div className="mt-3 h-5 w-3/4 rounded bg-white/5" />
                      <div className="mt-2 h-4 w-1/2 rounded bg-white/5" />
                    </div>
                  ))}
                </div>
              ) : topPopularMovies.length > 0 ? (
                <div className="grid gap-5 sm:grid-cols-2 md:grid-cols-3 lg:grid-cols-4">
                  {topPopularMovies.map((movie, index) => (
                    <motion.div
                      key={movie.id}
                      initial={{ opacity: 0, y: 20 }}
                      whileInView={{ opacity: 1, y: 0 }}
                      viewport={{ once: true }}
                      transition={{ delay: index * 0.05 }}
                    >
                      <Link 
                        href={`/movies/${movie.id}`}
                        className="group block"
                      >
                        <div className="relative overflow-hidden rounded-xl border border-white/5 bg-gradient-to-b from-white/[0.05] to-white/[0.02] transition-all duration-300 group-hover:border-red-500/50 group-hover:shadow-lg group-hover:shadow-red-500/10">
                          {/* 海报 */}
                          <div className="relative aspect-[2/3] overflow-hidden">
                            {movie.poster_path ? (
                              <img 
                                src={`https://image.tmdb.org/t/p/w500${movie.poster_path}`}
                                alt={movie.title}
                                className="h-full w-full object-cover transition-transform duration-500 group-hover:scale-105"
                              />
                            ) : (
                              <div className="flex h-full w-full items-center justify-center bg-white/5">
                                <Clapperboard className="h-12 w-12 text-white/20" />
                              </div>
                            )}
                            
                            {/* 悬停遮罩 */}
                            <div className="absolute inset-0 bg-gradient-to-t from-black/80 via-black/20 to-transparent opacity-0 transition-opacity duration-300 group-hover:opacity-100" />
                            
                            {/* 播放按钮 */}
                            <div className="absolute inset-0 flex items-center justify-center opacity-0 transition-opacity duration-300 group-hover:opacity-100">
                              <div className="flex h-14 w-14 items-center justify-center rounded-full bg-red-600/90 shadow-lg shadow-red-600/50 backdrop-blur-sm">
                                <Play className="h-6 w-6 text-white ml-1" />
                              </div>
                            </div>

                            {/* 排名标签 */}
                            <div className="absolute top-3 left-3">
                              <div className="flex h-8 w-8 items-center justify-center rounded-lg bg-black/60 backdrop-blur-sm text-sm font-bold text-white border border-white/10">
                                #{index + 1}
                              </div>
                            </div>

                            {/* 评分标签 */}
                            {movie.vote_average && (
                              <div className="absolute top-3 right-3">
                                <div className="flex items-center gap-1 rounded-full bg-red-600/90 px-2.5 py-1 text-xs font-bold text-white shadow-lg">
                                  <Star className="h-3 w-3 fill-current" />
                                  {movie.vote_average.toFixed(1)}
                                </div>
                              </div>
                            )}
                          </div>

                          {/* 电影信息 */}
                          <div className="p-4">
                            <h3 className="font-semibold text-white truncate group-hover:text-red-300 transition-colors">
                              {movie.title}
                            </h3>
                            <div className="mt-2 flex items-center justify-between text-sm">
                              <span className="text-white/50">
                                {movie.release_date?.split('-')[0] || '未知年份'}
                              </span>
                              <div className="flex items-center gap-1 text-orange-400">
                                <TrendingUp className="h-3.5 w-3.5" />
                                <span className="text-xs">热门</span>
                              </div>
                            </div>
                          </div>
                        </div>
                      </Link>
                    </motion.div>
                  ))}
                </div>
              ) : (
                <div className="flex h-64 items-center justify-center rounded-2xl border border-white/5 bg-white/[0.03]">
                  <div className="text-center">
                    <Clapperboard className="mx-auto h-12 w-12 text-white/20" />
                    <p className="mt-4 text-white/50">暂无热门电影数据</p>
                    <p className="mt-1 text-sm text-white/30">请确保后端服务正在运行</p>
                  </div>
                </div>
              )}
            </div>
          </section>

          {/* 票房TOP */}
          {topBoxOfficeMovies.length > 0 && (
            <section className="py-16 border-t border-white/5">
              <div className="mx-auto max-w-7xl px-4 sm:px-6 lg:px-8">
                <motion.div 
                  initial={{ opacity: 0, y: 20 }}
                  whileInView={{ opacity: 1, y: 0 }}
                  viewport={{ once: true }}
                  className="mb-10 flex items-center justify-between"
                >
                  <div className="flex items-center gap-4">
                    <div className="flex h-12 w-12 items-center justify-center rounded-xl bg-gradient-to-br from-emerald-500/20 to-emerald-600/10 border border-emerald-500/20">
                      <DollarSign className="h-6 w-6 text-emerald-400" />
                    </div>
                    <div>
                      <h2 className="text-2xl font-bold text-white">票房榜单</h2>
                      <p className="text-sm text-white/50">全球票房最高的电影</p>
                    </div>
                  </div>
                  <Link 
                    href="/search" 
                    className="flex items-center gap-2 text-sm font-medium text-emerald-400 hover:text-emerald-300 transition-colors"
                  >
                    查看全部
                    <ChevronRight className="h-4 w-4" />
                  </Link>
                </motion.div>

                <div className="grid gap-5 sm:grid-cols-2 md:grid-cols-3 lg:grid-cols-4">
                  {topBoxOfficeMovies.map((movie, index) => (
                    <motion.div
                      key={movie.id}
                      initial={{ opacity: 0, y: 20 }}
                      whileInView={{ opacity: 1, y: 0 }}
                      viewport={{ once: true }}
                      transition={{ delay: index * 0.05 }}
                    >
                      <Link 
                        href={`/movies/${movie.id}`}
                        className="group block"
                      >
                        <div className="relative overflow-hidden rounded-xl border border-emerald-500/20 bg-gradient-to-b from-emerald-500/5 to-transparent transition-all duration-300 group-hover:border-emerald-500/50 group-hover:shadow-lg group-hover:shadow-emerald-500/10">
                          <div className="relative aspect-[2/3] overflow-hidden">
                            {movie.poster_path ? (
                              <img 
                                src={`https://image.tmdb.org/t/p/w500${movie.poster_path}`}
                                alt={movie.title}
                                className="h-full w-full object-cover transition-transform duration-500 group-hover:scale-105"
                              />
                            ) : (
                              <div className="flex h-full w-full items-center justify-center bg-white/5">
                                <Clapperboard className="h-12 w-12 text-white/20" />
                              </div>
                            )}
                            <div className="absolute inset-0 bg-gradient-to-t from-black/80 via-black/20 to-transparent opacity-0 transition-opacity duration-300 group-hover:opacity-100" />
                            <div className="absolute top-3 left-3">
                              <div className="flex items-center gap-1 rounded-full bg-emerald-500/90 px-2.5 py-1 text-xs font-bold text-white">
                                <DollarSign className="h-3 w-3" />
                                票房
                              </div>
                            </div>
                            {movie.vote_average && (
                              <div className="absolute top-3 right-3">
                                <div className="flex items-center gap-1 rounded-full bg-black/60 backdrop-blur-sm px-2.5 py-1 text-xs font-bold text-white">
                                  <Star className="h-3 w-3 fill-current text-yellow-400" />
                                  {movie.vote_average.toFixed(1)}
                                </div>
                              </div>
                            )}
                          </div>
                          <div className="p-3">
                            <h3 className="text-sm font-medium text-white truncate group-hover:text-emerald-300 transition-colors">
                              {movie.title}
                            </h3>
                            <p className="mt-1 text-xs text-white/50">
                              {movie.release_date?.split('-')[0] || '未知'}
                            </p>
                          </div>
                        </div>
                      </Link>
                    </motion.div>
                  ))}
                </div>
              </div>
            </section>
          )}

          {/* 底部 CTA */}
          <section className="py-20 border-t border-white/5">
            <div className="mx-auto max-w-4xl px-4 sm:px-6 lg:px-8 text-center">
              <motion.div
                initial={{ opacity: 0, y: 20 }}
                whileInView={{ opacity: 1, y: 0 }}
                viewport={{ once: true }}
              >
                <div className="inline-flex items-center gap-2 rounded-full border border-orange-500/30 bg-orange-500/10 px-4 py-1.5 mb-6">
                  <Tv2 className="h-3.5 w-3.5 text-orange-400" />
                  <span className="text-xs font-medium text-orange-300">更多精彩内容</span>
                </div>
                <h2 className="text-3xl font-bold text-white sm:text-4xl">
                  准备好探索电影世界了吗？
                </h2>
                <p className="mx-auto mt-4 max-w-xl text-white/50">
                  加入 MovieAI，发现专属于你的观影体验
                </p>
                <div className="mt-8 flex flex-wrap items-center justify-center gap-4">
                  <Link 
                    href="/search"
                    className="inline-flex items-center gap-2 rounded-xl bg-gradient-to-r from-red-600 to-red-700 px-6 py-3 text-sm font-medium text-white shadow-lg shadow-red-600/30 hover:from-red-500 hover:to-red-600 transition-all"
                  >
                    <Search className="h-4 w-4" />
                    开始探索
                  </Link>
                  <Link 
                    href="/auth/register"
                    className="inline-flex items-center gap-2 rounded-xl border border-white/10 bg-white/5 px-6 py-3 text-sm font-medium text-white hover:bg-white/10 transition-all"
                  >
                    创建账号
                  </Link>
                </div>
              </motion.div>
            </div>
          </section>
        </div>

        {/* 页脚 */}
        <footer className="border-t border-white/5 py-8">
          <div className="mx-auto max-w-7xl px-4 sm:px-6 lg:px-8">
            <div className="flex flex-col items-center justify-between gap-4 sm:flex-row">
              <div className="flex items-center gap-2">
                <div className="h-8 w-8 rounded-lg bg-gradient-to-br from-red-600 to-red-700 flex items-center justify-center">
                  <Clapperboard className="h-4 w-4 text-white" />
                </div>
                <span className="text-sm text-white/50">
                  © 2024 MovieAI. 基于 TMDB API 构建
                </span>
              </div>
              <div className="flex items-center gap-6 text-sm text-white/40">
                <Link href="#" className="hover:text-white transition-colors">关于我们</Link>
                <Link href="#" className="hover:text-white transition-colors">隐私政策</Link>
                <Link href="#" className="hover:text-white transition-colors">使用条款</Link>
              </div>
            </div>
          </div>
        </footer>

        {/* AI 助手悬浮按钮 */}
        <Link
          href="/chat"
          className="fixed bottom-6 right-6 flex h-14 w-14 items-center justify-center rounded-full bg-gradient-to-br from-red-600 to-red-700 shadow-lg shadow-red-600/30 transition-all hover:scale-105 hover:shadow-red-600/50 group"
        >
          <div className="relative">
            <Sparkles className="h-6 w-6 text-white" />
            <div className="absolute -inset-2 rounded-full bg-red-500 opacity-0 blur transition-opacity group-hover:opacity-50" />
          </div>
        </Link>
      </main>
    </div>
  );
}
