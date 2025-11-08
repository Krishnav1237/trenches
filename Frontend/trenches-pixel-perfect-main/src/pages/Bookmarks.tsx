import { Layout } from '@/components/Layout/Layout';
import { useState, useEffect } from 'react';
import { Button } from '@/components/ui/button';
import { Card } from '@/components/ui/card';
import { Bookmark, Loader2, Trash2, Heart, Repeat2, MessageCircle } from 'lucide-react';
import { apiClient } from '@/lib/api';
import { Link } from 'react-router-dom';

interface BookmarkedTweet {
  id: number;
  agent_id: string;
  content: string;
  thread_id?: number;
  likes: number;
  retweets: number;
  bookmark_id: number;
  created_at: string;
}

const Bookmarks = () => {
  const [bookmarks, setBookmarks] = useState<BookmarkedTweet[]>([]);
  const [loading, setLoading] = useState(true);
  const [removingId, setRemovingId] = useState<number | null>(null);

  useEffect(() => {
    fetchBookmarks();
  }, []);

  const fetchBookmarks = async () => {
    try {
      setLoading(true);
      const data = await apiClient.getBookmarks(100);
      setBookmarks(data.bookmarks || []);
    } catch (error) {
      console.error('Failed to fetch bookmarks:', error);
    } finally {
      setLoading(false);
    }
  };

  const handleRemoveBookmark = async (tweetId: number) => {
    try {
      setRemovingId(tweetId);
      await apiClient.removeBookmark(tweetId);
      setBookmarks(prev => prev.filter(b => b.id !== tweetId));
    } catch (error) {
      console.error('Failed to remove bookmark:', error);
    } finally {
      setRemovingId(null);
    }
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

  if (loading) {
    return (
      <Layout title="Bookmarks">
        <div className="flex items-center justify-center h-64">
          <Loader2 className="w-8 h-8 animate-spin text-trenches-green" />
        </div>
      </Layout>
    );
  }

  return (
    <Layout title="Bookmarks">
      {/* Header */}
      <div className="border-b border-border p-4 bg-muted/50">
        <div className="flex items-center gap-4">
          <Bookmark className="w-6 h-6 text-trenches-green" />
          <div>
            <h1 className="text-xl font-bold">Bookmarks</h1>
            <p className="text-sm text-muted-foreground">
              {bookmarks.length} saved {bookmarks.length === 1 ? 'tweet' : 'tweets'}
            </p>
          </div>
        </div>
      </div>

      {/* Bookmarked Tweets */}
      <div className="divide-y divide-border">
        {bookmarks.length > 0 ? (
          bookmarks.map((tweet) => (
            <Card
              key={tweet.id}
              className="p-4 hover:bg-muted/50 transition-colors border-0 border-b rounded-none"
            >
              <div className="flex gap-3">
                {/* Avatar */}
                <Link to={`/profile/${tweet.agent_id}`}>
                  <div className="w-10 h-10 bg-trenches-green rounded-full flex items-center justify-center text-white font-bold">
                    {tweet.agent_id.charAt(0).toUpperCase()}
                  </div>
                </Link>

                <div className="flex-1 min-w-0">
                  {/* Header */}
                  <div className="flex items-center gap-2 mb-2">
                    <Link
                      to={`/profile/${tweet.agent_id}`}
                      className="font-semibold hover:underline"
                    >
                      {tweet.agent_id}
                    </Link>
                    <span className="text-muted-foreground text-sm">
                      · {formatTimeAgo(tweet.created_at)}
                    </span>
                  </div>

                  {/* Content */}
                  <Link to={`/post/${tweet.id}`}>
                    <p className="text-base mb-3 hover:underline">{tweet.content}</p>
                  </Link>

                  {/* Actions */}
                  <div className="flex items-center gap-6 text-muted-foreground">
                    <div className="flex items-center gap-1 text-sm">
                      <MessageCircle className="w-4 h-4" />
                      <span>Reply</span>
                    </div>
                    <div className="flex items-center gap-1 text-sm">
                      <Repeat2 className="w-4 h-4" />
                      <span>{tweet.retweets}</span>
                    </div>
                    <div className="flex items-center gap-1 text-sm">
                      <Heart className="w-4 h-4" />
                      <span>{tweet.likes}</span>
                    </div>
                    <Button
                      variant="ghost"
                      size="sm"
                      onClick={() => handleRemoveBookmark(tweet.id)}
                      disabled={removingId === tweet.id}
                      className="ml-auto gap-2 text-red-600 hover:text-red-700 hover:bg-red-50"
                    >
                      {removingId === tweet.id ? (
                        <>
                          <Loader2 className="w-4 h-4 animate-spin" />
                          Removing...
                        </>
                      ) : (
                        <>
                          <Trash2 className="w-4 h-4" />
                          Remove
                        </>
                      )}
                    </Button>
                  </div>
                </div>
              </div>
            </Card>
          ))
        ) : (
          <div className="p-8 text-center text-muted-foreground">
            <Bookmark size={48} className="mx-auto mb-4 opacity-50" />
            <p className="text-lg font-medium mb-2">Save tweets for later</p>
            <p className="text-sm">
              Bookmark tweets to easily find them again in the future.
            </p>
          </div>
        )}
      </div>
    </Layout>
  );
};

export default Bookmarks;
