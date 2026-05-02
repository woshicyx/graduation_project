"use client";

import { useState, useEffect, useCallback } from 'react';
import { Heart, Loader2, AlertCircle } from 'lucide-react';
import { useAuth } from '@/contexts/AuthContext';
import { toggleFavorite, checkFavoriteStatus, FavoriteStatus } from '@/lib/api/favorites';
import { useRouter } from 'next/navigation';

interface FavoriteButtonProps {
  movieId: number;
  movieTitle?: string;
  size?: 'sm' | 'md' | 'lg';
  showText?: boolean;
  className?: string;
}

export default function FavoriteButton({
  movieId,
  movieTitle,
  size = 'md',
  showText = false,
  className = '',
}: FavoriteButtonProps) {
  const router = useRouter();
  const { user, isAuthenticated } = useAuth();
  
  const [isFavorite, setIsFavorite] = useState(false);
  const [isLoading, setIsLoading] = useState(true);
  const [isToggling, setIsToggling] = useState(false);
  const [error, setError] = useState<string | null>(null);

  // 获取收藏状态
  useEffect(() => {
    if (!isAuthenticated || !user) {
      setIsFavorite(false);
      setIsLoading(false);
      return;
    }

    const fetchStatus = async () => {
      try {
        const status = await checkFavoriteStatus(movieId, user.id);
        setIsFavorite(status.is_liked);
        setError(null);
      } catch (err) {
        console.error('获取收藏状态失败:', err);
      } finally {
        setIsLoading(false);
      }
    };

    fetchStatus();
  }, [movieId, isAuthenticated, user]);

  // 切换收藏状态
  const handleToggle = useCallback(async () => {
    if (!isAuthenticated) {
      // 未登录，跳转到登录页
      router.push('/auth/login');
      return;
    }

    if (isToggling || !user) return;

    setIsToggling(true);
    setError(null);

    try {
      const action = isFavorite ? 'unlike' : 'like';
      await toggleFavorite(movieId, action);
      setIsFavorite(!isFavorite);
    } catch (err) {
      const message = err instanceof Error ? err.message : '操作失败';
      setError(message);
    } finally {
      setIsToggling(false);
    }
  }, [isAuthenticated, isToggling, isFavorite, movieId, user, router]);

  // 尺寸配置
  const sizeConfig = {
    sm: {
      button: 'h-8 w-8',
      icon: 16,
      text: 'text-xs',
    },
    md: {
      button: 'h-10 w-10',
      icon: 20,
      text: 'text-sm',
    },
    lg: {
      button: 'h-12 w-12',
      icon: 24,
      text: 'text-base',
    },
  };

  const config = sizeConfig[size];

  // 加载状态
  if (isLoading) {
    return (
      <button
        className={`flex items-center justify-center rounded-full bg-white/10 ${config.button} ${className}`}
        disabled
      >
        <Loader2 className={`h-${config.icon} w-${config.icon} animate-spin text-white/50`} />
      </button>
    );
  }

  return (
    <div className="relative">
      <button
        onClick={handleToggle}
        disabled={isToggling}
        className={`
          flex items-center justify-center rounded-full transition-all duration-300
          ${config.button}
          ${isFavorite
            ? 'bg-red-500 text-white shadow-lg shadow-red-500/30 hover:bg-red-600'
            : 'bg-white/10 text-white/70 hover:bg-white/20 hover:text-white hover:shadow-lg'
          }
          ${isToggling ? 'opacity-70 cursor-not-allowed' : 'cursor-pointer'}
          ${className}
        `}
        title={isFavorite ? '取消收藏' : '添加收藏'}
        aria-label={isFavorite ? '取消收藏' : '添加收藏'}
      >
        {isToggling ? (
          <Loader2 className={`h-${config.icon} w-${config.icon} animate-spin`} />
        ) : (
          <Heart
            className={`transition-transform duration-300 ${
              isFavorite ? 'scale-110 fill-current' : 'scale-100'
            }`}
            size={config.icon}
          />
        )}
      </button>

      {/* 收藏数量文字 */}
      {showText && (
        <span className={`ml-2 ${config.text} text-white/70`}>
          {isFavorite ? '已收藏' : '收藏'}
        </span>
      )}

      {/* 错误提示 */}
      {error && (
        <div className="absolute -bottom-8 left-0 flex items-center gap-1 text-xs text-red-400 whitespace-nowrap">
          <AlertCircle size={12} />
          {error}
        </div>
      )}
    </div>
  );
}
