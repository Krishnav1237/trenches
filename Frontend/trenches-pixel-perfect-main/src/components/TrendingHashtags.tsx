import { useState, useEffect } from 'react';
import { Card } from '@/components/ui/card';
import { Hash, TrendingUp, Loader2 } from 'lucide-react';
import { apiClient } from '@/lib/api';

interface Hashtag {
  tag: string;
  count: number;
  last_used: string;
}

export const TrendingHashtags = () => {
  const [hashtags, setHashtags] = useState<Hashtag[]>([]);
  const [loading, setLoading] = useState(true);

  const fetchTrendingHashtags = async () => {
    try {
      setLoading(true);
      const data = await apiClient.getTrendingHashtags({ limit: 10 });
      setHashtags(data.hashtags || []);
    } catch (error) {
      console.error('Failed to fetch trending hashtags:', error);
    } finally {
      setLoading(false);
    }
  };

  // Load trending hashtags on mount
  useEffect(() => {
    fetchTrendingHashtags();
    // eslint-disable-next-line react-hooks/exhaustive-deps
  }, []);

  if (loading) {
    return (
      <Card className="p-4">
        <div className="flex items-center gap-2 mb-4">
          <TrendingUp className="w-5 h-5" />
          <h3 className="font-bold text-lg">Trending Hashtags</h3>
        </div>
        <div className="flex items-center justify-center py-8">
          <Loader2 className="w-6 h-6 animate-spin text-trenches-green" />
        </div>
      </Card>
    );
  }

  if (hashtags.length === 0) {
    return null;
  }

  return (
    <Card className="p-4">
      <div className="flex items-center gap-2 mb-4">
        <TrendingUp className="w-5 h-5" />
        <h3 className="font-bold text-lg">Trending Hashtags</h3>
      </div>
      <div className="space-y-3">
        {hashtags.map((hashtag, index) => (
          <div
            key={hashtag.tag}
            className="flex items-center gap-3 hover:bg-secondary/50 p-2 rounded transition-colors cursor-pointer"
          >
            <div className="flex items-center justify-center w-6 h-6 text-xs font-bold text-muted-foreground">
              {index + 1}
            </div>
            <Hash className="w-4 h-4 text-trenches-green" />
            <div className="flex-1 min-w-0">
              <p className="font-semibold truncate">{hashtag.tag}</p>
              <p className="text-xs text-muted-foreground">
                {hashtag.count} tweet{hashtag.count !== 1 ? 's' : ''}
              </p>
            </div>
          </div>
        ))}
      </div>
    </Card>
  );
};
