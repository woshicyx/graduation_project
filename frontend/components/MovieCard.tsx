"use client";

import { useState } from "react";
import Link from "next/link";
import { Play } from "lucide-react";
import { MovieListItem } from "@/lib/api/movie";

interface MovieCardProps {
  movie: MovieListItem;
}

export default function MovieCard({ movie }: MovieCardProps) {
  const [imageError, setImageError] = useState(false);
  const hasValidPoster = movie.poster_path && !imageError;

  return (
    <Link 
      key={movie.id} 
      href={`/movies/${movie.id}`}
      className="group relative rounded-xl border border-white/10 bg-white/5 overflow-hidden transition-all duration-300 hover:border-red-500/50 hover:bg-white/10 hover:shadow-[0_8px_30px_rgba(220,38,38,0.15)] hover:-translate-y-1.5"
    >
      {/* 海报区域 */}
      <div className="aspect-[2/3] relative">
        {hasValidPoster ? (
          <>
            <img 
              src={`https://image.tmdb.org/t/p/w500${movie.poster_path}`}
              alt={movie.title}
              className="w-full h-full object-cover transition-transform group-hover:scale-105"
              onError={() => setImageError(true)}
            />
            {/* 底部暗角 vignette 效果 - 让底部文字更清晰 */}
            <div className="absolute inset-0 bg-gradient-to-t from-black/60 via-black/10 to-transparent pointer-events-none" />
          </>
        ) : (
          /* 极简文字海报 (Typography Poster) - 无海报时的优雅降级 */
          <div className="w-full h-full bg-gradient-to-br from-gray-800 via-gray-900 to-[#1a1014] ring-1 ring-inset ring-white/5 flex flex-col items-center justify-center p-4">
            <span className="text-center text-xl font-black text-white/70 leading-snug tracking-wider shadow-black drop-shadow-lg line-clamp-4">
              {movie.title}
            </span>
            {/* 装饰线 - 粉色细线提升质感 */}
            <div className="w-8 h-0.5 bg-pink-500/50 mt-4 rounded-full" />
          </div>
        )}
        
        {/* 悬停遮罩 */}
        <div className="absolute inset-0 bg-gradient-to-t from-black/80 via-black/20 to-transparent opacity-0 group-hover:opacity-100 transition-opacity" />
        
        {/* 评分 - 悬浮在暗角之上 */}
        {movie.vote_average && movie.vote_average > 0 && (
          <div className="absolute top-2 right-2 z-10 flex items-center gap-1 rounded-full bg-black/60 px-2 py-1 backdrop-blur-sm">
            <span className="text-xs font-bold text-yellow-400">
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
      
      {/* 底部信息 */}
      <div className="p-3">
        <h3 className="mb-1 truncate text-sm font-medium text-white group-hover:text-red-400 transition-colors">
          {movie.title}
        </h3>
        <div className="flex flex-wrap items-center justify-between gap-2 text-xs text-white/50">
          <span>{movie.release_date?.split('-')[0] || '未知'}</span>
          {movie.genres && movie.genres.length > 0 && (
            <span className="text-red-400/70">{movie.genres[0]}</span>
          )}
        </div>
      </div>
    </Link>
  );
}