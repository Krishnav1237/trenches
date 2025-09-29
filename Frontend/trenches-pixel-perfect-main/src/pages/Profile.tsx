import { useParams } from 'react-router-dom';
import { Layout } from '@/components/Layout/Layout';
import { PostCard } from '@/components/Post/PostCard';
import { Button } from '@/components/ui/button';
import { Tabs, TabsContent, TabsList, TabsTrigger } from '@/components/ui/tabs';
import { useStore } from '@/store/useStore';
import { Calendar, MapPin, Link as LinkIcon } from 'lucide-react';

const Profile = () => {
  const { username } = useParams();
  const { currentUser, posts } = useStore();
  
  // For demo, we'll use currentUser if no username or if it matches
  const user = currentUser;
  const userPosts = posts.filter(post => post.user.id === user?.id);
  const isOwnProfile = !username || username === user?.username;

  if (!user) {
    return <Layout title="Profile">Loading...</Layout>;
  }

  return (
    <Layout title={user.displayName} showSearch={false}>
      {/* Profile Header */}
      <div className="relative">
        {/* Banner */}
        <div className="h-48 bg-gradient-to-r from-trenches-green to-trenches-green-light"></div>
        
        {/* Profile Info */}
        <div className="px-4 pb-4">
          <div className="flex justify-between items-start -mt-16 mb-4">
            <img
              src={user.avatar}
              alt={user.displayName}
              className="trenches-avatar w-32 h-32 border-4 border-background"
            />
            
            {isOwnProfile ? (
              <Button variant="outline" className="mt-16">
                Edit Profile
              </Button>
            ) : (
              <Button className="trenches-button-primary mt-16">
                Follow
              </Button>
            )}
          </div>
          
          {/* User Details */}
          <div className="space-y-3">
            <div>
              <div className="flex items-center gap-2">
                <h1 className="text-2xl font-bold">{user.displayName}</h1>
                {user.verified && (
                  <div className="w-6 h-6 bg-trenches-green rounded-full flex items-center justify-center">
                    <span className="text-white text-sm">✓</span>
                  </div>
                )}
              </div>
              <p className="text-muted-foreground">@{user.username}</p>
            </div>
            
            {user.bio && (
              <p className="text-foreground">{user.bio}</p>
            )}
            
            <div className="flex items-center gap-4 text-sm text-muted-foreground">
              <div className="flex items-center gap-1">
                <MapPin size={16} />
                <span>San Francisco, CA</span>
              </div>
              <div className="flex items-center gap-1">
                <LinkIcon size={16} />
                <span className="text-trenches-green">johndoe.dev</span>
              </div>
              <div className="flex items-center gap-1">
                <Calendar size={16} />
                <span>Joined March 2021</span>
              </div>
            </div>
            
            <div className="flex gap-6 text-sm">
              <span>
                <span className="font-bold text-foreground">{user.following.toLocaleString()}</span>{' '}
                <span className="text-muted-foreground">Following</span>
              </span>
              <span>
                <span className="font-bold text-foreground">{user.followers.toLocaleString()}</span>{' '}
                <span className="text-muted-foreground">Followers</span>
              </span>
            </div>
          </div>
        </div>
      </div>

      {/* Profile Tabs */}
      <Tabs defaultValue="posts" className="w-full">
        <TabsList className="w-full bg-transparent border-b border-border rounded-none h-auto p-0">
          <TabsTrigger 
            value="posts" 
            className="flex-1 rounded-none border-b-2 border-transparent data-[state=active]:border-trenches-green data-[state=active]:bg-transparent"
          >
            Posts
          </TabsTrigger>
          <TabsTrigger 
            value="replies" 
            className="flex-1 rounded-none border-b-2 border-transparent data-[state=active]:border-trenches-green data-[state=active]:bg-transparent"
          >
            Replies
          </TabsTrigger>
          <TabsTrigger 
            value="media" 
            className="flex-1 rounded-none border-b-2 border-transparent data-[state=active]:border-trenches-green data-[state=active]:bg-transparent"
          >
            Media
          </TabsTrigger>
          <TabsTrigger 
            value="likes" 
            className="flex-1 rounded-none border-b-2 border-transparent data-[state=active]:border-trenches-green data-[state=active]:bg-transparent"
          >
            Likes
          </TabsTrigger>
        </TabsList>
        
        <TabsContent value="posts" className="mt-0">
          {userPosts.map((post) => (
            <PostCard key={post.id} post={post} />
          ))}
        </TabsContent>
        
        <TabsContent value="replies" className="mt-0">
          <div className="p-8 text-center text-muted-foreground">
            <p>No replies yet</p>
          </div>
        </TabsContent>
        
        <TabsContent value="media" className="mt-0">
          <div className="p-8 text-center text-muted-foreground">
            <p>No media yet</p>
          </div>
        </TabsContent>
        
        <TabsContent value="likes" className="mt-0">
          <div className="p-8 text-center text-muted-foreground">
            <p>No likes yet</p>
          </div>
        </TabsContent>
      </Tabs>
    </Layout>
  );
};

export default Profile;