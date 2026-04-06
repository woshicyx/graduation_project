'use client';

import { useState } from 'react';
import { Button } from '@/components/ui/button';
import { Card, CardContent, CardFooter, CardHeader, CardTitle } from '@/components/ui/card';
import { Input } from '@/components/ui/input';
import { Textarea } from '@/components/ui/textarea';
import { Star, X } from 'lucide-react';

interface ReviewFormProps {
  onSubmit: (reviewData: {
    rating: number;
    title: string;
    content: string;
    author?: string;
  }) => Promise<void>;
  onCancel: () => void;
  isLoading?: boolean;
}

export default function ReviewForm({ onSubmit, onCancel, isLoading = false }: ReviewFormProps) {
  const [rating, setRating] = useState(8);
  const [title, setTitle] = useState('');
  const [content, setContent] = useState('');
  const [author, setAuthor] = useState('');

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    
    if (!title.trim() || !content.trim()) {
      alert('请填写标题和内容');
      return;
    }

    await onSubmit({
      rating,
      title: title.trim(),
      content: content.trim(),
      author: author.trim() || undefined,
    });

    // 重置表单
    setRating(8);
    setTitle('');
    setContent('');
    setAuthor('');
  };

  return (
    <Card>
      <CardHeader>
        <div className="flex items-center justify-between">
          <CardTitle>写影评</CardTitle>
          <Button variant="ghost" size="icon" onClick={onCancel} disabled={isLoading}>
            <X className="w-4 h-4" />
          </Button>
        </div>
      </CardHeader>
      
      <form onSubmit={handleSubmit}>
        <CardContent className="space-y-6">
          {/* 评分 */}
          <div>
            <div className="text-sm font-medium mb-2">评分</div>
            <div className="flex items-center gap-1">
              {[1, 2, 3, 4, 5, 6, 7, 8, 9, 10].map((star) => (
                <button
                  key={star}
                  type="button"
                  onClick={() => setRating(star)}
                  className="p-1 hover:scale-110 transition-transform"
                  disabled={isLoading}
                >
                  <Star
                    className={`w-6 h-6 ${
                      star <= rating
                        ? 'text-yellow-500 fill-current'
                        : 'text-gray-300'
                    }`}
                  />
                </button>
              ))}
              <span className="ml-2 text-lg font-semibold">{rating.toFixed(1)}</span>
            </div>
          </div>

          {/* 标题 */}
          <div>
            <div className="text-sm font-medium mb-2">标题</div>
            <Input
              value={title}
              onChange={(e) => setTitle(e.target.value)}
              placeholder="为你的影评起个标题"
              maxLength={200}
              required
              disabled={isLoading}
            />
          </div>

          {/* 内容 */}
          <div>
            <div className="text-sm font-medium mb-2">内容</div>
            <Textarea
              value={content}
              onChange={(e) => setContent(e.target.value)}
              placeholder="分享你对这部电影的看法..."
              rows={6}
              maxLength={5000}
              required
              disabled={isLoading}
            />
            <div className="text-xs text-gray-500 mt-1 text-right">
              {content.length}/5000
            </div>
          </div>

          {/* 作者 */}
          <div>
            <div className="text-sm font-medium mb-2">作者（可选）</div>
            <Input
              value={author}
              onChange={(e) => setAuthor(e.target.value)}
              placeholder="匿名用户"
              maxLength={100}
              disabled={isLoading}
            />
          </div>
        </CardContent>

        <CardFooter className="flex justify-end gap-2">
          <Button type="button" variant="outline" onClick={onCancel} disabled={isLoading}>
            取消
          </Button>
          <Button type="submit" disabled={isLoading}>
            {isLoading ? '提交中...' : '提交影评'}
          </Button>
        </CardFooter>
      </form>
    </Card>
  );
}