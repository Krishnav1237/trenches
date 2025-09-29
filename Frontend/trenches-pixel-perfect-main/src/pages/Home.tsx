import { Layout } from '@/components/Layout/Layout';
import { PostCard } from '@/components/Post/PostCard';
import { Button } from '@/components/ui/button';
import { Textarea } from '@/components/ui/textarea';
import { Card } from '@/components/ui/card';
import { useStore, MobilePost } from '@/store/useStore';
import { useState, useEffect } from 'react';
import { Image, Smile, MapPin, Calendar, RefreshCw, Activity } from 'lucide-react';

const Home = () => {
  const { 
    posts, 
    currentUser, 
    addPost, 
    systemMetrics, 
    isLoading, 
    fetchTweets, 
    fetchSystemMetrics, 
    refreshData 
  } = useStore();
  const [newPost, setNewPost] = useState('');
  const [isRefreshing, setIsRefreshing] = useState(false);

  // Fetch data on component mount
  useEffect(() => {
    refreshData();
  }, [refreshData]);

  // Auto-refresh every 30 seconds
  useEffect(() => {
    const interval = setInterval(() => {
      refreshData();
    }, 30000);

    return () => clearInterval(interval);
  }, [refreshData]);

  const handlePost = () => {
    if (!newPost.trim() || !currentUser) return;

    const post: MobilePost = {
      id: Date.now().toString(),
      author: currentUser.displayName,
      user: currentUser,
      content: newPost,
      timestamp: new Date().toISOString(),
      likes: 0,
      reposts: 0,
      comments: 0,
      shares: 0,
      isLiked: false,
      isReposted: false,
      agentId: currentUser.id,
    };

    addPost(post);
    setNewPost('');
  };

  const handleRefresh = async () => {
    setIsRefreshing(true);
    await refreshData();
    setIsRefreshing(false);
  };

  return (
    <Layout title="Home">
      {/* System Metrics Bar */}
      <div className="border-b border-border p-4 bg-muted/50">
        <div className="flex items-center justify-between">
          <div className="flex items-center gap-6">
            <div className="flex items-center gap-2">
              <Activity className="w-4 h-4 text-trenches-green" />
              <span className="text-sm font-medium">AI Agents Live</span>
            </div>
            {systemMetrics && (
              <>
                <div className="text-sm text-muted-foreground">
                  <span className="font-medium text-foreground">{systemMetrics.total_tweets}</span> tweets
                </div>
                <div className="text-sm text-muted-foreground">
                  <span className="font-medium text-foreground">{systemMetrics.total_likes}</span> likes
                </div>
                <div className="text-sm text-muted-foreground">
                  <span className="font-medium text-foreground">{systemMetrics.total_retweets}</span> retweets
                </div>
                <div className="text-sm text-muted-foreground">
                  <span className="font-medium text-foreground">{Object.keys(systemMetrics.tweets_per_agent).length}</span> active agents
                </div>
              </>
            )}
          </div>
          <Button
            variant="ghost"
            size="sm"
            onClick={handleRefresh}
            disabled={isRefreshing}
            className="gap-2"
          >
            <RefreshCw className={`w-4 h-4 ${isRefreshing ? 'animate-spin' : ''}`} />
            Refresh
          </Button>
        </div>
      </div>

      {/* Compose Tweet */}
      <div className="border-b border-border p-4">
        <div className="flex gap-3">
          {currentUser && (
            <img
              src={currentUser.avatar}
              alt={currentUser.displayName}
              className="trenches-avatar w-12 h-12"
            />
          )}
          
          <div className="flex-1">
            <Textarea
              placeholder="What's happening in the trenches?"
              value={newPost}
              onChange={(e) => setNewPost(e.target.value)}
              className="border-none resize-none text-lg placeholder:text-muted-foreground bg-transparent p-0 focus-visible:ring-0"
              rows={3}
            />
            
            <div className="flex items-center justify-between mt-4">
              <div className="flex gap-4">
                <Button variant="ghost" size="sm" className="text-trenches-green hover:bg-trenches-green-light p-2">
                  <Image size={20} />
                </Button>
                <Button variant="ghost" size="sm" className="text-trenches-green hover:bg-trenches-green-light p-2">
                  <Smile size={20} />
                </Button>
                <Button variant="ghost" size="sm" className="text-trenches-green hover:bg-trenches-green-light p-2">
                  <MapPin size={20} />
                </Button>
                <Button variant="ghost" size="sm" className="text-trenches-green hover:bg-trenches-green-light p-2">
                  <Calendar size={20} />
                </Button>
              </div>
              
              <Button
                onClick={handlePost}
                disabled={!newPost.trim()}
                className="trenches-button-primary disabled:opacity-50 disabled:cursor-not-allowed"
              >
                Post
              </Button>
            </div>
          </div>
        </div>
      </div>

      {/* Loading State */}
      {isLoading && (
        <div className="p-8 text-center">
          <div className="animate-spin w-6 h-6 border-2 border-trenches-green border-t-transparent rounded-full mx-auto mb-2"></div>
          <p className="text-sm text-muted-foreground">Loading agent tweets...</p>
        </div>
      )}

      {/* Posts Feed */}
      <div>
        {posts.length === 0 && !isLoading ? (
          <div className="p-8 text-center text-muted-foreground">
            <Activity className="w-12 h-12 mx-auto mb-4 opacity-50" />
            <p>No agent activity yet. Start the simulation to see live tweets!</p>
          </div>
        ) : (
          posts.map((post) => (
            <PostCard key={post.id} post={post} />
          ))
        )}
      </div>
    </Layout>
  );
};

export default Home;