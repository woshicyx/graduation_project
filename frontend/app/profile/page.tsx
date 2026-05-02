"use client";

import Link from "next/link";
import { useAuth } from "@/contexts/AuthContext";
import { Sparkles, Heart, Clock, User, LogOut, ChevronRight, Film } from "lucide-react";

export default function ProfilePage() {
  const { user, isAuthenticated, isLoading, logout } = useAuth();

  const handleLogout = async () => {
    if (confirm("确定要退出登录吗？")) {
      await logout();
    }
  };

  return (
    <div className="relative min-h-screen bg-[#0a0a0f]">
      {/* 背景装饰 */}
      <div className="fixed inset-0 overflow-hidden pointer-events-none">
        <div className="absolute -top-40 -right-40 h-80 w-80 rounded-full bg-red-500/10 blur-3xl" />
        <div className="absolute bottom-40 left-1/4 h-96 w-96 rounded-full bg-purple-500/5 blur-3xl" />
      </div>

      {/* 导航 */}
      <header className="relative z-10 border-b border-white/10 bg-black/50 backdrop-blur-md">
        <div className="mx-auto flex h-16 max-w-7xl items-center justify-between px-4">
          <Link href="/" className="flex items-center gap-3">
            <div className="flex h-10 w-10 items-center justify-center rounded-xl bg-gradient-to-br from-red-600 to-red-700">
              <Sparkles className="h-5 w-5 text-white" />
            </div>
            <span className="text-xl font-bold tracking-tight text-white">
              Movie<span className="text-red-500">AI</span>
            </span>
          </Link>
          <div className="flex items-center gap-4">
            <Link href="/chat" className="text-sm text-white/70 hover:text-white">
              AI助手
            </Link>
            <Link href="/search" className="text-sm text-white/70 hover:text-white">
              搜索
            </Link>
          </div>
        </div>
      </header>

      {/* 主内容 */}
      <main className="relative z-10 mx-auto max-w-4xl px-4 py-8">
        {/* 用户信息卡片 */}
        <div className="mb-8 rounded-2xl border border-white/10 bg-gradient-to-br from-white/5 to-transparent p-6 backdrop-blur">
          {isLoading ? (
            <div className="flex items-center gap-4">
              <div className="h-16 w-16 rounded-full bg-white/10 animate-pulse" />
              <div className="flex-1 space-y-2">
                <div className="h-5 w-32 rounded bg-white/10 animate-pulse" />
                <div className="h-4 w-48 rounded bg-white/10 animate-pulse" />
              </div>
            </div>
          ) : isAuthenticated && user ? (
            <div className="flex items-center gap-4">
              <div className="flex h-16 w-16 items-center justify-center rounded-full bg-gradient-to-br from-red-600 to-red-700">
                <User className="h-8 w-8 text-white" />
              </div>
              <div className="flex-1">
                <h2 className="text-xl font-semibold text-white">
                  {user.username || user.email || "用户"}
                </h2>
                <p className="text-sm text-white/50">
                  {user.email ? `📧 ${user.email}` : "欢迎回来！"}
                </p>
              </div>
              <button
                onClick={handleLogout}
                className="flex items-center gap-2 rounded-lg border border-white/10 bg-white/5 px-4 py-2 text-sm text-white/70 hover:bg-white/10 hover:text-white transition-all"
              >
                <LogOut className="h-4 w-4" />
                退出
              </button>
            </div>
          ) : (
            <div className="text-center py-4">
              <h2 className="mb-2 text-xl font-semibold text-white">登录后可查看个人中心</h2>
              <p className="mb-4 text-sm text-white/50">
                登录后将解锁浏览历史、收藏管理和个性化推荐功能
              </p>
              <Link 
                href="/auth/login"
                className="inline-block rounded-lg bg-gradient-to-r from-red-600 to-red-700 px-6 py-3 font-medium text-white transition-all hover:from-red-500 hover:to-red-600"
              >
                立即登录
              </Link>
            </div>
          )}
        </div>

        {/* 功能菜单 */}
        <div className="grid gap-4">
          {isAuthenticated ? (
            <>
              <Link
                href="/favorites"
                className="group flex items-center gap-4 rounded-xl border border-white/10 bg-white/5 p-4 transition-all hover:border-red-500/50 hover:bg-white/10"
              >
                <div className="flex h-12 w-12 items-center justify-center rounded-xl bg-red-500/20">
                  <Heart className="h-6 w-6 text-red-400" />
                </div>
                <div className="flex-1">
                  <h3 className="font-medium text-white">我的收藏</h3>
                  <p className="text-sm text-white/50">查看你收藏的电影</p>
                </div>
                <ChevronRight className="h-5 w-5 text-white/30 group-hover:text-white/60 transition-colors" />
              </Link>

              <Link
                href="/history"
                className="group flex items-center gap-4 rounded-xl border border-white/10 bg-white/5 p-4 transition-all hover:border-purple-500/50 hover:bg-white/10"
              >
                <div className="flex h-12 w-12 items-center justify-center rounded-xl bg-purple-500/20">
                  <Clock className="h-6 w-6 text-purple-400" />
                </div>
                <div className="flex-1">
                  <h3 className="font-medium text-white">浏览历史</h3>
                  <p className="text-sm text-white/50">记录你看过的电影</p>
                </div>
                <ChevronRight className="h-5 w-5 text-white/30 group-hover:text-white/60 transition-colors" />
              </Link>

              <Link
                href="/chat"
                className="group flex items-center gap-4 rounded-xl border border-white/10 bg-white/5 p-4 transition-all hover:border-blue-500/50 hover:bg-white/10"
              >
                <div className="flex h-12 w-12 items-center justify-center rounded-xl bg-blue-500/20">
                  <Sparkles className="h-6 w-6 text-blue-400" />
                </div>
                <div className="flex-1">
                  <h3 className="font-medium text-white">AI智能推荐</h3>
                  <p className="text-sm text-white/50">告诉我你想看什么类型的电影</p>
                </div>
                <ChevronRight className="h-5 w-5 text-white/30 group-hover:text-white/60 transition-colors" />
              </Link>
            </>
          ) : (
            <>
              <div className="flex items-center gap-4 rounded-xl border border-white/5 bg-white/5 p-4 opacity-60">
                <div className="flex h-12 w-12 items-center justify-center rounded-xl bg-white/10">
                  <Heart className="h-6 w-6 text-white/30" />
                </div>
                <div className="flex-1">
                  <h3 className="font-medium text-white/50">我的收藏</h3>
                  <p className="text-sm text-white/30">登录后解锁</p>
                </div>
              </div>

              <div className="flex items-center gap-4 rounded-xl border border-white/5 bg-white/5 p-4 opacity-60">
                <div className="flex h-12 w-12 items-center justify-center rounded-xl bg-white/10">
                  <Clock className="h-6 w-6 text-white/30" />
                </div>
                <div className="flex-1">
                  <h3 className="font-medium text-white/50">浏览历史</h3>
                  <p className="text-sm text-white/30">登录后解锁</p>
                </div>
              </div>

              <Link
                href="/chat"
                className="group flex items-center gap-4 rounded-xl border border-white/10 bg-white/5 p-4 transition-all hover:border-blue-500/50 hover:bg-white/10"
              >
                <div className="flex h-12 w-12 items-center justify-center rounded-xl bg-blue-500/20">
                  <Sparkles className="h-6 w-6 text-blue-400" />
                </div>
                <div className="flex-1">
                  <h3 className="font-medium text-white">AI智能推荐</h3>
                  <p className="text-sm text-white/50">无需登录即可使用</p>
                </div>
                <ChevronRight className="h-5 w-5 text-white/30 group-hover:text-white/60 transition-colors" />
              </Link>
            </>
          )}
        </div>

        {/* 快速入口 */}
        <div className="mt-8">
          <h3 className="mb-4 text-sm font-medium text-white/50 uppercase tracking-wider">快速入口</h3>
          <div className="grid grid-cols-2 gap-4 sm:grid-cols-4">
            <Link
              href="/"
              className="flex flex-col items-center gap-2 rounded-xl border border-white/10 bg-white/5 p-4 transition-all hover:border-white/20 hover:bg-white/10"
            >
              <Film className="h-6 w-6 text-white/60" />
              <span className="text-xs text-white/60">首页</span>
            </Link>
            <Link
              href="/search"
              className="flex flex-col items-center gap-2 rounded-xl border border-white/10 bg-white/5 p-4 transition-all hover:border-white/20 hover:bg-white/10"
            >
              <svg className="h-6 w-6 text-white/60" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M21 21l-6-6m2-5a7 7 0 11-14 0 7 7 0 0114 0z" />
              </svg>
              <span className="text-xs text-white/60">搜索</span>
            </Link>
            <Link
              href="/movies/680"
              className="flex flex-col items-center gap-2 rounded-xl border border-white/10 bg-white/5 p-4 transition-all hover:border-white/20 hover:bg-white/10"
            >
              <svg className="h-6 w-6 text-white/60" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M14.752 11.168l-3.197-2.132A1 1 0 0010 9.87v4.263a1 1 0 001.555.832l3.197-2.132a1 1 0 000-1.664z" />
                <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M21 12a9 9 0 11-18 0 9 9 0 0118 0z" />
              </svg>
              <span className="text-xs text-white/60">电影</span>
            </Link>
            <Link
              href="/chat"
              className="flex flex-col items-center gap-2 rounded-xl border border-white/10 bg-white/5 p-4 transition-all hover:border-white/20 hover:bg-white/10"
            >
              <Sparkles className="h-6 w-6 text-white/60" />
              <span className="text-xs text-white/60">AI</span>
            </Link>
          </div>
        </div>

        {/* 返回首页 */}
        <div className="mt-8 text-center">
          <Link href="/" className="text-sm text-white/40 hover:text-white/60 transition-colors">
            ← 返回首页
          </Link>
        </div>
      </main>

      {/* AI 助手悬浮按钮 */}
      <Link
        href="/chat"
        className="fixed bottom-6 right-6 flex h-14 w-14 items-center justify-center rounded-full bg-gradient-to-r from-red-600 to-red-700 shadow-lg shadow-red-500/25 transition-all hover:scale-105"
      >
        <Sparkles className="h-6 w-6 text-white" />
      </Link>
    </div>
  );
}
