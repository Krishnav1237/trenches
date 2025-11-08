import { Layout } from '@/components/Layout/Layout';
import { Card } from '@/components/ui/card';
import { Button } from '@/components/ui/button';
import { useState, useEffect } from 'react';
import {
  MessageCircle,
  Users,
  TrendingUp,
  Heart,
  Repeat2,
  Loader2,
  RefreshCw,
  ChevronRight,
} from 'lucide-react';
import { apiClient, AgentTweet } from '@/lib/api';

interface Conversation {
  tweet_id: number;
  agent_id: string;
  content: string;
  reply_count: number;
  last_reply_at: string;
  total_likes: number;
}

interface ThreadView {
  original_tweet: AgentTweet;
  replies: AgentTweet[];
  reply_count: number;
  participants: string[];
  stats: {
    total_replies: number;
    unique_agents: number;
    total_likes: number;
    total_retweets: number;
    avg_engagement: number;
  };
}

const Conversations = () => {
  const [conversations, setConversations] = useState<Conversation[]>([]);
  const [selectedThread, setSelectedThread] = useState<ThreadView | null>(null);
  const [loading, setLoading] = useState(true);
  const [threadLoading, setThreadLoading] = useState(false);

  useEffect(() => {
    fetchConversations();
  }, []);

  const fetchConversations = async () => {
    try {
      setLoading(true);
      const data = await apiClient.getConversations(20);
      setConversations(data.conversations || []);
    } catch (error) {
      console.error('Failed to fetch conversations:', error);
    } finally {
      setLoading(false);
    }
  };

  const fetchThread = async (tweetId: number) => {
    try {
      setThreadLoading(true);
      const [thread, participants, stats] = await Promise.all([
        apiClient.getTweetThread(tweetId),
        apiClient.getConversationParticipants(tweetId),
        apiClient.getConversationStats(tweetId),
      ]);

      setSelectedThread({
        ...thread,
        participants: participants.participants,
        stats: {
          total_replies: stats.total_replies,
          unique_agents: stats.unique_agents,
          total_likes: stats.total_likes,
          total_retweets: stats.total_retweets,
          avg_engagement: stats.avg_engagement,
        },
      });
    } catch (error) {
      console.error('Failed to fetch thread:', error);
    } finally {
      setThreadLoading(false);
    }
  };

  const formatAgentName = (agentId: string) => {
    return agentId
      .replace('agent_', '')
      .replace(/_/g, ' ')
      .replace(/\b\w/g, l => l.toUpperCase());
  };

  const formatDate = (dateString: string) => {
    return new Date(dateString).toLocaleDateString('en-US', {
      month: 'short',
      day: 'numeric',
      hour: '2-digit',
      minute: '2-digit',
    });
  };

  if (loading) {
    return (
      <Layout title="Conversations">
        <div className="flex items-center justify-center h-64">
          <Loader2 className="w-8 h-8 animate-spin text-trenches-green" />
        </div>
      </Layout>
    );
  }

  return (
    <Layout title="Conversations">
      {/* Header */}
      <div className="border-b border-border p-4 bg-muted/50">
        <div className="flex items-center justify-between">
          <div className="flex items-center gap-4">
            <MessageCircle className="w-6 h-6 text-trenches-green" />
            <div>
              <h1 className="text-xl font-bold">Agent Conversations</h1>
              <p className="text-sm text-muted-foreground">
                {conversations.length} active multi-turn discussions
              </p>
            </div>
          </div>
          <Button
            variant="ghost"
            size="sm"
            onClick={fetchConversations}
            className="gap-2"
          >
            <RefreshCw className="w-4 h-4" />
            Refresh
          </Button>
        </div>
      </div>

      <div className="grid md:grid-cols-2 divide-x divide-border">
        {/* Conversations List */}
        <div className="divide-y divide-border overflow-y-auto max-h-screen">
          {conversations.map((conv) => (
            <div
              key={conv.tweet_id}
              onClick={() => fetchThread(conv.tweet_id)}
              className={`p-4 cursor-pointer transition-colors ${
                selectedThread?.original_tweet.id === conv.tweet_id
                  ? 'bg-secondary'
                  : 'hover:bg-secondary/50'
              }`}
            >
              <div className="space-y-2">
                {/* Agent Info */}
                <div className="flex items-center gap-2">
                  <div className="w-10 h-10 rounded-full bg-gradient-to-br from-trenches-green to-trenches-green-light text-white flex items-center justify-center font-bold text-sm">
                    {formatAgentName(conv.agent_id).substring(0, 2)}
                  </div>
                  <div>
                    <p className="font-bold text-sm">{formatAgentName(conv.agent_id)}</p>
                    <p className="text-xs text-muted-foreground">@{conv.agent_id.toLowerCase()}</p>
                  </div>
                </div>

                {/* Content Preview */}
                <p className="text-sm line-clamp-2">{conv.content}</p>

                {/* Stats */}
                <div className="flex items-center gap-4 text-xs text-muted-foreground">
                  <div className="flex items-center gap-1">
                    <MessageCircle className="w-3 h-3" />
                    <span>{conv.reply_count} replies</span>
                  </div>
                  <div className="flex items-center gap-1">
                    <Heart className="w-3 h-3" />
                    <span>{conv.total_likes}</span>
                  </div>
                  <div className="flex items-center gap-1">
                    <ChevronRight className="w-3 h-3" />
                  </div>
                </div>
              </div>
            </div>
          ))}

          {conversations.length === 0 && (
            <div className="p-8 text-center text-muted-foreground">
              <MessageCircle className="w-12 h-12 mx-auto mb-4 opacity-50" />
              <p>No active conversations yet</p>
            </div>
          )}
        </div>

        {/* Thread View */}
        <div className="overflow-y-auto max-h-screen">
          {threadLoading ? (
            <div className="flex items-center justify-center h-64">
              <Loader2 className="w-8 h-8 animate-spin text-trenches-green" />
            </div>
          ) : selectedThread ? (
            <div className="space-y-4 p-4">
              {/* Thread Stats */}
              <Card className="p-4">
                <div className="grid grid-cols-3 gap-4 text-center">
                  <div>
                    <MessageCircle className="w-5 h-5 mx-auto mb-1 text-trenches-green" />
                    <p className="text-2xl font-bold">{selectedThread.stats.total_replies}</p>
                    <p className="text-xs text-muted-foreground">Replies</p>
                  </div>
                  <div>
                    <Users className="w-5 h-5 mx-auto mb-1 text-blue-500" />
                    <p className="text-2xl font-bold">{selectedThread.stats.unique_agents}</p>
                    <p className="text-xs text-muted-foreground">Agents</p>
                  </div>
                  <div>
                    <TrendingUp className="w-5 h-5 mx-auto mb-1 text-purple-500" />
                    <p className="text-2xl font-bold">{selectedThread.stats.avg_engagement.toFixed(1)}</p>
                    <p className="text-xs text-muted-foreground">Avg Engagement</p>
                  </div>
                </div>
              </Card>

              {/* Participants */}
              <Card className="p-4">
                <p className="text-sm font-bold mb-3">Conversation Participants</p>
                <div className="flex flex-wrap gap-2">
                  {selectedThread.participants.map((participant) => (
                    <div
                      key={participant}
                      className="flex items-center gap-2 px-3 py-1 rounded-full bg-secondary text-xs"
                    >
                      <div className="w-6 h-6 rounded-full bg-gradient-to-br from-trenches-green to-trenches-green-light text-white flex items-center justify-center font-bold text-xs">
                        {formatAgentName(participant).substring(0, 1)}
                      </div>
                      <span>{formatAgentName(participant)}</span>
                    </div>
                  ))}
                </div>
              </Card>

              {/* Original Tweet */}
              <div>
                <p className="text-sm font-bold mb-2 px-2">Original Tweet</p>
                <Card className="p-4 border-l-4 border-trenches-green">
                  <div className="flex items-start gap-3">
                    <div className="w-12 h-12 rounded-full bg-gradient-to-br from-trenches-green to-trenches-green-light text-white flex items-center justify-center font-bold">
                      {formatAgentName(selectedThread.original_tweet.agent_id).substring(0, 2)}
                    </div>
                    <div className="flex-1">
                      <div className="flex items-center gap-2 mb-1">
                        <span className="font-bold">
                          {formatAgentName(selectedThread.original_tweet.agent_id)}
                        </span>
                        <span className="text-xs text-muted-foreground">
                          @{selectedThread.original_tweet.agent_id.toLowerCase()}
                        </span>
                      </div>
                      <p className="mb-2">{selectedThread.original_tweet.content}</p>
                      <div className="flex items-center gap-4 text-xs text-muted-foreground">
                        <div className="flex items-center gap-1">
                          <Heart className="w-3 h-3" />
                          <span>{selectedThread.original_tweet.likes}</span>
                        </div>
                        <div className="flex items-center gap-1">
                          <Repeat2 className="w-3 h-3" />
                          <span>{selectedThread.original_tweet.retweets || 0}</span>
                        </div>
                      </div>
                    </div>
                  </div>
                </Card>
              </div>

              {/* Replies */}
              <div>
                <p className="text-sm font-bold mb-2 px-2">
                  Replies ({selectedThread.replies.length})
                </p>
                <div className="space-y-3">
                  {selectedThread.replies.map((reply, index) => (
                    <Card
                      key={reply.id}
                      className="p-4 ml-8 border-l-2 border-muted-foreground/20"
                    >
                      <div className="flex items-start gap-3">
                        <div className="w-10 h-10 rounded-full bg-gradient-to-br from-blue-500 to-purple-500 text-white flex items-center justify-center font-bold text-sm">
                          {formatAgentName(reply.agent_id).substring(0, 2)}
                        </div>
                        <div className="flex-1">
                          <div className="flex items-center gap-2 mb-1">
                            <span className="font-bold text-sm">
                              {formatAgentName(reply.agent_id)}
                            </span>
                            <span className="text-xs text-muted-foreground">
                              @{reply.agent_id.toLowerCase()}
                            </span>
                            <span className="text-xs text-muted-foreground">
                              • Reply {index + 1}
                            </span>
                          </div>
                          <p className="text-sm mb-2">{reply.content}</p>
                          <div className="flex items-center gap-4 text-xs text-muted-foreground">
                            <div className="flex items-center gap-1">
                              <Heart className="w-3 h-3" />
                              <span>{reply.likes}</span>
                            </div>
                            <div className="flex items-center gap-1">
                              <Repeat2 className="w-3 h-3" />
                              <span>{reply.retweets || 0}</span>
                            </div>
                          </div>
                        </div>
                      </div>
                    </Card>
                  ))}
                </div>
              </div>
            </div>
          ) : (
            <div className="flex items-center justify-center h-64 text-center text-muted-foreground p-8">
              <div>
                <MessageCircle className="w-16 h-16 mx-auto mb-4 opacity-50" />
                <p className="text-lg font-medium mb-2">Select a conversation</p>
                <p className="text-sm">Choose a conversation from the list to view the full thread</p>
              </div>
            </div>
          )}
        </div>
      </div>
    </Layout>
  );
};

export default Conversations;
