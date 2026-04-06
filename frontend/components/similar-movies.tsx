'use client';

import { useState, useEffect } from 'react';
import Image from 'next/image';
import Link from 'next/link';
import { Card, CardContent } from '@/components/ui/card';
import { Button } from '@/components/ui/button';
import { ChevronLeft, ChevronRight, Film } from 'lucide-react';
import { Movie } from '@/lib/api/movies';
import { useMovies } from '@/hooks/useMovies';
import { getSimilarMovies } from '@/hooks/useMovieDetail';

interface SimilarMoviesProps {
  movie: Movie;
}

export default function SimilarMovies({ movie }: SimilarMoviesProps) {
  const [currentIndex, setCurrentIndex] = useState(0);
  const [similarMovies, setSimilarMovies] = useState<Movie[]>([]);
  
  // 获取所有电影
  const { data: moviesData } = useMovies({ page_size: 100 });

  useEffect(() => {
    if (moviesData?.items && movie) {
      const similar = getSimilarMovies(movie, moviesData.items, 10);
      setSimilarMovies(similar);
    }
  }, [moviesData, movie]);

  if (!similarMovies.length) {
    return null;
  }

  const visibleMovies = similarMovies.slice(currentIndex, currentIndex + 5);
  
  const nextSlide = () => {
    if (currentIndex + 5 < similarMovies.length) {
      setCurrentIndex(currentIndex + 1);
    }
  };

  const prevSlide = () => {
    if (currentIndex > 0) {
      setCurrentIndex(currentIndex - 1);
    }
  };

  return (
    <div className="mb-12">
      <div className="flex items-center justify-between mb-6">
        <h2 className="text-2xl font-bold">相似电影推荐</h2>
        <div className="flex items-center gap-2">
          <Button
            variant="outline"
            size="icon"
            onClick={prevSlide}
            disabled={currentIndex === 0}
          >
            <ChevronLeft className="w-4 h-4" />
          </Button>
          <Button
            variant="outline"
            size="icon"
            onClick={nextSlide}
            disabled={currentIndex + 5 >= similarMovies.length}
          >
            <ChevronRight className="w-4 h-4" />
          </Button>
        </div>
      </div>

      <div className="grid grid-cols-2 md:grid-cols-5 gap-4">
        {visibleMovies.map((similarMovie) => (
          <Link key={similarMovie.id} href={`/movies/${similarMovie.id}`}>
            <Card className="group hover:shadow-lg transition-shadow cursor-pointer h-full">
              <CardContent className="p-0">
                {/* 海报 */}
                <div className="relative aspect-[2/3] overflow-hidden rounded-t-lg">
                  {similarMovie.posterUrl ? (
                    <Image
                      src={similarMovie.posterUrl}
                      alt={similarMovie.title}
                      fill
                      className="object-cover group-hover:scale-105 transition-transform duration-300"
                      sizes="(max-width: 768px) 50vw, 20vw"
                    />
                  ) : (
                    <div className="w-full h-full bg-gray-100 flex items-center justify-center">
                      <Film className="w-12 h-12 text-gray-400" />
                    </div>
                  )}
                  
                  {/* 评分标签 */}
                  <div className="absolute top-2 right-2 bg-black/80 text-white text-xs font-bold px-2 py-1 rounded">
                    {similarMovie.rating.toFixed(1)}
                  </div>
                </div>
                
                {/* 电影信息 */}
                <div className="p-3">
                  <h3 className="font-semibold text-sm line-clamp-1 mb-1">
                    {similarMovie.title}
                  </h3>
                  <div className="flex items-center justify-between text-xs text-gray-600">
                    <span>{similarMovie.director}</span>
                    <span>{new Date(similarMovie.releaseDate).getFullYear()}</span>
                  </div>
                  
                  {/* 类型标签 */}
                  <div className="flex flex-wrap gap-1 mt-2">
                    {similarMovie.genres.slice(0, 2).map((genre, index) => (
                      <span
                        key={index}
                        className="text-xs px-1.5 py-0.5 bg-gray-100 text-gray-700 rounded"
                      >
                        {genre}
                      </span>
                    ))}
                  </div>
                </div>
              </CardContent>
            </Card>
          </Link>
        ))}
      </div>

      {/* 如果没有相似电影 */}
      {similarMovies.length === 0 && (
        <Card>
          <CardContent className="py-8 text-center">
            <Film className="w-12 h-12 text-gray-300 mx-auto mb-4" />
            <h3 className="text-lg font-semibold mb-2">暂无相似电影</h3>
            <p className="text-gray-600">暂时没有找到与这部电影相似的其他电影</p>
          </CardContent>
        </Card>
      )}
    </div>
  );
}