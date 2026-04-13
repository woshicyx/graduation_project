"use client";

import Link from "next/link";
import { useState, useRef, useEffect } from "react";
import { recommendMoviesStream, StreamMovieItem } from "@/lib/api/ai";
import { Sparkles, Loader2 } from "lucide-react";

interface Message {
  role: "user" | "assistant";
  content: string;
  movies?: StreamMovieItem[];
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
  const [currentMovie, setCurrentMovie] = useState<StreamMovieItem | null>(null);
  const messagesEndRef = useRef<HTMLDivElement>(null);

  // 自动滚动到最新消息
  useEffect(() => {
    messagesEndRef.current?.scrollIntoView({ behavior: "smooth" });
  }, [messages, currentMovie]);

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    if (!input.trim() || isLoading) return;

    const userMessage = { role: "user" as const, content: input };
    setMessages(prev => [...prev, userMessage]);
    setInput("");
    setIsLoading(true);
    setCurrentMovie(null);

    const query = input;
    const movies: StreamMovieItem[] = [];

    try {
      await recommendMoviesStream(
        {
          query: query,
          max_results: 5,
          include_reasons: true,
        },
        // onMovie callback
        (movie) => {
          setCurrentMovie(movie);
          movies.push(movie);
        },
        // onDone callback
        (total, timeMs) => {
          if (movies.length > 0) {
            const recommendations = movies.map((item, i) => {
              return `🎬 **${item.title}** (相关性: ${(item.relevance_score * 100).toFixed(0)}%)${item.genres?.length ? '\n   📽️ ' + item.genres.join(', ') : ''}`;
            }).join('\n\n');

            const aiResponse = `根据你的需求「${query}」，我为你推荐以下电影：\n\n${recommendations}\n\n点击电影标题可以查看详细信息，要了解其中任何一部吗？`;
            
            setMessages(prev => [...prev, { role: "assistant", content: aiResponse, movies }]);
          } else {
            setMessages(prev => [...prev, { 
              role: "assistant", 
              content: "抱歉，我没有找到符合你需求的电影。你可以尝试用不同的方式描述，比如指定电影类型、导演或者心情。" 
            }]);
          }
          setCurrentMovie(null);
          setIsLoading(false);
        },
        // onError callback
        (error) => {
          console.error("流式推荐失败:", error);
          setMessages(prev => [...prev, { 
            role: "assistant", 
            content: "抱歉，AI 推荐服务暂时不可用。后端服务可能未启动或出现问题。请稍后再试，或直接使用搜索功能。" 
          }]);
          setCurrentMovie(null);
          setIsLoading(false);
        }
      );
    } catch (err) {
      console.error("AI推荐失败:", err);
      setMessages(prev => [...prev, { 
        role: "assistant", 
        content: "抱歉，AI 推荐服务暂时不可用。后端服务可能未启动或出现问题。请稍后再试，或直接使用搜索功能。" 
      }]);
      setCurrentMovie(null);
      setIsLoading(false);
    }
  };

  return (
    <div className="relative min-h-screen bg-[#0a0a0f]">
      {/* 背景装饰 */}
      <div className="fixed inset-0 overflow-hidden pointer-events-none">
        <div className="absolute -top-1/2 -right-1/4 h-[800px] w-[800px] rounded-full bg-purple-600/5 blur-[120px]" />
        <div className="absolute -top-1/3 left-1/4 h-[600px] w-[600px] rounded-full bg-blue-500/5 blur-[100px]" />
      </div>

      {/* 导航 */}
      <header className="relative z-10 border-b border-white/5 bg-[#0a0a0f]/80 backdrop-blur-xl">
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
            <Link href="/search" className="text-sm text-white/70 hover:text-white">
              搜索
            </Link>
            <Link href="/profile" className="text-sm text-white/70 hover:text-white">
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
              <div className={`max-w-[85%] rounded-2xl px-4 py-3 ${
                msg.role === "user"
                  ? "bg-gradient-to-r from-red-600 to-red-700 text-white"
                  : "border border-white/10 bg-white/5 text-white/90 backdrop-blur"
              }`}>
                {msg.role === "assistant" && (
                  <div className="mb-2 flex items-center gap-2 border-b border-white/10 pb-2">
                    <div className="h-6 w-6 rounded-full bg-gradient-to-br from-red-600 to-red-700 flex items-center justify-center">
                      <Sparkles className="h-3 w-3 text-white" />
                    </div>
                    <span className="text-xs font-medium text-red-400">MovieAI</span>
                  </div>
                )}
                <div className="whitespace-pre-wrap text-sm leading-relaxed">{msg.content}</div>
              </div>
            </div>
          ))}
          
          {/* 流式输出 - 单个电影卡片 */}
          {currentMovie && (
            <div className="flex justify-start">
              <div className="max-w-[85%] rounded-2xl border border-white/10 bg-white/5 p-4 backdrop-blur">
                <div className="mb-2 flex items-center gap-2 border-b border-white/10 pb-2">
                  <div className="flex items-center gap-1">
                    <Loader2 className="h-4 w-4 animate-spin text-purple-400" />
                    <span className="text-xs font-medium text-purple-400">正在搜索...</span>
                  </div>
                </div>
                
                <div className="animate-pulse">
                  <div className="flex gap-4">
                    <div className="h-24 w-16 rounded-lg bg-white/10 flex-shrink-0" />
                    <div className="flex-1 space-y-2">
                      <div className="h-4 w-3/4 rounded bg-white/10" />
                      <div className="h-3 w-1/2 rounded bg-white/10" />
                      <div className="h-3 w-1/4 rounded bg-white/10" />
                    </div>
                  </div>
                  <p className="mt-3 text-xs text-white/50">
                    正在分析: <span className="text-white/70">{currentMovie.title}</span>
                  </p>
                </div>
              </div>
            </div>
          )}
          
          {isLoading && !currentMovie && (
            <div className="flex justify-start">
              <div className="rounded-2xl border border-white/10 bg-white/5 px-4 py-3 backdrop-blur">
                <div className="flex items-center gap-2">
                  <div className="h-2 w-2 animate-bounce rounded-full bg-purple-400" style={{animationDelay: "0ms"}} />
                  <div className="h-2 w-2 animate-bounce rounded-full bg-purple-400" style={{animationDelay: "150ms"}} />
                  <div className="h-2 w-2 animate-bounce rounded-full bg-purple-400" style={{animationDelay: "300ms"}} />
                </div>
              </div>
            </div>
          )}
          <div ref={messagesEndRef} />
        </div>

        {/* 输入区域 */}
        <form onSubmit={handleSubmit} className="mt-4">
          <div className="relative">
            <textarea
              value={input}
              onChange={(e) => setInput(e.target.value)}
              placeholder="描述你想要的电影，比如：'我想看一部类似《盗梦空间》的烧脑悬疑片'"
              rows={2}
              className="w-full resize-none rounded-xl border border-white/10 bg-white/5 px-4 py-3 pr-12 text-white placeholder-white/40 focus:border-purple-500 focus:outline-none focus:ring-1 focus:ring-purple-500"
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
              className="absolute bottom-3 right-3 flex h-8 w-8 items-center justify-center rounded-lg bg-gradient-to-r from-red-600 to-red-700 text-white transition-all hover:from-red-500 hover:to-red-600 disabled:opacity-50"
            >
              <svg className="h-4 w-4" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M12 19l9 2-9-18-9 18 9-2zm0 0v-8" />
              </svg>
            </button>
          </div>
          <p className="mt-2 text-center text-xs text-white/40">
            支持中文和英文描述，如："Nolan's sci-fi movies with high rating"
          </p>
        </form>
      </main>
    </div>
  );
}
