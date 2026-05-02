"use client";

import Link from "next/link";
import { useState } from "react";
import { useRouter } from "next/navigation";
import { useAuth } from "@/contexts/AuthContext";
import { validateEmail, validatePassword } from "@/lib/api/auth";
import { Loader2, Mail, Lock, AlertCircle, CheckCircle } from "lucide-react";

export default function LoginPage() {
  const router = useRouter();
  const { login, isLoading, error, clearError } = useAuth();
  
  const [identifier, setIdentifier] = useState(""); // 用户名或邮箱
  const [password, setPassword] = useState("");
  const [formErrors, setFormErrors] = useState<{
    identifier?: string;
    password?: string;
    general?: string;
  }>({});
  const [successMessage, setSuccessMessage] = useState<string | null>(null);

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    setFormErrors({});
    setSuccessMessage(null);
    clearError();

    // 表单验证
    const errors: typeof formErrors = {};
    
    if (!identifier.trim()) {
      errors.identifier = "请输入用户名或邮箱";
    }
    
    const passwordError = validatePassword(password);
    if (passwordError) {
      errors.password = passwordError;
    }

    if (Object.keys(errors).length > 0) {
      setFormErrors(errors);
      return;
    }

    try {
      await login({ identifier, password });
      setSuccessMessage("登录成功！正在跳转...");
      // 延迟跳转，让用户看到成功消息
      setTimeout(() => {
        router.push("/");
      }, 500);
    } catch (err) {
      // 错误已在 AuthContext 中设置
      console.error("登录失败:", err);
    }
  };

  return (
    <div className="relative min-h-screen overflow-hidden bg-[#0a0a0f]">
      {/* 背景装饰 */}
      <div className="fixed inset-0 overflow-hidden pointer-events-none">
        {/* 顶部渐变光晕 */}
        <div className="absolute -top-1/2 -right-1/4 h-[800px] w-[800px] rounded-full bg-red-600/5 blur-[120px]" />
        <div className="absolute -top-1/3 left-1/4 h-[600px] w-[600px] rounded-full bg-orange-500/5 blur-[100px]" />
        
        {/* 底部渐变 */}
        <div className="absolute bottom-0 left-0 right-0 h-1/2 bg-gradient-to-t from-[#0a0a0f] via-[#0a0a0f]/50 to-transparent" />
      </div>

      <main className="relative z-10 flex min-h-screen items-center justify-center px-4">
        <div className="w-full max-w-md">
          {/* Logo */}
          <div className="mb-8 text-center">
            <Link href="/" className="inline-flex items-center gap-3 group">
              <div className="relative">
                <div className="flex h-12 w-12 items-center justify-center rounded-xl bg-gradient-to-br from-red-600 to-red-700 shadow-lg shadow-red-600/30">
                  <svg className="h-6 w-6 text-white" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                    <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M7 4v16M17 4v16M3 8h4m10 0h4M3 12h18M3 16h4m10 0h4M4 20h16a1 1 0 001-1V5a1 1 0 00-1-1H4a1 1 0 00-1 1v14a1 1 0 001 1z" />
                  </svg>
                </div>
                <div className="absolute -inset-1 rounded-xl bg-gradient-to-br from-red-600 to-red-700 opacity-0 blur transition-opacity duration-300 group-hover:opacity-50" />
              </div>
              <div className="flex items-baseline gap-1">
                <span className="text-2xl font-bold tracking-tight text-white">
                  Movie
                </span>
                <span className="text-2xl font-bold tracking-tight text-red-500">
                  AI
                </span>
              </div>
            </Link>
          </div>

          {/* 登录表单 */}
          <div className="rounded-2xl border border-white/5 bg-gradient-to-b from-white/[0.05] to-transparent p-8 backdrop-blur-sm">
            <h2 className="mb-2 text-center text-2xl font-bold text-white">登录账号</h2>
            <p className="mb-6 text-center text-sm text-white/50">欢迎回来，继续探索精彩电影</p>
            
            {/* 成功消息 */}
            {successMessage && (
              <div className="mb-6 flex items-center gap-2 rounded-lg bg-green-500/20 border border-green-500/30 px-4 py-3 text-green-300">
                <CheckCircle className="h-5 w-5" />
                <span className="text-sm">{successMessage}</span>
              </div>
            )}
            
            {/* 错误消息 */}
            {(error || formErrors.general) && (
              <div className="mb-6 flex items-center gap-2 rounded-lg bg-red-500/20 border border-red-500/30 px-4 py-3 text-red-300">
                <AlertCircle className="h-5 w-5" />
                <span className="text-sm">{error || formErrors.general}</span>
              </div>
            )}
            
            <form onSubmit={handleSubmit} className="space-y-5">
              {/* 用户名/邮箱 */}
              <div>
                <label className="mb-2 block text-sm font-medium text-white/80">
                  用户名或邮箱
                </label>
                <div className="relative">
                  <Mail className="absolute left-4 top-1/2 h-5 w-5 -translate-y-1/2 text-white/40" />
                  <input
                    type="text"
                    value={identifier}
                    onChange={(e) => setIdentifier(e.target.value)}
                    placeholder="输入用户名或邮箱"
                    className={`w-full rounded-xl border ${formErrors.identifier ? 'border-red-500' : 'border-white/10'} bg-white/5 py-3.5 pl-12 pr-4 text-white placeholder-white/30 focus:border-red-500/50 focus:outline-none focus:ring-2 focus:ring-red-500/20 transition-all`}
                  />
                </div>
                {formErrors.identifier && (
                  <p className="mt-2 text-xs text-red-400">{formErrors.identifier}</p>
                )}
              </div>

              {/* 密码 */}
              <div>
                <label className="mb-2 block text-sm font-medium text-white/80">
                  密码
                </label>
                <div className="relative">
                  <Lock className="absolute left-4 top-1/2 h-5 w-5 -translate-y-1/2 text-white/40" />
                  <input
                    type="password"
                    value={password}
                    onChange={(e) => setPassword(e.target.value)}
                    placeholder="输入密码"
                    className={`w-full rounded-xl border ${formErrors.password ? 'border-red-500' : 'border-white/10'} bg-white/5 py-3.5 pl-12 pr-4 text-white placeholder-white/30 focus:border-red-500/50 focus:outline-none focus:ring-2 focus:ring-red-500/20 transition-all`}
                  />
                </div>
                {formErrors.password && (
                  <p className="mt-2 text-xs text-red-400">{formErrors.password}</p>
                )}
              </div>

              {/* 忘记密码 */}
              <div className="flex items-center justify-end">
                <Link href="/auth/forgot-password" className="text-xs text-white/50 hover:text-red-400 transition-colors">
                  忘记密码？
                </Link>
              </div>

              {/* 提交按钮 */}
              <button
                type="submit"
                disabled={isLoading}
                className="w-full rounded-xl bg-gradient-to-r from-red-600 to-rose-600 py-3.5 text-sm font-bold text-white shadow-lg shadow-red-900/50 transition-all hover:brightness-110 hover:shadow-red-600/50 active:scale-95 disabled:opacity-50 disabled:cursor-not-allowed flex items-center justify-center gap-2"
              >
                {isLoading ? (
                  <>
                    <Loader2 className="h-5 w-5 animate-spin" />
                    登录中...
                  </>
                ) : (
                  "登录"
                )}
              </button>
            </form>

            {/* 分隔线 */}
            <div className="relative my-6">
              <div className="absolute inset-0 flex items-center">
                <div className="w-full border-t border-white/10" />
              </div>
              <div className="relative flex justify-center text-xs">
                <span className="bg-[#0a0a0f] px-4 text-white/40">或</span>
              </div>
            </div>

            {/* 第三方登录 */}
            <div className="space-y-3">
              <button className="flex w-full items-center justify-center gap-3 rounded-xl border border-white/10 bg-white/5 py-3 text-sm text-white/80 transition-all hover:bg-white/10 hover:text-white">
                <svg className="h-5 w-5" viewBox="0 0 24 24" fill="currentColor">
                  <path d="M12 0c-6.626 0-12 5.373-12 12 0 5.302 3.438 9.8 8.207 11.387.599.111.793-.261.793-.577v-2.234c-3.338.726-4.033-1.416-4.033-1.416-.546-1.387-1.333-1.756-1.333-1.756-1.089-.745.083-.729.083-.729 1.205.084 1.839 1.237 1.839 1.237 1.07 1.834 2.807 1.304 3.492.997.107-.775.418-1.305.762-1.604-2.665-.305-5.467-1.334-5.467-5.931 0-1.311.469-2.381 1.236-3.221-.124-.303-.535-1.524.117-3.176 0 0 1.008-.322 3.301 1.23.957-.266 1.983-.399 3.003-.404 1.02.005 2.047.138 3.006.404 2.291-1.552 3.297-1.23 3.297-1.23.653 1.653.242 2.874.118 3.176.77.84 1.235 1.911 1.235 3.221 0 4.609-2.807 5.624-5.479 5.921.43.372.823 1.102.823 2.222v3.293c0 .319.192.694.801.576 4.765-1.589 8.199-6.086 8.199-11.386 0-6.627-5.373-12-12-12z"/>
                </svg>
                使用 GitHub 登录
              </button>

              <button className="flex w-full items-center justify-center gap-3 rounded-xl border border-white/10 bg-white/5 py-3 text-sm text-white/80 transition-all hover:bg-white/10 hover:text-white">
                <svg className="h-5 w-5" viewBox="0 0 24 24">
                  <path fill="#4285F4" d="M22.56 12.25c0-.78-.07-1.53-.2-2.25H12v4.26h5.92c-.26 1.37-1.04 2.53-2.21 3.31v2.77h3.57c2.08-1.92 3.28-4.74 3.28-8.09z"/>
                  <path fill="#34A853" d="M12 23c2.97 0 5.46-.98 7.28-2.66l-3.57-2.77c-.98.66-2.23 1.06-3.71 1.06-2.86 0-5.29-1.93-6.16-4.53H2.18v2.84C3.99 20.53 7.7 23 12 23z"/>
                  <path fill="#FBBC05" d="M5.84 14.09c-.22-.66-.35-1.36-.35-2.09s.13-1.43.35-2.09V7.07H2.18C1.43 8.55 1 10.22 1 12s.43 3.45 1.18 4.93l2.85-2.22.81-.62z"/>
                  <path fill="#EA4335" d="M12 5.38c1.62 0 3.06.56 4.21 1.64l3.15-3.15C17.45 2.09 14.97 1 12 1 7.7 1 3.99 3.47 2.18 7.07l3.66 2.84c.87-2.6 3.3-4.53 6.16-4.53z"/>
                </svg>
                使用 Google 登录
              </button>
            </div>

            {/* 注册链接 */}
            <p className="mt-6 text-center text-sm text-white/50">
              还没有账号？{" "}
              <Link href="/auth/register" className="font-medium text-red-400 hover:text-red-300 transition-colors">
                立即注册
              </Link>
            </p>
          </div>

          {/* 返回首页 */}
          <p className="mt-6 text-center">
            <Link href="/" className="inline-flex items-center gap-2 text-sm text-white/40 hover:text-white transition-colors">
              <svg className="h-4 w-4" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M15 19l-7-7 7-7" />
              </svg>
              返回首页
            </Link>
          </p>
        </div>
      </main>
    </div>
  );
}
