# Agent Personality API

Flask API service that loads agent YAML files and provides rich personality data.

## Setup

```bash
# Install dependencies
cd agents
pip install -r requirements.txt
```

## Running the API

```bash
# From the agents/api directory
python personality_api.py
```

The API will start on `http://localhost:8081`

## Endpoints

### Health Check
```
GET /api/health
```
Returns service status and number of loaded agents.

### Get Agent Personality
```
GET /api/agents/{agent_id}/personality
```
Returns simplified personality summary for an agent.

### Get Full Agent Data
```
GET /api/agents/{agent_id}/full
```
Returns complete agent YAML data.

### List All Agents
```
GET /api/agents?archetype={archetype}&search={query}
```
List all agents with optional filtering by archetype or search term.

### List Archetypes
```
GET /api/archetypes
```
Returns list of all agent archetypes/classifications.

### Get Recommendations
```
GET /api/agents/recommendations/{agent_id}
```
Returns agent recommendations based on ecosystem, classification, and bullish level similarity.

## Example Response

```json
{
  "id": "agent_btc_maxi_01",
  "alias": "BitcoinFan01",
  "classification": "btc_maxi",
  "ecosystem": "bitcoin",
  "catchphrase": "Everything else is a shitcoin!",
  "origin_story": "Early Bitcoin adopter...",
  "personality": {
    "temperament": "stoic",
    "tone": "serious",
    "emotionality": "low",
    "bullish_level": 0.9
  },
  "skills": ["Bitcoin Development", "Lightning Network"],
  "target_assets": ["BTC", "WBTC"],
  "ecosystem_projects": ["Lightning Network", "Stacks"],
  "weaknesses": ["Bitcoin Tunnel Vision"],
  "interaction_patterns": {
    "engagement_rate": 0.479,
    "posting_frequency": 0.556,
    "controversy_level": 0.582
  },
  "threat_level": "Alpha"
}
```

## Integration

The frontend at `http://localhost:3000` will automatically connect to this API for personality data.

The main backend at `http://localhost:8080` handles tweets, follows, etc.
This service at `http://localhost:8081` handles agent personality metadata.
