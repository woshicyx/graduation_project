"use client";

import Link from "next/link";

interface MoviePageProps {
  params: Promise<{ id: string }>;
}

export default async function MovieDetailPage({ params }: MoviePageProps) {
  const { id } = await params;

  return (
    <div className="relative min-h-screen bg-gradient-to-br from-slate-950 via-slate-950 to-slate-900">
      {/* 背景装饰 */}
      <div className="fixed inset-0 overflow-hidden">
        <div className="absolute -top-40 -right-40 h-80 w-80 rounded-full bg-emerald-500/10 blur-3xl" />
        <div className="absolute bottom-40 left-1/4 h-96 w-96 rounded-full bg-blue-500/10 blur-3xl" />
      </div>

      {/* 导航 */}
      <header className="relative z-10 border-b border-slate-800 bg-slate-950/80 backdrop-blur">
        <div className="mx-auto flex h-16 max-w-7xl items-center justify-between px-4">
          <Link href="/" className="flex items-center gap-3">
            <div className="h-8 w-8 rounded-lg bg-gradient-to-br from-emerald-500 to-emerald-600" />
            <h1 className="text-xl font-bold tracking-tight text-white">
              Movie<span className="text-emerald-400">AI</span>
            </h1>
          </Link>
          <div className="flex items-center gap-4">
            <Link href="/search" className="text-sm text-slate-300 hover:text-emerald-400">
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

      {/* 电影详情内容 */}
      <main className="relative z-10 mx-auto max-w-7xl px-4 py-8">
        {/* 面包屑导航 */}
        <div className="mb-6 flex items-center gap-2 text-sm text-slate-500">
          <Link href="/" className="hover:text-emerald-400">首页</Link>
          <span>/</span>
          <Link href="/search" className="hover:text-emerald-400">搜索</Link>
          <span>/</span>
          <span className="text-slate-400">电影详情</span>
        </div>

        {/* 电影信息区域 */}
        <div className="grid gap-8 lg:grid-cols-3">
          {/* 海报 */}
          <div className="lg:col-span-1">
            <div className="sticky top-8">
              <div className="aspect-[2/3] overflow-hidden rounded-2xl border border-slate-800 bg-slate-800">
                <div className="flex h-full w-full items-center justify-center">
                  <div className="text-center">
                    <svg className="mx-auto h-16 w-16 text-slate-600" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                      <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M7 4v16M17 4v16M3 8h4m10 0h4M3 12h18M3 16h4m10 0h4M4 20h16a1 1 0 001-1V5a1 1 0 00-1-1H4a1 1 0 00-1 1v14a1 1 0 001 1z" />
                    </svg>
                    <p className="mt-2 text-sm text-slate-500">ID: {id}</p>
                  </div>
                </div>
              </div>
              
              {/* 收藏按钮 */}
              <button className="mt-4 w-full rounded-xl border border-slate-700 bg-slate-800/50 py-3 text-white transition-colors hover:border-emerald-500 hover:bg-slate-800">
                <span className="flex items-center justify-center gap-2">
                  <svg className="h-5 w-5" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                    <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M4.318 6.318a4.5 4.5 0 000 6.364L12 20.364l7.682-7.682a4.5 4.5 0 00-6.364-6.364L12 7.636l-1.318-1.318a4.5 4.5 0 00-6.364 0z" />
                  </svg>
                  收藏这部电影
                </span>
              </button>
            </div>
          </div>

          {/* 电影详情 */}
          <div className="lg:col-span-2 space-y-6">
            {/* 标题区域 */}
            <div>
              <h1 className="text-3xl font-bold text-white">电影标题</h1>
              <p className="mt-1 text-slate-400">原标题 / 英文标题</p>
            </div>

            {/* 基本信息 */}
            <div className="flex flex-wrap gap-4 text-sm text-slate-400">
              <span className="flex items-center gap-1">
                <svg className="h-4 w-4 text-yellow-500" fill="currentColor" viewBox="0 0 20 20">
                  <path d="M9.049 2.927c.3-.921 1.603-.921 1.902 0l1.07 3.292a1 1 0 00.95.69h3.462c.969 0 1.371 1.24.588 1.81l-2.8 2.034a1 1 0 00-.364 1.118l1.07 3.292c.3.921-.755 1.688-1.54 1.118l-2.8-2.034a1 1 0 00-1.175 0l-2.8 2.034c-.784.57-1.838-.197-1.539-1.118l1.07-3.292a1 1 0 00-.364-1.118L2.98 8.72c-.783-.57-.38-1.81.588-1.81h3.461a1 1 0 00.951-.69l1.07-3.292z" />
                </svg>
                8.5
              </span>
              <span>2024</span>
              <span>120 分钟</span>
              <span>动作 / 科幻</span>
            </div>

            {/* 剧情简介 */}
            <div className="rounded-xl border border-slate-800 bg-slate-900/50 p-6">
              <h2 className="mb-3 text-lg font-semibold text-white">剧情简介</h2>
              <p className="text-sm leading-relaxed text-slate-400">
                电影详情加载中...请确保后端数据库连接正常。
              </p>
            </div>

            {/* 导演和演员 */}
            <div className="grid gap-6 sm:grid-cols-2">
              <div className="rounded-xl border border-slate-800 bg-slate-900/50 p-6">
                <h2 className="mb-3 text-lg font-semibold text-white">导演</h2>
                <p className="text-sm text-slate-400">导演名称</p>
              </div>
              <div className="rounded-xl border border-slate-800 bg-slate-900/50 p-6">
                <h2 className="mb-3 text-lg font-semibold text-white">主演</h2>
                <p className="text-sm text-slate-400">演员1, 演员2, 演员3...</p>
              </div>
            </div>

            {/* 相似推荐 */}
            <div className="rounded-xl border border-slate-800 bg-slate-900/50 p-6">
              <h2 className="mb-4 text-lg font-semibold text-white">相似推荐</h2>
              <div className="grid gap-4 sm:grid-cols-2 md:grid-cols-3">
                {[1, 2, 3, 4, 5, 6].map((i) => (
                  <Link 
                    key={i} 
                    href={`/movies/${i}`}
                    className="group rounded-lg border border-slate-800 bg-slate-800/50 p-3 transition-colors hover:border-emerald-500/50"
                  >
                    <div className="aspect-[2/3] rounded bg-slate-700" />
                    <h3 className="mt-2 truncate text-sm text-white group-hover:text-emerald-400">
                      相似电影 {i}
                    </h3>
                  </Link>
                ))}
              </div>
            </div>

            {/* 影评区域 */}
            <div className="rounded-xl border border-slate-800 bg-slate-900/50 p-6">
              <h2 className="mb-4 text-lg font-semibold text-white">精选影评</h2>
              <div className="space-y-4">
                {[1, 2, 3].map((i) => (
                  <div key={i} className="rounded-lg border border-slate-800 bg-slate-800/50 p-4">
                    <div className="mb-2 flex items-center justify-between">
                      <span className="font-medium text-white">用户{i}</span>
                      <span className="text-sm text-yellow-500">★★★★★</span>
                    </div>
                    <p className="text-sm text-slate-400">
                      影评内容加载中...数据库连接后显示。
                    </p>
                  </div>
                ))}
              </div>
            </div>
          </div>
        </div>
      </main>

      {/* AI 助手悬浮按钮 */}
      <Link
        href="/chat"
        className="fixed bottom-6 right-6 flex h-14 w-14 items-center justify-center rounded-full bg-emerald-500 shadow-lg shadow-emerald-500/25 transition-transform hover:scale-105"
      >
        <svg className="h-6 w-6 text-white" fill="none" stroke="currentColor" viewBox="0 0 24 24">
          <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M8 10h.01M12 10h.01M16 10h.01M9 16H5a2 2 0 01-2-2V6a2 2 0 012-2h14a2 2 0 012 2v8a2 2 0 01-2 2h-5l-5 5v-5z" />
        </svg>
      </Link>
    </div>
  );
}