"use client";

import Link from "next/link";
import { useState } from "react";

export default function SearchPage() {
  const [query, setQuery] = useState("");

  return (
    <div className="relative min-h-screen bg-gradient-to-br from-slate-950 via-slate-950 to-slate-900">
      {/* 背景装饰 */}
      <div className="fixed inset-0 overflow-hidden">
        <div className="absolute -top-40 -right-40 h-80 w-80 rounded-full bg-emerald-500/10 blur-3xl" />
        <div className="absolute top-1/3 -left-40 h-64 w-64 rounded-full bg-blue-500/10 blur-3xl" />
      </div>

      <main className="relative z-10 flex min-h-screen flex-col px-4 pb-20 pt-4 text-slate-50 sm:px-6 lg:px-8">
        {/* 导航 */}
        <header className="mx-auto mb-8 w-full max-w-7xl">
          <div className="flex items-center justify-between">
            <Link href="/" className="flex items-center gap-3">
              <div className="h-8 w-8 rounded-lg bg-gradient-to-br from-emerald-500 to-emerald-600" />
              <h1 className="text-xl font-bold tracking-tight text-white">
                Movie<span className="text-emerald-400">AI</span>
              </h1>
            </Link>
            <div className="flex items-center gap-4">
              <Link href="/search" className="text-sm text-emerald-400">
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

        {/* 搜索区域 */}
        <div className="mx-auto mb-12 w-full max-w-3xl">
          <div className="relative">
            <svg 
              className="absolute left-4 top-1/2 h-5 w-5 -translate-y-1/2 text-slate-400" 
              fill="none" 
              stroke="currentColor" 
              viewBox="0 0 24 24"
            >
              <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M21 21l-6-6m2-5a7 7 0 11-14 0 7 7 0 0114 0z" />
            </svg>
            <input
              type="text"
              value={query}
              onChange={(e) => setQuery(e.target.value)}
              placeholder="搜索电影、导演、类型..."
              className="w-full rounded-xl border border-slate-700 bg-slate-800/50 py-4 pl-12 pr-4 text-white placeholder-slate-400 backdrop-blur focus:border-emerald-500 focus:outline-none"
            />
          </div>

          {/* 筛选标签 */}
          <div className="mt-4 flex flex-wrap gap-2">
            {["动作", "喜剧", "科幻", "爱情", "悬疑", "动画"].map((tag) => (
              <button
                key={tag}
                className="rounded-full border border-slate-700 px-4 py-1.5 text-sm text-slate-400 hover:border-emerald-500 hover:text-emerald-400"
              >
                {tag}
              </button>
            ))}
          </div>
        </div>

        {/* 搜索结果 */}
        <div className="mx-auto w-full max-w-7xl">
          <div className="mb-6">
            <h2 className="text-2xl font-bold text-white">搜索结果</h2>
            <p className="text-sm text-slate-400">
              {query ? `搜索 "${query}" 的结果` : "输入关键词开始搜索"}
            </p>
          </div>

          {/* 静态占位内容 - 数据库连接后可替换 */}
          <div className="grid gap-6 sm:grid-cols-2 md:grid-cols-3 lg:grid-cols-4 xl:grid-cols-5">
            {[1, 2, 3, 4, 5, 6, 7, 8, 9, 10].map((i) => (
              <Link 
                key={i} 
                href={`/movie/${i}`}
                className="group rounded-xl border border-slate-800 bg-slate-900/50 overflow-hidden transition-colors hover:border-emerald-500/50"
              >
                <div className="aspect-[2/3] bg-slate-800">
                  {/* 海报占位 */}
                  <div className="flex h-full w-full items-center justify-center text-slate-600">
                    <svg className="h-12 w-12" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                      <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M7 4v16M17 4v16M3 8h4m10 0h4M3 12h18M3 16h4m10 0h4M4 20h16a1 1 0 001-1V5a1 1 0 00-1-1H4a1 1 0 00-1 1v14a1 1 0 001 1z" />
                    </svg>
                  </div>
                </div>
                <div className="p-4">
                  <h3 className="mb-1 truncate text-sm font-medium text-white group-hover:text-emerald-400">
                    {query ? `搜索结果 ${i}` : "电影标题"}
                  </h3>
                  <div className="flex items-center justify-between text-xs text-slate-500">
                    <span>2024</span>
                    <span className="flex items-center">
                      <svg className="mr-1 h-3 w-3 text-yellow-500" fill="currentColor" viewBox="0 0 20 20">
                        <path d="M9.049 2.927c.3-.921 1.603-.921 1.902 0l1.07 3.292a1 1 0 00.95.69h3.462c.969 0 1.371 1.24.588 1.81l-2.8 2.034a1 1 0 00-.364 1.118l1.07 3.292c.3.921-.755 1.688-1.54 1.118l-2.8-2.034a1 1 0 00-1.175 0l-2.8 2.034c-.784.57-1.838-.197-1.539-1.118l1.07-3.292a1 1 0 00-.364-1.118L2.98 8.72c-.783-.57-.38-1.81.588-1.81h3.461a1 1 0 00.951-.69l1.07-3.292z" />
                      </svg>
                      8.5
                    </span>
                  </div>
                </div>
              </Link>
            ))}
          </div>

          {query && (
            <div className="mt-8 text-center text-slate-500">
              <p>数据库连接后可显示真实搜索结果</p>
            </div>
          )}
        </div>

        {/* AI 助手悬浮按钮 */}
        <Link
          href="/chat"
          className="fixed bottom-6 right-6 flex h-14 w-14 items-center justify-center rounded-full bg-emerald-500 shadow-lg shadow-emerald-500/25 transition-transform hover:scale-105"
        >
          <svg className="h-6 w-6 text-white" fill="none" stroke="currentColor" viewBox="0 0 24 24">
            <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M8 10h.01M12 10h.01M16 10h.01M9 16H5a2 2 0 01-2-2V6a2 2 0 012-2h14a2 2 0 012 2v8a2 2 0 01-2 2h-5l-5 5v-5z" />
          </svg>
        </Link>
      </main>
    </div>
  );
}