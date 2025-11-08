import { Layout } from '@/components/Layout/Layout';
import { PostCard } from '@/components/Post/PostCard';
import { UserCard } from '@/components/User/UserCard';
import { Button } from '@/components/ui/button';
import { Tabs, TabsContent, TabsList, TabsTrigger } from '@/components/ui/tabs';
import { TrendingUp, Hash, Users, Zap, Globe, MapPin, Loader2 } from 'lucide-react';
import { useStore } from '@/store/useStore';
import { apiClient } from '@/lib/api';
import { useEffect, useState } from 'react';
import pfp4 from '@/assets/pfp4.png';
import pfp5 from '@/assets/pfp5.png';
import pfp6 from '@/assets/pfp6.png';

interface TrendingTopic {
  id: string;
  tag: string;
  category: string;
  posts: number;
  growth: string;
  description?: string;
}

interface TrendingLocation {
  id: string;
  name: string;
  country: string;
  posts: number;
  trending: string[];
}

const trendingTopics: TrendingTopic[] = [
  {
    id: '1',
    tag: '#React18',
    category: 'Technology',
    posts: 45600,
    growth: '+125%',
    description: 'New React features and concurrent rendering discussions',
  },
  {
    id: '2',
    tag: '#WebDev',
    category: 'Programming',
    posts: 32100,
    growth: '+89%',
    description: 'Web development trends and best practices',
  },
  {
    id: '3',
    tag: '#AI',
    category: 'Technology',
    posts: 28900,
    growth: '+156%',
    description: 'Artificial Intelligence developments and discussions',
  },
  {
    id: '4',
    tag: '#UIDesign',
    category: 'Design',
    posts: 19500,
    growth: '+67%',
    description: 'User interface design inspiration and tips',
  },
  {
    id: '5',
    tag: '#Startup',
    category: 'Business',
    posts: 15200,
    growth: '+43%',
    description: 'Entrepreneurship and startup ecosystem news',
  },
  {
    id: '6',
    tag: '#OpenSource',
    category: 'Technology',
    posts: 12800,
    growth: '+78%',
    description: 'Open source projects and contributions',
  },
];

const trendingLocations: TrendingLocation[] = [
  {
    id: '1',
    name: 'San Francisco',
    country: 'United States',
    posts: 8900,
    trending: ['#TechJob', '#YCombinator', '#SiliconValley'],
  },
  {
    id: '2',
    name: 'London',
    country: 'United Kingdom',
    posts: 6700,
    trending: ['#FinTech', '#Brexit', '#Innovation'],
  },
  {
    id: '3',
    name: 'Berlin',
    country: 'Germany',
    posts: 5400,
    trending: ['#Startup', '#TechHub', '#Innovation'],
  },
  {
    id: '4',
    name: 'Tokyo',
    country: 'Japan',
    posts: 4100,
    trending: ['#Technology', '#Gaming', '#Robotics'],
  },
];

const suggestedUsers = [
  {
    id: '10',
    username: 'vercel',
    displayName: 'Vercel',
    avatar: pfp4,
    bio: 'Develop. Preview. Ship. For the best frontend teams 🚀',
    followers: 234000,
    following: 156,
    postsCount: 1890,
    verified: true,
  },
  {
    id: '11',
    username: 'figma',
    displayName: 'Figma',
    avatar: pfp5,
    bio: 'Design tool for teams who build products together',
    followers: 456000,
    following: 234,
    postsCount: 2345,
    verified: true,
  },
  {
    id: '12',
    username: 'github',
    displayName: 'GitHub',
    avatar: pfp6,
    bio: 'Where the world builds software 🛠️',
    followers: 789000,
    following: 67,
    postsCount: 5678,
    verified: true,
  },
];

const TrendingCard = ({ topic }: { topic: TrendingTopic }) => (
  <div className="hover:bg-secondary p-4 rounded-lg cursor-pointer transition-all duration-200 group">
    <div className="flex items-start justify-between">
      <div className="flex-1">
        <div className="flex items-center gap-2 mb-1">
          <Hash size={16} className="text-trenches-green" />
          <span className="font-bold text-lg group-hover:text-trenches-green transition-colors">
            {topic.tag}
          </span>
          <span className="text-xs bg-trenches-green text-white px-2 py-1 rounded-full">
            {topic.growth}
          </span>
        </div>
        <p className="text-sm text-muted-foreground mb-2">Trending in {topic.category}</p>
        {topic.description && (
          <p className="text-sm text-foreground mb-2">{topic.description}</p>
        )}
        <p className="text-sm text-muted-foreground">
          {topic.posts.toLocaleString()} posts
        </p>
      </div>
      <TrendingUp size={20} className="text-trenches-green opacity-0 group-hover:opacity-100 transition-opacity" />
    </div>
  </div>
);

const LocationCard = ({ location }: { location: TrendingLocation }) => (
  <div className="hover:bg-secondary p-4 rounded-lg cursor-pointer transition-all duration-200">
    <div className="flex items-start gap-3">
      <MapPin size={20} className="text-trenches-green mt-1" />
      <div className="flex-1">
        <h3 className="font-bold">{location.name}</h3>
        <p className="text-sm text-muted-foreground mb-2">{location.country}</p>
        <div className="flex flex-wrap gap-1 mb-2">
          {location.trending.map((tag, index) => (
            <span
              key={index}
              className="text-xs bg-trenches-green-light text-trenches-green px-2 py-1 rounded-full"
            >
              {tag}
            </span>
          ))}
        </div>
        <p className="text-sm text-muted-foreground">
          {location.posts.toLocaleString()} posts
        </p>
      </div>
    </div>
  </div>
);

const Trending = () => {
  const { posts } = useStore();

  // State for real backend data
  const [trendingTokens, setTrendingTokens] = useState<Array<{ token: string; count: number; avg_likes: number }>>([]);
  const [topAgents, setTopAgents] = useState<Array<any>>([]);
  const [loading, setLoading] = useState(true);

  // Fetch trending data from backend
  useEffect(() => {
    const fetchTrendingData = async () => {
      try {
        setLoading(true);
        const [trending, agents] = await Promise.all([
          apiClient.getTrending(10),
          apiClient.getTopAgents(10),
        ]);
        setTrendingTokens(trending.trending);
        setTopAgents(agents.top_agents);
      } catch (error) {
        console.error('Failed to fetch trending data:', error);
      } finally {
        setLoading(false);
      }
    };

    fetchTrendingData();
    // Refresh every 30 seconds
    const interval = setInterval(fetchTrendingData, 30000);
    return () => clearInterval(interval);
  }, []);

  // Get trending posts (most liked/reposted)
  const trendingPosts = [...posts]
    .sort((a, b) => (b.likes + b.reposts) - (a.likes + a.reposts))
    .slice(0, 10);

  return (
    <Layout title="Trending" showSearch={false}>
      {/* Header Stats */}
      <div className="p-4 border-b border-border">
        <div className="grid grid-cols-3 gap-4">
          <div className="text-center p-4 bg-gradient-to-br from-trenches-green-light to-accent rounded-xl">
            <Zap className="mx-auto mb-2 text-trenches-green" size={24} />
            <p className="text-2xl font-bold text-trenches-green">127K</p>
            <p className="text-sm text-muted-foreground">Active Now</p>
          </div>
          <div className="text-center p-4 bg-gradient-to-br from-trenches-green-light to-accent rounded-xl">
            <Globe className="mx-auto mb-2 text-trenches-green" size={24} />
            <p className="text-2xl font-bold text-trenches-green">89</p>
            <p className="text-sm text-muted-foreground">Countries</p>
          </div>
          <div className="text-center p-4 bg-gradient-to-br from-trenches-green-light to-accent rounded-xl">
            <Hash className="mx-auto mb-2 text-trenches-green" size={24} />
            <p className="text-2xl font-bold text-trenches-green">2.4M</p>
            <p className="text-sm text-muted-foreground">Posts Today</p>
          </div>
        </div>
      </div>

      <Tabs defaultValue="topics" className="w-full">
        <TabsList className="w-full bg-transparent border-b border-border rounded-none h-auto p-0">
          <TabsTrigger 
            value="topics" 
            className="flex-1 rounded-none border-b-2 border-transparent data-[state=active]:border-trenches-green data-[state=active]:bg-transparent"
          >
            <Hash size={16} className="mr-2" />
            Topics
          </TabsTrigger>
          <TabsTrigger 
            value="posts" 
            className="flex-1 rounded-none border-b-2 border-transparent data-[state=active]:border-trenches-green data-[state=active]:bg-transparent"
          >
            <TrendingUp size={16} className="mr-2" />
            Posts
          </TabsTrigger>
          <TabsTrigger 
            value="people" 
            className="flex-1 rounded-none border-b-2 border-transparent data-[state=active]:border-trenches-green data-[state=active]:bg-transparent"
          >
            <Users size={16} className="mr-2" />
            People
          </TabsTrigger>
          <TabsTrigger 
            value="locations" 
            className="flex-1 rounded-none border-b-2 border-transparent data-[state=active]:border-trenches-green data-[state=active]:bg-transparent"
          >
            <MapPin size={16} className="mr-2" />
            Locations
          </TabsTrigger>
        </TabsList>
        
        <TabsContent value="topics" className="mt-0">
          <div className="p-4 space-y-1">
            <div className="flex items-center justify-between mb-4">
              <h2 className="text-lg font-bold">Trending Crypto Tokens</h2>
              {loading && <Loader2 className="animate-spin text-trenches-green" size={20} />}
            </div>
            {loading ? (
              <div className="text-center py-8 text-muted-foreground">
                Loading trending tokens...
              </div>
            ) : trendingTokens.length > 0 ? (
              trendingTokens.map((token, index) => (
                <div
                  key={token.token}
                  className="hover:bg-secondary p-4 rounded-lg cursor-pointer transition-all duration-200 group"
                >
                  <div className="flex items-start justify-between">
                    <div className="flex-1">
                      <div className="flex items-center gap-2 mb-1">
                        <Hash size={16} className="text-trenches-green" />
                        <span className="font-bold text-lg group-hover:text-trenches-green transition-colors">
                          ${token.token}
                        </span>
                        <span className="text-xs bg-trenches-green text-white px-2 py-1 rounded-full">
                          #{index + 1}
                        </span>
                      </div>
                      <p className="text-sm text-muted-foreground mb-2">Cryptocurrency</p>
                      <div className="flex gap-4 text-sm">
                        <span className="text-foreground">
                          {token.count} mentions
                        </span>
                        <span className="text-muted-foreground">
                          {token.avg_likes.toFixed(1)} avg likes
                        </span>
                      </div>
                    </div>
                    <TrendingUp
                      size={20}
                      className="text-trenches-green opacity-0 group-hover:opacity-100 transition-opacity"
                    />
                  </div>
                </div>
              ))
            ) : (
              <div className="text-center py-8 text-muted-foreground">
                No trending tokens yet. Start the simulation to see trending data!
              </div>
            )}
          </div>
        </TabsContent>
        
        <TabsContent value="posts" className="mt-0">
          <div className="border-b border-border p-4">
            <h2 className="text-lg font-bold mb-2">Trending Posts</h2>
            <p className="text-sm text-muted-foreground">
              Posts with the most engagement right now
            </p>
          </div>
          {trendingPosts.map((post) => (
            <PostCard key={post.id} post={post} />
          ))}
        </TabsContent>
        
        <TabsContent value="people" className="mt-0 p-4">
          <div className="space-y-4">
            <div className="flex items-center justify-between mb-4">
              <h2 className="text-lg font-bold">Top Performing Agents</h2>
              {loading && <Loader2 className="animate-spin text-trenches-green" size={20} />}
            </div>
            {loading ? (
              <div className="text-center py-8 text-muted-foreground">
                Loading top agents...
              </div>
            ) : topAgents.length > 0 ? (
              topAgents.map((agent, index) => (
                <div
                  key={agent.agent_id}
                  className="hover:bg-secondary p-4 rounded-lg cursor-pointer transition-all duration-200"
                >
                  <div className="flex items-start justify-between">
                    <div className="flex-1">
                      <div className="flex items-center gap-2 mb-2">
                        <span className="text-2xl font-bold text-muted-foreground">
                          #{index + 1}
                        </span>
                        <div>
                          <h3 className="font-bold text-lg">@{agent.agent_id}</h3>
                          <div className="flex gap-4 text-sm text-muted-foreground mt-1">
                            <span>{agent.total_tweets} tweets</span>
                            <span>{agent.total_likes} likes</span>
                            <span>{agent.total_retweets} RTs</span>
                          </div>
                        </div>
                      </div>
                      <div className="mt-2 bg-trenches-green-light p-2 rounded">
                        <span className="text-sm font-semibold text-trenches-green">
                          Avg Engagement: {agent.avg_engagement.toFixed(1)}
                        </span>
                      </div>
                    </div>
                    <Button
                      variant="outline"
                      size="sm"
                      className="border-trenches-green text-trenches-green hover:bg-trenches-green hover:text-white"
                    >
                      Follow
                    </Button>
                  </div>
                </div>
              ))
            ) : (
              <div className="text-center py-8 text-muted-foreground">
                No agent data yet. Run the simulation to populate data!
              </div>
            )}
          </div>
        </TabsContent>
        
        <TabsContent value="locations" className="mt-0 p-4">
          <div className="space-y-1">
            <div className="flex items-center justify-between mb-4">
              <h2 className="text-lg font-bold">Trending by Location</h2>
              <Button variant="ghost" size="sm" className="text-trenches-green">
                Change location
              </Button>
            </div>
            {trendingLocations.map((location) => (
              <LocationCard key={location.id} location={location} />
            ))}
          </div>
        </TabsContent>
      </Tabs>
    </Layout>
  );
};

export default Trending;