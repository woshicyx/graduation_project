"use client";

import { motion, AnimatePresence } from "framer-motion";
import { Search, SlidersHorizontal, ChevronDown, X, Loader2 } from "lucide-react";
import { Input } from "@/components/ui/input";
import { Button } from "@/components/ui/button";
import {
  Dialog,
  DialogContent,
  DialogHeader,
  DialogTitle,
  DialogDescription,
  DialogTrigger,
} from "@/components/ui/dialog";
import { useState, useRef, useEffect, useCallback } from "react";
import { useSearchSuggestions } from "@/hooks/useMovies";

// 数据库中的电影类型（从实际数据中提取）
const genres = [
  "Action", "Adventure", "Animation", "Comedy", "Crime", 
  "Documentary", "Drama", "Family", "Fantasy", "History",
  "Horror", "Music", "Mystery", "Romance", "Science Fiction",
  "TV Movie", "Thriller", "War", "Western"
];

// 年份范围（从1916到2017）
const years = ["2020-2024", "2015-2019", "2010-2014", "2005-2009", "2000-2004", "1995-1999", "1990-1994", "更早"];
const ratings = ["8.0+", "7.5+", "7.0+", "6.5+", "6.0+"] as const;

export function SearchHero() {
  const [selectedGenre, setSelectedGenre] = useState<string | null>(null);
  const [selectedYear, setSelectedYear] = useState<string | null>(null);
  const [selectedRating, setSelectedRating] = useState<string | null>(null);
  const [isDropdownOpen, setIsDropdownOpen] = useState(false);
  const [searchQuery, setSearchQuery] = useState("");
  const [isSearching, setIsSearching] = useState(false);
  const dropdownRef = useRef<HTMLDivElement>(null);
  const inputRef = useRef<HTMLInputElement>(null);

  // 使用React Query获取搜索建议
  const { data: suggestions, isLoading: isLoadingSuggestions } = useSearchSuggestions(searchQuery, 5);

  // 点击外部关闭下拉菜单
  useEffect(() => {
    const handleClickOutside = (event: MouseEvent) => {
      if (dropdownRef.current && !dropdownRef.current.contains(event.target as Node)) {
        setIsDropdownOpen(false);
      }
    };

    document.addEventListener("mousedown", handleClickOutside);
    return () => document.removeEventListener("mousedown", handleClickOutside);
  }, []);

  // 清除所有筛选条件
  const clearFilters = () => {
    setSelectedGenre(null);
    setSelectedYear(null);
    setSelectedRating(null);
  };

  // 获取当前筛选条件文本
  const getFilterText = () => {
    const filters = [];
    if (selectedGenre) filters.push(`类型: ${selectedGenre}`);
    if (selectedYear) filters.push(`年份: ${selectedYear}`);
    if (selectedRating) filters.push(`评分: ${selectedRating}`);
    return filters.length > 0 ? filters.join(" · ") : "点击展开筛选条件";
  };

  // 处理搜索
  const handleSearch = useCallback(async () => {
    if (!searchQuery.trim() && !selectedGenre && !selectedYear && !selectedRating) {
      return;
    }

    setIsSearching(true);
    
    // 构建搜索参数
    const searchParams = new URLSearchParams();
    
    if (searchQuery.trim()) {
      searchParams.set('q', searchQuery.trim());
    }
    
    if (selectedGenre) {
      searchParams.set('genre', selectedGenre);
    }
    
    if (selectedYear) {
      // 解析年份范围
      if (selectedYear.includes('-')) {
        const [startYear, endYear] = selectedYear.split('-');
        searchParams.set('release_date_from', `${startYear}-01-01`);
        searchParams.set('release_date_to', `${endYear}-12-31`);
      }
    }
    
    if (selectedRating) {
      const ratingMin = parseFloat(selectedRating.replace('+', ''));
      if (!isNaN(ratingMin)) {
        searchParams.set('rating_min', ratingMin.toString());
      }
    }

    // 导航到搜索结果页面（或更新当前页面状态）
    const queryString = searchParams.toString();
    console.log("搜索参数:", { queryString });
    
    // 这里可以导航到搜索结果页面，或者更新当前页面的状态
    // 暂时先显示搜索状态
    setTimeout(() => {
      setIsSearching(false);
      alert(`搜索完成！参数: ${queryString || "无筛选条件"}`);
    }, 1000);
  }, [searchQuery, selectedGenre, selectedYear, selectedRating]);

  // 处理键盘事件
  const handleKeyDown = (e: React.KeyboardEvent) => {
    if (e.key === 'Enter') {
      handleSearch();
    }
  };

  // 处理搜索建议点击
  const handleSuggestionClick = (title: string) => {
    setSearchQuery(title);
    setIsDropdownOpen(false);
  };

  return (
    <section className="relative mx-auto flex max-w-5xl flex-col items-center gap-6 pt-12 pb-10 text-center">
      <motion.div
        initial={{ opacity: 0, y: 16 }}
        animate={{ opacity: 1, y: 0 }}
        transition={{ duration: 0.4 }}
        className="space-y-3"
      >
        <h1 className="text-3xl font-bold tracking-tight text-white sm:text-4xl md:text-5xl">
          从4,803部电影中找到你的最爱
        </h1>
        <p className="text-sm text-slate-300/90 sm:text-base">
          支持按类型、年份、评分组合筛选，或直接搜索电影名、导演
        </p>
      </motion.div>

      <motion.div
        initial={{ opacity: 0, y: 20 }}
        animate={{ opacity: 1, y: 0 }}
        transition={{ delay: 0.1, duration: 0.4 }}
        className="w-full rounded-2xl border border-slate-700/60 bg-gradient-to-br from-slate-900/90 via-slate-900/70 to-slate-950/90 p-5 shadow-2xl backdrop-blur"
      >
        <div className="flex flex-col gap-4">
          {/* 搜索输入区域 */}
          <div className="relative" ref={dropdownRef}>
            <div className="relative">
              <Search className="pointer-events-none absolute left-4 top-1/2 h-5 w-5 -translate-y-1/2 text-slate-400" />
              <Input
                ref={inputRef}
                value={searchQuery}
                onChange={(e) => setSearchQuery(e.target.value)}
                onKeyDown={handleKeyDown}
                placeholder="输入电影名、导演，或一句话描述你的心情…"
                className="h-14 w-full rounded-xl border-slate-700/80 bg-slate-900/80 pl-12 pr-12 text-base placeholder:text-slate-400 focus-visible:ring-2 focus-visible:ring-emerald-500/50"
                onFocus={() => setIsDropdownOpen(true)}
              />
              <button
                type="button"
                onClick={() => setIsDropdownOpen(!isDropdownOpen)}
                className="absolute right-3 top-1/2 flex h-8 w-8 -translate-y-1/2 items-center justify-center rounded-lg border border-slate-700/80 bg-slate-800/80 text-slate-300 hover:bg-slate-700/80"
              >
                <ChevronDown className={`h-4 w-4 transition-transform ${isDropdownOpen ? "rotate-180" : ""}`} />
              </button>
            </div>

            {/* 搜索建议下拉菜单 */}
            <AnimatePresence>
              {isDropdownOpen && searchQuery.length >= 2 && (
                <motion.div
                  initial={{ opacity: 0, y: -10, height: 0 }}
                  animate={{ opacity: 1, y: 0, height: "auto" }}
                  exit={{ opacity: 0, y: -10, height: 0 }}
                  transition={{ duration: 0.2 }}
                  className="absolute left-0 right-0 top-full z-50 mt-2 overflow-hidden rounded-xl border border-slate-700/80 bg-slate-900/95 shadow-2xl backdrop-blur"
                >
                  <div className="p-3">
                    <div className="mb-2 flex items-center justify-between">
                      <h3 className="text-xs font-semibold text-white">搜索建议</h3>
                      {isLoadingSuggestions && (
                        <Loader2 className="h-3 w-3 animate-spin text-emerald-400" />
                      )}
                    </div>
                    
                    {suggestions && suggestions.length > 0 ? (
                      <div className="space-y-1">
                        {suggestions.map((movie) => (
                          <button
                            key={movie.id}
                            type="button"
                            onClick={() => handleSuggestionClick(movie.title)}
                            className="flex w-full items-center gap-3 rounded-lg p-2 text-left hover:bg-slate-800/80"
                          >
                            <div className="h-10 w-8 flex-shrink-0 overflow-hidden rounded bg-slate-800">
                              {movie.posterUrl && movie.posterUrl !== '/placeholder-poster.jpg' ? (
                                <img 
                                  src={movie.posterUrl} 
                                  alt={movie.title}
                                  className="h-full w-full object-cover"
                                />
                              ) : (
                                <div className="flex h-full items-center justify-center bg-slate-700">
                                  <span className="text-xs text-slate-400">无图</span>
                                </div>
                              )}
                            </div>
                            <div className="flex-1 overflow-hidden">
                              <p className="truncate text-sm font-medium text-white">{movie.title}</p>
                              <p className="truncate text-xs text-slate-400">
                                {movie.director} · {movie.releaseDate.split('-')[0]}
                              </p>
                            </div>
                            <div className="flex items-center gap-1">
                              <span className="text-xs font-medium text-amber-400">{movie.rating.toFixed(1)}</span>
                            </div>
                          </button>
                        ))}
                      </div>
                    ) : (
                      <div className="py-4 text-center">
                        <p className="text-sm text-slate-400">暂无搜索建议</p>
                      </div>
                    )}
                  </div>
                </motion.div>
              )}
            </AnimatePresence>
          </div>

          {/* 操作按钮区域 */}
          <div className="flex flex-col gap-3 sm:flex-row sm:items-center">
            <div className="flex-1 text-left">
              <p className="text-xs text-slate-400">
                {selectedGenre || selectedYear || selectedRating
                  ? `已选择：${getFilterText()}`
                  : "点击搜索栏箭头展开筛选条件"}
              </p>
            </div>
            <div className="flex gap-3">
              <Dialog>
                <DialogTrigger asChild>
                  <Button
                    variant="outline"
                    className="h-11 shrink-0 rounded-xl border-slate-700/70 bg-slate-800/60 text-sm text-slate-200 hover:bg-slate-700/60"
                  >
                    <SlidersHorizontal className="mr-2 h-4 w-4" />
                    高级筛选
                  </Button>
                </DialogTrigger>
                <DialogContent className="max-w-md border-slate-700/80 bg-slate-900/95 text-white">
                  <DialogHeader>
                    <DialogTitle className="text-white">高级筛选条件</DialogTitle>
                    <DialogDescription className="text-slate-400">
                      这些筛选条件会与后端搜索接口联动。
                    </DialogDescription>
                  </DialogHeader>
                  <div className="space-y-4 pt-2 text-left">
                    <div>
                      <p className="mb-2 text-xs font-medium text-slate-400">按类型</p>
                      <div className="flex flex-wrap gap-2">
                        {genres.map((g) => (
                          <button
                            key={g}
                            type="button"
                            onClick={() => setSelectedGenre(g)}
                            className={`rounded-full border px-3 py-1 text-xs transition-colors ${
                              selectedGenre === g
                                ? "border-emerald-500 bg-emerald-500/20 text-emerald-300"
                                : "border-slate-700/70 bg-slate-800/40 text-slate-300 hover:border-slate-600 hover:bg-slate-700/60"
                            }`}
                          >
                            {g}
                          </button>
                        ))}
                      </div>
                    </div>
                    <div>
                      <p className="mb-2 text-xs font-medium text-slate-400">按年份区间</p>
                      <div className="flex flex-wrap gap-2">
                        {years.map((y) => (
                          <button
                            key={y}
                            type="button"
                            onClick={() => setSelectedYear(y)}
                            className={`rounded-full border px-3 py-1 text-xs transition-colors ${
                              selectedYear === y
                                ? "border-blue-500 bg-blue-500/20 text-blue-300"
                                : "border-slate-700/70 bg-slate-800/40 text-slate-300 hover:border-slate-600 hover:bg-slate-700/60"
                            }`}
                          >
                            {y}
                          </button>
                        ))}
                      </div>
                    </div>
                    <div>
                      <p className="mb-2 text-xs font-medium text-slate-400">按评分下限</p>
                      <div className="flex flex-wrap gap-2">
                        {ratings.map((r) => (
                          <button
                            key={r}
                            type="button"
                            onClick={() => setSelectedRating(r)}
                            className={`rounded-full border px-3 py-1 text-xs transition-colors ${
                              selectedRating === r
                                ? "border-amber-500 bg-amber-500/20 text-amber-300"
                                : "border-slate-700/70 bg-slate-800/40 text-slate-300 hover:border-slate-600 hover:bg-slate-700/60"
                            }`}
                          >
                            {r}
                          </button>
                        ))}
                      </div>
                    </div>
                  </div>
                </DialogContent>
              </Dialog>
              <Button 
                onClick={handleSearch}
                disabled={isSearching}
                className="h-11 shrink-0 rounded-xl bg-gradient-to-r from-emerald-500 to-emerald-600 px-6 text-sm font-medium text-white hover:from-emerald-600 hover:to-emerald-700 disabled:opacity-70"
              >
                {isSearching ? (
                  <>
                    <Loader2 className="mr-2 h-4 w-4 animate-spin" />
                    搜索中...
                  </>
                ) : (
                  "开始搜索"
                )}
              </Button>
            </div>
          </div>
        </div>
      </motion.div>
    </section>
  );
}