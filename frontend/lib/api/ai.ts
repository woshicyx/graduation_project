/**
 * AI推荐相关API
 */
import { post } from './client';

export interface RecommendRequest {
  query: string;
  user_id?: number;
  max_results?: number;
  include_reasons?: boolean;
}

export interface RecommendItem {
  movie_id: number;
  title: string;
  relevance_score: number;
  reason: string | null;
}

export interface RecommendResponse {
  query: string;
  items: RecommendItem[];
  total_time_ms: number;
}

/**
 * AI电影推荐
 */
export async function recommendMovies(request: RecommendRequest): Promise<RecommendResponse> {
  return post<RecommendResponse>('/api/ai/recommend', request);
}

// 流式推荐电影项
export interface StreamMovieItem {
  type: 'movie';
  index: number;
  movie_id: number;
  title: string;
  poster_path: string | null;
  vote_average: number | null;
  release_date: string | null;
  relevance_score: number;
  genres: string[];
  reason?: string | null;  // AI推荐理由
}

// 流式事件类型
export interface StreamEvent {
  event: 'info' | 'movie' | 'done' | 'error';
  data: {
    type?: string;
    query?: string;
    llm_success?: boolean;
    index?: number;
    movie_id?: number;
    title?: string;
    poster_path?: string | null;
    vote_average?: number | null;
    release_date?: string | null;
    relevance_score?: number;
    genres?: string[];
    total?: number;
    time_ms?: number;
    error?: string;
  };
}

/**
 * 流式AI电影推荐
 */
export async function recommendMoviesStream(
  request: RecommendRequest,
  onMovie: (movie: StreamMovieItem) => void,
  onDone?: (total: number, timeMs: number) => void,
  onError?: (error: string) => void
): Promise<void> {
  const apiUrl = process.env.NEXT_PUBLIC_API_URL || 'http://localhost:8000';
  
  const response = await fetch(`${apiUrl}/api/ai/recommend/stream`, {
    method: 'POST',
    headers: {
      'Content-Type': 'application/json',
    },
    body: JSON.stringify(request),
  });

  if (!response.ok) {
    throw new Error(`HTTP error! status: ${response.status}`);
  }

  const reader = response.body?.getReader();
  if (!reader) {
    throw new Error('无法获取响应流');
  }

  const decoder = new TextDecoder();
  let buffer = '';

  try {
    while (true) {
      const { done, value } = await reader.read();
      if (done) break;

      buffer += decoder.decode(value, { stream: true });
      
      // 处理SSE事件
      const lines = buffer.split('\n');
      buffer = lines.pop() || '';

      for (const line of lines) {
        if (line.startsWith('event: ')) {
          const event = line.slice(7).trim();
          continue;
        }
        if (line.startsWith('data: ')) {
          const data = line.slice(6).trim();
          try {
            const parsed = JSON.parse(data);
            
            if (parsed.type === 'movie') {
              onMovie({
                type: 'movie',
                index: parsed.index,
                movie_id: parsed.movie_id,
                title: parsed.title,
                poster_path: parsed.poster_path,
                vote_average: parsed.vote_average,
                release_date: parsed.release_date,
                relevance_score: parsed.relevance_score,
                genres: parsed.genres || [],
                reason: parsed.reason || null,  // 传递推荐理由
              });
            } else if (parsed.total !== undefined && parsed.time_ms !== undefined) {
              onDone?.(parsed.total, parsed.time_ms);
            } else if (parsed.error) {
              onError?.(parsed.error);
            }
          } catch (e) {
            console.error('解析SSE数据失败:', e);
          }
        }
      }
    }
  } finally {
    reader.releaseLock();
  }
}
