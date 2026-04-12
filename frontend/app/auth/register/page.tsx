"use client";

import Link from "next/link";
import { useState } from "react";

export default function RegisterPage() {
  const [username, setUsername] = useState("");
  const [email, setEmail] = useState("");
  const [password, setPassword] = useState("");
  const [confirmPassword, setConfirmPassword] = useState("");
  const [isLoading, setIsLoading] = useState(false);

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    
    if (password !== confirmPassword) {
      alert("两次输入的密码不一致");
      return;
    }
    
    setIsLoading(true);
    // 模拟注册请求
    setTimeout(() => {
      setIsLoading(false);
      alert("请确保后端数据库连接正常后实现注册功能");
    }, 1000);
  };

  return (
    <div className="relative min-h-screen bg-gradient-to-br from-slate-950 via-slate-950 to-slate-900">
      {/* 背景装饰 */}
      <div className="fixed inset-0 overflow-hidden">
        <div className="absolute -top-40 -right-40 h-80 w-80 rounded-full bg-emerald-500/10 blur-3xl" />
        <div className="absolute bottom-40 left-1/4 h-96 w-96 rounded-full bg-blue-500/10 blur-3xl" />
      </div>

      <main className="relative z-10 flex min-h-screen items-center justify-center px-4">
        <div className="w-full max-w-md">
          {/* Logo */}
          <div className="mb-8 text-center">
            <Link href="/" className="inline-flex items-center gap-3">
              <div className="h-10 w-10 rounded-xl bg-gradient-to-br from-emerald-500 to-emerald-600" />
              <h1 className="text-2xl font-bold tracking-tight text-white">
                Movie<span className="text-emerald-400">AI</span>
              </h1>
            </Link>
          </div>

          {/* 注册表单 */}
          <div className="rounded-2xl border border-slate-800 bg-slate-900/50 p-8 backdrop-blur">
            <h2 className="mb-6 text-center text-2xl font-bold text-white">创建账号</h2>
            
            <form onSubmit={handleSubmit} className="space-y-4">
              <div>
                <label className="mb-2 block text-sm text-slate-300">用户名</label>
                <input
                  type="text"
                  value={username}
                  onChange={(e) => setUsername(e.target.value)}
                  placeholder="设置用户名"
                  required
                  className="w-full rounded-lg border border-slate-700 bg-slate-800/50 px-4 py-3 text-white placeholder-slate-500 focus:border-emerald-500 focus:outline-none"
                />
              </div>

              <div>
                <label className="mb-2 block text-sm text-slate-300">邮箱地址</label>
                <input
                  type="email"
                  value={email}
                  onChange={(e) => setEmail(e.target.value)}
                  placeholder="your@email.com"
                  required
                  className="w-full rounded-lg border border-slate-700 bg-slate-800/50 px-4 py-3 text-white placeholder-slate-500 focus:border-emerald-500 focus:outline-none"
                />
              </div>

              <div>
                <label className="mb-2 block text-sm text-slate-300">密码</label>
                <input
                  type="password"
                  value={password}
                  onChange={(e) => setPassword(e.target.value)}
                  placeholder="设置密码（至少6位）"
                  required
                  minLength={6}
                  className="w-full rounded-lg border border-slate-700 bg-slate-800/50 px-4 py-3 text-white placeholder-slate-500 focus:border-emerald-500 focus:outline-none"
                />
              </div>

              <div>
                <label className="mb-2 block text-sm text-slate-300">确认密码</label>
                <input
                  type="password"
                  value={confirmPassword}
                  onChange={(e) => setConfirmPassword(e.target.value)}
                  placeholder="再次输入密码"
                  required
                  className="w-full rounded-lg border border-slate-700 bg-slate-800/50 px-4 py-3 text-white placeholder-slate-500 focus:border-emerald-500 focus:outline-none"
                />
              </div>

              <button
                type="submit"
                disabled={isLoading}
                className="w-full rounded-lg bg-emerald-500 py-3 font-medium text-white transition-colors hover:bg-emerald-600 disabled:opacity-50"
              >
                {isLoading ? "注册中..." : "注册"}
              </button>
            </form>

            {/* 服务条款 */}
            <p className="mt-4 text-center text-xs text-slate-500">
              注册即表示同意我们的{" "}
              <Link href="#" className="text-emerald-400 hover:text-emerald-300">
                服务条款
              </Link>{" "}
              和{" "}
              <Link href="#" className="text-emerald-400 hover:text-emerald-300">
                隐私政策
              </Link>
            </p>

            {/* 登录链接 */}
            <p className="mt-6 text-center text-sm text-slate-400">
              已有账号？{" "}
              <Link href="/auth/login" className="text-emerald-400 hover:text-emerald-300">
                立即登录
              </Link>
            </p>
          </div>

          {/* 返回首页 */}
          <p className="mt-6 text-center">
            <Link href="/" className="text-sm text-slate-500 hover:text-emerald-400">
              ← 返回首页
            </Link>
          </p>
        </div>
      </main>
    </div>
  );
}