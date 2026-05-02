"use client";

import Link from "next/link";
import Image from "next/image";
import { useState, useRef, useEffect } from "react";
import { recommendMoviesStream, StreamMovieItem } from "@/lib/api/ai";
import { Sparkles, Loader2, Trash2, Star, Play } from "lucide-react";

interface Message {
  role: "user" | "assistant";
  content: string;
  movies?: StreamMovieItem[];
  timestamp?: number;
}

const CHAT_HISTORY_KEY = "movieai_chat_history";
const MAX_HISTORY_MESSAGES = 50;

export default function ChatPage() {
  const [messages, setMessages] = useState<Message[]>([]);
  const [input, setInput] = useState("");
  const [isLoading, setIsLoading] = useState(false);
  const [currentMovie, setCurrentMovie] = useState<StreamMovieItem | null>(null);
  const [isHistoryLoaded, setIsHistoryLoaded] = useState(false);
  const messagesEndRef = useRef<HTMLDivElement>(null);

  // 加载历史记录
  useEffect(() => {
    try {
      const saved = localStorage.getItem(CHAT_HISTORY_KEY);
      if (saved) {
        const history = JSON.parse(saved) as Message[];
        if (history.length > 0) {
          setMessages(history);
        } else {
          setMessages([{ 
            role: "assistant", 
            content: "你好！我是 MovieAI 智能助手。我可以根据你的喜好推荐电影，比如告诉我你想看什么类型的电影，或者描述一下你的心情，我来分析并给你推荐！",
            timestamp: Date.now()
          }]);
        }
      } else {
        setMessages([{ 
          role: "assistant", 
          content: "你好！我是 MovieAI 智能助手。我可以根据你的喜好推荐电影，比如告诉我你想看什么类型的电影，或者描述一下你的心情，我来分析并给你推荐！",
          timestamp: Date.now()
        }]);
      }
    } catch (e) {
      console.error("加载聊天历史失败:", e);
      setMessages([{ 
        role: "assistant", 
        content: "你好！我是 MovieAI 智能助手。我可以根据你的喜好推荐电影，比如告诉我你想看什么类型的电影，或者描述一下你的心情，我来分析并给你推荐！",
        timestamp: Date.now()
      }]);
    }
    setIsHistoryLoaded(true);
  }, []);

  // 保存历史记录
  useEffect(() => {
    if (!isHistoryLoaded) return;
    try {
      const recentMessages = messages.slice(-MAX_HISTORY_MESSAGES);
      localStorage.setItem(CHAT_HISTORY_KEY, JSON.stringify(recentMessages));
    } catch (e) {
      console.error("保存聊天历史失败:", e);
    }
  }, [messages, isHistoryLoaded]);

  // 自动滚动
  useEffect(() => {
    messagesEndRef.current?.scrollIntoView({ behavior: "smooth" });
  }, [messages, currentMovie]);

  // 清空对话
  const handleClearChat = () => {
    if (confirm("确定要清空所有对话记录吗？")) {
      localStorage.removeItem(CHAT_HISTORY_KEY);
      setMessages([{ 
        role: "assistant", 
        content: "对话已清空。我是 MovieAI 智能助手，告诉我你想看什么类型的电影，我来给你推荐！",
        timestamp: Date.now()
      }]);
    }
  };

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
          max_results: 6,
          include_reasons: true,
        },
        (movie) => {
          setCurrentMovie(movie);
          movies.push(movie);
        },
        (total, timeMs) => {
          if (movies.length > 0) {
            const aiResponse = `根据你的需求「${query}」，我为你推荐以下 ${movies.length} 部电影，点击卡片可以查看详细信息：`;
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

  // 获取海报URL
  const getPosterUrl = (posterPath: string | null) => {
    if (posterPath) {
      return `https://image.tmdb.org/t/p/w500${posterPath}`;
    }
    return null;
  };

  return (
    <div className="relative min-h-screen bg-[#0a0a0f]">
      {/* 背景装饰 */}
      <div className="fixed inset-0 overflow-hidden pointer-events-none">
        <div className="absolute -top-1/2 -right-1/4 h-[800px] w-[800px] rounded-full bg-purple-600/5 blur-[120px]" />
        <div className="absolute -top-1/3 left-1/4 h-[600px] w-[600px] rounded-full bg-blue-500/5 blur-[100px]" />
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
            <button
              onClick={handleClearChat}
              className="flex items-center gap-1.5 text-sm text-white/50 hover:text-white transition-colors"
              title="清空对话"
            >
              <Trash2 className="h-4 w-4" />
              <span className="hidden sm:inline">清空</span>
            </button>
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
      <main className="relative z-10 mx-auto flex h-[calc(100vh-64px)] max-w-5xl flex-col px-4 py-6">
        {/* 消息列表 */}
        <div className="flex-1 overflow-y-auto space-y-6">
          {messages.map((msg, i) => (
            <div key={i}>
              {/* 消息文本 */}
              <div className={`flex ${msg.role === "user" ? "justify-end" : "justify-start"} mb-3`}>
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

              {/* 推荐电影卡片 */}
              {msg.movies && msg.movies.length > 0 && (
                <div className="grid grid-cols-2 sm:grid-cols-3 lg:grid-cols-3 gap-4 px-2">
                  {msg.movies.map((movie, idx) => (
                    <Link
                      key={`${movie.movie_id}-${idx}`}
                      href={`/movies/${movie.movie_id}`}
                      className="group relative overflow-hidden rounded-xl border border-white/10 bg-gradient-to-b from-white/5 to-transparent hover:border-red-500/50 hover:bg-white/10 transition-all duration-300"
                    >
                      {/* 海报 */}
                      <div className="relative aspect-[2/3] overflow-hidden">
                        {getPosterUrl(movie.poster_path) ? (
                          <Image
                            src={getPosterUrl(movie.poster_path)!}
                            alt={movie.title}
                            fill
                            className="object-cover transition-transform duration-300 group-hover:scale-105"
                            sizes="(max-width: 640px) 50vw, (max-width: 1024px) 33vw, 220px"
                          />
                        ) : (
                          <div className="absolute inset-0 flex items-center justify-center bg-white/10">
                            <Play className="h-12 w-12 text-white/30" />
                          </div>
                        )}
                        
                        {/* 悬停遮罩 */}
                        <div className="absolute inset-0 bg-gradient-to-t from-black/80 via-transparent to-transparent opacity-0 group-hover:opacity-100 transition-opacity" />
                        
                        {/* 评分 */}
                        {movie.vote_average && movie.vote_average > 0 && (
                          <div className="absolute top-2 right-2 flex items-center gap-1 rounded-full bg-black/60 px-2 py-1 backdrop-blur">
                            <Star className="h-3 w-3 text-yellow-400 fill-yellow-400" />
                            <span className="text-xs font-medium text-white">
                              {movie.vote_average.toFixed(1)}
                            </span>
                          </div>
                        )}
                        
                        {/* 悬停播放图标 */}
                        <div className="absolute inset-0 flex items-center justify-center opacity-0 group-hover:opacity-100 transition-opacity">
                          <div className="h-12 w-12 rounded-full bg-white/20 backdrop-blur flex items-center justify-center">
                            <Play className="h-6 w-6 text-white ml-1" />
                          </div>
                        </div>
                      </div>
                      
                      {/* 电影信息 */}
                      <div className="p-3">
                        <h3 className="font-medium text-white text-sm leading-tight line-clamp-2 mb-1">
                          {movie.title}
                        </h3>
                        <div className="flex items-center justify-between">
                          <span className="text-xs text-white/50">
                            {movie.release_date?.split("-")[0] || "未知年份"}
                          </span>
                          <span className="text-xs text-red-400 font-medium">
                            {movie.relevance_score > 0 ? `${(movie.relevance_score * 100).toFixed(0)}%` : ""}
                          </span>
                        </div>
                        {movie.genres && movie.genres.length > 0 && (
                          <div className="mt-2 flex flex-wrap gap-1">
                            {movie.genres.slice(0, 2).map((genre, gi) => (
                              <span
                                key={gi}
                                className="text-[10px] px-1.5 py-0.5 rounded bg-white/10 text-white/70"
                              >
                                {genre}
                              </span>
                            ))}
                          </div>
                        )}
                        {/* AI推荐理由 - 独立引言块 */}
                        {movie.reason && (
                          <div className="mt-3 p-3 rounded-lg bg-red-500/10 border-l-4 border-red-500 shadow-inner">
                            <p className="text-sm text-gray-200 leading-relaxed">
                              <Sparkles className="inline-block w-4 h-4 text-red-500 mr-1 mb-0.5" />
                              {movie.reason}
                            </p>
                          </div>
                        )}
                      </div>
                    </Link>
                  ))}
                </div>
              )}
            </div>
          ))}
          
          {/* 流式输出 - 预览卡片 */}
          {currentMovie && (
            <div className="flex justify-start">
              <div className="rounded-2xl border border-white/10 bg-white/5 p-4 backdrop-blur max-w-xs">
                <div className="mb-2 flex items-center gap-2 border-b border-white/10 pb-2">
                  <Loader2 className="h-4 w-4 animate-spin text-purple-400" />
                  <span className="text-xs font-medium text-purple-400">正在搜索...</span>
                </div>
                
                <div className="animate-pulse">
                  <div className="relative aspect-[2/3] rounded-lg overflow-hidden bg-white/10 mb-3">
                    <div className="absolute inset-0 flex items-center justify-center">
                      <Play className="h-8 w-8 text-white/20" />
                    </div>
                  </div>
                  <div className="h-4 w-3/4 rounded bg-white/10 mb-2" />
                  <div className="h-3 w-1/2 rounded bg-white/10" />
                </div>
                <p className="mt-3 text-xs text-white/50">
                  正在分析: <span className="text-white/70">{currentMovie.title}</span>
                </p>
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
