import { useParams } from 'react-router-dom';
import { Layout } from '@/components/Layout/Layout';
import { PostCard } from '@/components/Post/PostCard';
import { Button } from '@/components/ui/button';
import { Textarea } from '@/components/ui/textarea';
import { useStore } from '@/store/useStore';
import { useState } from 'react';
import { ArrowLeft } from 'lucide-react';
import { Link } from 'react-router-dom';
import pfp5 from '@/assets/pfp5.png';
import pfp2 from '@/assets/pfp2.png';

const PostDetail = () => {
  const { postId } = useParams();
  const { posts, currentUser } = useStore();
  const [reply, setReply] = useState('');

  const post = posts.find(p => p.id === postId);

  // Mock replies for demo
  const mockReplies = [
    {
      id: 'reply1',
      user: {
        id: '2',
        username: 'techfan',
        displayName: 'Tech Fan',
        avatar: pfp5,
        followers: 234,
        following: 345,
        postsCount: 56,
      },
      content: 'This looks amazing! Great work on the design 🎨',
      timestamp: '1h',
      likes: 5,
      reposts: 1,
      comments: 0,
      shares: 0,
      replyTo: postId,
    },
    {
      id: 'reply2',
      user: {
        id: '3',
        username: 'developer',
        displayName: 'Full Stack Dev',
        avatar: pfp2,
        followers: 567,
        following: 123,
        postsCount: 89,
        verified: true,
      },
      content: 'Can\'t wait to try this out! The UI looks so clean and modern.',
      timestamp: '45m',
      likes: 12,
      reposts: 2,
      comments: 1,
      shares: 0,
      replyTo: postId,
    },
  ];

  const handleReply = () => {
    if (!reply.trim()) return;
    // In a real app, this would add a reply to the post
    setReply('');
  };

  if (!post) {
    return (
      <Layout title="Post" showSearch={false}>
        <div className="p-8 text-center">
          <p className="text-muted-foreground">Post not found</p>
          <Link to="/" className="text-trenches-green hover:underline mt-2 inline-block">
            Go back to home
          </Link>
        </div>
      </Layout>
    );
  }

  return (
    <Layout title="Post" showSearch={false}>
      {/* Back Button */}
      <div className="flex items-center gap-3 p-4 border-b border-border">
        <Link to="/" className="p-2 hover:bg-secondary rounded-full transition-colors">
          <ArrowLeft size={20} />
        </Link>
        <span className="text-xl font-bold">Post</span>
      </div>

      {/* Main Post */}
      <div className="border-b border-border">
        <PostCard post={post} detailed />
      </div>

      {/* Reply Composer */}
      {currentUser && (
        <div className="border-b border-border p-4">
          <div className="flex gap-3">
            <img
              src={currentUser.avatar}
              alt={currentUser.displayName}
              className="trenches-avatar w-12 h-12"
            />
            
            <div className="flex-1">
              <Textarea
                placeholder={`Reply to @${post.user.username}`}
                value={reply}
                onChange={(e) => setReply(e.target.value)}
                className="border-none resize-none placeholder:text-muted-foreground bg-transparent p-0 focus-visible:ring-0"
                rows={3}
              />
              
              <div className="flex justify-end mt-3">
                <Button
                  onClick={handleReply}
                  disabled={!reply.trim()}
                  className="trenches-button-primary disabled:opacity-50"
                >
                  Reply
                </Button>
              </div>
            </div>
          </div>
        </div>
      )}

      {/* Replies */}
      <div>
        {mockReplies.map((replyPost) => (
          <div key={replyPost.id} className="border-l-2 border-trenches-green-light ml-6">
            <PostCard post={replyPost} />
          </div>
        ))}
        
        {mockReplies.length === 0 && (
          <div className="p-8 text-center text-muted-foreground">
            <p>No replies yet</p>
            <p className="text-sm">Be the first to reply!</p>
          </div>
        )}
      </div>
    </Layout>
  );
};

export default PostDetail;