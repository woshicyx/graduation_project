"use client";

import Link from "next/link";

export default function ProfilePage() {
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

      {/* 个人中心内容 */}
      <main className="relative z-10 mx-auto max-w-4xl px-4 py-8">
        {/* 登录提示 */}
        <div className="mb-8 rounded-2xl border border-slate-800 bg-slate-900/50 p-8 text-center">
          <div className="mx-auto mb-4 flex h-16 w-16 items-center justify-center rounded-full bg-slate-800">
            <svg className="h-8 w-8 text-slate-500" fill="none" stroke="currentColor" viewBox="0 0 24 24">
              <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M16 7a4 4 0 11-8 0 4 4 0 018 0zM12 14a7 7 0 00-7 7h14a7 7 0 00-7-7z" />
            </svg>
          </div>
          <h2 className="mb-2 text-xl font-semibold text-white">登录后可查看个人中心</h2>
          <p className="mb-6 text-sm text-slate-400">
            登录后将解锁浏览历史、收藏管理和个性化推荐功能
          </p>
          <Link 
            href="/auth/login"
            className="inline-block rounded-lg bg-emerald-500 px-6 py-3 font-medium text-white transition-colors hover:bg-emerald-600"
          >
            立即登录
          </Link>
        </div>

        {/* 功能预览 */}
        <div className="grid gap-6 md:grid-cols-3">
          <div className="rounded-xl border border-slate-800 bg-slate-900/50 p-6">
            <div className="mb-4 flex h-12 w-12 items-center justify-center rounded-xl bg-emerald-500/20">
              <svg className="h-6 w-6 text-emerald-400" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M12 8v4l3 3m6-3a9 9 0 11-18 0 9 9 0 0118 0z" />
              </svg>
            </div>
            <h3 className="mb-2 font-semibold text-white">浏览历史</h3>
            <p className="text-sm text-slate-400">记录你看过的电影，方便回顾</p>
          </div>

          <div className="rounded-xl border border-slate-800 bg-slate-900/50 p-6">
            <div className="mb-4 flex h-12 w-12 items-center justify-center rounded-xl bg-blue-500/20">
              <svg className="h-6 w-6 text-blue-400" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M4.318 6.318a4.5 4.5 0 000 6.364L12 20.364l7.682-7.682a4.5 4.5 0 00-6.364-6.364L12 7.636l-1.318-1.318a4.5 4.5 0 00-6.364 0z" />
              </svg>
            </div>
            <h3 className="mb-2 font-semibold text-white">我的收藏</h3>
            <p className="text-sm text-slate-400">收藏喜欢的电影，构建个人片单</p>
          </div>

          <div className="rounded-xl border border-slate-800 bg-slate-900/50 p-6">
            <div className="mb-4 flex h-12 w-12 items-center justify-center rounded-xl bg-purple-500/20">
              <svg className="h-6 w-6 text-purple-400" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M9.663 17h4.673M12 3v1m6.364 1.636l-.707.707M21 12h-1M4 12H3m3.343-5.657l-.707-.707m2.828 9.9a5 5 0 117.072 0l-.548.547A3.374 3.374 0 0014 18.469V19a2 2 0 11-4 0v-.531c0-.895-.356-1.754-.988-2.386l-.548-.547z" />
              </svg>
            </div>
            <h3 className="mb-2 font-semibold text-white">猜你喜欢</h3>
            <p className="text-sm text-slate-400">基于你的偏好推荐个性化电影</p>
          </div>
        </div>

        {/* 返回首页 */}
        <div className="mt-8 text-center">
          <Link href="/" className="text-sm text-slate-500 hover:text-emerald-400">
            ← 返回首页
          </Link>
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