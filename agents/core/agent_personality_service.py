"""
Agent personality loader service
Loads agent YAML files and provides personality data
"""

import yaml
import os
from pathlib import Path
from typing import Dict, List, Optional
import logging

logger = logging.getLogger(__name__)

class AgentPersonalityService:
    def __init__(self, agent_spec_dir: str = "/home/user/trenches/agents/agent_spec"):
        self.agent_spec_dir = Path(agent_spec_dir)
        self._cache: Dict[str, dict] = {}
        self._load_all_agents()

    def _load_all_agents(self):
        """Load all agent YAML files into cache"""
        if not self.agent_spec_dir.exists():
            logger.warning(f"Agent spec directory not found: {self.agent_spec_dir}")
            return

        for yaml_file in self.agent_spec_dir.glob("*.yaml"):
            try:
                with open(yaml_file, 'r') as f:
                    data = yaml.safe_load(f)
                    if data and 'id' in data:
                        self._cache[data['id']] = data
                        logger.debug(f"Loaded agent: {data['id']}")
            except Exception as e:
                logger.error(f"Failed to load {yaml_file}: {e}")

        logger.info(f"Loaded {len(self._cache)} agent personalities")

    def get_agent_personality(self, agent_id: str) -> Optional[dict]:
        """Get personality data for a specific agent"""
        return self._cache.get(agent_id)

    def get_all_agents(self) -> List[dict]:
        """Get all agent personalities"""
        return list(self._cache.values())

    def get_agents_by_archetype(self, archetype: str) -> List[dict]:
        """Get all agents of a specific archetype/classification"""
        return [
            agent for agent in self._cache.values()
            if agent.get('classification') == archetype
        ]

    def get_archetype_list(self) -> List[str]:
        """Get list of all unique archetypes"""
        archetypes = set()
        for agent in self._cache.values():
            if 'classification' in agent:
                archetypes.add(agent['classification'])
        return sorted(list(archetypes))

    def get_agent_summary(self, agent_id: str) -> Optional[dict]:
        """Get simplified agent summary for API responses"""
        agent = self._cache.get(agent_id)
        if not agent:
            return None

        return {
            'id': agent.get('id'),
            'alias': agent.get('alias'),
            'classification': agent.get('classification'),
            'ecosystem': agent.get('ecosystem'),
            'catchphrase': agent.get('catchphrase'),
            'origin_story': agent.get('origin_story'),
            'personality': {
                'temperament': agent.get('personality', {}).get('temperament'),
                'tone': agent.get('personality', {}).get('tone'),
                'emotionality': agent.get('personality', {}).get('emotionality'),
                'bullish_level': agent.get('personality', {}).get('bullish_level'),
            },
            'skills': agent.get('skills', []),
            'target_assets': agent.get('target_assets', []),
            'ecosystem_projects': agent.get('ecosystem_projects', []),
            'weaknesses': agent.get('weaknesses', []),
            'interaction_patterns': agent.get('interaction_patterns', {}),
            'threat_level': agent.get('threat_level'),
        }

    def search_agents(self, query: str) -> List[dict]:
        """Search agents by name, alias, or classification"""
        query_lower = query.lower()
        results = []

        for agent in self._cache.values():
            if (query_lower in agent.get('id', '').lower() or
                query_lower in agent.get('alias', '').lower() or
                query_lower in agent.get('classification', '').lower()):
                results.append(self.get_agent_summary(agent['id']))

        return results


# Global instance
_service_instance: Optional[AgentPersonalityService] = None

def get_agent_service() -> AgentPersonalityService:
    """Get or create the global agent personality service instance"""
    global _service_instance
    if _service_instance is None:
        _service_instance = AgentPersonalityService()
    return _service_instance
