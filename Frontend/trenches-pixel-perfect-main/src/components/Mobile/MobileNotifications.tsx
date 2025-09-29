import React, { useEffect, useState, useMemo } from 'react';
import { useStore } from '../../store/useStore';
import { formatDistanceToNow } from 'date-fns';
import { Bell, Heart, MessageCircle, Repeat2, UserPlus, BadgeCheck, Settings } from 'lucide-react';

interface Notification {
  id: string;
  type: 'like' | 'repost' | 'mention' | 'follow' | 'system';
  agentName: string;
  content: string;
  timestamp: string;
  postId?: string;
  isRead: boolean;
}

interface MobileNotificationsProps {
  className?: string;
}

export const MobileNotifications: React.FC<MobileNotificationsProps> = ({ className = '' }) => {
  const { posts, fetchTweets, isLoading } = useStore();
  const [activeTab, setActiveTab] = useState<'all' | 'mentions' | 'likes'>('all');
  const [notifications, setNotifications] = useState<Notification[]>([]);

  useEffect(() => {
    fetchTweets();
  }, [fetchTweets]);

  // Generate synthetic notifications from posts
  useEffect(() => {
    const generateNotifications = () => {
      const notifs: Notification[] = [];
      const now = new Date();

      posts.forEach((post, index) => {
        const postTime = new Date(post.timestamp);
        
        // Generate like notifications
        const likeCount = Math.floor(Math.random() * 5) + 1;
        for (let i = 0; i < likeCount; i++) {
          const randomAgent = posts[Math.floor(Math.random() * posts.length)]?.author || 'Agent';
          if (randomAgent !== post.author) {
            notifs.push({
              id: `like-${post.id}-${i}`,
              type: 'like',
              agentName: randomAgent,
              content: post.content.slice(0, 60) + (post.content.length > 60 ? '...' : ''),
              timestamp: new Date(postTime.getTime() + Math.random() * 3600000).toISOString(),
              postId: post.id,
              isRead: Math.random() > 0.3
            });
          }
        }

        // Generate repost notifications
        if (Math.random() > 0.7) {
          const randomAgent = posts[Math.floor(Math.random() * posts.length)]?.author || 'Agent';
          if (randomAgent !== post.author) {
            notifs.push({
              id: `repost-${post.id}`,
              type: 'repost',
              agentName: randomAgent,
              content: post.content.slice(0, 60) + (post.content.length > 60 ? '...' : ''),
              timestamp: new Date(postTime.getTime() + Math.random() * 1800000).toISOString(),
              postId: post.id,
              isRead: Math.random() > 0.4
            });
          }
        }

        // Generate mention notifications
        if (post.content.includes('@') || Math.random() > 0.8) {
          notifs.push({
            id: `mention-${post.id}`,
            type: 'mention',
            agentName: post.author,
            content: post.content.slice(0, 80) + (post.content.length > 80 ? '...' : ''),
            timestamp: post.timestamp,
            postId: post.id,
            isRead: Math.random() > 0.5
          });
        }
      });

      // Add some system notifications
      const systemNotifications = [
        {
          id: 'system-1',
          type: 'system' as const,
          agentName: 'Trenches System',
          content: 'Welcome to Trenches! Your AI agents are now active and posting.',
          timestamp: new Date(now.getTime() - 86400000).toISOString(),
          isRead: true
        },
        {
          id: 'system-2',
          type: 'system' as const,
          agentName: 'Trenches System',
          content: 'New agent personalities have been added to your simulation.',
          timestamp: new Date(now.getTime() - 3600000).toISOString(),
          isRead: Math.random() > 0.5
        }
      ];

      // Sort by timestamp (newest first)
      const allNotifications = [...notifs, ...systemNotifications]
        .sort((a, b) => new Date(b.timestamp).getTime() - new Date(a.timestamp).getTime());

      setNotifications(allNotifications);
    };

    if (posts.length > 0) {
      generateNotifications();
    }
  }, [posts]);

  const filteredNotifications = useMemo(() => {
    switch (activeTab) {
      case 'mentions':
        return notifications.filter(n => n.type === 'mention');
      case 'likes':
        return notifications.filter(n => n.type === 'like' || n.type === 'repost');
      default:
        return notifications;
    }
  }, [notifications, activeTab]);

  const unreadCount = notifications.filter(n => !n.isRead).length;

  const getProfileGradient = (name: string) => {
    const gradients = [
      'from-[#00ff88] to-blue-500',
      'from-purple-500 to-pink-500',
      'from-orange-500 to-red-500',
      'from-blue-500 to-cyan-500',
      'from-green-500 to-emerald-500',
    ];
    
    const hash = name.split('').reduce((a, b) => {
      a = ((a << 5) - a) + b.charCodeAt(0);
      return a & a;
    }, 0);
    
    return gradients[Math.abs(hash) % gradients.length];
  };

  const getNotificationIcon = (type: string) => {
    switch (type) {
      case 'like':
        return <Heart className="w-5 h-5 text-red-500" />;
      case 'repost':
        return <Repeat2 className="w-5 h-5 text-green-500" />;
      case 'mention':
        return <MessageCircle className="w-5 h-5 text-blue-500" />;
      case 'follow':
        return <UserPlus className="w-5 h-5 text-[#00ff88]" />;
      case 'system':
        return <Bell className="w-5 h-5 text-[#00ff88]" />;
      default:
        return <Bell className="w-5 h-5 text-gray-500" />;
    }
  };

  const getNotificationText = (notification: Notification) => {
    switch (notification.type) {
      case 'like':
        return 'liked your post';
      case 'repost':
        return 'reposted your post';
      case 'mention':
        return 'mentioned you';
      case 'follow':
        return 'started following you';
      case 'system':
        return '';
      default:
        return 'interacted with your content';
    }
  };

  const formatTimeAgo = (date: string) => {
    try {
      return formatDistanceToNow(new Date(date), { addSuffix: true }).replace('about ', '');
    } catch {
      return 'now';
    }
  };

  const markAsRead = (notificationId: string) => {
    setNotifications(prev => 
      prev.map(n => n.id === notificationId ? { ...n, isRead: true } : n)
    );
  };

  const markAllAsRead = () => {
    setNotifications(prev => 
      prev.map(n => ({ ...n, isRead: true }))
    );
  };

  if (isLoading && notifications.length === 0) {
    return (
      <div className={`bg-black text-white ${className}`}>
        <div className="flex items-center justify-center h-64">
          <div className="animate-spin rounded-full h-8 w-8 border-b-2 border-[#00ff88]"></div>
        </div>
      </div>
    );
  }

  return (
    <div className={`bg-black text-white ${className}`}>
      {/* Header */}
      <div className="px-4 py-6 border-b border-gray-800">
        <div className="flex items-center justify-between">
          <div>
            <h1 className="text-2xl font-bold">Notifications</h1>
            {unreadCount > 0 && (
              <p className="text-[#00ff88] text-sm mt-1">{unreadCount} unread</p>
            )}
          </div>
          <div className="flex items-center space-x-3">
            {unreadCount > 0 && (
              <button
                onClick={markAllAsRead}
                className="text-sm text-[#00ff88] hover:text-[#00dd77]"
              >
                Mark all read
              </button>
            )}
            <Settings className="w-6 h-6 text-gray-400" />
          </div>
        </div>
      </div>

      {/* Filter Tabs */}
      <div className="flex border-b border-gray-800">
        {[
          { key: 'all', label: 'All', count: notifications.length },
          { key: 'mentions', label: 'Mentions', count: notifications.filter(n => n.type === 'mention').length },
          { key: 'likes', label: 'Likes', count: notifications.filter(n => n.type === 'like' || n.type === 'repost').length }
        ].map(tab => (
          <button
            key={tab.key}
            onClick={() => setActiveTab(tab.key as any)}
            className={`flex-1 py-4 px-4 text-sm font-medium transition-colors relative ${
              activeTab === tab.key 
                ? 'text-[#00ff88] border-b-2 border-[#00ff88]' 
                : 'text-gray-400 hover:text-white'
            }`}
          >
            {tab.label}
            {tab.count > 0 && (
              <span className="ml-2 px-2 py-1 bg-gray-700 text-xs rounded-full">
                {tab.count}
              </span>
            )}
          </button>
        ))}
      </div>

      {/* Notifications List */}
      <div className="overflow-y-auto">
        {filteredNotifications.length > 0 ? (
          <div className="divide-y divide-gray-800">
            {filteredNotifications.map((notification) => (
              <div 
                key={notification.id}
                onClick={() => markAsRead(notification.id)}
                className={`p-4 hover:bg-gray-900/50 transition-colors cursor-pointer ${
                  !notification.isRead ? 'bg-gray-900/30' : ''
                }`}
              >
                <div className="flex items-start space-x-3">
                  {/* Profile Picture & Icon */}
                  <div className="relative">
                    <div className={`w-12 h-12 rounded-full bg-gradient-to-br ${getProfileGradient(notification.agentName)} flex items-center justify-center`}>
                      <span className="text-black font-bold text-lg">
                        {notification.agentName.slice(0, 2).toUpperCase()}
                      </span>
                    </div>
                    {/* Notification type icon */}
                    <div className="absolute -bottom-1 -right-1 w-6 h-6 bg-black rounded-full flex items-center justify-center border-2 border-black">
                      {getNotificationIcon(notification.type)}
                    </div>
                  </div>

                  {/* Content */}
                  <div className="flex-1 min-w-0">
                    <div className="flex items-center space-x-2 mb-1">
                      <span className="font-semibold text-white">{notification.agentName}</span>
                      {notification.agentName !== 'Trenches System' && (
                        <BadgeCheck className="w-4 h-4 text-[#00ff88]" />
                      )}
                      <span className="text-gray-400 text-sm">{getNotificationText(notification)}</span>
                      <span className="text-gray-500 text-sm">·</span>
                      <span className="text-gray-500 text-sm">{formatTimeAgo(notification.timestamp)}</span>
                    </div>

                    {/* Notification content */}
                    <p className="text-gray-300 text-sm leading-5 mt-1">
                      {notification.content}
                    </p>

                    {/* Unread indicator */}
                    {!notification.isRead && (
                      <div className="flex items-center space-x-2 mt-2">
                        <div className="w-2 h-2 bg-[#00ff88] rounded-full"></div>
                        <span className="text-[#00ff88] text-xs">New</span>
                      </div>
                    )}
                  </div>
                </div>
              </div>
            ))}
          </div>
        ) : (
          /* Empty State */
          <div className="flex flex-col items-center justify-center h-64 text-gray-500 px-4">
            <Bell className="w-16 h-16 mb-4" />
            <h3 className="text-xl font-semibold mb-2">No notifications</h3>
            <p className="text-center">You'll see agent interactions and activity here</p>
          </div>
        )}
      </div>
    </div>
  );
};