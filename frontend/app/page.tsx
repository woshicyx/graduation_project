import Link from "next/link";

export default function Home() {
  return (
    <div className="relative min-h-screen bg-gradient-to-br from-slate-950 via-slate-950 to-slate-900">
      {/* 背景装饰 */}
      <div className="fixed inset-0 overflow-hidden">
        <div className="absolute -top-40 -right-40 h-80 w-80 rounded-full bg-emerald-500/10 blur-3xl" />
        <div className="absolute top-1/3 -left-40 h-64 w-64 rounded-full bg-blue-500/10 blur-3xl" />
        <div className="absolute bottom-40 right-1/4 h-96 w-96 rounded-full bg-purple-500/5 blur-3xl" />
        <div className="absolute inset-0 bg-gradient-to-b from-transparent via-slate-950/50 to-slate-950" />
      </div>

      <main className="relative z-10 flex min-h-screen flex-col px-4 pb-20 pt-4 text-slate-50 sm:px-6 lg:px-8">
        {/* 导航 */}
        <header className="mx-auto mb-8 w-full max-w-7xl">
          <div className="flex items-center justify-between">
            <div className="flex items-center gap-3">
              <div className="h-8 w-8 rounded-lg bg-gradient-to-br from-emerald-500 to-emerald-600" />
              <h1 className="text-xl font-bold tracking-tight text-white">
                Movie<span className="text-emerald-400">AI</span>
              </h1>
            </div>
            <div className="flex items-center gap-4">
              <Link href="/search" className="text-sm text-slate-300 hover:text-emerald-400">
                搜索电影
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

        {/* 主要内容 */}
        <div className="mx-auto w-full max-w-7xl flex-1">
          {/* 搜索区域 */}
          <section className="mb-16 text-center">
            <h2 className="mb-4 text-4xl font-bold tracking-tight text-white sm:text-5xl">
              发现你的<span className="text-emerald-400">下一部电影</span>
            </h2>
            <p className="mb-8 text-lg text-slate-400">
              基于 AI 智能推荐，找到最适合你的电影
            </p>
            <div className="mx-auto max-w-2xl">
              <Link href="/search">
                <div className="flex items-center rounded-xl border border-slate-700 bg-slate-800/50 px-6 py-4 text-slate-400 backdrop-blur transition-colors hover:border-emerald-500/50 hover:bg-slate-800">
                  <svg className="h-5 w-5" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                    <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M21 21l-6-6m2-5a7 7 0 11-14 0 7 7 0 0114 0z" />
                  </svg>
                  <span className="ml-3">搜索电影、导演、类型...</span>
                </div>
              </Link>
            </div>
          </section>

          {/* 功能介绍 */}
          <section className="grid gap-8 md:grid-cols-3">
            <div className="rounded-2xl border border-slate-800 bg-slate-900/50 p-6 backdrop-blur">
              <div className="mb-4 flex h-12 w-12 items-center justify-center rounded-xl bg-emerald-500/20">
                <svg className="h-6 w-6 text-emerald-400" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                  <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M21 21l-6-6m2-5a7 7 0 11-14 0 7 7 0 0114 0z" />
                </svg>
              </div>
              <h3 className="mb-2 text-lg font-semibold text-white">智能搜索</h3>
              <p className="text-sm text-slate-400">支持按电影名、类型、导演、评分等多维度筛选</p>
            </div>

            <div className="rounded-2xl border border-slate-800 bg-slate-900/50 p-6 backdrop-blur">
              <div className="mb-4 flex h-12 w-12 items-center justify-center rounded-xl bg-blue-500/20">
                <svg className="h-6 w-6 text-blue-400" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                  <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M9.663 17h4.673M12 3v1m6.364 1.636l-.707.707M21 12h-1M4 12H3m3.343-5.657l-.707-.707m2.828 9.9a5 5 0 117.072 0l-.548.547A3.374 3.374 0 0014 18.469V19a2 2 0 11-4 0v-.531c0-.895-.356-1.754-.988-2.386l-.548-.547z" />
                </svg>
              </div>
              <h3 className="mb-2 text-lg font-semibold text-white">AI 推荐</h3>
              <p className="text-sm text-slate-400">基于 RAG 技术的智能推荐，理解你的喜好</p>
            </div>

            <div className="rounded-2xl border border-slate-800 bg-slate-900/50 p-6 backdrop-blur">
              <div className="mb-4 flex h-12 w-12 items-center justify-center rounded-xl bg-purple-500/20">
                <svg className="h-6 w-6 text-purple-400" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                  <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M5 5a2 2 0 012-2h10a2 2 0 012 2v16l-7-3.5L5 21V5z" />
                </svg>
              </div>
              <h3 className="mb-2 text-lg font-semibold text-white">收藏管理</h3>
              <p className="text-sm text-slate-400">登录后可收藏喜欢的电影，记录观影历史</p>
            </div>
          </section>

          {/* 热门榜单占位 */}
          <section className="mt-16">
            <div className="mb-6 flex items-center justify-between">
              <div>
                <h3 className="text-2xl font-bold text-white">热门电影</h3>
                <p className="text-sm text-slate-400">根据数据库统计的热门电影榜单</p>
              </div>
              <Link href="/search" className="text-sm text-emerald-400 hover:text-emerald-300">
                查看更多 →
              </Link>
            </div>
            <div className="grid gap-4 sm:grid-cols-2 md:grid-cols-3 lg:grid-cols-4">
              {/* 占位卡片 - 数据库连接后可替换为真实数据 */}
              {[1, 2, 3, 4].map((i) => (
                <div key={i} className="group rounded-xl border border-slate-800 bg-slate-900/50 p-4">
                  <div className="aspect-[2/3] rounded-lg bg-slate-800" />
                  <h4 className="mt-3 text-sm font-medium text-white">加载中...</h4>
                  <p className="text-xs text-slate-500">数据库连接后显示</p>
                </div>
              ))}
            </div>
          </section>
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