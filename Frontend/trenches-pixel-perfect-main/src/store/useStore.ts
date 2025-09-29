import { create } from 'zustand';
import { apiClient, AgentTweet, AgentProfile, SystemMetrics } from '@/lib/api';

export interface User {
  id: string;
  username: string;
  displayName: string;
  avatar: string;
  bio?: string;
  followers: number;
  following: number;
  postsCount: number;
  verified?: boolean;
}

// Unified post interface that works for both mobile and desktop
export interface Post {
  id: string;
  user: User;
  content: string;
  timestamp: string;
  likes: number;
  reposts: number;
  comments: number;
  shares: number;
  image?: string;
  isLiked?: boolean;
  isReposted?: boolean;
  replyTo?: string;
  agentId?: string; // Link to agent system
}

// Simplified post for mobile components that just use basic fields
export interface MobilePost {
  id: string;
  author: string;
  content: string;
  timestamp: string;
  likes: number;
  user: User; // Add missing user property
  reposts: number; // Add missing reposts property
  comments: number; // Add missing comments property  
  shares: number; // Add missing shares property
  isLiked?: boolean; // Add missing isLiked property
  isReposted?: boolean; // Add missing isReposted property
  agentId: string;
}

export interface Notification {
  id: string;
  type: 'like' | 'repost' | 'comment' | 'follow' | 'mention';
  user: User;
  post?: Post;
  timestamp: string;
  read: boolean;
}

interface AppState {
  currentUser: User | null;
  posts: MobilePost[];
  notifications: Notification[];
  searchQuery: string;
  darkMode: boolean;
  systemMetrics: SystemMetrics | null;
  isLoading: boolean;
  
  // Actions
  setCurrentUser: (user: User) => void;
  setPosts: (posts: MobilePost[]) => void;
  addPost: (post: MobilePost) => void;
  likePost: (postId: string) => void;
  repostPost: (postId: string) => void;
  setNotifications: (notifications: Notification[]) => void;
  setSearchQuery: (query: string) => void;
  toggleDarkMode: () => void;
  setSystemMetrics: (metrics: SystemMetrics) => void;
  setLoading: (loading: boolean) => void;
  
  // API integration actions
  fetchTweets: () => Promise<void>;
  fetchSystemMetrics: () => Promise<void>;
  refreshData: () => Promise<void>;
}

// Import pixel art profile pictures
import pfp1 from '@/assets/pfp1.png';
import pfp2 from '@/assets/pfp2.png';
import pfp3 from '@/assets/pfp3.png';
import pfp4 from '@/assets/pfp4.png';
import pfp5 from '@/assets/pfp5.png';
import pfp6 from '@/assets/pfp6.png';

// Current user (can be set later)
const currentUser: User | null = null;

// Helper function to convert AgentTweet to MobilePost
const convertAgentTweetToMobilePost = (tweet: AgentTweet): MobilePost => {
  // Generate clean display name from agent_id
  const cleanName = tweet.agent_id
    .replace('agent_', '')
    .replace(/_/g, ' ')
    .replace(/\b\w/g, l => l.toUpperCase());

  // Create a user object for the agent
  const agentUser: User = {
    id: tweet.agent_id,
    username: tweet.agent_id.toLowerCase(),
    displayName: cleanName,
    avatar: '', // Will be generated in component
    followers: Math.floor(Math.random() * 10000),
    following: Math.floor(Math.random() * 1000),
    postsCount: Math.floor(Math.random() * 500),
    verified: true
  };

  return {
    id: tweet.id.toString(),
    author: cleanName,
    content: tweet.content,
    timestamp: tweet.created_at || new Date().toISOString(),
    likes: tweet.likes,
    user: agentUser,
    reposts: tweet.retweets || Math.floor(Math.random() * 50),
    comments: Math.floor(Math.random() * 25),
    shares: Math.floor(Math.random() * 10),
    isLiked: false,
    isReposted: false,
    agentId: tweet.agent_id,
  };
};

export const useStore = create<AppState>((set, get) => ({
  currentUser: currentUser,
  posts: [],
  notifications: [],
  searchQuery: '',
  darkMode: false,
  systemMetrics: null,
  isLoading: false,

  setCurrentUser: (user) => set({ currentUser: user }),
  
  setPosts: (posts) => set({ posts }),
  
  addPost: (post) => set((state) => ({ posts: [post, ...state.posts] })),
  
  likePost: async (postId) => {
    const state = get();
    const post = state.posts.find(p => p.id === postId);
    
    if (post?.agentId) {
      try {
        await apiClient.likeTweet(parseInt(postId));
      } catch (error) {
        console.error('Failed to like tweet:', error);
      }
    }
    
    set((state) => ({
      posts: state.posts.map(post => 
        post.id === postId 
          ? { ...post, likes: post.isLiked ? post.likes - 1 : post.likes + 1, isLiked: !post.isLiked }
          : post
      )
    }));
  },
  
  repostPost: async (postId) => {
    const state = get();
    const post = state.posts.find(p => p.id === postId);
    
    if (post?.agentId) {
      try {
        await apiClient.retweetTweet(parseInt(postId));
      } catch (error) {
        console.error('Failed to retweet:', error);
      }
    }
    
    set((state) => ({
      posts: state.posts.map(post => 
        post.id === postId 
          ? { ...post, reposts: post.isReposted ? post.reposts - 1 : post.reposts + 1, isReposted: !post.isReposted }
          : post
      )
    }));
  },
  
  setNotifications: (notifications) => set({ notifications }),
  
  setSearchQuery: (query) => set({ searchQuery: query }),
  
  toggleDarkMode: () => set((state) => ({ darkMode: !state.darkMode })),
  
  setSystemMetrics: (metrics) => set({ systemMetrics: metrics }),
  
  setLoading: (loading) => set({ isLoading: loading }),

  // API integration methods
  fetchTweets: async () => {
    set({ isLoading: true });
    try {
      const tweets = await apiClient.getTimeline(50); // Get latest 50 tweets
      const posts = tweets.map(tweet => convertAgentTweetToMobilePost(tweet));
      set({ posts });
    } catch (error) {
      console.error('Failed to fetch tweets:', error);
      // No fallback - just show empty state
      set({ posts: [] });
    } finally {
      set({ isLoading: false });
    }
  },

  fetchSystemMetrics: async () => {
    try {
      const metrics = await apiClient.getSystemMetrics();
      set({ systemMetrics: metrics });
    } catch (error) {
      console.error('Failed to fetch system metrics:', error);
    }
  },

  refreshData: async () => {
    const { fetchTweets, fetchSystemMetrics } = get();
    await Promise.all([
      fetchTweets(),
      fetchSystemMetrics()
    ]);
  },
}));