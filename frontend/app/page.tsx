import { HeroSection } from "@/components/hero-section";
import { MovieCarousel } from "@/components/movie-carousel";
import { SearchHero } from "@/components/search-hero";
import { AiChatFab } from "@/components/ai-chat-fab";
import { UserNavigation } from "@/components/user-navigation";

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
        {/* 导航占位符 */}
        <header className="mx-auto mb-8 w-full max-w-7xl">
          <div className="flex items-center justify-between">
            <div className="flex items-center gap-3">
              <div className="h-8 w-8 rounded-lg bg-gradient-to-br from-emerald-500 to-emerald-600" />
              <h1 className="text-xl font-bold tracking-tight text-white">
                Movie<span className="text-emerald-400">AI</span>
              </h1>
            </div>
            <UserNavigation />
          </div>
        </header>

        {/* 主要内容 */}
        <div className="mx-auto w-full max-w-7xl flex-1">
          <SearchHero />
          <HeroSection />
          
          <div className="mt-12 space-y-12">
            <MovieCarousel
              title="影史票房 TOP 50"
              subtitle="基于真实数据库中的票房数据，实时从4,803部电影中统计"
              variant="boxOffice"
              limit={12}
            />
            
            <div className="relative">
              <div className="absolute inset-0 rounded-3xl bg-gradient-to-r from-emerald-500/5 via-transparent to-blue-500/5 blur-3xl" />
              <MovieCarousel
                title="最高评分 TOP 50"
                subtitle="基于真实数据库中的评分数据，实时从4,803部电影中统计"
                variant="rating"
                limit={12}
              />
            </div>
          </div>

          {/* 功能说明区域 */}
          <div className="mt-16 rounded-3xl border border-slate-700/60 bg-gradient-to-br from-slate-900/40 via-slate-900/20 to-slate-950/40 p-8 backdrop-blur">
            <div className="grid gap-8 md:grid-cols-3">
              <div className="space-y-4">
                <div className="inline-flex rounded-xl bg-emerald-500/20 p-3">
                  <div className="h-6 w-6 rounded-lg bg-gradient-to-br from-emerald-500 to-emerald-600" />
                </div>
                <h3 className="text-lg font-semibold text-white">智能搜索</h3>
                <p className="text-sm text-slate-400">
                  支持自然语言描述、多维度筛选，结合传统 SQL 查询与向量语义检索。
                </p>
              </div>
              
              <div className="space-y-4">
                <div className="inline-flex rounded-xl bg-blue-500/20 p-3">
                  <div className="h-6 w-6 rounded-lg bg-gradient-to-br from-blue-500 to-blue-600" />
                </div>
                <h3 className="text-lg font-semibold text-white">AI 推荐</h3>
                <p className="text-sm text-slate-400">
                  基于 RAG + LLM 技术，理解你的观影偏好，生成个性化电影推荐列表。
                </p>
              </div>
              
              <div className="space-y-4">
                <div className="inline-flex rounded-xl bg-purple-500/20 p-3">
                  <div className="h-6 w-6 rounded-lg bg-gradient-to-br from-purple-500 to-purple-600" />
                </div>
                <h3 className="text-lg font-semibold text-white">数据驱动</h3>
                <p className="text-sm text-slate-400">
                  整合电影元数据、影评、票房等多维度信息，提供全面的电影分析。
                </p>
              </div>
            </div>
          </div>

          {/* 技术栈展示 */}
          <div className="mt-12 text-center">
            <p className="text-sm text-slate-500">
              技术栈：Next.js 14 · TypeScript · Tailwind CSS · FastAPI · PostgreSQL · pgvector · OpenAI API
            </p>
            <p className="mt-2 text-xs text-slate-600">
              毕业设计项目 · 智能电影推荐平台 · 当前版本：v1.0.0-alpha
            </p>
          </div>
        </div>

        {/* AI 聊天悬浮按钮 */}
        <AiChatFab />
      </main>
    </div>
  );
}