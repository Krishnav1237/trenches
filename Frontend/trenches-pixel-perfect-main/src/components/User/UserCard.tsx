import { Button } from '@/components/ui/button';
import { User } from '@/store/useStore';
import { Link } from 'react-router-dom';

interface UserCardProps {
  user: User;
  showBio?: boolean;
  showFollowButton?: boolean;
}

export const UserCard = ({ user, showBio = true, showFollowButton = true }: UserCardProps) => {
  return (
    <div className="trenches-card">
      <div className="flex items-start gap-3">
        <Link to={`/profile/${user.username}`}>
          <img
            src={user.avatar}
            alt={user.displayName}
            className="trenches-avatar w-12 h-12"
          />
        </Link>
        
        <div className="flex-1 min-w-0">
          <div className="flex items-center justify-between">
            <div>
              <Link 
                to={`/profile/${user.username}`}
                className="flex items-center gap-1 hover:underline"
              >
                <h3 className="font-bold truncate">{user.displayName}</h3>
                {user.verified && (
                  <div className="w-4 h-4 bg-trenches-green rounded-full flex items-center justify-center flex-shrink-0">
                    <span className="text-white text-xs">✓</span>
                  </div>
                )}
              </Link>
              <p className="text-muted-foreground text-sm">@{user.username}</p>
            </div>
            
            {showFollowButton && (
              <Button size="sm" className="trenches-button-primary">
                Follow
              </Button>
            )}
          </div>
          
          {showBio && user.bio && (
            <p className="text-sm mt-2 text-foreground">{user.bio}</p>
          )}
          
          <div className="flex gap-4 mt-3 text-sm">
            <span className="text-muted-foreground">
              <span className="font-semibold text-foreground">{user.following.toLocaleString()}</span> Following
            </span>
            <span className="text-muted-foreground">
              <span className="font-semibold text-foreground">{user.followers.toLocaleString()}</span> Followers
            </span>
          </div>
        </div>
      </div>
    </div>
  );
};