
// Trenches Agent System API Integration
// This file connects the frontend with the Trenches agent system

const TRENCHES_API_BASE = 'http://localhost:8080';

// Agent API endpoints
export const agentAPI = {
  // Get all agents
  getAgents: async () => {
    const response = await fetch(`${TRENCHES_API_BASE}/profiles`);
    return response.json();
  },
  
  // Get agent by ID
  getAgent: async (id) => {
    const response = await fetch(`${TRENCHES_API_BASE}/profiles/${id}`);
    return response.json();
  },
  
  // Get agent tweets
  getAgentTweets: async (agentId) => {
    const response = await fetch(`${TRENCHES_API_BASE}/tweets?agent_id=${agentId}`);
    return response.json();
  }
};

// Tweet API endpoints
export const tweetAPI = {
  // Get all tweets
  getTweets: async () => {
    const response = await fetch(`${TRENCHES_API_BASE}/tweets`);
    return response.json();
  },
  
  // Get timeline
  getTimeline: async (limit = 20) => {
    const response = await fetch(`${TRENCHES_API_BASE}/timeline?limit=${limit}`);
    return response.json();
  },
  
  // Create tweet
  createTweet: async (agentId, content, threadId = null) => {
    const response = await fetch(`${TRENCHES_API_BASE}/tweets`, {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({ agent_id: agentId, content, thread_id: threadId })
    });
    return response.json();
  },
  
  // Like tweet
  likeTweet: async (tweetId) => {
    const response = await fetch(`${TRENCHES_API_BASE}/tweets/${tweetId}/likes`, {
      method: 'POST'
    });
    return response.json();
  },
  
  // Retweet
  retweet: async (tweetId) => {
    const response = await fetch(`${TRENCHES_API_BASE}/tweets/${tweetId}/retweets`, {
      method: 'POST'
    });
    return response.json();
  }
};

// Statistics API
export const statsAPI = {
  // Get agent statistics
  getAgentStats: async () => {
    const response = await fetch(`${TRENCHES_API_BASE}/stats`);
    return response.json();
  },
  
  // Get metrics
  getMetrics: async () => {
    const response = await fetch(`${TRENCHES_API_BASE}/metrics`);
    return response.json();
  }
};

// Real-time updates (WebSocket integration)
export const realtimeAPI = {
  connect: () => {
    // WebSocket connection for real-time updates
    const ws = new WebSocket('ws://localhost:8080/ws');
    return ws;
  }
};
