"use client";

import { useState, useEffect, useRef } from "react";
import Link from "next/link";
import { Star, TrendingUp, DollarSign, Play, Heart, Loader2 } from "lucide-react";
import { motion } from "framer-motion";
import { Movie } from "@/lib/api/movies";
import { useTopBoxOffice, useTopRated } from "@/hooks/useMovies";
import {
  Carousel,
  CarouselContent,
  CarouselItem,
  CarouselNext,
  CarouselPrevious,
} from "@/components/ui/carousel";
import {
  Card,
  CardContent,
  CardDescription,
  CardHeader,
  CardTitle,
} from "@/components/ui/card";
import { Button } from "@/components/ui/button";

type MovieCarouselProps = {
  title: string;
  subtitle?: string;
  variant: "boxOffice" | "rating";
  limit?: number;
};

export function MovieCarousel({
  title,
  subtitle,
  variant,
  limit = 12,
}: MovieCarouselProps) {
  const [isHovered, setIsHovered] = useState(false);
  const [favorites, setFavorites] = useState<Set<string>>(new Set());
  const carouselRef = useRef<HTMLDivElement>(null);

  // 使用React Query获取数据
  const { 
    data: boxOfficeData, 
    isLoading: isLoadingBoxOffice,
    error: boxOfficeError 
  } = useTopBoxOffice({ limit });
  
  const { 
    data: ratedData, 
    isLoading: isLoadingRated,
    error: ratedError 
  } = useTopRated({ limit });

  const isLoading = variant === "boxOffice" ? isLoadingBoxOffice : isLoadingRated;
  const error = variant === "boxOffice" ? boxOfficeError : ratedError;
  const movies = variant === "boxOffice" 
    ? (boxOfficeData?.items || [])
    : (ratedData?.items || []);

  // 自动轮播效果
  useEffect(() => {
    if (isHovered || !carouselRef.current || movies.length === 0) return;

    const interval = setInterval(() => {
      const nextButton = carouselRef.current?.querySelector(
        "[data-carousel-next]"
      ) as HTMLButtonElement;
      if (nextButton && !nextButton.disabled) {
        nextButton.click();
      }
    }, 5000);

    return () => clearInterval(interval);
  }, [isHovered, movies.length]);

  const toggleFavorite = (movieId: string) => {
    setFavorites((prev) => {
      const newFavorites = new Set(prev);
      if (newFavorites.has(movieId)) {
        newFavorites.delete(movieId);
      } else {
        newFavorites.add(movieId);
      }
      return newFavorites;
    });
  };

  // 加载状态
  if (isLoading) {
    return (
      <section className="mx-auto mb-12 mt-6 w-full max-w-6xl">
        <div className="mb-6 flex flex-col items-start justify-between gap-4 px-2 sm:flex-row sm:items-center sm:px-0">
          <div>
            <div className="flex items-center gap-3">
              <div className={`rounded-xl p-2.5 ${variant === "boxOffice" ? "bg-gradient-to-br from-red-500/20 to-red-600/10 border border-red-500/20" : "bg-gradient-to-br from-orange-500/20 to-orange-600/10 border border-orange-500/20"}`}>
                {variant === "boxOffice" ? (
                  <DollarSign className="h-5 w-5 text-red-400" />
                ) : (
                  <TrendingUp className="h-5 w-5 text-orange-400" />
                )}
              </div>
              <div>
                <h3 className="text-xl font-bold text-white sm:text-2xl">
                  {title}
                </h3>
                {subtitle && (
                  <p className="mt-1 text-sm text-white/50 sm:text-base">
                    {subtitle}
                  </p>
                )}
              </div>
            </div>
          </div>
        </div>
        <div className="flex h-64 items-center justify-center rounded-2xl bg-gradient-to-b from-white/[0.03] to-transparent border border-white/5">
          <div className="flex flex-col items-center gap-3">
            <Loader2 className="h-8 w-8 animate-spin text-red-500" />
            <p className="text-sm text-white/50">正在加载电影数据...</p>
          </div>
        </div>
      </section>
    );
  }

  // 错误状态
  if (error) {
    return (
      <section className="mx-auto mb-12 mt-6 w-full max-w-6xl">
        <div className="mb-6 flex flex-col items-start justify-between gap-4 px-2 sm:flex-row sm:items-center sm:px-0">
          <div>
            <div className="flex items-center gap-3">
              <div className={`rounded-xl p-2.5 ${variant === "boxOffice" ? "bg-gradient-to-br from-red-500/20 to-red-600/10 border border-red-500/20" : "bg-gradient-to-br from-orange-500/20 to-orange-600/10 border border-orange-500/20"}`}>
                {variant === "boxOffice" ? (
                  <DollarSign className="h-5 w-5 text-red-400" />
                ) : (
                  <TrendingUp className="h-5 w-5 text-orange-400" />
                )}
              </div>
              <div>
                <h3 className="text-xl font-bold text-white sm:text-2xl">
                  {title}
                </h3>
                {subtitle && (
                  <p className="mt-1 text-sm text-white/50 sm:text-base">
                    {subtitle}
                  </p>
                )}
              </div>
            </div>
          </div>
        </div>
        <div className="flex h-64 items-center justify-center rounded-2xl bg-gradient-to-b from-red-500/5 to-transparent border border-red-500/20">
          <div className="flex flex-col items-center gap-3">
            <p className="text-red-400">加载电影数据失败</p>
            <p className="text-sm text-white/50">请检查后端API连接</p>
          </div>
        </div>
      </section>
    );
  }

  // 空数据状态
  if (movies.length === 0) {
    return (
      <section className="mx-auto mb-12 mt-6 w-full max-w-6xl">
        <div className="mb-6 flex flex-col items-start justify-between gap-4 px-2 sm:flex-row sm:items-center sm:px-0">
          <div>
            <div className="flex items-center gap-3">
              <div className={`rounded-xl p-2.5 ${variant === "boxOffice" ? "bg-gradient-to-br from-red-500/20 to-red-600/10 border border-red-500/20" : "bg-gradient-to-br from-orange-500/20 to-orange-600/10 border border-orange-500/20"}`}>
                {variant === "boxOffice" ? (
                  <DollarSign className="h-5 w-5 text-red-400" />
                ) : (
                  <TrendingUp className="h-5 w-5 text-orange-400" />
                )}
              </div>
              <div>
                <h3 className="text-xl font-bold text-white sm:text-2xl">
                  {title}
                </h3>
                {subtitle && (
                  <p className="mt-1 text-sm text-white/50 sm:text-base">
                    {subtitle}
                  </p>
                )}
              </div>
            </div>
          </div>
        </div>
        <div className="flex h-64 items-center justify-center rounded-2xl bg-gradient-to-b from-white/[0.03] to-transparent border border-white/5">
          <p className="text-white/50">暂无电影数据</p>
        </div>
      </section>
    );
  }

  return (
    <section 
      className="mx-auto mb-12 mt-6 w-full max-w-6xl"
      onMouseEnter={() => setIsHovered(true)}
      onMouseLeave={() => setIsHovered(false)}
    >
      {/* 标题区域 */}
      <div className="mb-6 flex flex-col items-start justify-between gap-4 px-2 sm:flex-row sm:items-center sm:px-0">
        <div>
          <div className="flex items-center gap-3">
            <div className={`rounded-xl p-2.5 ${variant === "boxOffice" ? "bg-gradient-to-br from-red-500/20 to-red-600/10 border border-red-500/20" : "bg-gradient-to-br from-orange-500/20 to-orange-600/10 border border-orange-500/20"}`}>
              {variant === "boxOffice" ? (
                <DollarSign className="h-5 w-5 text-red-400" />
              ) : (
                <TrendingUp className="h-5 w-5 text-orange-400" />
              )}
            </div>
            <div>
              <h3 className="text-xl font-bold text-white sm:text-2xl">
                {title}
              </h3>
              {subtitle && (
                <p className="mt-1 text-sm text-white/50 sm:text-base">
                  {subtitle}
                </p>
              )}
            </div>
          </div>
        </div>
        
        <div className="flex items-center gap-3">
          <span className="text-xs text-white/40">
            共 {movies.length} 部电影
          </span>
          <div className="flex gap-1">
            <div className="h-1 w-6 rounded-full bg-gradient-to-r from-red-600 to-red-500" />
            <div className="h-1 w-2 rounded-full bg-white/10" />
            <div className="h-1 w-2 rounded-full bg-white/10" />
          </div>
        </div>
      </div>

      {/* 轮播区域 */}
      <div ref={carouselRef}>
        <Carousel className="relative">
          <CarouselContent className="-ml-2 md:-ml-4">
            {movies.map((movie, index) => (
              <CarouselItem
                key={movie.id}
                className="basis-3/4 pl-2 sm:basis-1/2 md:basis-1/3 md:pl-4 lg:basis-1/4"
              >
                <motion.div
                  initial={{ opacity: 0, y: 20 }}
                  whileInView={{ opacity: 1, y: 0 }}
                  viewport={{ once: true, amount: 0.3 }}
                  transition={{ duration: 0.4, delay: index * 0.05 }}
                  whileHover={{ y: -8 }}
                  className="group relative"
                >
                  {/* 收藏按钮 */}
                  <button
                    onClick={() => toggleFavorite(movie.id)}
                    className="absolute right-3 top-3 z-10 rounded-full bg-black/60 backdrop-blur-sm p-2 transition-all hover:scale-110 hover:bg-red-500/80 border border-white/10"
                    aria-label={favorites.has(movie.id) ? "取消收藏" : "收藏"}
                  >
                    <Heart
                      className={`h-4 w-4 transition-colors ${
                        favorites.has(movie.id)
                          ? "fill-red-500 text-red-500"
                          : "text-white/80"
                      }`}
                    />
                  </button>

                  <Link href={`/movies/${movie.id}`}>
                    <Card className="overflow-hidden border border-white/5 bg-gradient-to-b from-white/[0.05] via-white/[0.03] to-transparent transition-all duration-300 group-hover:border-red-500/50 group-hover:shadow-lg group-hover:shadow-red-500/10 cursor-pointer">
                      {/* 海报区域 */}
                      <div className="relative aspect-[2/3] w-full overflow-hidden">
                        <img
                          src={movie.posterUrl}
                          alt={movie.title}
                          className="h-full w-full object-cover transition-transform duration-500 group-hover:scale-110"
                        />
                        
                        {/* 渐变遮罩 */}
                        <div className="absolute inset-0 bg-gradient-to-t from-black/80 via-black/20 to-transparent opacity-0 transition-opacity duration-300 group-hover:opacity-100" />
                        
                        {/* 评分标签 */}
                        {variant === "rating" && (
                          <div className="absolute left-3 top-3 inline-flex items-center rounded-full bg-red-600/90 px-3 py-1.5 text-xs font-bold text-white shadow-lg backdrop-blur-sm">
                            <Star className="mr-1.5 h-3.5 w-3.5 fill-current text-white" />
                            {movie.rating.toFixed(1)}
                          </div>
                        )}
                        
                        {/* 票房标签 */}
                        {variant === "boxOffice" && (
                          <div className="absolute left-3 top-3 inline-flex items-center rounded-full bg-gradient-to-r from-orange-500 to-yellow-500 px-3 py-1.5 text-xs font-bold text-black shadow-lg backdrop-blur-sm">
                            <DollarSign className="mr-1.5 h-3.5 w-3.5" />
                            {formatBoxOfficeShort(movie.boxOffice)}
                          </div>
                        )}
                        
                        {/* 悬停遮罩 */}
                        <div className="absolute inset-0 bg-gradient-to-t from-[#0a0a0f] via-transparent to-transparent opacity-0 transition-opacity duration-300 group-hover:opacity-100" />
                        
                        {/* 播放按钮 */}
                        <div className="absolute inset-0 flex items-center justify-center opacity-0 transition-all duration-300 group-hover:opacity-100">
                          <Button className="rounded-full bg-red-600/90 backdrop-blur-sm hover:bg-red-500 shadow-lg shadow-red-600/50">
                            <Play className="h-6 w-6 text-white ml-0.5" />
                          </Button>
                        </div>
                      </div>

                      {/* 电影信息 */}
                      <CardHeader className="space-y-2 pb-3 pt-4">
                        <CardTitle className="line-clamp-1 text-base font-semibold text-white group-hover:text-red-300 transition-colors">
                          {movie.title}
                        </CardTitle>
                        <CardDescription className="line-clamp-1 text-sm text-white/50">
                          {movie.genres.join(" · ")}
                        </CardDescription>
                      </CardHeader>
                      
                      <CardContent className="pb-5 pt-0">
                        <div className="space-y-3">
                          {/* 导演信息 */}
                          <div className="flex items-center gap-2">
                            <span className="text-xs text-white/40">导演：</span>
                            <span className="text-xs font-medium text-white/70">
                              {movie.director}
                            </span>
                          </div>
                          
                          {/* 主要指标 */}
                          <div className="flex items-center justify-between">
                            <div className="flex items-center gap-2">
                              <div className="flex items-center gap-1">
                                <Star className="h-3 w-3 text-yellow-400" />
                                <span className="text-xs font-medium text-white">
                                  {movie.rating.toFixed(1)}
                                </span>
                              </div>
                              <span className="text-xs text-white/20">|</span>
                              <div className="flex items-center gap-1">
                                <TrendingUp className="h-3 w-3 text-blue-400" />
                                <span className="text-xs font-medium text-white/70">
                                  {movie.popularity.toFixed(1)}
                                </span>
                              </div>
                            </div>
                            
                            {/* 详细数据 */}
                            <div className="text-right">
                              {variant === "boxOffice" ? (
                                <p className="text-xs font-semibold text-red-300">
                                  {formatBoxOffice(movie.boxOffice)}
                                </p>
                              ) : (
                                <p className="text-xs text-white/40">
                                  上映：{movie.releaseDate.split("-")[0]}
                                </p>
                              )}
                            </div>
                          </div>
                        </div>
                      </CardContent>
                    </Card>
                  </Link>
                </motion.div>
              </CarouselItem>
            ))}
          </CarouselContent>
          
          {/* 导航按钮 */}
          <CarouselPrevious className="left-2 h-10 w-10 rounded-xl border border-white/10 bg-black/60 backdrop-blur-sm text-white hover:bg-white/10 hover:text-white transition-all" />
          <CarouselNext className="right-2 h-10 w-10 rounded-xl border border-white/10 bg-black/60 backdrop-blur-sm text-white hover:bg-white/10 hover:text-white transition-all" />
        </Carousel>
      </div>

      {/* 底部指示器 */}
      <div className="mt-6 flex items-center justify-center gap-2">
        {movies.slice(0, 5).map((_, index) => (
          <div
            key={index}
            className={`h-1 rounded-full transition-all ${
              index === 0
                ? "w-8 bg-gradient-to-r from-red-600 to-red-500"
                : "w-2 bg-white/10"
            }`}
          />
        ))}
      </div>
    </section>
  );
}

function formatBoxOffice(amount: number): string {
  if (amount >= 1_000_000_000) {
    return `${(amount / 1_000_000_000).toFixed(1)}B USD`;
  }
  if (amount >= 1_000_000) {
    return `${(amount / 1_000_000).toFixed(1)}M USD`;
  }
  if (amount >= 1_000) {
    return `${(amount / 1_000).toFixed(1)}K USD`;
  }
  return `${amount.toLocaleString()} USD`;
}

function formatBoxOfficeShort(amount: number): string {
  if (amount >= 1_000_000_000) {
    return `${(amount / 1_000_000_000).toFixed(1)}B`;
  }
  if (amount >= 1_000_000) {
    return `${(amount / 1_000_000).toFixed(1)}M`;
  }
  if (amount >= 1_000) {
    return `${(amount / 1_000).toFixed(1)}K`;
  }
  return `${amount}`;
}
