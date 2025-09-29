import { Heart, MessageCircle, Repeat2, Share, MoreHorizontal } from 'lucide-react';
import { Button } from '@/components/ui/button';
import { formatDistanceToNow } from 'date-fns';
import { Post } from '@/store/useStore';
import { useStore } from '@/store/useStore';
import { Link } from 'react-router-dom';

interface PostCardProps {
  post: Post;
  detailed?: boolean;
}

export const PostCard = ({ post, detailed = false }: PostCardProps) => {
  const { likePost, repostPost } = useStore();

  const handleLike = (e: React.MouseEvent) => {
    e.preventDefault();
    e.stopPropagation();
    likePost(post.id);
  };

  const handleRepost = (e: React.MouseEvent) => {
    e.preventDefault();
    e.stopPropagation();
    repostPost(post.id);
  };

  const formatTime = (timestamp: string) => {
    // For demo purposes, we'll use the timestamp as is
    return timestamp;
  };

  return (
    <Link to={`/post/${post.id}`} className="block">
      <div className={`trenches-post ${detailed ? 'p-6' : ''}`}>
        <div className="flex gap-3">
          {/* Avatar */}
          <Link to={`/profile/${post.user.username}`} onClick={(e) => e.stopPropagation()}>
            <img
              src={post.user.avatar}
              alt={post.user.displayName}
              className="trenches-avatar w-12 h-12"
            />
          </Link>

          {/* Post Content */}
          <div className="flex-1 min-w-0">
            {/* Header */}
            <div className="flex items-center gap-2 mb-2">
              <Link 
                to={`/profile/${post.user.username}`} 
                className="font-bold hover:underline"
                onClick={(e) => e.stopPropagation()}
              >
                {post.user.displayName}
              </Link>
              {post.user.verified && (
                <div className="w-4 h-4 bg-trenches-green rounded-full flex items-center justify-center">
                  <span className="text-white text-xs">✓</span>
                </div>
              )}
              <span className="text-muted-foreground">@{post.user.username}</span>
              <span className="text-muted-foreground">·</span>
              <span className="text-muted-foreground">{formatTime(post.timestamp)}</span>
              
              <div className="ml-auto">
                <Button
                  variant="ghost"
                  size="sm"
                  className="p-1 hover:bg-secondary rounded-full"
                  onClick={(e) => e.stopPropagation()}
                >
                  <MoreHorizontal size={16} className="text-muted-foreground" />
                </Button>
              </div>
            </div>

            {/* Content */}
            <div className="mb-3">
              <p className="text-foreground leading-relaxed">{post.content}</p>
              
              {post.image && (
                <div className="mt-3 rounded-xl overflow-hidden border border-border">
                  <img
                    src={post.image}
                    alt="Post image"
                    className="w-full h-auto max-h-96 object-cover"
                  />
                </div>
              )}
            </div>

            {/* Interaction Buttons */}
            <div className="flex items-center justify-between max-w-md">
              <button
                className="trenches-stat group"
                onClick={handleLike}
              >
                <Heart 
                  size={18} 
                  className={`group-hover:text-like-color transition-colors ${
                    post.isLiked ? 'fill-like-color text-like-color' : ''
                  }`} 
                />
                <span className="group-hover:text-like-color">{post.likes}</span>
              </button>

              <button className="trenches-stat group">
                <MessageCircle 
                  size={18} 
                  className="group-hover:text-comment-color transition-colors" 
                />
                <span className="group-hover:text-comment-color">{post.comments}</span>
              </button>

              <button
                className="trenches-stat group"
                onClick={handleRepost}
              >
                <Repeat2 
                  size={18} 
                  className={`group-hover:text-repost-color transition-colors ${
                    post.isReposted ? 'text-repost-color' : ''
                  }`} 
                />
                <span className="group-hover:text-repost-color">{post.reposts}</span>
              </button>

              <button className="trenches-stat group">
                <Share 
                  size={18} 
                  className="group-hover:text-share-color transition-colors" 
                />
                <span className="group-hover:text-share-color">{post.shares}</span>
              </button>
            </div>
          </div>
        </div>
      </div>
    </Link>
  );
};