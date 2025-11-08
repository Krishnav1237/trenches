import { useState, useEffect } from 'react';
import { Button } from '@/components/ui/button';
import { Card } from '@/components/ui/card';
import { Check, Loader2 } from 'lucide-react';
import { apiClient } from '@/lib/api';
import { useToast } from '@/hooks/use-toast';

interface PollOption {
  id: number;
  poll_id: number;
  option_text: string;
  vote_count: number;
  option_index: number;
}

interface Poll {
  id: number;
  tweet_id: number;
  duration_hours: number;
  ends_at: string;
  is_ended: boolean;
  total_votes: number;
  options: PollOption[];
  user_vote?: number;
}

interface PollDisplayProps {
  tweetId: number;
}

export const PollDisplay = ({ tweetId }: PollDisplayProps) => {
  const [poll, setPoll] = useState<Poll | null>(null);
  const [loading, setLoading] = useState(true);
  const [voting, setVoting] = useState(false);
  const { toast } = useToast();

  useEffect(() => {
    fetchPoll();
  }, [tweetId]);

  const fetchPoll = async () => {
    try {
      setLoading(true);
      const data = await apiClient.getPoll(tweetId);
      setPoll(data);
    } catch (error) {
      console.error('Failed to fetch poll:', error);
    } finally {
      setLoading(false);
    }
  };

  const handleVote = async (optionId: number) => {
    if (!poll || poll.is_ended || poll.user_vote !== undefined || voting) return;

    try {
      setVoting(true);
      await apiClient.votePoll(poll.id, optionId);
      await fetchPoll();
      toast({
        title: 'Success',
        description: 'Vote recorded',
      });
    } catch (error) {
      console.error('Failed to vote:', error);
      toast({
        title: 'Error',
        description: 'Failed to record vote',
        variant: 'destructive',
      });
    } finally {
      setVoting(false);
    }
  };

  const getTimeRemaining = (endsAt: string): string => {
    const now = new Date();
    const end = new Date(endsAt);
    const diffMs = end.getTime() - now.getTime();

    if (diffMs <= 0) return 'Poll ended';

    const diffMins = Math.floor(diffMs / 60000);
    const diffHours = Math.floor(diffMins / 60);
    const diffDays = Math.floor(diffHours / 24);

    if (diffDays > 0) return `${diffDays} day${diffDays > 1 ? 's' : ''} left`;
    if (diffHours > 0) return `${diffHours} hour${diffHours > 1 ? 's' : ''} left`;
    if (diffMins > 0) return `${diffMins} minute${diffMins > 1 ? 's' : ''} left`;
    return 'Less than a minute left';
  };

  const getPercentage = (voteCount: number): number => {
    if (!poll || poll.total_votes === 0) return 0;
    return Math.round((voteCount / poll.total_votes) * 100);
  };

  if (loading) {
    return (
      <Card className="p-4">
        <div className="flex items-center justify-center">
          <Loader2 className="w-6 h-6 animate-spin text-trenches-green" />
        </div>
      </Card>
    );
  }

  if (!poll) {
    return null;
  }

  const hasVoted = poll.user_vote !== undefined;
  const showResults = hasVoted || poll.is_ended;

  return (
    <Card className="p-4">
      <div className="space-y-3">
        {poll.options.map((option) => {
          const percentage = getPercentage(option.vote_count);
          const isSelected = poll.user_vote === option.id;

          return (
            <div key={option.id}>
              {showResults ? (
                <div className="relative">
                  <div
                    className="absolute inset-0 bg-trenches-green/20 rounded transition-all"
                    style={{ width: `${percentage}%` }}
                  />
                  <div className="relative flex items-center justify-between p-3 rounded border border-border">
                    <div className="flex items-center gap-2 flex-1">
                      <span className="font-medium">{option.option_text}</span>
                      {isSelected && <Check className="w-4 h-4 text-trenches-green" />}
                    </div>
                    <span className="font-bold text-sm">{percentage}%</span>
                  </div>
                </div>
              ) : (
                <Button
                  variant="outline"
                  className="w-full justify-start p-3 h-auto hover:bg-trenches-green/10"
                  onClick={() => handleVote(option.id)}
                  disabled={voting}
                >
                  {option.option_text}
                </Button>
              )}
            </div>
          );
        })}

        <div className="flex items-center justify-between text-sm text-muted-foreground pt-2">
          <span>{poll.total_votes} vote{poll.total_votes !== 1 ? 's' : ''}</span>
          <span>·</span>
          <span>{getTimeRemaining(poll.ends_at)}</span>
        </div>
      </div>
    </Card>
  );
};
