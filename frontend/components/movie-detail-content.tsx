'use client';

import { useState } from 'react';
import Image from 'next/image';
import Link from 'next/link';
import { Button } from '@/components/ui/button';
import { Card, CardContent } from '@/components/ui/card';
import { Badge } from '@/components/ui/badge';
import { Star, Calendar, Clock, DollarSign, Users, ThumbsUp, MessageSquare, Share2, Bookmark } from 'lucide-react';
import { useMovieDetail, useMovieReviews, useMovieReviewStats, useCreateReview, useVoteReview, formatBoxOffice, formatRuntime, formatRating, getRatingColor, getRatingBgColor, parseJsonArray } from '@/hooks/useMovieDetail';
import { formatReviewDate, calculateHelpfulRate } from '@/lib/api/reviews';
import ReviewForm from './review-form';
import SimilarMovies from './similar-movies';

interface MovieDetailContentProps {
  movieId: string;
}

export default function MovieDetailContent({ movieId }: MovieDetailContentProps) {
  const [showReviewForm, setShowReviewForm] = useState(false);
  const [reviewSortBy, setReviewSortBy] = useState<'newest' | 'most_helpful'>('newest');

  // 获取电影详情
  const { data: movie, isLoading: movieLoading, error: movieError } = useMovieDetail(movieId);
  
  // 获取影评列表
  const { data: reviewsData, isLoading: reviewsLoading } = useMovieReviews(movieId, {
    sort_by: reviewSortBy,
    page_size: 10,
  });
  
  // 获取影评统计
  const { data: reviewStats, isLoading: statsLoading } = useMovieReviewStats(movieId);
  
  // 创建影评
  const createReviewMutation = useCreateReview();
  
  // 投票影评
  const voteReviewMutation = useVoteReview();

  if (movieLoading) {
    return null; // 由Suspense处理加载状态
  }

  if (movieError || !movie) {
    return (
      <div className="container mx-auto px-4 py-16 text-center">
        <h1 className="text-2xl font-bold text-gray-800 mb-4">电影未找到</h1>
        <p className="text-gray-600 mb-8">抱歉，找不到您要查看的电影信息。</p>
        <Link href="/">
          <Button>返回首页</Button>
        </Link>
      </div>
    );
  }

  // 解析电影数据
  const genres = parseJsonArray<string>(movie.genres as any);
  const productionCompanies = parseJsonArray<string>(movie.production_companies as any);
  const spokenLanguages = parseJsonArray<string>(movie.spoken_languages as any);

  // 处理创建影评
  const handleCreateReview = async (reviewData: any) => {
    try {
      await createReviewMutation.mutateAsync({
        movie_id: parseInt(movieId),
        ...reviewData,
      });
      setShowReviewForm(false);
    } catch (error) {
      console.error('创建影评失败:', error);
    }
  };

  // 处理投票
  const handleVoteReview = async (reviewId: number, helpful: boolean) => {
    try {
      await voteReviewMutation.mutateAsync({ reviewId, helpful });
    } catch (error) {
      console.error('投票失败:', error);
    }
  };

  return (
    <div className="container mx-auto px-4 py-8">
      {/* 顶部海报和基本信息 */}
      <div className="flex flex-col lg:flex-row gap-8 mb-12">
        {/* 海报区域 */}
        <div className="lg:w-1/3">
          <div className="relative aspect-[2/3] rounded-xl overflow-hidden shadow-xl mb-4">
            <Image
              src={movie.posterUrl || '/placeholder-poster.jpg'}
              alt={movie.title}
              fill
              className="object-cover"
              sizes="(max-width: 768px) 100vw, 33vw"
              priority
            />
          </div>
          
          {/* 操作按钮 */}
          <div className="flex gap-2 mb-4">
            <Button className="flex-1" variant="outline">
              <Bookmark className="w-4 h-4 mr-2" />
              收藏
            </Button>
            <Button className="flex-1" variant="outline">
              <Share2 className="w-4 h-4 mr-2" />
              分享
            </Button>
          </div>
          
          {/* 评分 */}
          <div className={`p-4 rounded-lg ${getRatingBgColor(movie.rating)}`}>
            <div className="flex items-center justify-between">
              <div>
                <div className="text-sm text-gray-600">TMDB评分</div>
                <div className={`text-3xl font-bold ${getRatingColor(movie.rating)}`}>
                  {formatRating(movie.rating)}
                </div>
              </div>
              <Star className="w-8 h-8 text-yellow-500 fill-current" />
            </div>
            <div className="text-sm text-gray-600 mt-2">
              {movie.vote_count ? `${movie.vote_count}人评分` : '暂无评分'}
            </div>
          </div>
        </div>

        {/* 基本信息区域 */}
        <div className="lg:w-2/3">
          {/* 标题和年份 */}
          <div className="mb-4">
            <h1 className="text-4xl font-bold text-gray-900 mb-2">{movie.title}</h1>
            {movie.releaseDate && (
              <div className="flex items-center text-gray-600">
                <Calendar className="w-4 h-4 mr-2" />
                {new Date(movie.releaseDate).getFullYear()}
                {movie.director && ` • 导演: ${movie.director}`}
              </div>
            )}
          </div>

          {/* 类型标签 */}
          <div className="flex flex-wrap gap-2 mb-8">
            {genres.map((genre, index) => (
              <Badge key={index} variant="secondary" className="px-3 py-1">
                {genre}
              </Badge>
            ))}
          </div>

          {/* 元数据网格 */}
          <div className="grid grid-cols-2 md:grid-cols-3 gap-6 mb-8">
            <div className="space-y-1">
              <div className="text-sm text-gray-500 flex items-center">
                <DollarSign className="w-4 h-4 mr-2" />
                票房
              </div>
              <div className="text-lg font-semibold">{formatBoxOffice(movie.boxOffice)}</div>
            </div>
            
            <div className="space-y-1">
              <div className="text-sm text-gray-500 flex items-center">
                <Clock className="w-4 h-4 mr-2" />
                时长
              </div>
              <div className="text-lg font-semibold">{formatRuntime(movie.runtime as any)}</div>
            </div>
            
            <div className="space-y-1">
              <div className="text-sm text-gray-500 flex items-center">
                <Users className="w-4 h-4 mr-2" />
                语言
              </div>
              <div className="text-lg font-semibold">
                {spokenLanguages[0] || movie.original_language || '未知'}
              </div>
            </div>
            
            <div className="space-y-1">
              <div className="text-sm text-gray-500">上映状态</div>
              <div className="text-lg font-semibold">{movie.status || '已上映'}</div>
            </div>
            
            <div className="space-y-1">
              <div className="text-sm text-gray-500">制作公司</div>
              <div className="text-lg font-semibold">
                {productionCompanies[0] || '未知'}
              </div>
            </div>
            
            <div className="space-y-1">
              <div className="text-sm text-gray-500">预算</div>
              <div className="text-lg font-semibold">
                {movie.budget ? formatBoxOffice(movie.budget as any) : '未知'}
              </div>
            </div>
          </div>

          {/* 剧情简介 */}
          <div className="mb-8">
            <h2 className="text-xl font-semibold mb-4">剧情简介</h2>
            <p className="text-gray-700 leading-relaxed">
              {movie.synopsis || '暂无剧情简介'}
            </p>
            {movie.tagline && (
              <div className="mt-4 italic text-gray-600 border-l-4 border-gray-300 pl-4">
                "{movie.tagline}"
              </div>
            )}
          </div>

          {/* 操作按钮 */}
          <div className="flex gap-4">
            <Button onClick={() => setShowReviewForm(true)}>
              <MessageSquare className="w-4 h-4 mr-2" />
              写影评
            </Button>
            <Button variant="outline">
              <ThumbsUp className="w-4 h-4 mr-2" />
              想看
            </Button>
          </div>
        </div>
      </div>

      {/* 影评区域 */}
      <div className="mb-12">
        <div className="flex items-center justify-between mb-6">
          <h2 className="text-2xl font-bold">影评</h2>
          <div className="flex gap-2">
            <Button
              variant={reviewSortBy === 'newest' ? 'default' : 'outline'}
              size="sm"
              onClick={() => setReviewSortBy('newest')}
            >
              最新
            </Button>
            <Button
              variant={reviewSortBy === 'most_helpful' ? 'default' : 'outline'}
              size="sm"
              onClick={() => setReviewSortBy('most_helpful')}
            >
              最有帮助
            </Button>
          </div>
        </div>

        {/* 影评统计 */}
        {!statsLoading && reviewStats && (
          <div className="grid grid-cols-1 md:grid-cols-4 gap-6 mb-8">
            <Card>
              <CardContent className="pt-6">
                <div className="text-sm text-gray-500 mb-1">总影评数</div>
                <div className="text-2xl font-bold">{reviewStats.total_reviews}</div>
              </CardContent>
            </Card>
            
            <Card>
              <CardContent className="pt-6">
                <div className="text-sm text-gray-500 mb-1">平均评分</div>
                <div className="text-2xl font-bold">{formatRating(reviewStats.average_rating)}</div>
              </CardContent>
            </Card>
            
            <Card>
              <CardContent className="pt-6">
                <div className="text-sm text-gray-500 mb-1">近期影评</div>
                <div className="text-2xl font-bold">{reviewStats.recent_reviews_count}</div>
                <div className="text-xs text-gray-500">30天内</div>
              </CardContent>
            </Card>
            
            <Card>
              <CardContent className="pt-6">
                <div className="text-sm text-gray-500 mb-1">评分分布</div>
                <div className="text-2xl font-bold">
                  {Object.keys(reviewStats.rating_distribution).length}档
                </div>
              </CardContent>
            </Card>
          </div>
        )}

        {/* 影评表单 */}
        {showReviewForm && (
          <div className="mb-8">
            <ReviewForm
              onSubmit={handleCreateReview}
              onCancel={() => setShowReviewForm(false)}
              isLoading={createReviewMutation.isPending}
            />
          </div>
        )}

        {/* 影评列表 */}
        {!reviewsLoading && reviewsData && reviewsData.items.length > 0 ? (
          <div className="space-y-6">
            {reviewsData.items.map((review) => (
              <Card key={review.id}>
                <CardContent className="pt-6">
                  <div className="flex items-start justify-between mb-4">
                    <div>
                      <h3 className="font-semibold text-lg mb-1">{review.title}</h3>
                      <div className="flex items-center text-sm text-gray-500">
                        <span>{review.author}</span>
                        <span className="mx-2">•</span>
                        <span>{formatReviewDate(review.created_at)}</span>
                      </div>
                    </div>
                    <div className={`px-3 py-1 rounded-full ${getRatingBgColor(review.rating)} ${getRatingColor(review.rating)} font-semibold`}>
                      {formatRating(review.rating)}
                    </div>
                  </div>
                  
                  <p className="text-gray-700 mb-4 leading-relaxed">{review.content}</p>
                  
                  <div className="flex items-center justify-between">
                    <div className="text-sm text-gray-500">
                      {calculateHelpfulRate(review)}% 的用户认为有帮助
                      ({review.helpful_count + review.not_helpful_count}票)
                    </div>
                    <div className="flex gap-2">
                      <Button
                        variant="outline"
                        size="sm"
                        onClick={() => handleVoteReview(review.id, true)}
                        disabled={voteReviewMutation.isPending}
                      >
                        <ThumbsUp className="w-4 h-4 mr-1" />
                        有帮助 ({review.helpful_count})
                      </Button>
                      <Button
                        variant="outline"
                        size="sm"
                        onClick={() => handleVoteReview(review.id, false)}
                        disabled={voteReviewMutation.isPending}
                      >
                        无帮助 ({review.not_helpful_count})
                      </Button>
                    </div>
                  </div>
                </CardContent>
              </Card>
            ))}
          </div>
        ) : (
          <Card>
            <CardContent className="py-8 text-center">
              <MessageSquare className="w-12 h-12 text-gray-300 mx-auto mb-4" />
              <h3 className="text-lg font-semibold mb-2">暂无影评</h3>
              <p className="text-gray-600 mb-4">成为第一个评论这部电影的人</p>
              <Button onClick={() => setShowReviewForm(true)}>
                写影评
              </Button>
            </CardContent>
          </Card>
        )}
      </div>

      {/* 相似电影推荐 */}
      <SimilarMovies movie={movie} />
    </div>
  );
}