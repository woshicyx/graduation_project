"use client";

import { useState, useRef, useEffect } from "react";
import { Bot, Send, X, Sparkles, MessageSquare, Film, Clock, Zap } from "lucide-react";
import { motion, AnimatePresence } from "framer-motion";
import { Button } from "@/components/ui/button";
import {
  Sheet,
  SheetContent,
  SheetHeader,
  SheetTitle,
  SheetDescription,
} from "@/components/ui/sheet";
import { ScrollArea } from "@/components/ui/scroll-area";
import { Input } from "@/components/ui/input";

export function AiChatFab() {
  const [open, setOpen] = useState(false);
  const [message, setMessage] = useState("");
  const [isTyping, setIsTyping] = useState(false);
  const [messages, setMessages] = useState([
    {
      id: 1,
      role: "assistant" as const,
      content: "嗨，我是你的 AI 观影搭子！可以告诉我你最近喜欢的电影、导演或剧情风格，我会结合影片 Metadata + 影评语义信息，帮你生成一份专属片单。",
      timestamp: "刚刚",
    },
    {
      id: 2,
      role: "user" as const,
      content: "例如：想看一部节奏适中、剧情烧脑，但情绪上不要太压抑的科幻片，有类似《盗梦空间》 / 《星际穿越》的感觉。",
      timestamp: "刚刚",
    },
  ]);
  const messagesEndRef = useRef<HTMLDivElement>(null);

  // 滚动到底部
  useEffect(() => {
    if (messagesEndRef.current) {
      messagesEndRef.current.scrollIntoView({ behavior: "smooth" });
    }
  }, [messages]);

  const handleSubmit = (e: React.FormEvent) => {
    e.preventDefault();
    if (!message.trim()) return;

    // 添加用户消息
    const userMessage = {
      id: messages.length + 1,
      role: "user" as const,
      content: message,
      timestamp: "刚刚",
    };
    setMessages([...messages, userMessage]);
    setMessage("");
    setIsTyping(true);

    // 模拟 AI 回复
    setTimeout(() => {
      const aiResponses = [
        "根据你的需求，我推荐《降临》——它是一部关于语言与时间的科幻片，既有深度又不失温情。",
        "《银翼杀手2049》如何？视觉震撼，剧情层层递进，探讨了记忆与身份的主题。",
        "如果你喜欢诺兰的风格，《信条》也是不错的选择，时间逆转的概念非常烧脑。",
        "《火星救援》虽然更偏向硬科幻，但节奏明快，充满幽默感，不会让人感到压抑。",
        "《头号玩家》融合了科幻与冒险，彩蛋丰富，观影体验非常轻松愉快。",
      ];
      
      const aiMessage = {
        id: messages.length + 2,
        role: "assistant" as const,
        content: aiResponses[Math.floor(Math.random() * aiResponses.length)],
        timestamp: "刚刚",
      };
      setMessages(prev => [...prev, aiMessage]);
      setIsTyping(false);
    }, 1500);
  };

  const quickPrompts = [
    "推荐类似《星际穿越》的科幻片",
    "最近有什么高评分悬疑片？",
    "适合周末放松的喜剧电影",
    "2024年最佳电影推荐",
    "经典电影重温推荐",
  ];

  return (
    <>
      {/* 悬浮按钮 */}
      <AnimatePresence>
        {!open && (
          <motion.div
            key="ai-fab"
            initial={{ opacity: 0, y: 40, scale: 0.8 }}
            animate={{ opacity: 1, y: 0, scale: 1 }}
            exit={{ opacity: 0, y: 40, scale: 0.8 }}
            transition={{ duration: 0.3 }}
            className="fixed bottom-6 right-6 z-50"
          >
            <motion.button
              whileHover={{ scale: 1.1 }}
              whileTap={{ scale: 0.95 }}
              onClick={() => setOpen(true)}
              className="group relative flex h-14 w-14 items-center justify-center rounded-full bg-gradient-to-br from-emerald-500 to-emerald-600 text-white shadow-2xl shadow-emerald-500/40 ring-2 ring-emerald-300/40 hover:from-emerald-600 hover:to-emerald-700"
              aria-label="打开 AI 观影助手"
            >
              <Bot className="h-7 w-7" />
              
              {/* 脉冲动画 */}
              <motion.div
                className="absolute inset-0 rounded-full border-2 border-emerald-400/30"
                animate={{
                  scale: [1, 1.2, 1],
                  opacity: [0.5, 0, 0.5],
                }}
                transition={{
                  duration: 2,
                  repeat: Infinity,
                  ease: "easeInOut",
                }}
              />
              
              {/* 通知点 */}
              <div className="absolute -right-1 -top-1 h-3 w-3 rounded-full bg-rose-500 ring-2 ring-slate-950" />
            </motion.button>
            
            {/* 提示文字 */}
            <motion.div
              initial={{ opacity: 0, y: 10 }}
              animate={{ opacity: 1, y: 0 }}
              transition={{ delay: 0.5 }}
              className="absolute -top-10 right-0 whitespace-nowrap rounded-lg bg-slate-800/90 px-3 py-1.5 text-xs text-slate-200 backdrop-blur"
            >
              <Sparkles className="mr-1 inline h-3 w-3" />
              问我推荐电影
            </motion.div>
          </motion.div>
        )}
      </AnimatePresence>

      {/* 聊天面板 */}
      <Sheet open={open} onOpenChange={setOpen}>
        <SheetContent
          side="right"
          className="flex h-full w-full flex-col gap-0 border-l border-slate-700/60 bg-gradient-to-b from-slate-950 via-slate-950 to-slate-950/95 p-0 text-slate-50 shadow-2xl sm:max-w-lg"
          showClose={false}
        >
          {/* 头部 */}
          <SheetHeader className="border-b border-slate-800/80 bg-gradient-to-r from-slate-900/80 to-slate-950/80 p-5 backdrop-blur">
            <div className="flex items-center justify-between">
              <div className="flex items-center gap-3">
                <div className="relative">
                  <div className="flex h-12 w-12 items-center justify-center rounded-full bg-gradient-to-br from-emerald-500 to-emerald-600">
                    <Bot className="h-6 w-6 text-white" />
                  </div>
                  <div className="absolute -right-1 -top-1 h-4 w-4 rounded-full bg-green-400 ring-2 ring-slate-950" />
                </div>
                <div className="text-left">
                  <SheetTitle className="flex items-center gap-2 text-lg font-bold text-white">
                    AI 观影助手
                    <span className="rounded-full border border-emerald-500/40 bg-emerald-500/10 px-2 py-0.5 text-xs text-emerald-300">
                      <Zap className="mr-1 inline h-3 w-3" />
                      在线
                    </span>
                  </SheetTitle>
                  <SheetDescription className="mt-1 flex items-center gap-2 text-sm text-slate-400">
                    <MessageSquare className="h-3 w-3" />
                    基于 RAG + LLM 的智能推荐
                    <Clock className="ml-2 h-3 w-3" />
                    响应时间：~1.5s
                  </SheetDescription>
                </div>
              </div>
              <button
                type="button"
                onClick={() => setOpen(false)}
                className="rounded-full bg-slate-800/60 p-2 text-slate-400 transition-colors hover:bg-slate-700/60 hover:text-white"
                aria-label="关闭"
              >
                <X className="h-5 w-5" />
              </button>
            </div>
          </SheetHeader>

          {/* 聊天区域 */}
          <ScrollArea className="flex-1 p-5">
            <div className="space-y-4">
              {/* 欢迎消息 */}
              <div className="mb-6 rounded-xl bg-gradient-to-r from-slate-800/40 to-slate-900/40 p-4">
                <div className="flex items-start gap-3">
                  <Film className="mt-0.5 h-5 w-5 text-emerald-400" />
                  <div>
                    <p className="text-sm font-medium text-white">🎬 智能电影推荐</p>
                    <p className="mt-1 text-xs text-slate-300">
                      我可以根据你的观影偏好、心情、甚至一句话描述，从数千部电影中精准推荐。
                      试试用自然语言告诉我你想看什么！
                    </p>
                  </div>
                </div>
              </div>

              {/* 消息列表 */}
              {messages.map((msg) => (
                <motion.div
                  key={msg.id}
                  initial={{ opacity: 0, y: 10 }}
                  animate={{ opacity: 1, y: 0 }}
                  transition={{ duration: 0.3 }}
                >
                  <ChatBubble message={msg} />
                </motion.div>
              ))}

              {/* 输入中状态 */}
              {isTyping && (
                <motion.div
                  initial={{ opacity: 0, y: 10 }}
                  animate={{ opacity: 1, y: 0 }}
                  className="flex items-center gap-2"
                >
                  <div className="flex h-8 w-8 items-center justify-center rounded-full bg-emerald-500/20">
                    <Bot className="h-4 w-4 text-emerald-400" />
                  </div>
                  <div className="rounded-2xl rounded-bl-none bg-slate-800/60 px-4 py-3">
                    <div className="flex gap-1">
                      <motion.div
                        className="h-2 w-2 rounded-full bg-emerald-400"
                        animate={{ y: [0, -5, 0] }}
                        transition={{ duration: 0.6, repeat: Infinity, delay: 0 }}
                      />
                      <motion.div
                        className="h-2 w-2 rounded-full bg-emerald-400"
                        animate={{ y: [0, -5, 0] }}
                        transition={{ duration: 0.6, repeat: Infinity, delay: 0.2 }}
                      />
                      <motion.div
                        className="h-2 w-2 rounded-full bg-emerald-400"
                        animate={{ y: [0, -5, 0] }}
                        transition={{ duration: 0.6, repeat: Infinity, delay: 0.4 }}
                      />
                    </div>
                  </div>
                </motion.div>
              )}

              <div ref={messagesEndRef} />
            </div>
          </ScrollArea>

          {/* 快速提示 */}
          <div className="border-t border-slate-800/60 bg-slate-900/40 p-4">
            <p className="mb-2 text-xs font-medium text-slate-400">快速提问：</p>
            <div className="flex flex-wrap gap-2">
              {quickPrompts.map((prompt, index) => (
                <button
                  key={index}
                  type="button"
                  onClick={() => setMessage(prompt)}
                  className="rounded-full border border-slate-700/60 bg-slate-800/40 px-3 py-1.5 text-xs text-slate-300 transition-all hover:border-slate-600 hover:bg-slate-700/60 hover:text-white"
                >
                  {prompt}
                </button>
              ))}
            </div>
          </div>

          {/* 输入区域 */}
          <form
            onSubmit={handleSubmit}
            className="border-t border-slate-800/60 bg-slate-900/60 p-4"
          >
            <div className="flex items-center gap-2">
              <Input
                value={message}
                onChange={(e) => setMessage(e.target.value)}
                placeholder="输入你想看的电影类型、心情或最近喜欢的片子…"
                className="h-11 flex-1 rounded-xl border-slate-700/60 bg-slate-800/40 text-sm placeholder:text-slate-500 focus-visible:ring-2 focus-visible:ring-emerald-500/50"
              />
              <Button
                type="submit"
                size="icon"
                className="h-11 w-11 rounded-full bg-gradient-to-r from-emerald-500 to-emerald-600 hover:from-emerald-600 hover:to-emerald-700"
                disabled={!message.trim() || isTyping}
              >
                <Send className="h-5 w-5" />
              </Button>
            </div>
            <p className="mt-2 text-center text-[10px] text-slate-500">
              当前为模拟对话，后续会接入后端 RAG + LLM 推荐接口
            </p>
          </form>
        </SheetContent>
      </Sheet>
    </>
  );
}

type Message = {
  id: number;
  role: "user" | "assistant";
  content: string;
  timestamp: string;
};

function ChatBubble({ message }: { message: Message }) {
  const isUser = message.role === "user";
  
  return (
    <div
      className={`flex gap-3 ${
        isUser ? "flex-row-reverse" : "flex-row"
      }`}
    >
      {/* 头像 */}
      <div
        className={`mt-0.5 flex h-8 w-8 items-center justify-center rounded-full ${
          isUser
            ? "bg-slate-700 text-slate-50"
            : "bg-gradient-to-br from-emerald-500 to-emerald-600 text-white"
        }`}
      >
        {isUser ? "你" : <Bot className="h-4 w-4" />}
      </div>

      {/* 消息内容 */}
      <div className="flex max-w-[75%] flex-col">
        <div
          className={`rounded-2xl px-4 py-3 ${
            isUser
              ? "rounded-br-none bg-slate-800/90 text-slate-50"
              : "rounded-bl-none bg-slate-800/60 text-slate-100"
          }`}
        >
          <p className="text-sm leading-relaxed">{message.content}</p>
        </div>
        
        {/* 时间戳 */}
        <div
          className={`mt-1 text-[10px] ${
            isUser ? "text-right text-slate-500" : "text-left text-slate-500"
          }`}
        >
          {message.timestamp}
        </div>
      </div>
    </div>
  );
}