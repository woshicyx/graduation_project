import { LoginForm } from "@/components/auth/login-form";
import Link from "next/link";
import { ArrowLeft } from "lucide-react";

export default function LoginPage() {
  return (
    <div className="min-h-screen bg-gradient-to-br from-slate-950 via-slate-950 to-slate-900">
      {/* 背景装饰 */}
      <div className="fixed inset-0 overflow-hidden">
        <div className="absolute -top-40 -right-40 h-80 w-80 rounded-full bg-emerald-500/10 blur-3xl" />
        <div className="absolute top-1/3 -left-40 h-64 w-64 rounded-full bg-blue-500/10 blur-3xl" />
        <div className="absolute bottom-40 right-1/4 h-96 w-96 rounded-full bg-purple-500/5 blur-3xl" />
        <div className="absolute inset-0 bg-gradient-to-b from-transparent via-slate-950/50 to-slate-950" />
      </div>

      <main className="relative z-10 flex min-h-screen flex-col items-center justify-center px-4 py-12">
        <div className="w-full max-w-md">
          {/* 返回首页链接 */}
          <Link 
            href="/" 
            className="mb-8 inline-flex items-center text-sm text-slate-300 hover:text-white transition-colors"
          >
            <ArrowLeft className="mr-2 h-4 w-4" />
            返回首页
          </Link>

          {/* Logo */}
          <div className="mb-8 text-center">
            <div className="inline-flex items-center gap-3 mb-4">
              <div className="h-10 w-10 rounded-lg bg-gradient-to-br from-emerald-500 to-emerald-600" />
              <h1 className="text-2xl font-bold tracking-tight text-white">
                Movie<span className="text-emerald-400">AI</span>
              </h1>
            </div>
            <p className="text-slate-300">
              智能电影推荐平台 - 发现属于你的电影世界
            </p>
          </div>

          {/* 登录表单 */}
          <LoginForm />

          {/* 功能说明 */}
          <div className="mt-8 rounded-lg border border-slate-800 bg-slate-900/50 p-4">
            <h3 className="mb-2 text-sm font-medium text-slate-200">
              注册用户专属功能
            </h3>
            <ul className="space-y-1 text-sm text-slate-400">
              <li className="flex items-center">
                <div className="mr-2 h-1.5 w-1.5 rounded-full bg-emerald-500" />
                个性化电影推荐（猜你喜欢）
              </li>
              <li className="flex items-center">
                <div className="mr-2 h-1.5 w-1.5 rounded-full bg-emerald-500" />
                收藏喜欢的电影
              </li>
              <li className="flex items-center">
                <div className="mr-2 h-1.5 w-1.5 rounded-full bg-emerald-500" />
                自动记录浏览历史
              </li>
              <li className="flex items-center">
                <div className="mr-2 h-1.5 w-1.5 rounded-full bg-emerald-500" />
                完整的个人中心
              </li>
            </ul>
          </div>
        </div>
      </main>
    </div>
  );
}