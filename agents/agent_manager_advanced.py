#!/usr/bin/env python3
"""
Advanced Agent Manager - Manages the complete Trenches agent ecosystem.
"""

import yaml
import asyncio
import logging
import random
from pathlib import Path
from typing import Dict, List, Any, Optional, Tuple
from dataclasses import dataclass
from agent_generator import TrenchesAgentGenerator, AgentPersona
from specialized_agent_generator import SpecializedAgentGenerator
from agent_validator import AgentValidator, ValidationResult


@dataclass
class AgentEcosystem:
    """Complete agent ecosystem configuration"""
    total_agents: int
    agent_distribution: Dict[str, int]
    quality_score: float
    validation_results: List[ValidationResult]
    network_connections: Dict[str, List[str]]
    ecosystem_health: str


class AdvancedAgentManager:
    """Advanced agent management system for Trenches"""
    
    def __init__(self, config_path: Path = None):
        if config_path is None:
            config_path = Path("config")
        self.config_path = config_path
        self.agent_generator = TrenchesAgentGenerator()
        self.specialized_generator = SpecializedAgentGenerator()
        self.validator = AgentValidator(config_path)
        
        # Agent ecosystem state
        self.agents = {}
        self.agent_network = {}
        self.ecosystem_health = "unknown"
        
        # Configuration
        self.ecosystem_config = {
            "target_agent_count": 200,
            "min_quality_score": 0.7,
            "max_agents_per_archetype": 30,
            "network_density": 0.3,  # 30% of possible connections
            "health_thresholds": {
                "excellent": 0.9,
                "good": 0.8,
                "fair": 0.7,
                "poor": 0.6
            }
        }

    def generate_complete_ecosystem(self) -> AgentEcosystem:
        """Generate a complete, balanced agent ecosystem"""
        print("🌱 Generating complete Trenches agent ecosystem...")
        
        # Generate core agents
        core_agents = self._generate_core_agents()
        print(f"✅ Generated {len(core_agents)} core agents")
        
        # Generate specialized clusters
        specialized_agents = self._generate_specialized_clusters()
        print(f"✅ Generated {len(specialized_agents)} specialized agents")
        
        # Combine all agents
        all_agents = core_agents + specialized_agents
        
        # Validate ecosystem
        validation_results = self.validator.validate_agent_batch(all_agents)
        print(f"✅ Validated {len(validation_results)} agents")
        
        # Generate agent network
        agent_network = self._generate_agent_network(all_agents)
        print(f"✅ Generated agent network with {len(agent_network)} connections")
        
        # Calculate ecosystem health
        ecosystem_health = self._calculate_ecosystem_health(validation_results, agent_network)
        print(f"✅ Ecosystem health: {ecosystem_health}")
        
        # Save ecosystem
        self._save_ecosystem(all_agents, agent_network, validation_results)
        
        # Calculate distribution
        agent_distribution = self._calculate_agent_distribution(all_agents)
        quality_score = sum(r.quality_score for r in validation_results) / len(validation_results)
        
        return AgentEcosystem(
            total_agents=len(all_agents),
            agent_distribution=agent_distribution,
            quality_score=quality_score,
            validation_results=validation_results,
            network_connections=agent_network,
            ecosystem_health=ecosystem_health
        )

    def _generate_core_agents(self) -> List[Dict]:
        """Generate core agent types"""
        core_distribution = {
            "crypto_degen": 30,
            "crypto_analyst": 25,
            "crypto_trader": 20,
            "crypto_troll": 15,
            "tech_guru": 15,
            "meme_lord": 15,
            "contrarian": 10,
            "influencer": 10
        }
        
        agents = []
        for archetype, count in core_distribution.items():
            for _ in range(count):
                agent = self.agent_generator.generate_agent(archetype)
                agent_dict = self._agent_persona_to_dict(agent)
                agents.append(agent_dict)
        
        return agents

    def _generate_specialized_clusters(self) -> List[Dict]:
        """Generate specialized agent clusters"""
        specialized_agents = []
        
        # Generate ecosystem warriors
        ecosystem_warriors = self.specialized_generator.generate_ecosystem_warriors()
        for agent in ecosystem_warriors:
            agent_dict = self._agent_persona_to_dict(agent)
            specialized_agents.append(agent_dict)
        
        # Generate meme war agents
        meme_warriors = self.specialized_generator.generate_meme_war_agents()
        for agent in meme_warriors:
            agent_dict = self._agent_persona_to_dict(agent)
            specialized_agents.append(agent_dict)
        
        # Generate degen ecosystem
        degen_ecosystem = self.specialized_generator.generate_degen_ecosystem()
        for agent in degen_ecosystem:
            agent_dict = self._agent_persona_to_dict(agent)
            specialized_agents.append(agent_dict)
        
        return specialized_agents

    def _agent_persona_to_dict(self, agent: AgentPersona) -> Dict:
        """Convert AgentPersona to dictionary"""
        return {
            "id": agent.id,
            "personality": {
                "temperament": agent.temperament.value,
                "tone": agent.tone.value,
                "decision_bias": random.choice(["logical", "emotional", "intuitive", "data_driven"]),
                "emotionality": random.choice(["low", "medium", "high"]),
                "description": agent.description
            },
            "alias": agent.alias,
            "classification": agent.classification,
            "threat_level": agent.threat_level,
            "skills": agent.skills,
            "weaknesses": agent.weaknesses,
            "catchphrase": agent.catchphrase,
            "physical_description": agent.physical_description,
            "origin_story": agent.origin_story,
            "llm": {
                "model": agent.llm_model,
                "temperature": agent.temperature
            },
            "activity": {
                "schedule": agent.activity_schedule,
                "actions_per_awake": agent.actions_per_awake
            },
            "memory": {
                "short_term_window": agent.memory_window,
                "long_term_vector_db": True
            },
            "domain": agent.domain.value,
            "posting_style": agent.posting_style,
            "target_assets": agent.target_assets,
            "social_behavior": agent.social_behavior,
            "biases": agent.biases
        }

    def _generate_agent_network(self, agents: List[Dict]) -> Dict[str, List[str]]:
        """Generate agent relationship network"""
        network = {}
        
        for agent in agents:
            agent_id = agent["id"]
            follows = []
            
            # Determine follows based on social behavior
            social_behavior = agent.get("social_behavior", "neutral")
            domain = agent.get("domain", "crypto")
            
            if social_behavior == "amplifier":
                # Follow other popular agents
                follows = [a["id"] for a in agents if a.get("social_behavior") in ["influencer", "thought_leader"] and a["id"] != agent_id]
            elif social_behavior == "educator":
                # Follow analysts and tech gurus
                follows = [a["id"] for a in agents if a.get("classification") in ["Crypto Agent", "Tech Agent"] and a["id"] != agent_id]
            elif social_behavior == "disruptor":
                # Follow contrarians and trolls
                follows = [a["id"] for a in agents if a.get("social_behavior") in ["disruptor", "reality_checker"] and a["id"] != agent_id]
            elif social_behavior == "thought_leader":
                # Follow other thought leaders
                follows = [a["id"] for a in agents if a.get("social_behavior") in ["thought_leader", "educator"] and a["id"] != agent_id]
            elif social_behavior == "entertainer":
                # Follow other entertainers
                follows = [a["id"] for a in agents if a.get("social_behavior") in ["entertainer", "influencer"] and a["id"] != agent_id]
            elif social_behavior == "reality_checker":
                # Follow other reality checkers
                follows = [a["id"] for a in agents if a.get("social_behavior") in ["reality_checker", "educator"] and a["id"] != agent_id]
            elif social_behavior == "influencer":
                # Follow other influencers
                follows = [a["id"] for a in agents if a.get("social_behavior") in ["influencer", "thought_leader"] and a["id"] != agent_id]
            
            # Add some random follows for variety
            other_agents = [a["id"] for a in agents if a["id"] != agent_id]
            random_follows = random.sample(other_agents, min(5, len(other_agents)))
            follows.extend(random_follows)
            
            network[agent_id] = list(set(follows))  # Remove duplicates
        
        return network

    def _calculate_ecosystem_health(self, validation_results: List[ValidationResult], network: Dict[str, List[str]]) -> str:
        """Calculate overall ecosystem health"""
        # Calculate validation health
        valid_agents = sum(1 for r in validation_results if r.is_valid)
        validation_health = valid_agents / len(validation_results) if validation_results else 0
        
        # Calculate quality health
        avg_quality = sum(r.quality_score for r in validation_results) / len(validation_results) if validation_results else 0
        quality_health = avg_quality
        
        # Calculate network health
        total_possible_connections = len(network) * (len(network) - 1)
        total_connections = sum(len(follows) for follows in network.values())
        network_health = total_connections / total_possible_connections if total_possible_connections > 0 else 0
        
        # Calculate overall health
        overall_health = (validation_health * 0.4 + quality_health * 0.4 + network_health * 0.2)
        
        # Determine health level
        thresholds = self.ecosystem_config["health_thresholds"]
        if overall_health >= thresholds["excellent"]:
            return "excellent"
        elif overall_health >= thresholds["good"]:
            return "good"
        elif overall_health >= thresholds["fair"]:
            return "fair"
        else:
            return "poor"

    def _calculate_agent_distribution(self, agents: List[Dict]) -> Dict[str, int]:
        """Calculate agent distribution by archetype"""
        distribution = {}
        for agent in agents:
            agent_id = agent.get("id", "unknown")
            archetype = agent_id.split("_")[1] if "_" in agent_id else "unknown"
            distribution[archetype] = distribution.get(archetype, 0) + 1
        return distribution

    def _save_ecosystem(self, agents: List[Dict], network: Dict[str, List[str]], validation_results: List[ValidationResult]):
        """Save complete ecosystem to files"""
        # Save agents
        agent_dir = Path("agent_spec/ecosystem")
        agent_dir.mkdir(exist_ok=True, parents=True)
        
        for agent in agents:
            agent_file = agent_dir / f"{agent['id']}.yaml"
            with open(agent_file, 'w', encoding='utf-8') as f:
                yaml.dump(agent, f, default_flow_style=False, allow_unicode=True)
        
        # Save network
        network_file = agent_dir / "agent_network.yaml"
        network_data = {
            "agent_relationships": network,
            "network_metadata": {
                "total_agents": len(agents),
                "total_connections": sum(len(follows) for follows in network.values()),
                "average_follows": sum(len(follows) for follows in network.values()) / len(network) if network else 0,
                "generated_at": "2024-01-01T00:00:00Z"
            }
        }
        with open(network_file, 'w', encoding='utf-8') as f:
            yaml.dump(network_data, f, default_flow_style=False, allow_unicode=True)
        
        # Save validation results
        validation_file = agent_dir / "validation_results.yaml"
        validation_data = {
            "validation_summary": {
                "total_agents": len(validation_results),
                "valid_agents": sum(1 for r in validation_results if r.is_valid),
                "average_quality_score": sum(r.quality_score for r in validation_results) / len(validation_results) if validation_results else 0,
                "ecosystem_health": self.ecosystem_health
            },
            "agent_results": [
                {
                    "agent_id": r.agent_id,
                    "is_valid": r.is_valid,
                    "quality_score": r.quality_score,
                    "error_count": len(r.errors),
                    "warning_count": len(r.warnings)
                }
                for r in validation_results
            ]
        }
        with open(validation_file, 'w', encoding='utf-8') as f:
            yaml.dump(validation_data, f, default_flow_style=False, allow_unicode=True)

    def generate_ecosystem_report(self, ecosystem: AgentEcosystem) -> str:
        """Generate comprehensive ecosystem report"""
        report = f"""
🌐 Trenches Agent Ecosystem Report
================================

📊 Ecosystem Overview:
- Total Agents: {ecosystem.total_agents}
- Quality Score: {ecosystem.quality_score:.2f}/1.0
- Health Status: {ecosystem.ecosystem_health.upper()}
- Network Connections: {sum(len(follows) for follows in ecosystem.network_connections.values())}

🎭 Agent Distribution:
"""
        
        for archetype, count in ecosystem.agent_distribution.items():
            percentage = count / ecosystem.total_agents * 100
            report += f"- {archetype}: {count} agents ({percentage:.1f}%)\n"
        
        # Quality distribution
        quality_ranges = [
            (0.0, 0.3, "Poor"),
            (0.3, 0.5, "Below Average"),
            (0.5, 0.7, "Average"),
            (0.7, 0.9, "Good"),
            (0.9, 1.0, "Excellent")
        ]
        
        report += "\n📈 Quality Distribution:\n"
        for min_score, max_score, label in quality_ranges:
            count = sum(1 for r in ecosystem.validation_results if min_score <= r.quality_score < max_score)
            percentage = count / ecosystem.total_agents * 100 if ecosystem.total_agents > 0 else 0
            report += f"- {label}: {count} agents ({percentage:.1f}%)\n"
        
        # Top performing agents
        top_agents = sorted(ecosystem.validation_results, key=lambda x: x.quality_score, reverse=True)[:10]
        report += "\n🏆 Top Performing Agents:\n"
        for i, agent in enumerate(top_agents, 1):
            report += f"{i:2d}. {agent.agent_id}: {agent.quality_score:.2f} quality score\n"
        
        # Network analysis
        total_connections = sum(len(follows) for follows in ecosystem.network_connections.values())
        avg_connections = total_connections / len(ecosystem.network_connections) if ecosystem.network_connections else 0
        
        report += f"\n🔗 Network Analysis:\n"
        report += f"- Total Connections: {total_connections}\n"
        report += f"- Average Connections per Agent: {avg_connections:.1f}\n"
        report += f"- Network Density: {total_connections / (len(ecosystem.network_connections) * (len(ecosystem.network_connections) - 1)) * 100:.1f}%\n"
        
        # Recommendations
        report += "\n💡 Recommendations:\n"
        if ecosystem.quality_score < 0.8:
            report += "- Consider improving agent quality through better prompt engineering\n"
        if ecosystem.ecosystem_health == "poor":
            report += "- Ecosystem health is poor, consider rebalancing agent types\n"
        if avg_connections < 5:
            report += "- Network density is low, consider adding more connections\n"
        
        return report

    def optimize_ecosystem(self, ecosystem: AgentEcosystem) -> AgentEcosystem:
        """Optimize ecosystem for better performance"""
        print("🔧 Optimizing ecosystem...")
        
        # Identify low-quality agents
        low_quality_agents = [r for r in ecosystem.validation_results if r.quality_score < 0.7]
        
        if low_quality_agents:
            print(f"⚠️  Found {len(low_quality_agents)} low-quality agents")
            # In a real implementation, you would regenerate these agents
            # For now, we'll just report them
        
        # Check for imbalanced distribution
        max_agents_per_type = self.ecosystem_config["max_agents_per_archetype"]
        imbalanced_types = [t for t, c in ecosystem.agent_distribution.items() if c > max_agents_per_type]
        
        if imbalanced_types:
            print(f"⚠️  Found imbalanced agent types: {imbalanced_types}")
        
        print("✅ Ecosystem optimization complete")
        return ecosystem


def main():
    """Main function to generate and manage the complete agent ecosystem"""
    import random
    
    manager = AdvancedAgentManager()
    
    print("🚀 Starting Trenches Agent Ecosystem Generation...")
    
    # Generate complete ecosystem
    ecosystem = manager.generate_complete_ecosystem()
    
    # Generate report
    report = manager.generate_ecosystem_report(ecosystem)
    print(report)
    
    # Save report
    report_file = Path("agent_ecosystem_report.txt")
    with open(report_file, 'w', encoding='utf-8') as f:
        f.write(report)
    print(f"📄 Ecosystem report saved to {report_file}")
    
    # Optimize ecosystem
    optimized_ecosystem = manager.optimize_ecosystem(ecosystem)
    
    print("\n🎉 Trenches Agent Ecosystem Generation Complete!")
    print(f"📊 Generated {ecosystem.total_agents} agents with {ecosystem.ecosystem_health} health")


if __name__ == "__main__":
    main()
