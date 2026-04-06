'use client';

import { Suspense } from 'react';
import { notFound } from 'next/navigation';
import MovieDetailContent from '@/components/movie-detail-content';
import MovieDetailLoading from '@/components/movie-detail-loading';

interface MovieDetailPageProps {
  params: {
    id: string;
  };
}

export default function MovieDetailPage({ params }: MovieDetailPageProps) {
  const { id } = params;

  if (!id) {
    notFound();
  }

  return (
    <div className="min-h-screen bg-gradient-to-b from-gray-50 to-white">
      <Suspense fallback={<MovieDetailLoading />}>
        <MovieDetailContent movieId={id} />
      </Suspense>
    </div>
  );
}