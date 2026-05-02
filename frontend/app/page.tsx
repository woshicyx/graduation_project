"use client";

import Link from "next/link";
import { useState, useEffect } from "react";
import { motion } from "framer-motion";
import { getRandomMovies, getTopRatedMovies, getTopPopularMovies, getTopBoxOfficeMovies, MovieListItem } from "@/lib/api/movie";
import HeroBackground from "@/components/HeroBackground";

// Fisher-Yates 洗牌算法
const shuffleArray = <T,>(array: T[]): T[] => {
  const shuffled = [...array];
  for (let i = shuffled.length - 1; i > 0; i--) {
    const j = Math.floor(Math.random() * (i + 1));
    [shuffled[i], shuffled[j]] = [shuffled[j], shuffled[i]];
  }
  return shuffled;
};
import { getPersonalizedRecommendations } from "@/lib/api/personalized";
import { Heart, X } from "lucide-react";
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
  TrendingUp as TrendingUpIcon,
  Loader2,
  Send
} from "lucide-react";

export default function Home() {
  const [aiRecommendMovies, setAiRecommendMovies] = useState<MovieListItem[]>([]);
  const [topRatedMovies, setTopRatedMovies] = useState<MovieListItem[]>([]);
  const [topPopularMovies, setTopPopularMovies] = useState<MovieListItem[]>([]);
  const [topBoxOfficeMovies, setTopBoxOfficeMovies] = useState<MovieListItem[]>([]);
  const [forYouMovies, setForYouMovies] = useState<MovieListItem[]>([]);
  const [isLoading, setIsLoading] = useState(true);
  
  // 展开状态
  const [expandedSections, setExpandedSections] = useState<Record<string, boolean>>({});
  
  // Top50轮播状态
  const [currentTop50Page, setCurrentTop50Page] = useState(0);
  const MOVIES_PER_PAGE = 10;
  const CARSOUSEL_INTERVAL = 5000; // 5秒

  useEffect(() => {
    // 并行获取多种类型的电影
    Promise.all([
      getRandomMovies(10).catch(() => []),
      getTopRatedMovies(50).catch(() => []),
      getTopPopularMovies(50).catch(() => []),
      getTopBoxOfficeMovies(50).catch(() => []),
      getPersonalizedRecommendations(10).catch(() => []),
    ])
      .then(([aiRecommend, topRated, topPopular, topBoxOffice, forYou]) => {
        setAiRecommendMovies(aiRecommend);
        // 初始化时对Top50随机打乱，每次访问显示不同的电影
        setTopRatedMovies(shuffleArray(topRated));
        setTopPopularMovies(shuffleArray(topPopular));
        setTopBoxOfficeMovies(shuffleArray(topBoxOffice));
        setForYouMovies(forYou);
        setIsLoading(false);
      })
      .catch((err) => {
        console.error("获取电影数据失败:", err);
        setIsLoading(false);
      });
  }, []);

  // 切换展开/收起
  const toggleExpand = (section: string) => {
    setExpandedSections(prev => ({
      ...prev,
      [section]: !prev[section]
    }));
  };

  // 获取显示的电影（根据展开状态或轮播页码）
  const getDisplayMovies = (movies: MovieListItem[], section: string) => {
    // 如果是轮播区域，使用轮播页码
    if (section === 'carousel') {
      const start = currentTop50Page * MOVIES_PER_PAGE;
      return movies.slice(start, start + MOVIES_PER_PAGE);
    }
    // 其他区域使用展开状态
    if (expandedSections[section]) {
      return movies;  // 显示全部
    }
    return movies.slice(0, 10);  // 显示前10部
  };

  // Top50轮播定时器
  useEffect(() => {
    const hasEnoughMovies = topRatedMovies.length >= MOVIES_PER_PAGE || 
                           topPopularMovies.length >= MOVIES_PER_PAGE || 
                           topBoxOfficeMovies.length >= MOVIES_PER_PAGE;
    
    if (!hasEnoughMovies || Object.values(expandedSections).some(v => v)) return;
    
    const interval = setInterval(() => {
      setCurrentTop50Page(prev => prev + 1);
    }, CARSOUSEL_INTERVAL);
    
    return () => clearInterval(interval);
  }, [topRatedMovies, topPopularMovies, topBoxOfficeMovies, expandedSections]);
  
  // 重置轮播页码当切换到展开模式
  useEffect(() => {
    if (Object.values(expandedSections).some(v => v)) {
      setCurrentTop50Page(0);
    }
  }, [expandedSections]);

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
        {/* 导航栏 - 透明悬浮，与海报墙融为一体 */}
        <header className="absolute w-full z-50 top-0 bg-transparent">
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

              {/* 导航链接 - 首页、电影、个人中心 */}
              <nav className="hidden md:flex items-center gap-8">
                <Link href="/" className="text-sm font-medium text-white hover:text-red-400 transition-colors">
                  首页
                </Link>
                <Link href="/movies" className="text-sm font-medium text-white/70 hover:text-red-400 transition-colors">
                  电影
                </Link>
              </nav>

              {/* 右侧操作 - 根据登录状态显示不同内容 */}
              <div className="flex items-center gap-4">
                <Link 
                  href="/search"
                  className="flex items-center gap-2 rounded-full bg-white/5 px-4 py-2 text-sm text-white/70 border border-white/10 hover:bg-white/10 hover:text-white transition-all"
                >
                  <Search className="h-4 w-4" />
                  <span className="hidden sm:inline">搜索电影...</span>
                </Link>
                <Link 
                  href="/profile" 
                  className="rounded-lg bg-gradient-to-r from-red-600 to-rose-600 px-5 py-2 text-sm font-bold text-white shadow-lg shadow-red-900/50 hover:brightness-110 hover:shadow-red-600/50 active:scale-95 transition-all"
                >
                  个人中心
                </Link>
              </div>
            </div>
          </div>
        </header>

        {/* 主要内容区域 */}
        <div className="flex-1">
        {/* 英雄区域 - Netflix 风格虚化电影背景 */}
          <section className="relative min-h-[85vh] overflow-hidden">
            {/* Hero背景组件 */}
            <HeroBackground />
            
            <div className="mx-auto max-w-7xl px-4 sm:px-6 lg:px-8">
              <motion.div 
                initial={{ opacity: 0, y: 20 }}
                animate={{ opacity: 1, y: 0 }}
                transition={{ duration: 0.6 }}
                className="text-center"
              >
                {/* 标签 - 增加上方间距，呼吸感 */}
                <div className="inline-flex items-center gap-2 rounded-full border border-red-500/30 bg-red-500/10 px-4 py-1.5 mb-8">
                  <Sparkles className="h-3.5 w-3.5 text-red-400" />
                  <span className="text-xs font-medium text-red-300">AI 驱动的智能推荐</span>
                </div>

                {/* 主标题 - 柔和发光，净化边缘 */}
                <h1 
                  className="text-4xl font-bold tracking-tight sm:text-5xl lg:text-7xl drop-shadow-[0_2px_20px_rgba(0,0,0,0.8)]"
                >
                  <span className="text-white">发现你的</span>
                  <span className="text-white">下一部电影</span>
                </h1>

                {/* 副标题 - 提亮 */}
                <p 
                  className="mx-auto mt-6 max-w-2xl text-lg text-gray-100 drop-shadow-[0_1px_10px_rgba(0,0,0,0.5)]"
                >
                  基于先进的 AI 技术，为你推荐最适合的电影和剧集
                </p>

                {/* 搜索框 */}
                <div className="mt-10 mx-auto max-w-2xl">
                  <Link href="/search">
                    <div className="group relative flex items-center rounded-2xl border border-white/20 bg-white/10 p-2 backdrop-blur-xl transition-all hover:border-red-500/50 hover:bg-white/15">
                      <div className="flex h-12 w-12 items-center justify-center rounded-xl bg-gradient-to-br from-red-600 to-red-700">
                        <Search className="h-5 w-5 text-white" />
                      </div>
                      <div className="ml-4 flex-1 text-left">
                        <p className="text-sm font-medium text-gray-100 group-hover:text-white">
                          搜索电影、导演、类型...
                        </p>
                        <p className="text-xs text-gray-400">
                          试试 "科幻电影" 或 "诺兰导演"
                        </p>
                      </div>
                      <div className="flex items-center gap-2">
                        <span className="hidden sm:inline-flex items-center gap-1 rounded-full bg-white/10 px-3 py-1 text-xs text-gray-200">
                          <Star className="h-3 w-3" />
                          AI 推荐
                        </span>
                        <div className="flex h-10 w-10 items-center justify-center rounded-xl bg-white/10 text-gray-200 group-hover:bg-red-600 group-hover:text-white transition-colors">
                          <ChevronRight className="h-5 w-5" />
                        </div>
                      </div>
                    </div>
                  </Link>
                </div>

                {/* 统计信息 - 玻璃拟态背景 */}
                <div 
                  className="mt-12 flex flex-wrap items-center justify-center gap-8 px-8 py-6 rounded-2xl"
                  style={{
                    background: 'rgba(255, 255, 255, 0.05)',
                    backdropFilter: 'blur(12px)',
                    border: '1px solid rgba(255, 255, 255, 0.1)',
                    boxShadow: '0 8px 32px rgba(0, 0, 0, 0.3)'
                  }}
                >
                  <div className="text-center">
                    <div className="text-2xl font-bold text-gray-100" style={{ textShadow: '0 2px 10px rgba(0,0,0,0.5)' }}>8,000+</div>
                    <div className="text-sm text-gray-400">电影资源</div>
                  </div>
                  <div className="h-8 w-px bg-white/20" />
                  <div className="text-center">
                    <div className="text-2xl font-bold text-gray-100" style={{ textShadow: '0 2px 10px rgba(0,0,0,0.5)' }}>AI</div>
                    <div className="text-sm text-gray-400">智能推荐</div>
                  </div>
                  <div className="h-8 w-px bg-white/20" />
                  <div className="text-center">
                    <div className="text-2xl font-bold text-gray-100" style={{ textShadow: '0 2px 10px rgba(0,0,0,0.5)' }}>24/7</div>
                    <div className="text-sm text-gray-400">随时发现</div>
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
                    查看更多
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
                              <div className="w-full h-full bg-gradient-to-br from-gray-800 via-gray-900 to-[#1a1014] ring-1 ring-inset ring-white/5 flex flex-col items-center justify-center p-4">
                                <span className="text-center text-xl font-black text-white/70 leading-snug tracking-wider shadow-black drop-shadow-lg line-clamp-4">
                                  {movie.title}
                                </span>
                                <div className="w-8 h-0.5 bg-pink-500/50 mt-4 rounded-full" />
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
                {topRatedMovies.length > 10 && (
                  <Link
                    href="/movies"
                    className="flex items-center gap-2 text-sm font-medium text-yellow-400 hover:text-yellow-300 transition-colors"
                  >
                    查看更多
                    <ChevronRight className="h-4 w-4" />
                  </Link>
                )}
                </motion.div>

                <div className="grid gap-5 sm:grid-cols-2 md:grid-cols-3 lg:grid-cols-4 xl:grid-cols-5">
                  {getDisplayMovies(topRatedMovies, 'rated').map((movie, index) => (
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
                              <div className="w-full h-full bg-gradient-to-br from-gray-800 via-gray-900 to-[#1a1014] ring-1 ring-inset ring-white/5 flex flex-col items-center justify-center p-4">
                                <span className="text-center text-xl font-black text-white/70 leading-snug tracking-wider shadow-black drop-shadow-lg line-clamp-4">
                                  {movie.title}
                                </span>
                                <div className="w-8 h-0.5 bg-pink-500/50 mt-4 rounded-full" />
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

          {/* 猜你喜欢 */}
          {forYouMovies.length > 0 && (
            <section className="py-16 border-t border-white/5">
              <div className="mx-auto max-w-7xl px-4 sm:px-6 lg:px-8">
                <motion.div 
                  initial={{ opacity: 0, y: 20 }}
                  whileInView={{ opacity: 1, y: 0 }}
                  viewport={{ once: true }}
                  className="mb-10 flex items-center justify-between"
                >
                  <div className="flex items-center gap-4">
                    <div className="flex h-12 w-12 items-center justify-center rounded-xl bg-gradient-to-br from-pink-500/20 to-pink-600/10 border border-pink-500/20">
                      <Heart className="h-6 w-6 text-pink-400" />
                    </div>
                    <div>
                      <h2 className="text-2xl font-bold text-white">猜你喜欢</h2>
                      <p className="text-sm text-white/50">基于你的偏好为你推荐</p>
                    </div>
                  </div>
                  <Link 
                    href="/auth/login" 
                    className="flex items-center gap-2 text-sm font-medium text-pink-400 hover:text-pink-300 transition-colors"
                  >
                    登录后获取更多
                    <ChevronRight className="h-4 w-4" />
                  </Link>
                </motion.div>

                <div className="grid gap-5 sm:grid-cols-2 md:grid-cols-3 lg:grid-cols-4 xl:grid-cols-5">
                  {forYouMovies.map((movie, index) => (
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
                        <div className="relative overflow-hidden rounded-xl border border-pink-500/20 bg-gradient-to-b from-pink-500/5 to-transparent transition-all duration-300 group-hover:border-pink-500/50 group-hover:shadow-lg group-hover:shadow-pink-500/10">
                          <div className="relative aspect-[2/3] overflow-hidden">
                            {movie.poster_path ? (
                              <img 
                                src={`https://image.tmdb.org/t/p/w500${movie.poster_path}`}
                                alt={movie.title}
                                className="h-full w-full object-cover transition-transform duration-500 group-hover:scale-105"
                              />
                            ) : (
                              <div className="w-full h-full bg-gradient-to-br from-gray-800 via-gray-900 to-[#1a1014] ring-1 ring-inset ring-white/5 flex flex-col items-center justify-center p-4">
                                <span className="text-center text-xl font-black text-white/70 leading-snug tracking-wider shadow-black drop-shadow-lg line-clamp-4">
                                  {movie.title}
                                </span>
                                <div className="w-8 h-0.5 bg-pink-500/50 mt-4 rounded-full" />
                              </div>
                            )}
                            <div className="absolute inset-0 bg-gradient-to-t from-black/80 via-black/20 to-transparent opacity-0 transition-opacity duration-300 group-hover:opacity-100" />
                            <div className="absolute top-3 left-3">
                              <div className="flex items-center gap-1 rounded-full bg-pink-500/90 px-2.5 py-1 text-xs font-bold text-white">
                                <Heart className="h-3 w-3" />
                                精选
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
                            <h3 className="text-sm font-medium text-white truncate group-hover:text-pink-300 transition-colors">
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
                {topPopularMovies.length > 10 && (
                  <Link
                    href="/movies?sort=popular"
                    className="flex items-center gap-2 text-sm font-medium text-red-400 hover:text-red-300 transition-colors"
                  >
                    查看更多
                    <ChevronRight className="h-4 w-4" />
                  </Link>
                )}
              </motion.div>

              {isLoading ? (
                <div className="grid gap-5 sm:grid-cols-2 md:grid-cols-3 lg:grid-cols-4 xl:grid-cols-5">
                  {[1, 2, 3, 4, 5, 6, 7, 8, 9, 10].map((i) => (
                    <div key={i} className="group rounded-xl border border-white/5 bg-white/[0.03] p-3 overflow-hidden">
                      <div className="aspect-[2/3] rounded-lg bg-gray-800/50 animate-pulse relative">
                        {/* 骨架屏暗角效果 */}
                        <div className="absolute inset-0 bg-gradient-to-t from-black/40 via-transparent to-transparent" />
                      </div>
                      <div className="mt-3 h-5 w-3/4 rounded bg-gray-800/50 animate-pulse" />
                      <div className="mt-2 h-4 w-1/2 rounded bg-gray-800/30 animate-pulse" />
                    </div>
                  ))}
                </div>
              ) : topPopularMovies.length > 0 ? (
                <div className="grid gap-5 sm:grid-cols-2 md:grid-cols-3 lg:grid-cols-4 xl:grid-cols-5">
                  {topPopularMovies.slice(0, 10).map((movie, index) => (
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
                              <div className="w-full h-full bg-gradient-to-br from-gray-800 via-gray-900 to-[#1a1014] ring-1 ring-inset ring-white/5 flex flex-col items-center justify-center p-4">
                                <span className="text-center text-xl font-black text-white/70 leading-snug tracking-wider shadow-black drop-shadow-lg line-clamp-4">
                                  {movie.title}
                                </span>
                                <div className="w-8 h-0.5 bg-pink-500/50 mt-4 rounded-full" />
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
                  {topBoxOfficeMovies.length > 10 && (
                    <Link
                      href="/movies?sort=boxoffice"
                      className="flex items-center gap-2 text-sm font-medium text-emerald-400 hover:text-emerald-300 transition-colors"
                    >
                      查看更多
                      <ChevronRight className="h-4 w-4" />
                    </Link>
                  )}
                </motion.div>

                <div className="grid gap-5 sm:grid-cols-2 md:grid-cols-3 lg:grid-cols-4 xl:grid-cols-5">
                  {topBoxOfficeMovies.slice(0, 10).map((movie, index) => (
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
                              <div className="w-full h-full bg-gradient-to-br from-gray-800 via-gray-900 to-[#1a1014] ring-1 ring-inset ring-white/5 flex flex-col items-center justify-center p-4">
                                <span className="text-center text-xl font-black text-white/70 leading-snug tracking-wider shadow-black drop-shadow-lg line-clamp-4">
                                  {movie.title}
                                </span>
                                <div className="w-8 h-0.5 bg-pink-500/50 mt-4 rounded-full" />
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
                    className="inline-flex items-center gap-2 rounded-xl bg-gradient-to-r from-red-600 to-rose-600 px-6 py-3 text-sm font-bold text-white shadow-lg shadow-red-900/50 hover:brightness-110 hover:shadow-red-600/50 active:scale-95 transition-all"
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

        {/* 页脚 - 增强版 */}
        <footer className="border-t border-white/5 bg-gradient-to-b from-transparent to-black/20">
          <div className="mx-auto max-w-7xl px-4 sm:px-6 lg:px-8 py-16">
            {/* 主要内容区域 */}
            <div className="grid gap-12 md:grid-cols-4">
              {/* 品牌区域 */}
              <div className="md:col-span-1">
                <Link href="/" className="flex items-center gap-3 mb-4">
                  <div className="h-10 w-10 rounded-lg bg-gradient-to-br from-red-600 to-red-700 flex items-center justify-center">
                    <Clapperboard className="h-5 w-5 text-white" />
                  </div>
                  <div className="flex items-baseline gap-1">
                    <span className="text-lg font-bold text-white">Movie</span>
                    <span className="text-lg font-bold text-red-500">AI</span>
                  </div>
                </Link>
                <p className="text-sm text-white/50 leading-relaxed">
                  基于先进的 AI 技术，为你推荐最适合的电影和剧集。发现你的下一部心仪之作。
                </p>
                {/* 社交媒体 */}
                <div className="flex items-center gap-4 mt-6">
                  <Link href="#" className="h-10 w-10 rounded-full bg-white/5 flex items-center justify-center text-white/50 hover:bg-red-600 hover:text-white transition-all">
                    <svg className="h-5 w-5" fill="currentColor" viewBox="0 0 24 24"><path d="M18.244 2.25h3.308l-7.227 8.26 8.502 11.24H16.17l-5.214-6.817L4.99 21.75H1.68l7.73-8.835L1.254 2.25H8.08l4.713 6.231zm-1.161 17.52h1.833L7.084 4.126H5.117z"/></svg>
                  </Link>
                  <Link href="#" className="h-10 w-10 rounded-full bg-white/5 flex items-center justify-center text-white/50 hover:bg-red-600 hover:text-white transition-all">
                    <svg className="h-5 w-5" fill="currentColor" viewBox="0 0 24 24"><path d="M12 2C6.477 2 2 6.477 2 12c0 4.991 3.657 9.128 8.438 9.879V14.89h-2.54V12h2.54V9.797c0-2.506 1.492-3.89 3.777-3.89 1.094 0 2.238.195 2.238.195v2.46h-1.26c-1.243 0-1.63.771-1.63 1.562V12h2.773l-.443 2.89h-2.33v6.989C18.343 21.129 22 16.99 22 12c0-5.523-4.477-10-10-10z"/></svg>
                  </Link>
                  <Link href="#" className="h-10 w-10 rounded-full bg-white/5 flex items-center justify-center text-white/50 hover:bg-red-600 hover:text-white transition-all">
                    <svg className="h-5 w-5" fill="currentColor" viewBox="0 0 24 24"><path d="M12 2.163c3.204 0 3.584.012 4.85.07 3.252.148 4.771 1.691 4.919 4.919.058 1.265.069 1.645.069 4.849 0 3.205-.012 3.584-.069 4.849-.149 3.225-1.664 4.771-4.919 4.919-1.266.058-1.644.07-4.85.07-3.204 0-3.584-.012-4.849-.07-3.26-.149-4.771-1.699-4.919-4.92-.058-1.265-.07-1.644-.07-4.849 0-3.204.013-3.583.07-4.849.149-3.227 1.664-4.771 4.919-4.919 1.266-.057 1.645-.069 4.849-.069zM12 0C8.741 0 8.333.014 7.053.072 2.695.272.273 2.69.073 7.052.014 8.333 0 8.741 0 12c0 3.259.014 3.668.072 4.948.2 4.358 2.618 6.78 6.98 6.98C8.333 23.986 8.741 24 12 24c3.259 0 3.668-.014 4.948-.072 4.354-.2 6.782-2.618 6.979-6.98.059-1.28.073-1.689.073-4.948 0-3.259-.014-3.667-.072-4.947-.196-4.354-2.617-6.78-6.979-6.98C15.668.014 15.259 0 12 0zm0 5.838a6.162 6.162 0 100 12.324 6.162 6.162 0 000-12.324zM12 16a4 4 0 110-8 4 4 0 010 8zm6.406-11.845a1.44 1.44 0 100 2.881 1.44 1.44 0 000-2.881z"/></svg>
                  </Link>
                </div>
              </div>

              {/* 快速链接 */}
              <div>
                <h4 className="text-sm font-semibold text-white mb-4">探索</h4>
                <ul className="space-y-3">
                  <li><Link href="/movies" className="text-sm text-white/50 hover:text-red-400 transition-colors">电影库</Link></li>
                  <li><Link href="/search" className="text-sm text-white/50 hover:text-red-400 transition-colors">搜索</Link></li>
                  <li><Link href="/chat" className="text-sm text-white/50 hover:text-red-400 transition-colors">AI 助手</Link></li>
                  <li><Link href="/profile" className="text-sm text-white/50 hover:text-red-400 transition-colors">个人中心</Link></li>
                </ul>
              </div>

              {/* 收藏 */}
              <div>
                <h4 className="text-sm font-semibold text-white mb-4">我的收藏</h4>
                <ul className="space-y-3">
                  <li><Link href="/favorites" className="text-sm text-white/50 hover:text-red-400 transition-colors">我的收藏</Link></li>
                  <li><Link href="/history" className="text-sm text-white/50 hover:text-red-400 transition-colors">观看历史</Link></li>
                  <li><Link href="/auth/login" className="text-sm text-white/50 hover:text-red-400 transition-colors">登录账号</Link></li>
                  <li><Link href="/auth/register" className="text-sm text-white/50 hover:text-red-400 transition-colors">注册账号</Link></li>
                </ul>
              </div>

              {/* 关于我们 */}
              <div>
                <h4 className="text-sm font-semibold text-white mb-4">关于</h4>
                <ul className="space-y-3">
                  <li><Link href="#" className="text-sm text-white/50 hover:text-red-400 transition-colors">关于我们</Link></li>
                  <li><Link href="#" className="text-sm text-white/50 hover:text-red-400 transition-colors">使用条款</Link></li>
                  <li><Link href="#" className="text-sm text-white/50 hover:text-red-400 transition-colors">隐私政策</Link></li>
                  <li><Link href="#" className="text-sm text-white/50 hover:text-red-400 transition-colors">联系我们</Link></li>
                </ul>
              </div>
            </div>

            {/* 底部版权 */}
            <div className="mt-12 pt-8 border-t border-white/5">
              <div className="flex flex-col md:flex-row items-center justify-between gap-4">
                <p className="text-sm text-white/40">
                  © 2024 MovieAI. 基于 TMDB API 构建 · 电影数据来源于 TMDB
                </p>
                <div className="flex items-center gap-2 text-sm text-white/30">
                  <span>Made with</span>
                  <Heart className="h-4 w-4 fill-red-500 text-red-500" />
                  <span>using AI</span>
                </div>
              </div>
            </div>
          </div>
        </footer>

        {/* AI 助手悬浮按钮 */}
        <Link
          href="/chat"
          className="fixed bottom-6 right-6 flex h-14 w-14 items-center justify-center rounded-full bg-gradient-to-r from-red-600 to-rose-600 shadow-lg shadow-red-900/50 transition-all hover:scale-110 hover:shadow-red-600/50 hover:brightness-110 active:scale-95 group"
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
