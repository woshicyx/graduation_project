"use client";

import { useState } from "react";
import { motion, AnimatePresence } from "framer-motion";
import { ChevronLeft, ChevronRight, Play, Star, Calendar, Users } from "lucide-react";
import { Button } from "@/components/ui/button";
import { dailyPick, topBoxOffice, topRated } from "@/lib/mock-movies";

// 创建每日推荐轮播数据
const dailyPicks = [
  dailyPick,
  topBoxOffice[0],
  topRated[0],
  topBoxOffice[1],
  topRated[1],
];

export function HeroSection() {
  const [currentIndex, setCurrentIndex] = useState(0);
  const currentMovie = dailyPicks[currentIndex];

  const nextSlide = () => {
    setCurrentIndex((prevIndex) => (prevIndex + 1) % dailyPicks.length);
  };

  const prevSlide = () => {
    setCurrentIndex((prevIndex) => (prevIndex - 1 + dailyPicks.length) % dailyPicks.length);
  };

  const goToSlide = (index: number) => {
    setCurrentIndex(index);
  };

  return (
    <section className="relative mx-auto mb-12 mt-6 max-w-6xl overflow-hidden rounded-3xl border border-slate-700/60 bg-gradient-to-br from-slate-950 via-slate-900 to-slate-950 shadow-2xl">
      {/* 背景图片 */}
      <div className="absolute inset-0 overflow-hidden">
        <AnimatePresence mode="wait">
          <motion.img
            key={currentMovie.id}
            src={currentMovie.posterUrl}
            alt={currentMovie.title}
            initial={{ opacity: 0, scale: 1.1 }}
            animate={{ opacity: 1, scale: 1.05 }}
            exit={{ opacity: 0, scale: 1.1 }}
            transition={{ duration: 0.5 }}
            className="h-full w-full object-cover"
          />
        </AnimatePresence>
        <div className="absolute inset-0 bg-gradient-to-t from-slate-950 via-slate-950/80 to-transparent" />
        <div className="absolute inset-0 bg-gradient-to-r from-slate-950 via-slate-950/60 to-transparent" />
      </div>

      {/* 内容区域 */}
      <div className="relative z-10 flex flex-col p-6 sm:p-8 md:flex-row md:items-end md:justify-between md:p-10">
        {/* 左侧电影信息 */}
        <div className="mb-6 md:mb-0 md:max-w-2xl">
          <motion.div
            key={currentMovie.id}
            initial={{ opacity: 0, y: 20 }}
            animate={{ opacity: 1, y: 0 }}
            exit={{ opacity: 0, y: -20 }}
            transition={{ duration: 0.4 }}
            className="space-y-4"
          >
            {/* 标签 */}
            <div className="flex items-center gap-2">
              <span className="inline-flex items-center rounded-full border border-emerald-500/40 bg-emerald-500/10 px-3 py-1 text-xs font-medium text-emerald-200">
                今日 AI 精选 #{currentIndex + 1}
                <span className="ml-2 rounded-full bg-emerald-500/80 px-1.5 py-0.5 text-[10px] text-emerald-950">
                  Daily Pick
                </span>
              </span>
              <span className="inline-flex items-center gap-1 rounded-full border border-slate-700/60 bg-slate-800/40 px-3 py-1 text-xs text-slate-300">
                <Calendar className="h-3 w-3" />
                {currentMovie.releaseDate.split("-")[0]}
              </span>
            </div>

            {/* 标题 */}
            <h2 className="text-3xl font-bold tracking-tight text-white sm:text-4xl md:text-5xl">
              {currentMovie.title}
            </h2>

            {/* 描述 */}
            <p className="line-clamp-3 text-base text-slate-200/90 sm:text-lg">
              {currentMovie.synopsis}
            </p>

            {/* 元数据 */}
            <div className="flex flex-wrap gap-3">
              <div className="flex items-center gap-2 rounded-full border border-slate-700/60 bg-slate-800/40 px-4 py-2">
                <Star className="h-4 w-4 text-amber-400" />
                <span className="text-sm font-medium text-white">
                  {currentMovie.rating.toFixed(1)}
                  <span className="ml-1 text-xs text-slate-400">/10</span>
                </span>
              </div>
              <div className="flex items-center gap-2 rounded-full border border-slate-700/60 bg-slate-800/40 px-4 py-2">
                <Users className="h-4 w-4 text-blue-400" />
                <span className="text-sm font-medium text-white">
                  {currentMovie.boxOffice >= 1000000000
                    ? `${(currentMovie.boxOffice / 1000000000).toFixed(1)}B`
                    : currentMovie.boxOffice >= 1000000
                    ? `${(currentMovie.boxOffice / 1000000).toFixed(1)}M`
                    : `${(currentMovie.boxOffice / 1000).toFixed(1)}K`}
                  <span className="ml-1 text-xs text-slate-400">USD</span>
                </span>
              </div>
              <div className="rounded-full border border-slate-700/60 bg-slate-800/40 px-4 py-2">
                <span className="text-sm text-slate-300">
                  导演：<span className="font-medium text-white">{currentMovie.director}</span>
                </span>
              </div>
              <div className="rounded-full border border-slate-700/60 bg-slate-800/40 px-4 py-2">
                <span className="text-sm text-slate-300">
                  类型：<span className="font-medium text-white">{currentMovie.genres.join(" / ")}</span>
                </span>
              </div>
            </div>
          </motion.div>

          {/* 操作按钮 */}
          <motion.div
            initial={{ opacity: 0, y: 16 }}
            animate={{ opacity: 1, y: 0 }}
            transition={{ delay: 0.2, duration: 0.4 }}
            className="mt-8 flex flex-wrap items-center gap-3"
          >
            <Button className="rounded-full bg-gradient-to-r from-emerald-500 to-emerald-600 px-6 py-3 text-sm font-medium hover:from-emerald-600 hover:to-emerald-700">
              <Play className="mr-2 h-4 w-4" />
              立即观看
            </Button>
            <Button
              variant="outline"
              className="rounded-full border-slate-600/70 bg-slate-800/40 px-6 py-3 text-sm text-slate-100 hover:bg-slate-700/60"
            >
              查看详情
            </Button>
            <Button
              variant="ghost"
              className="rounded-full border-slate-700/60 bg-slate-800/30 px-6 py-3 text-sm text-slate-300 hover:bg-slate-700/50"
              onClick={nextSlide}
            >
              换一部推荐
            </Button>
          </motion.div>
        </div>

        {/* 右侧轮播控制 */}
        <div className="flex flex-col items-end gap-4">
          {/* 轮播指示器 */}
          <div className="flex gap-2">
            {dailyPicks.map((_, index) => (
              <button
                key={index}
                onClick={() => goToSlide(index)}
                className={`h-2 rounded-full transition-all ${
                  index === currentIndex
                    ? "w-8 bg-emerald-500"
                    : "w-2 bg-slate-700/60 hover:bg-slate-600"
                }`}
                aria-label={`切换到第 ${index + 1} 个推荐`}
              />
            ))}
          </div>

          {/* 导航按钮 */}
          <div className="flex gap-2">
            <Button
              variant="outline"
              size="icon"
              onClick={prevSlide}
              className="h-10 w-10 rounded-full border-slate-700/60 bg-slate-800/40 text-slate-300 hover:bg-slate-700/60"
            >
              <ChevronLeft className="h-5 w-5" />
            </Button>
            <Button
              variant="outline"
              size="icon"
              onClick={nextSlide}
              className="h-10 w-10 rounded-full border-slate-700/60 bg-slate-800/40 text-slate-300 hover:bg-slate-700/60"
            >
              <ChevronRight className="h-5 w-5" />
            </Button>
          </div>

          {/* 当前进度 */}
          <div className="text-right">
            <p className="text-xs text-slate-400">
              {currentIndex + 1} / {dailyPicks.length}
            </p>
            <p className="mt-1 text-sm text-slate-300">每日 AI 精选轮播</p>
          </div>
        </div>
      </div>

      {/* 底部渐变 */}
      <div className="absolute bottom-0 left-0 right-0 h-32 bg-gradient-to-t from-slate-950 to-transparent" />
    </section>
  );
}

