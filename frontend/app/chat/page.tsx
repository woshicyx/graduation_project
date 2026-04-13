"use client";

import Link from "next/link";
import { useState, useRef, useEffect } from "react";
import { recommendMovies, RecommendItem } from "@/lib/api/ai";
import { getMovieDetail } from "@/lib/api/movie";

interface Message {
  role: "user" | "assistant";
  content: string;
  movieId?: number;
}

export default function ChatPage() {
  const [messages, setMessages] = useState<Message[]>([
    { 
      role: "assistant", 
      content: "你好！我是 MovieAI 智能助手。我可以根据你的喜好推荐电影，比如告诉我你想看什么类型的电影，或者描述一下你的心情，我来分析并给你推荐！" 
    }
  ]);
  const [input, setInput] = useState("");
  const [isLoading, setIsLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);
  const messagesEndRef = useRef<HTMLDivElement>(null);

  // 自动滚动到最新消息
  useEffect(() => {
    messagesEndRef.current?.scrollIntoView({ behavior: "smooth" });
  }, [messages]);

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    if (!input.trim() || isLoading) return;

    const userMessage = { role: "user" as const, content: input };
    setMessages(prev => [...prev, userMessage]);
    setInput("");
    setIsLoading(true);
    setError(null);

    try {
      // 调用后端 AI 推荐 API
      const result = await recommendMovies({
        query: input,
        max_results: 5,
        include_reasons: true,
      });

      // 构建 AI 回复
      if (result.items && result.items.length > 0) {
        const recommendations = result.items.map((item: RecommendItem) => {
          const reason = item.reason || "推荐观看";
          return `🎬 **${item.title}** (相关性: ${(item.relevance_score * 100).toFixed(0)}%)\n   ${reason}`;
        }).join('\n\n');

        const aiResponse = `根据你的需求「${input}」，我为你推荐以下电影：\n\n${recommendations}\n\n点击电影标题可以查看详细信息，要了解其中任何一部吗？`;
        
        // 添加电影ID到消息中
        setMessages(prev => [...prev, { 
          role: "assistant", 
          content: aiResponse,
          movieId: result.items[0]?.movie_id
        }]);
      } else {
        setMessages(prev => [...prev, { 
          role: "assistant", 
          content: "抱歉，我没有找到符合你需求的电影。你可以尝试用不同的方式描述，比如指定电影类型、导演或者心情。" 
        }]);
      }
    } catch (err) {
      console.error("AI推荐失败:", err);
      setError("AI 推荐服务暂时不可用，请检查后端服务是否运行");
      setMessages(prev => [...prev, { 
        role: "assistant", 
        content: "抱歉，AI 推荐服务暂时不可用。后端服务可能未启动或出现问题。请稍后再试，或直接使用搜索功能。" 
      }]);
    } finally {
      setIsLoading(false);
    }
  };

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
            <Link href="/profile" className="text-sm text-slate-300 hover:text-emerald-400">
              个人中心
            </Link>
          </div>
        </div>
      </header>

      {/* 聊天区域 */}
      <main className="relative z-10 mx-auto flex h-[calc(100vh-64px)] max-w-4xl flex-col px-4 py-6">
        {/* 消息列表 */}
        <div className="flex-1 overflow-y-auto space-y-4">
          {messages.map((msg, i) => (
            <div key={i} className={`flex ${msg.role === "user" ? "justify-end" : "justify-start"}`}>
              <div className={`max-w-[80%] rounded-2xl px-4 py-3 ${
                msg.role === "user"
                  ? "bg-emerald-500 text-white"
                  : "border border-slate-700 bg-slate-800/50 text-slate-100"
              }`}>
                {msg.role === "assistant" && (
                  <div className="mb-2 flex items-center gap-2 border-b border-slate-700 pb-2">
                    <div className="h-6 w-6 rounded-full bg-emerald-500" />
                    <span className="text-xs font-medium text-emerald-400">MovieAI</span>
                  </div>
                )}
                <div className="whitespace-pre-wrap text-sm leading-relaxed">{msg.content}</div>
              </div>
            </div>
          ))}
          {isLoading && (
            <div className="flex justify-start">
              <div className="rounded-2xl border border-slate-700 bg-slate-800/50 px-4 py-3">
                <div className="flex items-center gap-2">
                  <div className="h-2 w-2 animate-bounce rounded-full bg-emerald-400" style={{animationDelay: "0ms"}} />
                  <div className="h-2 w-2 animate-bounce rounded-full bg-emerald-400" style={{animationDelay: "150ms"}} />
                  <div className="h-2 w-2 animate-bounce rounded-full bg-emerald-400" style={{animationDelay: "300ms"}} />
                </div>
              </div>
            </div>
          )}
          <div ref={messagesEndRef} />
        </div>

        {/* 错误提示 */}
        {error && (
          <div className="mx-auto mb-4 w-full rounded-lg bg-red-500/20 border border-red-500/50 px-4 py-2 text-red-400 text-sm">
            {error}
          </div>
        )}

        {/* 输入区域 */}
        <form onSubmit={handleSubmit} className="mt-4">
          <div className="relative">
            <textarea
              value={input}
              onChange={(e) => setInput(e.target.value)}
              placeholder="描述你想要的电影，比如：'我想看一部类似《盗梦空间》的烧脑悬疑片'"
              rows={2}
              className="w-full resize-none rounded-xl border border-slate-700 bg-slate-800/50 px-4 py-3 pr-12 text-white placeholder-slate-500 focus:border-emerald-500 focus:outline-none"
              onKeyDown={(e) => {
                if (e.key === 'Enter' && !e.shiftKey) {
                  e.preventDefault();
                  handleSubmit(e);
                }
              }}
            />
            <button
              type="submit"
              disabled={!input.trim() || isLoading}
              className="absolute bottom-3 right-3 flex h-8 w-8 items-center justify-center rounded-lg bg-emerald-500 text-white transition-colors hover:bg-emerald-600 disabled:opacity-50"
            >
              <svg className="h-4 w-4" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M12 19l9 2-9-18-9 18 9-2zm0 0v-8" />
              </svg>
            </button>
          </div>
          <p className="mt-2 text-center text-xs text-slate-500">
            支持中文和英文描述，如："Nolan's sci-fi movies with high rating"
          </p>
        </form>
      </main>
    </div>
  );
}
