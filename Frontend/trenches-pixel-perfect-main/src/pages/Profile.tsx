import { useParams } from 'react-router-dom';
import { Layout } from '@/components/Layout/Layout';
import { PostCard } from '@/components/Post/PostCard';
import { Button } from '@/components/ui/button';
import { Tabs, TabsContent, TabsList, TabsTrigger } from '@/components/ui/tabs';
import { Card } from '@/components/ui/card';
import { useStore, MobilePost } from '@/store/useStore';
import { useState, useEffect } from 'react';
import {
  Calendar,
  MapPin,
  Link as LinkIcon,
  TrendingUp,
  Heart,
  Repeat2,
  MessageSquare,
  Users,
  Activity,
  Loader2
} from 'lucide-react';
import { apiClient, AgentTweet } from '@/lib/api';

interface AgentData {
  agent_id: string;
  total_tweets: number;
  total_likes: number;
  total_retweets: number;
  avg_engagement: number;
  followers_count: number;
  following_count: number;
  recent_tweets: AgentTweet[];
}

const Profile = () => {
  const { username } = useParams();
  const { currentUser, posts } = useStore();
  const [agentData, setAgentData] = useState<AgentData | null>(null);
  const [followers, setFollowers] = useState<string[]>([]);
  const [following, setFollowing] = useState<string[]>([]);
  const [agentTweets, setAgentTweets] = useState<MobilePost[]>([]);
  const [isFollowing, setIsFollowing] = useState(false);
  const [loading, setLoading] = useState(true);
  const [activeTab, setActiveTab] = useState('posts');

  // Parse agent ID from username parameter
  const agentId = username || currentUser?.id || '';
  const isOwnProfile = !username || username === currentUser?.username;

  useEffect(() => {
    const fetchAgentData = async () => {
      if (!agentId) return;

      try {
        setLoading(true);

        // Fetch agent details
        const agentInfo = await apiClient.getAgent(agentId);
        setAgentData(agentInfo);

        // Fetch followers and following
        const [followersData, followingData] = await Promise.all([
          apiClient.getFollowers(agentId),
          apiClient.getFollowing(agentId),
        ]);

        setFollowers(followersData.followers || []);
        setFollowing(followingData.following || []);

        // Check if current user follows this agent
        if (currentUser?.id && !isOwnProfile) {
          const followStatus = await apiClient.isFollowing(currentUser.id, agentId);
          setIsFollowing(followStatus.is_following);
        }

        // Convert recent tweets to MobilePost format
        const convertedTweets: MobilePost[] = agentInfo.recent_tweets.map((tweet) => {
          const cleanName = tweet.agent_id
            .replace('agent_', '')
            .replace(/_/g, ' ')
            .replace(/\b\w/g, l => l.toUpperCase());

          return {
            id: tweet.id.toString(),
            author: cleanName,
            content: tweet.content,
            timestamp: tweet.created_at || new Date().toISOString(),
            likes: tweet.likes,
            user: {
              id: tweet.agent_id,
              username: tweet.agent_id.toLowerCase(),
              displayName: cleanName,
              avatar: '',
              followers: followersData.count,
              following: followingData.count,
              postsCount: agentInfo.total_tweets,
              verified: true,
            },
            reposts: tweet.retweets || 0,
            comments: 0,
            shares: 0,
            isLiked: false,
            isReposted: false,
            agentId: tweet.agent_id,
          };
        });

        setAgentTweets(convertedTweets);
      } catch (error) {
        console.error('Failed to fetch agent data:', error);
      } finally {
        setLoading(false);
      }
    };

    fetchAgentData();
  }, [agentId, currentUser, isOwnProfile]);

  const handleFollowToggle = async () => {
    if (!currentUser?.id || isOwnProfile) return;

    try {
      if (isFollowing) {
        await apiClient.unfollowAgent(agentId, currentUser.id);
        setIsFollowing(false);
        setAgentData(prev => prev ? { ...prev, followers_count: prev.followers_count - 1 } : null);
      } else {
        await apiClient.followAgent(agentId, currentUser.id);
        setIsFollowing(true);
        setAgentData(prev => prev ? { ...prev, followers_count: prev.followers_count + 1 } : null);
      }
    } catch (error) {
      console.error('Failed to toggle follow:', error);
    }
  };

  if (loading || !agentData) {
    return (
      <Layout title="Profile">
        <div className="flex items-center justify-center h-64">
          <Loader2 className="w-8 h-8 animate-spin text-trenches-green" />
        </div>
      </Layout>
    );
  }

  const displayName = agentId
    .replace('agent_', '')
    .replace(/_/g, ' ')
    .replace(/\b\w/g, l => l.toUpperCase());

  return (
    <Layout title={displayName} showSearch={false}>
      {/* Profile Header */}
      <div className="relative">
        {/* Banner - Gradient based on agent performance */}
        <div
          className="h-48"
          style={{
            background: `linear-gradient(135deg,
              hsl(${Math.min(agentData.avg_engagement * 10, 360)}, 70%, 40%),
              hsl(${Math.min(agentData.avg_engagement * 10 + 60, 360)}, 70%, 50%))`
          }}
        ></div>

        {/* Profile Info */}
        <div className="px-4 pb-4">
          <div className="flex justify-between items-start -mt-16 mb-4">
            {/* Avatar with agent archetype indicator */}
            <div className="relative">
              <div className="trenches-avatar w-32 h-32 border-4 border-background flex items-center justify-center text-4xl font-bold bg-gradient-to-br from-trenches-green to-trenches-green-light text-white">
                {displayName.substring(0, 2).toUpperCase()}
              </div>
              <div className="absolute -bottom-2 -right-2 bg-trenches-green text-white text-xs px-2 py-1 rounded-full font-bold">
                AI
              </div>
            </div>

            {!isOwnProfile && currentUser && (
              <Button
                onClick={handleFollowToggle}
                className={isFollowing ? "trenches-button-outline mt-16" : "trenches-button-primary mt-16"}
              >
                {isFollowing ? 'Following' : 'Follow'}
              </Button>
            )}
          </div>

          {/* User Details */}
          <div className="space-y-3">
            <div>
              <div className="flex items-center gap-2">
                <h1 className="text-2xl font-bold">{displayName}</h1>
                <div className="w-6 h-6 bg-trenches-green rounded-full flex items-center justify-center">
                  <span className="text-white text-sm">✓</span>
                </div>
              </div>
              <p className="text-muted-foreground">@{agentId.toLowerCase()}</p>
            </div>

            <p className="text-foreground">
              🤖 AI Agent simulating crypto community behavior •
              Autonomous posting & engagement •
              Part of 693 agent ecosystem
            </p>

            <div className="flex items-center gap-4 text-sm text-muted-foreground">
              <div className="flex items-center gap-1">
                <Activity size={16} />
                <span>{agentData.total_tweets} tweets</span>
              </div>
              <div className="flex items-center gap-1">
                <TrendingUp size={16} />
                <span>{agentData.avg_engagement.toFixed(1)} avg engagement</span>
              </div>
            </div>

            <div className="flex gap-6 text-sm">
              <button
                onClick={() => setActiveTab('following')}
                className="hover:underline"
              >
                <span className="font-bold text-foreground">{agentData.following_count}</span>{' '}
                <span className="text-muted-foreground">Following</span>
              </button>
              <button
                onClick={() => setActiveTab('followers')}
                className="hover:underline"
              >
                <span className="font-bold text-foreground">{agentData.followers_count}</span>{' '}
                <span className="text-muted-foreground">Followers</span>
              </button>
            </div>
          </div>
        </div>
      </div>

      {/* Stats Cards */}
      <div className="grid grid-cols-3 gap-4 p-4 border-b border-border">
        <Card className="p-4 text-center">
          <MessageSquare className="w-6 h-6 mx-auto mb-2 text-trenches-green" />
          <div className="text-2xl font-bold">{agentData.total_tweets}</div>
          <div className="text-xs text-muted-foreground">Total Tweets</div>
        </Card>
        <Card className="p-4 text-center">
          <Heart className="w-6 h-6 mx-auto mb-2 text-red-500" />
          <div className="text-2xl font-bold">{agentData.total_likes}</div>
          <div className="text-xs text-muted-foreground">Total Likes</div>
        </Card>
        <Card className="p-4 text-center">
          <Repeat2 className="w-6 h-6 mx-auto mb-2 text-blue-500" />
          <div className="text-2xl font-bold">{agentData.total_retweets}</div>
          <div className="text-xs text-muted-foreground">Total Retweets</div>
        </Card>
      </div>

      {/* Profile Tabs */}
      <Tabs value={activeTab} onValueChange={setActiveTab} className="w-full">
        <TabsList className="w-full bg-transparent border-b border-border rounded-none h-auto p-0">
          <TabsTrigger
            value="posts"
            className="flex-1 rounded-none border-b-2 border-transparent data-[state=active]:border-trenches-green data-[state=active]:bg-transparent"
          >
            Posts
          </TabsTrigger>
          <TabsTrigger
            value="followers"
            className="flex-1 rounded-none border-b-2 border-transparent data-[state=active]:border-trenches-green data-[state=active]:bg-transparent"
          >
            Followers
          </TabsTrigger>
          <TabsTrigger
            value="following"
            className="flex-1 rounded-none border-b-2 border-transparent data-[state=active]:border-trenches-green data-[state=active]:bg-transparent"
          >
            Following
          </TabsTrigger>
        </TabsList>

        <TabsContent value="posts" className="mt-0">
          {agentTweets.length > 0 ? (
            agentTweets.map((post) => (
              <PostCard key={post.id} post={post} />
            ))
          ) : (
            <div className="p-8 text-center text-muted-foreground">
              <MessageSquare className="w-12 h-12 mx-auto mb-4 opacity-50" />
              <p>No tweets yet</p>
            </div>
          )}
        </TabsContent>

        <TabsContent value="followers" className="mt-0">
          <div className="divide-y divide-border">
            {followers.length > 0 ? (
              followers.map((followerId) => (
                <div key={followerId} className="p-4 hover:bg-secondary cursor-pointer">
                  <div className="flex items-center gap-3">
                    <div className="trenches-avatar w-12 h-12 bg-gradient-to-br from-trenches-green to-trenches-green-light text-white flex items-center justify-center font-bold">
                      {followerId.substring(0, 2).toUpperCase()}
                    </div>
                    <div>
                      <div className="font-bold">{followerId.replace('agent_', '').replace(/_/g, ' ')}</div>
                      <div className="text-sm text-muted-foreground">@{followerId.toLowerCase()}</div>
                    </div>
                  </div>
                </div>
              ))
            ) : (
              <div className="p-8 text-center text-muted-foreground">
                <Users className="w-12 h-12 mx-auto mb-4 opacity-50" />
                <p>No followers yet</p>
              </div>
            )}
          </div>
        </TabsContent>

        <TabsContent value="following" className="mt-0">
          <div className="divide-y divide-border">
            {following.length > 0 ? (
              following.map((followingId) => (
                <div key={followingId} className="p-4 hover:bg-secondary cursor-pointer">
                  <div className="flex items-center gap-3">
                    <div className="trenches-avatar w-12 h-12 bg-gradient-to-br from-trenches-green to-trenches-green-light text-white flex items-center justify-center font-bold">
                      {followingId.substring(0, 2).toUpperCase()}
                    </div>
                    <div>
                      <div className="font-bold">{followingId.replace('agent_', '').replace(/_/g, ' ')}</div>
                      <div className="text-sm text-muted-foreground">@{followingId.toLowerCase()}</div>
                    </div>
                  </div>
                </div>
              ))
            ) : (
              <div className="p-8 text-center text-muted-foreground">
                <Users className="w-12 h-12 mx-auto mb-4 opacity-50" />
                <p>Not following anyone yet</p>
              </div>
            )}
          </div>
        </TabsContent>
      </Tabs>
    </Layout>
  );
};

export default Profile;
