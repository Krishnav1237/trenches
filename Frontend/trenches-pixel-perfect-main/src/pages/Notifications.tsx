import { Layout } from '@/components/Layout/Layout';
import { Tabs, TabsContent, TabsList, TabsTrigger } from '@/components/ui/tabs';
import { Button } from '@/components/ui/button';
import { Heart, Repeat2, MessageCircle, UserPlus, AtSign, Bell } from 'lucide-react';
import { Link } from 'react-router-dom';
import pfp2 from '@/assets/pfp2.png';
import pfp3 from '@/assets/pfp3.png';
import pfp4 from '@/assets/pfp4.png';
import pfp5 from '@/assets/pfp5.png';
import pfp6 from '@/assets/pfp6.png';

interface NotificationItem {
  id: string;
  type: 'like' | 'repost' | 'comment' | 'follow' | 'mention';
  user: {
    username: string;
    displayName: string;
    avatar: string;
    verified?: boolean;
  };
  content?: string;
  timestamp: string;
  read: boolean;
}

const mockNotifications: NotificationItem[] = [
  {
    id: '1',
    type: 'like',
    user: {
      username: 'techguru',
      displayName: 'Tech Guru',
      avatar: pfp2,
      verified: true,
    },
    content: 'Just shipped a new feature for Trenches! The timeline is now even smoother.',
    timestamp: '2h',
    read: false,
  },
  {
    id: '2',
    type: 'follow',
    user: {
      username: 'designer',
      displayName: 'UI Designer',
      avatar: pfp3,
    },
    timestamp: '4h',
    read: false,
  },
  {
    id: '3',
    type: 'repost',
    user: {
      username: 'entrepreneur',
      displayName: 'Startup Founder',
      avatar: pfp4,
      verified: true,
    },
    content: 'The future of social media is decentralized. Building in public and loving every moment of it!',
    timestamp: '6h',
    read: true,
  },
  {
    id: '4',
    type: 'mention',
    user: {
      username: 'coder',
      displayName: 'Full Stack Developer',
      avatar: pfp5,
    },
    content: 'Hey @johndoe, what do you think about the new Trenches update?',
    timestamp: '1d',
    read: true,
  },
  {
    id: '5',
    type: 'comment',
    user: {
      username: 'productmanager',
      displayName: 'Product Manager',
      avatar: pfp6,
    },
    content: 'This is exactly what we needed! Great work on the implementation.',
    timestamp: '2d',
    read: true,
  },
];

const NotificationCard = ({ notification }: { notification: NotificationItem }) => {
  const getIcon = () => {
    switch (notification.type) {
      case 'like':
        return <Heart className="text-like-color" size={16} fill="currentColor" />;
      case 'repost':
        return <Repeat2 className="text-repost-color" size={16} />;
      case 'comment':
        return <MessageCircle className="text-comment-color" size={16} />;
      case 'follow':
        return <UserPlus className="text-trenches-green" size={16} />;
      case 'mention':
        return <AtSign className="text-trenches-green" size={16} />;
      default:
        return null;
    }
  };

  const getActionText = () => {
    switch (notification.type) {
      case 'like':
        return 'liked your post';
      case 'repost':
        return 'reposted your post';
      case 'comment':
        return 'commented on your post';
      case 'follow':
        return 'followed you';
      case 'mention':
        return 'mentioned you';
      default:
        return '';
    }
  };

  return (
    <div className={`flex gap-3 p-4 border-b border-border hover:bg-secondary/50 transition-colors ${!notification.read ? 'bg-trenches-green-light/20' : ''}`}>
      <div className="flex-shrink-0 mt-1">
        {getIcon()}
      </div>
      
      <div className="flex gap-3 flex-1">
        <Link to={`/profile/${notification.user.username}`}>
          <img
            src={notification.user.avatar}
            alt={notification.user.displayName}
            className="trenches-avatar w-8 h-8"
          />
        </Link>
        
        <div className="flex-1 min-w-0">
          <div className="flex items-center gap-1 mb-1">
            <Link 
              to={`/profile/${notification.user.username}`}
              className="font-semibold hover:underline"
            >
              {notification.user.displayName}
            </Link>
            {notification.user.verified && (
              <div className="w-4 h-4 bg-trenches-green rounded-full flex items-center justify-center">
                <span className="text-white text-xs">✓</span>
              </div>
            )}
            <span className="text-muted-foreground text-sm">
              @{notification.user.username}
            </span>
            <span className="text-muted-foreground text-sm">·</span>
            <span className="text-muted-foreground text-sm">{notification.timestamp}</span>
          </div>
          
          <p className="text-sm mb-2">
            <span className="text-muted-foreground">{getActionText()}</span>
          </p>
          
          {notification.content && (
            <div className="bg-secondary p-3 rounded-lg text-sm text-muted-foreground">
              {notification.content}
            </div>
          )}
          
          {notification.type === 'follow' && (
            <Button size="sm" className="trenches-button-primary mt-2">
              Follow back
            </Button>
          )}
        </div>
      </div>
    </div>
  );
};

const Notifications = () => {
  const allNotifications = mockNotifications;
  const mentionNotifications = mockNotifications.filter(n => n.type === 'mention');
  const followNotifications = mockNotifications.filter(n => n.type === 'follow');

  return (
    <Layout title="Notifications" showSearch={false}>
      <Tabs defaultValue="all" className="w-full">
        <TabsList className="w-full bg-transparent border-b border-border rounded-none h-auto p-0">
          <TabsTrigger 
            value="all" 
            className="flex-1 rounded-none border-b-2 border-transparent data-[state=active]:border-trenches-green data-[state=active]:bg-transparent"
          >
            All
          </TabsTrigger>
          <TabsTrigger 
            value="mentions" 
            className="flex-1 rounded-none border-b-2 border-transparent data-[state=active]:border-trenches-green data-[state=active]:bg-transparent"
          >
            Mentions
          </TabsTrigger>
          <TabsTrigger 
            value="follows" 
            className="flex-1 rounded-none border-b-2 border-transparent data-[state=active]:border-trenches-green data-[state=active]:bg-transparent"
          >
            Follows
          </TabsTrigger>
        </TabsList>
        
        <TabsContent value="all" className="mt-0">
          {allNotifications.length > 0 ? (
            allNotifications.map((notification) => (
              <NotificationCard key={notification.id} notification={notification} />
            ))
          ) : (
            <div className="p-8 text-center text-muted-foreground">
              <Bell size={48} className="mx-auto mb-4 opacity-50" />
              <p className="text-lg">No notifications yet</p>
              <p className="text-sm">When someone interacts with you, it'll show up here.</p>
            </div>
          )}
        </TabsContent>
        
        <TabsContent value="mentions" className="mt-0">
          {mentionNotifications.length > 0 ? (
            mentionNotifications.map((notification) => (
              <NotificationCard key={notification.id} notification={notification} />
            ))
          ) : (
            <div className="p-8 text-center text-muted-foreground">
              <AtSign size={48} className="mx-auto mb-4 opacity-50" />
              <p className="text-lg">No mentions yet</p>
              <p className="text-sm">When someone mentions you, it'll show up here.</p>
            </div>
          )}
        </TabsContent>
        
        <TabsContent value="follows" className="mt-0">
          {followNotifications.length > 0 ? (
            followNotifications.map((notification) => (
              <NotificationCard key={notification.id} notification={notification} />
            ))
          ) : (
            <div className="p-8 text-center text-muted-foreground">
              <UserPlus size={48} className="mx-auto mb-4 opacity-50" />
              <p className="text-lg">No new followers</p>
              <p className="text-sm">When someone follows you, it'll show up here.</p>
            </div>
          )}
        </TabsContent>
      </Tabs>
    </Layout>
  );
};

export default Notifications;