import { Layout } from '@/components/Layout/Layout';
import { useState, useEffect } from 'react';
import { apiClient } from '@/lib/api';
import { Button } from '@/components/ui/button';
import { Input } from '@/components/ui/input';
import { Send, Loader2, MessageCircle } from 'lucide-react';
import { Link } from 'react-router-dom';
import { useToast } from '@/hooks/use-toast';

interface Conversation {
  conversation_id: number;
  other_user_id: number;
  other_username: string;
  other_display_name: string;
  other_avatar: string;
  last_message: string;
  last_message_at: string;
  unread_count: number;
}

interface Message {
  id: number;
  conversation_id: number;
  sender_id: number;
  content: string;
  read: boolean;
  created_at: string;
}

const Messages = () => {
  const [conversations, setConversations] = useState<Conversation[]>([]);
  const [selectedConversation, setSelectedConversation] = useState<Conversation | null>(null);
  const [messages, setMessages] = useState<Message[]>([]);
  const [newMessage, setNewMessage] = useState('');
  const [loading, setLoading] = useState(true);
  const [loadingMessages, setLoadingMessages] = useState(false);
  const [sending, setSending] = useState(false);
  const { toast } = useToast();

  useEffect(() => {
    fetchConversations();
  }, []);

  useEffect(() => {
    if (selectedConversation) {
      fetchMessages(selectedConversation.other_user_id);
    }
  }, [selectedConversation]);

  const fetchConversations = async () => {
    try {
      setLoading(true);
      const data = await apiClient.getConversationsList();
      setConversations(data.conversations || []);
    } catch (error) {
      console.error('Failed to fetch conversations:', error);
      toast({
        title: 'Error',
        description: 'Failed to load conversations',
        variant: 'destructive',
      });
    } finally {
      setLoading(false);
    }
  };

  const fetchMessages = async (userId: number) => {
    try {
      setLoadingMessages(true);
      const data = await apiClient.getConversationMessages(userId);
      setMessages(data.messages || []);
    } catch (error) {
      console.error('Failed to fetch messages:', error);
      toast({
        title: 'Error',
        description: 'Failed to load messages',
        variant: 'destructive',
      });
    } finally {
      setLoadingMessages(false);
    }
  };

  const handleSendMessage = async () => {
    if (!newMessage.trim() || !selectedConversation || sending) return;

    try {
      setSending(true);
      await apiClient.sendMessage(selectedConversation.other_user_id, newMessage);
      setNewMessage('');
      await fetchMessages(selectedConversation.other_user_id);
      await fetchConversations();
    } catch (error) {
      console.error('Failed to send message:', error);
      toast({
        title: 'Error',
        description: 'Failed to send message',
        variant: 'destructive',
      });
    } finally {
      setSending(false);
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

  const getCurrentUserId = (): number => {
    // This would come from auth context
    // For now, we'll use a placeholder
    return 1;
  };

  if (loading) {
    return (
      <Layout title="Messages" showSearch={false}>
        <div className="flex items-center justify-center h-64">
          <Loader2 className="w-8 h-8 animate-spin text-trenches-green" />
        </div>
      </Layout>
    );
  }

  return (
    <Layout title="Messages" showSearch={false}>
      <div className="flex h-[calc(100vh-53px)]">
        {/* Conversations List */}
        <div className="w-full md:w-96 border-r border-border overflow-y-auto">
          {conversations.length > 0 ? (
            conversations.map((conversation) => (
              <div
                key={conversation.conversation_id}
                onClick={() => setSelectedConversation(conversation)}
                className={`flex items-start gap-3 p-4 border-b border-border hover:bg-secondary/50 cursor-pointer transition-colors ${
                  selectedConversation?.conversation_id === conversation.conversation_id
                    ? 'bg-secondary/50'
                    : ''
                }`}
              >
                <Link to={`/profile/${conversation.other_username}`}>
                  <img
                    src={conversation.other_avatar}
                    alt={conversation.other_display_name}
                    className="trenches-avatar w-12 h-12"
                  />
                </Link>
                <div className="flex-1 min-w-0">
                  <div className="flex items-center justify-between mb-1">
                    <div className="flex items-center gap-2">
                      <span className="font-semibold truncate">
                        {conversation.other_display_name}
                      </span>
                      {conversation.unread_count > 0 && (
                        <span className="bg-trenches-green text-white text-xs px-2 py-0.5 rounded-full">
                          {conversation.unread_count}
                        </span>
                      )}
                    </div>
                    <span className="text-xs text-muted-foreground">
                      {formatTimeAgo(conversation.last_message_at)}
                    </span>
                  </div>
                  <p className="text-sm text-muted-foreground truncate">
                    @{conversation.other_username}
                  </p>
                  <p className="text-sm text-muted-foreground truncate mt-1">
                    {conversation.last_message}
                  </p>
                </div>
              </div>
            ))
          ) : (
            <div className="p-8 text-center text-muted-foreground">
              <MessageCircle size={48} className="mx-auto mb-4 opacity-50" />
              <p className="text-lg">No conversations yet</p>
              <p className="text-sm">Start a conversation by sending a message!</p>
            </div>
          )}
        </div>

        {/* Messages View */}
        <div className="hidden md:flex flex-col flex-1">
          {selectedConversation ? (
            <>
              {/* Conversation Header */}
              <div className="flex items-center gap-3 p-4 border-b border-border">
                <Link to={`/profile/${selectedConversation.other_username}`}>
                  <img
                    src={selectedConversation.other_avatar}
                    alt={selectedConversation.other_display_name}
                    className="trenches-avatar w-10 h-10"
                  />
                </Link>
                <div>
                  <p className="font-semibold">{selectedConversation.other_display_name}</p>
                  <p className="text-sm text-muted-foreground">
                    @{selectedConversation.other_username}
                  </p>
                </div>
              </div>

              {/* Messages */}
              <div className="flex-1 overflow-y-auto p-4 space-y-4">
                {loadingMessages ? (
                  <div className="flex items-center justify-center h-full">
                    <Loader2 className="w-8 h-8 animate-spin text-trenches-green" />
                  </div>
                ) : messages.length > 0 ? (
                  messages.map((message) => {
                    const isCurrentUser = message.sender_id === getCurrentUserId();
                    return (
                      <div
                        key={message.id}
                        className={`flex ${isCurrentUser ? 'justify-end' : 'justify-start'}`}
                      >
                        <div
                          className={`max-w-[70%] rounded-2xl px-4 py-2 ${
                            isCurrentUser
                              ? 'bg-trenches-green text-white'
                              : 'bg-secondary text-foreground'
                          }`}
                        >
                          <p className="text-sm break-words">{message.content}</p>
                          <p
                            className={`text-xs mt-1 ${
                              isCurrentUser ? 'text-white/70' : 'text-muted-foreground'
                            }`}
                          >
                            {formatTimeAgo(message.created_at)}
                          </p>
                        </div>
                      </div>
                    );
                  })
                ) : (
                  <div className="flex items-center justify-center h-full text-muted-foreground">
                    <p>No messages yet. Start the conversation!</p>
                  </div>
                )}
              </div>

              {/* Message Input */}
              <div className="p-4 border-t border-border">
                <div className="flex gap-2">
                  <Input
                    type="text"
                    placeholder="Type a message..."
                    value={newMessage}
                    onChange={(e) => setNewMessage(e.target.value)}
                    onKeyPress={(e) => {
                      if (e.key === 'Enter' && !e.shiftKey) {
                        e.preventDefault();
                        handleSendMessage();
                      }
                    }}
                    disabled={sending}
                    className="flex-1"
                  />
                  <Button
                    onClick={handleSendMessage}
                    disabled={!newMessage.trim() || sending}
                    className="bg-trenches-green hover:bg-trenches-green-dark"
                  >
                    {sending ? (
                      <Loader2 className="w-4 h-4 animate-spin" />
                    ) : (
                      <Send className="w-4 h-4" />
                    )}
                  </Button>
                </div>
              </div>
            </>
          ) : (
            <div className="flex items-center justify-center h-full text-muted-foreground">
              <div className="text-center">
                <MessageCircle size={64} className="mx-auto mb-4 opacity-30" />
                <p className="text-lg">Select a conversation</p>
                <p className="text-sm">Choose a conversation from the list to start messaging</p>
              </div>
            </div>
          )}
        </div>
      </div>
    </Layout>
  );
};

export default Messages;
