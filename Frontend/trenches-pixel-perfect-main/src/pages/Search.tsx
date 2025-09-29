import { Layout } from '@/components/Layout/Layout';
import { UserCard } from '@/components/User/UserCard';
import { PostCard } from '@/components/Post/PostCard';
import { Input } from '@/components/ui/input';
import { Tabs, TabsContent, TabsList, TabsTrigger } from '@/components/ui/tabs';
import { useStore } from '@/store/useStore';
import { Search as SearchIcon, TrendingUp, BarChart3 } from 'lucide-react';
import { useState } from 'react';
import pfp4 from '@/assets/pfp4.png';
import pfp5 from '@/assets/pfp5.png';
import pfp6 from '@/assets/pfp6.png';

const Search = () => {
  const { posts, searchQuery, setSearchQuery } = useStore();
  const [localQuery, setLocalQuery] = useState(searchQuery);

  // Mock users for search results
  const mockUsers = [
    {
      id: '1',
      username: 'techguru',
      displayName: 'Tech Guru',
      avatar: pfp4,
      bio: 'Building the future, one line of code at a time 🚀',
      followers: 15600,
      following: 892,
      postsCount: 1205,
      verified: true,
    },
    {
      id: '2',
      username: 'designer',
      displayName: 'UI Designer',
      avatar: pfp5,
      bio: 'Creating beautiful experiences through design ✨',
      followers: 8943,
      following: 456,
      postsCount: 789,
    },
    {
      id: '3',
      username: 'entrepreneur',
      displayName: 'Startup Founder',
      avatar: pfp6,
      bio: 'Building the next big thing 💡',
      followers: 12340,
      following: 234,
      postsCount: 567,
      verified: true,
    },
  ];

  const filteredPosts = posts.filter(post => 
    post.content.toLowerCase().includes(localQuery.toLowerCase()) ||
    post.user.displayName.toLowerCase().includes(localQuery.toLowerCase())
  );

  const filteredUsers = mockUsers.filter(user =>
    user.displayName.toLowerCase().includes(localQuery.toLowerCase()) ||
    user.username.toLowerCase().includes(localQuery.toLowerCase()) ||
    (user.bio && user.bio.toLowerCase().includes(localQuery.toLowerCase()))
  );

  const handleSearch = (value: string) => {
    setLocalQuery(value);
    setSearchQuery(value);
  };

  return (
    <Layout title="Search" showSearch={false}>
      {/* Search Bar */}
      <div className="p-4 border-b border-border">
        <div className="relative">
          <SearchIcon className="absolute left-3 top-1/2 transform -translate-y-1/2 text-muted-foreground" size={20} />
          <Input
            placeholder="Search for people, posts, and topics"
            value={localQuery}
            onChange={(e) => handleSearch(e.target.value)}
            className="pl-12 bg-secondary border-none rounded-full text-lg h-12"
          />
        </div>
      </div>

      {!localQuery ? (
        // Trending/Discover Content
        <div className="p-4 space-y-6">
          {/* Trending Topics */}
          <div className="trenches-card">
            <div className="flex items-center gap-2 mb-4">
              <TrendingUp className="text-trenches-green" size={20} />
              <h2 className="text-xl font-bold">Trending for you</h2>
            </div>
            <div className="space-y-3">
              <div className="hover:bg-secondary p-3 rounded-lg cursor-pointer transition-colors">
                <p className="text-sm text-muted-foreground">Trending in Technology</p>
                <p className="font-bold text-lg">React 18</p>
                <p className="text-sm text-muted-foreground">12.5K posts</p>
              </div>
              <div className="hover:bg-secondary p-3 rounded-lg cursor-pointer transition-colors">
                <p className="text-sm text-muted-foreground">Trending</p>
                <p className="font-bold text-lg">#WebDev</p>
                <p className="text-sm text-muted-foreground">8.2K posts</p>
              </div>
              <div className="hover:bg-secondary p-3 rounded-lg cursor-pointer transition-colors">
                <p className="text-sm text-muted-foreground">Trending in Design</p>
                <p className="font-bold text-lg">UI/UX Design</p>
                <p className="text-sm text-muted-foreground">5.7K posts</p>
              </div>
            </div>
          </div>

          {/* Who to Follow */}
          <div className="trenches-card">
            <h2 className="text-xl font-bold mb-4">Who to follow</h2>
            <div className="space-y-4">
              {mockUsers.slice(0, 3).map((user) => (
                <UserCard key={user.id} user={user} showBio={false} />
              ))}
            </div>
          </div>

          {/* Statistics */}
          <div className="trenches-card">
            <div className="flex items-center gap-2 mb-4">
              <BarChart3 className="text-trenches-green" size={20} />
              <h2 className="text-xl font-bold">Platform Stats</h2>
            </div>
            <div className="grid grid-cols-2 gap-4">
              <div className="text-center p-4 bg-secondary rounded-lg">
                <p className="text-2xl font-bold text-trenches-green">50.2K</p>
                <p className="text-sm text-muted-foreground">Active Users</p>
              </div>
              <div className="text-center p-4 bg-secondary rounded-lg">
                <p className="text-2xl font-bold text-trenches-green">128K</p>
                <p className="text-sm text-muted-foreground">Posts Today</p>
              </div>
            </div>
          </div>
        </div>
      ) : (
        // Search Results
        <Tabs defaultValue="posts" className="w-full">
          <TabsList className="w-full bg-transparent border-b border-border rounded-none h-auto p-0">
            <TabsTrigger 
              value="posts" 
              className="flex-1 rounded-none border-b-2 border-transparent data-[state=active]:border-trenches-green data-[state=active]:bg-transparent"
            >
              Posts ({filteredPosts.length})
            </TabsTrigger>
            <TabsTrigger 
              value="people" 
              className="flex-1 rounded-none border-b-2 border-transparent data-[state=active]:border-trenches-green data-[state=active]:bg-transparent"
            >
              People ({filteredUsers.length})
            </TabsTrigger>
          </TabsList>
          
          <TabsContent value="posts" className="mt-0">
            {filteredPosts.length > 0 ? (
              filteredPosts.map((post) => (
                <PostCard key={post.id} post={post} />
              ))
            ) : (
              <div className="p-8 text-center text-muted-foreground">
                <p>No posts found for "{localQuery}"</p>
              </div>
            )}
          </TabsContent>
          
          <TabsContent value="people" className="mt-0 p-4">
            {filteredUsers.length > 0 ? (
              <div className="space-y-4">
                {filteredUsers.map((user) => (
                  <UserCard key={user.id} user={user} />
                ))}
              </div>
            ) : (
              <div className="p-8 text-center text-muted-foreground">
                <p>No people found for "{localQuery}"</p>
              </div>
            )}
          </TabsContent>
        </Tabs>
      )}
    </Layout>
  );
};

export default Search;