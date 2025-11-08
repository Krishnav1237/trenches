import { Layout } from '@/components/Layout/Layout';
import { Card } from '@/components/ui/card';
import { Button } from '@/components/ui/button';
import { useState, useEffect } from 'react';
import {
  Newspaper,
  ExternalLink,
  RefreshCw,
  Loader2,
  TrendingUp,
  Clock,
} from 'lucide-react';
import { apiClient } from '@/lib/api';

interface NewsItem {
  id: number;
  source: string;
  title: string;
  url: string;
  timestamp: string;
}

const News = () => {
  const [news, setNews] = useState<NewsItem[]>([]);
  const [loading, setLoading] = useState(true);
  const [refreshing, setRefreshing] = useState(false);

  useEffect(() => {
    fetchNews();
  }, []);

  const fetchNews = async () => {
    try {
      setLoading(true);
      const data = await apiClient.getNews(50);
      setNews(data.news || []);
    } catch (error) {
      console.error('Failed to fetch news:', error);
    } finally {
      setLoading(false);
    }
  };

  const handleRefresh = async () => {
    setRefreshing(true);
    await fetchNews();
    setRefreshing(false);
  };

  const getSourceColor = (source: string): string => {
    const colors: Record<string, string> = {
      'NewsAPI': 'bg-blue-500/10 text-blue-600 border-blue-500/20',
      'CryptoPanic': 'bg-purple-500/10 text-purple-600 border-purple-500/20',
      'Reddit': 'bg-orange-500/10 text-orange-600 border-orange-500/20',
      'CoinMarketCap': 'bg-green-500/10 text-green-600 border-green-500/20',
    };
    return colors[source] || 'bg-gray-500/10 text-gray-600 border-gray-500/20';
  };

  const formatTimeAgo = (timestamp: string): string => {
    const now = new Date();
    const time = new Date(timestamp);
    const diffMs = now.getTime() - time.getTime();
    const diffMins = Math.floor(diffMs / 60000);
    const diffHours = Math.floor(diffMins / 60);
    const diffDays = Math.floor(diffHours / 24);

    if (diffDays > 0) return `${diffDays}d ago`;
    if (diffHours > 0) return `${diffHours}h ago`;
    if (diffMins > 0) return `${diffMins}m ago`;
    return 'Just now';
  };

  if (loading && news.length === 0) {
    return (
      <Layout title="Crypto News">
        <div className="flex items-center justify-center h-64">
          <Loader2 className="w-8 h-8 animate-spin text-trenches-green" />
        </div>
      </Layout>
    );
  }

  return (
    <Layout title="Crypto News">
      {/* Header */}
      <div className="border-b border-border p-4 bg-muted/50">
        <div className="flex items-center justify-between">
          <div className="flex items-center gap-4">
            <Newspaper className="w-6 h-6 text-trenches-green" />
            <div>
              <h1 className="text-xl font-bold">Crypto News Feed</h1>
              <p className="text-sm text-muted-foreground">
                Latest crypto news from multiple sources
              </p>
            </div>
          </div>
          <Button
            variant="ghost"
            size="sm"
            onClick={handleRefresh}
            disabled={refreshing}
            className="gap-2"
          >
            <RefreshCw className={`w-4 h-4 ${refreshing ? 'animate-spin' : ''}`} />
            Refresh
          </Button>
        </div>
      </div>

      {/* Stats Bar */}
      <div className="border-b border-border p-4 bg-background">
        <div className="flex items-center gap-6 text-sm">
          <div className="flex items-center gap-2">
            <TrendingUp className="w-4 h-4 text-trenches-green" />
            <span className="text-muted-foreground">Total Articles:</span>
            <span className="font-bold">{news.length}</span>
          </div>
          <div className="flex items-center gap-2">
            <Clock className="w-4 h-4 text-blue-500" />
            <span className="text-muted-foreground">Last Updated:</span>
            <span className="font-medium">
              {news.length > 0 ? formatTimeAgo(news[0].timestamp) : 'Never'}
            </span>
          </div>
        </div>
      </div>

      {/* News Feed */}
      <div className="divide-y divide-border">
        {news.length === 0 ? (
          <div className="p-8 text-center text-muted-foreground">
            <Newspaper className="w-16 h-16 mx-auto mb-4 opacity-50" />
            <p className="text-lg font-medium mb-2">No news available</p>
            <p className="text-sm">Check back later for crypto news updates</p>
          </div>
        ) : (
          news.map((item) => (
            <Card
              key={item.id}
              className="p-4 hover:bg-muted/50 transition-colors border-0 border-b rounded-none"
            >
              <div className="space-y-3">
                {/* Header */}
                <div className="flex items-center justify-between">
                  <span
                    className={`text-xs px-2 py-1 rounded-full border ${getSourceColor(item.source)}`}
                  >
                    {item.source}
                  </span>
                  <span className="text-xs text-muted-foreground">
                    {formatTimeAgo(item.timestamp)}
                  </span>
                </div>

                {/* Title */}
                <h3 className="text-base font-semibold leading-snug hover:text-trenches-green transition-colors">
                  {item.title}
                </h3>

                {/* Footer */}
                <div className="flex items-center justify-between pt-2">
                  <a
                    href={item.url}
                    target="_blank"
                    rel="noopener noreferrer"
                    className="text-sm text-trenches-green hover:underline flex items-center gap-1"
                  >
                    Read Article
                    <ExternalLink className="w-3 h-3" />
                  </a>
                </div>
              </div>
            </Card>
          ))
        )}
      </div>
    </Layout>
  );
};

export default News;
