import { Layout } from '@/components/Layout/Layout';
import { Tabs, TabsContent, TabsList, TabsTrigger } from '@/components/ui/tabs';
import { Button } from '@/components/ui/button';
import { Heart, Repeat2, MessageCircle, UserPlus, AtSign, Bell, Loader2, CheckCheck } from 'lucide-react';
import { Link } from 'react-router-dom';
import { useState, useEffect } from 'react';
import { apiClient } from '@/lib/api';

interface NotificationItem {
  id: number;
  type: string;
  read: boolean;
  created_at: string;
  actor_username: string;
  actor_display_name: string;
  actor_avatar: string;
  tweet_id?: number;
  tweet_content?: string;
}

const NotificationCard = ({
  notification,
  onMarkAsRead
}: {
  notification: NotificationItem;
  onMarkAsRead: (id: number) => void;
}) => {
  const getIcon = () => {
    switch (notification.type) {
      case 'like':
        return <Heart className="text-like-color" size={16} fill="currentColor" />;
      case 'retweet':
        return <Repeat2 className="text-repost-color" size={16} />;
      case 'reply':
      case 'comment':
        return <MessageCircle className="text-comment-color" size={16} />;
      case 'follow':
        return <UserPlus className="text-trenches-green" size={16} />;
      case 'mention':
        return <AtSign className="text-trenches-green" size={16} />;
      default:
        return <Bell size={16} />;
    }
  };

  const getActionText = () => {
    switch (notification.type) {
      case 'like':
        return 'liked your post';
      case 'retweet':
        return 'retweeted your post';
      case 'reply':
      case 'comment':
        return 'replied to your post';
      case 'follow':
        return 'followed you';
      case 'mention':
        return 'mentioned you';
      default:
        return 'interacted with you';
    }
  };

  const formatTimeAgo = (timestamp: string): string => {
    const now = new Date();
    const time = new Date(timestamp);
    const diffMs = now.getTime() - time.getTime();
    const diffMins = Math.floor(diffMs / 60000);
    const diffHours = Math.floor(diffMins / 60);
    const diffDays = Math.floor(diffHours / 24);

    if (diffDays > 0) return `${diffDays}d`;
    if (diffHours > 0) return `${diffHours}h`;
    if (diffMins > 0) return `${diffMins}m`;
    return 'Just now';
  };

  const handleClick = () => {
    if (!notification.read) {
      onMarkAsRead(notification.id);
    }
  };

  return (
    <div
      className={`flex gap-3 p-4 border-b border-border hover:bg-secondary/50 transition-colors cursor-pointer ${!notification.read ? 'bg-trenches-green-light/10' : ''}`}
      onClick={handleClick}
    >
      <div className="flex-shrink-0 mt-1">
        {getIcon()}
      </div>

      <div className="flex gap-3 flex-1">
        <Link to={`/profile/${notification.actor_username}`}>
          <img
            src={notification.actor_avatar}
            alt={notification.actor_display_name}
            className="trenches-avatar w-8 h-8"
          />
        </Link>

        <div className="flex-1 min-w-0">
          <div className="flex items-center gap-1 mb-1">
            <Link
              to={`/profile/${notification.actor_username}`}
              className="font-semibold hover:underline"
            >
              {notification.actor_display_name}
            </Link>
            <span className="text-muted-foreground text-sm">
              @{notification.actor_username}
            </span>
            <span className="text-muted-foreground text-sm">·</span>
            <span className="text-muted-foreground text-sm">
              {formatTimeAgo(notification.created_at)}
            </span>
            {!notification.read && (
              <div className="ml-auto w-2 h-2 bg-trenches-green rounded-full"></div>
            )}
          </div>

          <p className="text-sm mb-2">
            <span className="text-muted-foreground">{getActionText()}</span>
          </p>

          {notification.tweet_content && (
            <Link to={`/post/${notification.tweet_id}`}>
              <div className="bg-secondary p-3 rounded-lg text-sm text-muted-foreground hover:bg-secondary/80">
                {notification.tweet_content}
              </div>
            </Link>
          )}
        </div>
      </div>
    </div>
  );
};

const Notifications = () => {
  const [notifications, setNotifications] = useState<NotificationItem[]>([]);
  const [loading, setLoading] = useState(true);
  const [markingAllAsRead, setMarkingAllAsRead] = useState(false);

  useEffect(() => {
    fetchNotifications();
  }, []);

  const fetchNotifications = async () => {
    try {
      setLoading(true);
      const data = await apiClient.getNotifications({ limit: 50 });
      setNotifications(data.notifications || []);
    } catch (error) {
      console.error('Failed to fetch notifications:', error);
    } finally {
      setLoading(false);
    }
  };

  const handleMarkAsRead = async (notificationId: number) => {
    try {
      await apiClient.markNotificationAsRead(notificationId);
      setNotifications(prev =>
        prev.map(n =>
          n.id === notificationId ? { ...n, read: true } : n
        )
      );
    } catch (error) {
      console.error('Failed to mark notification as read:', error);
    }
  };

  const handleMarkAllAsRead = async () => {
    try {
      setMarkingAllAsRead(true);
      await apiClient.markAllNotificationsAsRead();
      setNotifications(prev =>
        prev.map(n => ({ ...n, read: true }))
      );
    } catch (error) {
      console.error('Failed to mark all as read:', error);
    } finally {
      setMarkingAllAsRead(false);
    }
  };

  const unreadCount = notifications.filter(n => !n.read).length;
  const mentionNotifications = notifications.filter(n => n.type === 'mention');
  const followNotifications = notifications.filter(n => n.type === 'follow');

  if (loading) {
    return (
      <Layout title="Notifications" showSearch={false}>
        <div className="flex items-center justify-center h-64">
          <Loader2 className="w-8 h-8 animate-spin text-trenches-green" />
        </div>
      </Layout>
    );
  }

  return (
    <Layout title="Notifications" showSearch={false}>
      {/* Mark All as Read Button */}
      {unreadCount > 0 && (
        <div className="border-b border-border p-3 bg-muted/50 flex justify-between items-center">
          <span className="text-sm text-muted-foreground">
            {unreadCount} unread notification{unreadCount !== 1 ? 's' : ''}
          </span>
          <Button
            variant="ghost"
            size="sm"
            onClick={handleMarkAllAsRead}
            disabled={markingAllAsRead}
            className="gap-2"
          >
            {markingAllAsRead ? (
              <>
                <Loader2 className="w-4 h-4 animate-spin" />
                Marking...
              </>
            ) : (
              <>
                <CheckCheck className="w-4 h-4" />
                Mark all as read
              </>
            )}
          </Button>
        </div>
      )}

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
          {notifications.length > 0 ? (
            notifications.map((notification) => (
              <NotificationCard
                key={notification.id}
                notification={notification}
                onMarkAsRead={handleMarkAsRead}
              />
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
              <NotificationCard
                key={notification.id}
                notification={notification}
                onMarkAsRead={handleMarkAsRead}
              />
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
              <NotificationCard
                key={notification.id}
                notification={notification}
                onMarkAsRead={handleMarkAsRead}
              />
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
