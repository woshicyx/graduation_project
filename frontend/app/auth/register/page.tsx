"use client";

import Link from "next/link";
import { useState } from "react";
import { useRouter } from "next/navigation";
import { useAuth } from "@/contexts/AuthContext";
import { validateEmail, validatePassword, validateUsername } from "@/lib/api/auth";
import { Loader2, User, Mail, Lock, AlertCircle, CheckCircle } from "lucide-react";

export default function RegisterPage() {
  const router = useRouter();
  const { register, isLoading, error, clearError } = useAuth();
  
  const [username, setUsername] = useState("");
  const [email, setEmail] = useState("");
  const [password, setPassword] = useState("");
  const [confirmPassword, setConfirmPassword] = useState("");
  const [formErrors, setFormErrors] = useState<{
    username?: string;
    email?: string;
    password?: string;
    confirmPassword?: string;
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
    
    const usernameError = validateUsername(username);
    if (usernameError) {
      errors.username = usernameError;
    }
    
    const emailError = validateEmail(email);
    if (emailError) {
      errors.email = emailError;
    }
    
    const passwordError = validatePassword(password);
    if (passwordError) {
      errors.password = passwordError;
    }
    
    if (password !== confirmPassword) {
      errors.confirmPassword = "两次输入的密码不一致";
    }

    if (Object.keys(errors).length > 0) {
      setFormErrors(errors);
      return;
    }

    try {
      await register({ username, email, password, confirm_password: password });
      setSuccessMessage("注册成功！正在跳转...");
      // 延迟跳转，让用户看到成功消息
      setTimeout(() => {
        router.push("/");
      }, 500);
    } catch (err) {
      // 错误已在 AuthContext 中设置
      console.error("注册失败:", err);
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

          {/* 注册表单 */}
          <div className="rounded-2xl border border-white/5 bg-gradient-to-b from-white/[0.05] to-transparent p-8 backdrop-blur-sm">
            <h2 className="mb-2 text-center text-2xl font-bold text-white">创建账号</h2>
            <p className="mb-6 text-center text-sm text-white/50">加入 MovieAI，开启精彩观影之旅</p>

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
              {/* 用户名 */}
              <div>
                <label className="mb-2 block text-sm font-medium text-white/80">
                  用户名
                </label>
                <div className="relative">
                  <User className="absolute left-4 top-1/2 h-5 w-5 -translate-y-1/2 text-white/40" />
                  <input
                    type="text"
                    value={username}
                    onChange={(e) => setUsername(e.target.value)}
                    placeholder="设置用户名"
                    className={`w-full rounded-xl border ${formErrors.username ? 'border-red-500' : 'border-white/10'} bg-white/5 py-3.5 pl-12 pr-4 text-white placeholder-white/30 focus:border-red-500/50 focus:outline-none focus:ring-2 focus:ring-red-500/20 transition-all`}
                  />
                </div>
                {formErrors.username && (
                  <p className="mt-2 text-xs text-red-400">{formErrors.username}</p>
                )}
              </div>

              {/* 邮箱 */}
              <div>
                <label className="mb-2 block text-sm font-medium text-white/80">
                  邮箱地址
                </label>
                <div className="relative">
                  <Mail className="absolute left-4 top-1/2 h-5 w-5 -translate-y-1/2 text-white/40" />
                  <input
                    type="email"
                    value={email}
                    onChange={(e) => setEmail(e.target.value)}
                    placeholder="your@email.com"
                    className={`w-full rounded-xl border ${formErrors.email ? 'border-red-500' : 'border-white/10'} bg-white/5 py-3.5 pl-12 pr-4 text-white placeholder-white/30 focus:border-red-500/50 focus:outline-none focus:ring-2 focus:ring-red-500/20 transition-all`}
                  />
                </div>
                {formErrors.email && (
                  <p className="mt-2 text-xs text-red-400">{formErrors.email}</p>
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
                    placeholder="设置密码（至少6位）"
                    className={`w-full rounded-xl border ${formErrors.password ? 'border-red-500' : 'border-white/10'} bg-white/5 py-3.5 pl-12 pr-4 text-white placeholder-white/30 focus:border-red-500/50 focus:outline-none focus:ring-2 focus:ring-red-500/20 transition-all`}
                  />
                </div>
                {formErrors.password && (
                  <p className="mt-2 text-xs text-red-400">{formErrors.password}</p>
                )}
              </div>

              {/* 确认密码 */}
              <div>
                <label className="mb-2 block text-sm font-medium text-white/80">
                  确认密码
                </label>
                <div className="relative">
                  <Lock className="absolute left-4 top-1/2 h-5 w-5 -translate-y-1/2 text-white/40" />
                  <input
                    type="password"
                    value={confirmPassword}
                    onChange={(e) => setConfirmPassword(e.target.value)}
                    placeholder="再次输入密码"
                    className={`w-full rounded-xl border ${formErrors.confirmPassword ? 'border-red-500' : 'border-white/10'} bg-white/5 py-3.5 pl-12 pr-4 text-white placeholder-white/30 focus:border-red-500/50 focus:outline-none focus:ring-2 focus:ring-red-500/20 transition-all`}
                  />
                </div>
                {formErrors.confirmPassword && (
                  <p className="mt-2 text-xs text-red-400">{formErrors.confirmPassword}</p>
                )}
              </div>

              {/* 服务条款 */}
              <p className="text-center text-xs text-white/40">
                注册即表示同意我们的{" "}
                <Link href="#" className="text-red-400 hover:text-red-300 transition-colors">
                  服务条款
                </Link>{" "}
                和{" "}
                <Link href="#" className="text-red-400 hover:text-red-300 transition-colors">
                  隐私政策
                </Link>
              </p>

              {/* 提交按钮 */}
              <button
                type="submit"
                disabled={isLoading}
                className="w-full rounded-xl bg-gradient-to-r from-red-600 to-red-700 py-3.5 text-sm font-medium text-white shadow-lg shadow-red-600/30 transition-all hover:from-red-500 hover:to-red-600 disabled:opacity-50 disabled:cursor-not-allowed flex items-center justify-center gap-2"
              >
                {isLoading ? (
                  <>
                    <Loader2 className="h-5 w-5 animate-spin" />
                    注册中...
                  </>
                ) : (
                  "注册"
                )}
              </button>
            </form>

            {/* 登录链接 */}
            <p className="mt-6 text-center text-sm text-white/50">
              已有账号？{" "}
              <Link href="/auth/login" className="font-medium text-red-400 hover:text-red-300 transition-colors">
                立即登录
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
