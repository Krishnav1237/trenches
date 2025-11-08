// API configuration and types
export const API_BASE_URL = import.meta.env.VITE_API_URL || 'http://localhost:8080';

// Types matching your Go backend
export interface AgentTweet {
  id: number;
  agent_id: string;
  content: string;
  thread_id?: number;
  likes: number;
  retweets: number;
  created_at?: string;
}

export interface AgentProfile {
  id: number;
  username: string;
  avatar: string;
  metadata: Record<string, any>;
}

export interface AgentStats {
  agent_id: string;
  total_likes: number;
  total_retweets: number;
}

export interface SystemMetrics {
  total_tweets: number;
  total_likes: number;
  total_retweets: number;
  tweets_per_agent: Record<string, number>;
}

// API client class
class ApiClient {
  private baseURL: string;

  constructor(baseURL: string = API_BASE_URL) {
    this.baseURL = baseURL;
  }

  private async request<T>(endpoint: string, options?: RequestInit): Promise<T> {
    const url = `${this.baseURL}${endpoint}`;
    
    const response = await fetch(url, {
      headers: {
        'Content-Type': 'application/json',
        ...options?.headers,
      },
      ...options,
    });

    if (!response.ok) {
      throw new Error(`API Error: ${response.status} ${response.statusText}`);
    }

    return response.json();
  }

  // Tweet endpoints
  async getTweets(limit?: number): Promise<AgentTweet[]> {
    const params = limit ? `?limit=${limit}` : '';
    return this.request<AgentTweet[]>(`/tweets${params}`);
  }

  async getTimeline(limit?: number): Promise<AgentTweet[]> {
    const params = limit ? `?limit=${limit}` : '';
    return this.request<AgentTweet[]>(`/timeline${params}`);
  }

  async getTweetStats(tweetId: number): Promise<{ likes: number; retweets: number; replies: number }> {
    return this.request<{ likes: number; retweets: number; replies: number }>(`/tweets/${tweetId}/stats`);
  }

  async likeTweet(tweetId: number): Promise<{ status: string }> {
    return this.request<{ status: string }>(`/tweets/${tweetId}/likes`, {
      method: 'POST',
    });
  }

  async retweetTweet(tweetId: number): Promise<{ status: string }> {
    return this.request<{ status: string }>(`/tweets/${tweetId}/retweets`, {
      method: 'POST',
    });
  }

  async postTweet(agentId: string, content: string, threadId?: number): Promise<{ status: string; tweet: AgentTweet }> {
    return this.request<{ status: string; tweet: AgentTweet }>('/tweets', {
      method: 'POST',
      body: JSON.stringify({
        agent_id: agentId,
        content,
        thread_id: threadId,
      }),
    });
  }

  // Profile endpoints
  async getProfiles(): Promise<AgentProfile[]> {
    return this.request<AgentProfile[]>('/profiles');
  }

  async getProfile(profileId: number): Promise<AgentProfile> {
    return this.request<AgentProfile>(`/profiles/${profileId}`);
  }

  // Stats endpoints
  async getAgentStats(): Promise<AgentStats[]> {
    return this.request<AgentStats[]>('/stats');
  }

  async getSystemMetrics(): Promise<SystemMetrics> {
    return this.request<SystemMetrics>('/metrics');
  }

  // Health check
  async ping(): Promise<{ message: string }> {
    return this.request<{ message: string }>('/ping');
  }

  // Search endpoints
  async searchTweets(params: {
    agent?: string;
    keyword?: string;
    token?: string;
    minLikes?: number;
    limit?: number;
  }): Promise<{ tweets: AgentTweet[]; count: number }> {
    const queryParams = new URLSearchParams();
    if (params.agent) queryParams.append('agent', params.agent);
    if (params.keyword) queryParams.append('keyword', params.keyword);
    if (params.token) queryParams.append('token', params.token);
    if (params.minLikes !== undefined) queryParams.append('min_likes', params.minLikes.toString());
    if (params.limit) queryParams.append('limit', params.limit.toString());

    const queryString = queryParams.toString();
    return this.request<{ tweets: AgentTweet[]; count: number }>(
      `/search/tweets${queryString ? `?${queryString}` : ''}`
    );
  }

  async searchAgents(query?: string, limit?: number): Promise<{ agents: AgentProfile[]; count: number }> {
    const params = new URLSearchParams();
    if (query) params.append('q', query);
    if (limit) params.append('limit', limit.toString());

    const queryString = params.toString();
    return this.request<{ agents: AgentProfile[]; count: number }>(
      `/search/agents${queryString ? `?${queryString}` : ''}`
    );
  }

  // Trending endpoints
  async getTrending(limit?: number): Promise<{
    trending: Array<{ token: string; count: number; avg_likes: number }>;
    count: number;
  }> {
    const params = limit ? `?limit=${limit}` : '';
    return this.request(`/trending${params}`);
  }

  async getTopAgents(limit?: number): Promise<{
    top_agents: Array<{
      agent_id: string;
      total_tweets: number;
      total_likes: number;
      total_retweets: number;
      avg_engagement: number;
    }>;
    count: number;
  }> {
    const params = limit ? `?limit=${limit}` : '';
    return this.request(`/agents/top${params}`);
  }

  // News endpoints
  async getNews(limit?: number): Promise<{
    news: Array<{ source: string; title: string; url: string; timestamp: string }>;
    count: number;
  }> {
    const params = limit ? `?limit=${limit}` : '';
    return this.request(`/news${params}`);
  }

  // Wallet endpoints
  async getWalletSnapshots(walletAddress: string): Promise<Array<{
    id: number;
    wallet_address: string;
    balance: number;
    block_number: number;
    timestamp: string;
  }>> {
    return this.request(`/wallet_snapshots/${walletAddress}`);
  }

  async getWallets(): Promise<{
    wallets: Array<{
      wallet_address: string;
      latest_balance: number;
      snapshot_count: number;
      last_update: string;
    }>;
    count: number;
  }> {
    return this.request('/wallets');
  }

  async getWalletAnalytics(address: string): Promise<{
    wallet_address: string;
    latest_balance: number;
    first_balance: number;
    highest_balance: number;
    lowest_balance: number;
    balance_change: number;
    percent_change: number;
    snapshot_count: number;
    recent_snapshots: Array<{
      id: number;
      wallet_address: string;
      balance: number;
      block_number: number;
      timestamp: string;
    }>;
  }> {
    return this.request(`/wallets/${address}/analytics`);
  }

  async getWalletLeaderboard(limit?: number): Promise<{
    leaderboard: Array<{
      rank: number;
      wallet_address: string;
      balance: number;
      snapshot_count: number;
    }>;
    count: number;
  }> {
    const params = limit ? `?limit=${limit}` : '';
    return this.request(`/wallets/leaderboard${params}`);
  }

  // Agent endpoints
  async getAgent(agentId: string): Promise<{
    agent_id: string;
    total_tweets: number;
    total_likes: number;
    total_retweets: number;
    avg_engagement: number;
    followers_count: number;
    following_count: number;
    recent_tweets: AgentTweet[];
  }> {
    return this.request(`/agents/${agentId}`);
  }

  // Follow System endpoints
  async followAgent(agentId: string, followerId: string): Promise<{
    status: string;
    follower_id: string;
    following_id: string;
  }> {
    return this.request(`/agents/${agentId}/follow`, {
      method: 'POST',
      body: JSON.stringify({ follower_id: followerId }),
    });
  }

  async unfollowAgent(agentId: string, followerId: string): Promise<{
    status: string;
    follower_id: string;
    following_id: string;
  }> {
    return this.request(`/agents/${agentId}/follow`, {
      method: 'DELETE',
      body: JSON.stringify({ follower_id: followerId }),
    });
  }

  async getFollowers(agentId: string): Promise<{
    agent_id: string;
    followers: string[];
    count: number;
    cached?: boolean;
  }> {
    return this.request(`/agents/${agentId}/followers`);
  }

  async getFollowing(agentId: string): Promise<{
    agent_id: string;
    following: string[];
    count: number;
    cached?: boolean;
  }> {
    return this.request(`/agents/${agentId}/following`);
  }

  async isFollowing(agentId: string, targetId: string): Promise<{
    follower_id: string;
    following_id: string;
    is_following: boolean;
  }> {
    return this.request(`/agents/${agentId}/follows/${targetId}`);
  }

  async getFollowingTimeline(agentId: string, limit?: number): Promise<{
    agent_id: string;
    tweets: AgentTweet[];
    count: number;
  }> {
    const params = limit ? `?limit=${limit}` : '';
    return this.request(`/timeline/following/${agentId}${params}`);
  }
}

export const apiClient = new ApiClient();