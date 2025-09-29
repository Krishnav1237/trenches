#!/usr/bin/env python3
"""
Agent Validator - Validates and tests generated agents for quality and functionality.
"""

import yaml
import asyncio
import logging
from pathlib import Path
from typing import Dict, List, Any, Optional
from dataclasses import dataclass
from agent_generator import TrenchesAgentGenerator
from core.agent_manager import AgentManager
from core.llm_client import LLMClient
from models.config import LLMConfig


@dataclass
class ValidationResult:
    """Result of agent validation"""
    agent_id: str
    is_valid: bool
    errors: List[str]
    warnings: List[str]
    quality_score: float
    recommendations: List[str]


class AgentValidator:
    """Validates and tests generated agents"""
    
    def __init__(self, config_path: Path = None):
        if config_path is None:
            config_path = Path("config")
        self.config_path = config_path
        self.agent_manager = AgentManager(config_path)
        self.llm_config = LLMConfig.from_env_and_file(config_path / "llm.yaml")
        self.llm_client = LLMClient(self.llm_config)
        
        # Validation rules
        self.validation_rules = {
            "required_fields": [
                "id", "personality", "alias", "classification", "threat_level",
                "skills", "weaknesses", "catchphrase", "origin_story",
                "llm", "activity", "memory"
            ],
            "personality_required": [
                "temperament", "tone", "decision_bias", "emotionality", "description"
            ],
            "llm_required": ["model", "temperature"],
            "activity_required": ["schedule", "actions_per_awake"],
            "memory_required": ["short_term_window", "long_term_vector_db"]
        }
        
        # Quality metrics
        self.quality_metrics = {
            "description_length": {"min": 50, "max": 500, "weight": 0.2},
            "skills_count": {"min": 3, "max": 8, "weight": 0.15},
            "weaknesses_count": {"min": 2, "max": 5, "weight": 0.15},
            "origin_story_length": {"min": 100, "max": 300, "weight": 0.15},
            "catchphrase_length": {"min": 10, "max": 100, "weight": 0.1},
            "target_assets_count": {"min": 3, "max": 10, "weight": 0.1},
            "biases_count": {"min": 2, "max": 5, "weight": 0.15}
        }

    def validate_agent(self, agent: Dict) -> ValidationResult:
        """Validate a single agent"""
        agent_id = agent.get("id", "unknown")
        errors = []
        warnings = []
        recommendations = []
        
        # Check required fields
        for field in self.validation_rules["required_fields"]:
            if field not in agent:
                errors.append(f"Missing required field: {field}")
        
        # Check personality fields
        personality = agent.get("personality", {})
        for field in self.validation_rules["personality_required"]:
            if field not in personality:
                errors.append(f"Missing required personality field: {field}")
        
        # Check LLM fields
        llm = agent.get("llm", {})
        for field in self.validation_rules["llm_required"]:
            if field not in llm:
                errors.append(f"Missing required LLM field: {field}")
        
        # Check activity fields
        activity = agent.get("activity", {})
        for field in self.validation_rules["activity_required"]:
            if field not in activity:
                errors.append(f"Missing required activity field: {field}")
        
        # Check memory fields
        memory = agent.get("memory", {})
        for field in self.validation_rules["memory_required"]:
            if field not in memory:
                errors.append(f"Missing required memory field: {field}")
        
        # Validate field values
        self._validate_field_values(agent, errors, warnings)
        
        # Calculate quality score
        quality_score = self._calculate_quality_score(agent, recommendations)
        
        # Generate recommendations
        self._generate_recommendations(agent, recommendations)
        
        return ValidationResult(
            agent_id=agent_id,
            is_valid=len(errors) == 0,
            errors=errors,
            warnings=warnings,
            quality_score=quality_score,
            recommendations=recommendations
        )

    def _validate_field_values(self, agent: Dict, errors: List[str], warnings: List[str]):
        """Validate field values"""
        # Validate temperature
        temperature = agent.get("llm", {}).get("temperature", 0.5)
        if not isinstance(temperature, (int, float)) or temperature < 0 or temperature > 2:
            errors.append("Temperature must be a number between 0 and 2")
        
        # Validate actions_per_awake
        actions = agent.get("activity", {}).get("actions_per_awake", [1, 2])
        if not isinstance(actions, list) or len(actions) != 2:
            errors.append("actions_per_awake must be a list of 2 integers")
        elif not all(isinstance(x, int) for x in actions):
            errors.append("actions_per_awake must contain only integers")
        elif actions[0] > actions[1]:
            errors.append("actions_per_awake[0] must be <= actions_per_awake[1]")
        
        # Validate memory window
        memory_window = agent.get("memory", {}).get("short_term_window", 60)
        if not isinstance(memory_window, int) or memory_window < 1 or memory_window > 1000:
            errors.append("short_term_window must be an integer between 1 and 1000")
        
        # Validate threat level
        threat_level = agent.get("threat_level", "Gamma")
        valid_threat_levels = ["Alpha", "Beta", "Gamma", "Delta"]
        if threat_level not in valid_threat_levels:
            warnings.append(f"Threat level '{threat_level}' not in standard levels: {valid_threat_levels}")
        
        # Validate temperament
        temperament = agent.get("personality", {}).get("temperament", "neutral")
        valid_temperaments = [
            "analytical", "sarcastic", "optimistic", "pessimistic", "playful",
            "contemplative", "neutral", "aggressive", "chill", "dramatic",
            "energetic", "decisive", "cheerful"
        ]
        if temperament not in valid_temperaments:
            warnings.append(f"Temperament '{temperament}' not in standard temperaments: {valid_temperaments}")

    def _calculate_quality_score(self, agent: Dict, recommendations: List[str]) -> float:
        """Calculate quality score for agent"""
        total_score = 0.0
        total_weight = 0.0
        
        for metric, config in self.quality_metrics.items():
            weight = config["weight"]
            total_weight += weight
            
            if metric == "description_length":
                length = len(agent.get("personality", {}).get("description", ""))
                score = self._score_range(length, config["min"], config["max"])
                if score < 0.5:
                    recommendations.append(f"Description is too short ({length} chars), consider expanding it")
                elif score > 1.0:
                    recommendations.append(f"Description is too long ({length} chars), consider shortening it")
            
            elif metric == "skills_count":
                count = len(agent.get("skills", []))
                score = self._score_range(count, config["min"], config["max"])
                if score < 0.5:
                    recommendations.append(f"Too few skills ({count}), consider adding more")
                elif score > 1.0:
                    recommendations.append(f"Too many skills ({count}), consider consolidating")
            
            elif metric == "weaknesses_count":
                count = len(agent.get("weaknesses", []))
                score = self._score_range(count, config["min"], config["max"])
                if score < 0.5:
                    recommendations.append(f"Too few weaknesses ({count}), consider adding more")
                elif score > 1.0:
                    recommendations.append(f"Too many weaknesses ({count}), consider consolidating")
            
            elif metric == "origin_story_length":
                length = len(agent.get("origin_story", ""))
                score = self._score_range(length, config["min"], config["max"])
                if score < 0.5:
                    recommendations.append(f"Origin story is too short ({length} chars), consider expanding it")
                elif score > 1.0:
                    recommendations.append(f"Origin story is too long ({length} chars), consider shortening it")
            
            elif metric == "catchphrase_length":
                length = len(agent.get("catchphrase", ""))
                score = self._score_range(length, config["min"], config["max"])
                if score < 0.5:
                    recommendations.append(f"Catchphrase is too short ({length} chars), consider expanding it")
                elif score > 1.0:
                    recommendations.append(f"Catchphrase is too long ({length} chars), consider shortening it")
            
            elif metric == "target_assets_count":
                count = len(agent.get("target_assets", []))
                score = self._score_range(count, config["min"], config["max"])
                if score < 0.5:
                    recommendations.append(f"Too few target assets ({count}), consider adding more")
                elif score > 1.0:
                    recommendations.append(f"Too many target assets ({count}), consider reducing")
            
            elif metric == "biases_count":
                count = len(agent.get("biases", []))
                score = self._score_range(count, config["min"], config["max"])
                if score < 0.5:
                    recommendations.append(f"Too few biases ({count}), consider adding more")
                elif score > 1.0:
                    recommendations.append(f"Too many biases ({count}), consider consolidating")
            
            total_score += score * weight
        
        return total_score / total_weight if total_weight > 0 else 0.0

    def _score_range(self, value: int, min_val: int, max_val: int) -> float:
        """Score a value within a range (0-1)"""
        if value < min_val:
            return value / min_val
        elif value > max_val:
            return max_val / value
        else:
            return 1.0

    def _generate_recommendations(self, agent: Dict, recommendations: List[str]):
        """Generate recommendations for improving agent quality"""
        # Check for diversity
        temperament = agent.get("personality", {}).get("temperament", "neutral")
        tone = agent.get("personality", {}).get("tone", "neutral")
        
        if temperament == tone:
            recommendations.append("Consider making temperament and tone more distinct for better personality diversity")
        
        # Check for realistic weaknesses
        weaknesses = agent.get("weaknesses", [])
        if len(weaknesses) < 2:
            recommendations.append("Add more realistic weaknesses to make the agent more believable")
        
        # Check for skill diversity
        skills = agent.get("skills", [])
        skill_names = [skill.get("name", "") for skill in skills]
        if len(set(skill_names)) != len(skill_names):
            recommendations.append("Remove duplicate skill names for better clarity")
        
        # Check for asset diversity
        target_assets = agent.get("target_assets", [])
        if len(target_assets) < 3:
            recommendations.append("Add more target assets for better market coverage")
        
        # Check for realistic biases
        biases = agent.get("biases", [])
        if len(biases) < 2:
            recommendations.append("Add more realistic cognitive biases to make the agent more human-like")

    def validate_agent_batch(self, agents: List[Dict]) -> List[ValidationResult]:
        """Validate a batch of agents"""
        results = []
        for agent in agents:
            result = self.validate_agent(agent)
            results.append(result)
        return results

    def validate_agent_files(self, agent_dir: Path) -> List[ValidationResult]:
        """Validate all agent files in a directory"""
        results = []
        for yaml_file in agent_dir.glob("*.yaml"):
            try:
                with open(yaml_file, 'r', encoding='utf-8') as f:
                    agent = yaml.safe_load(f)
                result = self.validate_agent(agent)
                results.append(result)
            except Exception as e:
                result = ValidationResult(
                    agent_id=yaml_file.stem,
                    is_valid=False,
                    errors=[f"Failed to load file: {e}"],
                    warnings=[],
                    quality_score=0.0,
                    recommendations=[]
                )
                results.append(result)
        return results

    def generate_validation_report(self, results: List[ValidationResult]) -> str:
        """Generate a comprehensive validation report"""
        total_agents = len(results)
        valid_agents = sum(1 for r in results if r.is_valid)
        invalid_agents = total_agents - valid_agents
        
        avg_quality = sum(r.quality_score for r in results) / total_agents if total_agents > 0 else 0.0
        
        report = f"""
Agent Validation Report
======================

Summary:
- Total agents: {total_agents}
- Valid agents: {valid_agents} ({valid_agents/total_agents*100:.1f}%)
- Invalid agents: {invalid_agents} ({invalid_agents/total_agents*100:.1f}%)
- Average quality score: {avg_quality:.2f}/1.0

Quality Distribution:
"""
        
        # Quality distribution
        quality_ranges = [
            (0.0, 0.3, "Poor"),
            (0.3, 0.5, "Below Average"),
            (0.5, 0.7, "Average"),
            (0.7, 0.9, "Good"),
            (0.9, 1.0, "Excellent")
        ]
        
        for min_score, max_score, label in quality_ranges:
            count = sum(1 for r in results if min_score <= r.quality_score < max_score)
            percentage = count / total_agents * 100 if total_agents > 0 else 0
            report += f"- {label}: {count} agents ({percentage:.1f}%)\n"
        
        # Top issues
        all_errors = []
        for result in results:
            all_errors.extend(result.errors)
        
        if all_errors:
            error_counts = {}
            for error in all_errors:
                error_counts[error] = error_counts.get(error, 0) + 1
            
            report += "\nTop Issues:\n"
            for error, count in sorted(error_counts.items(), key=lambda x: x[1], reverse=True)[:10]:
                report += f"- {error}: {count} occurrences\n"
        
        # Top recommendations
        all_recommendations = []
        for result in results:
            all_recommendations.extend(result.recommendations)
        
        if all_recommendations:
            rec_counts = {}
            for rec in all_recommendations:
                rec_counts[rec] = rec_counts.get(rec, 0) + 1
            
            report += "\nTop Recommendations:\n"
            for rec, count in sorted(rec_counts.items(), key=lambda x: x[1], reverse=True)[:10]:
                report += f"- {rec}: {count} agents\n"
        
        # Invalid agents details
        if invalid_agents > 0:
            report += "\nInvalid Agents:\n"
            for result in results:
                if not result.is_valid:
                    report += f"- {result.agent_id}: {', '.join(result.errors)}\n"
        
        return report

    async def test_agent_llm_generation(self, agent: Dict) -> Dict[str, Any]:
        """Test agent's LLM generation capabilities"""
        try:
            # Test basic content generation
            prompt = f"You are {agent.get('alias', 'Agent')}. Generate a short tweet about crypto."
            content = await self.llm_client.generate_content_async(agent, prompt)
            
            return {
                "success": True,
                "content": content,
                "content_length": len(content),
                "error": None
            }
        except Exception as e:
            return {
                "success": False,
                "content": None,
                "content_length": 0,
                "error": str(e)
            }

    async def test_agent_batch_llm(self, agents: List[Dict]) -> Dict[str, Any]:
        """Test LLM generation for a batch of agents"""
        results = {}
        successful_tests = 0
        
        for agent in agents:
            agent_id = agent.get("id", "unknown")
            test_result = await self.test_agent_llm_generation(agent)
            results[agent_id] = test_result
            
            if test_result["success"]:
                successful_tests += 1
        
        return {
            "total_agents": len(agents),
            "successful_tests": successful_tests,
            "success_rate": successful_tests / len(agents) if agents else 0,
            "results": results
        }


def main():
    """Main function to validate agents"""
    validator = AgentValidator()
    
    # Validate main agent directory
    agent_dir = Path("agent_spec")
    print(f"Validating agents in {agent_dir}...")
    
    results = validator.validate_agent_files(agent_dir)
    
    # Generate report
    report = validator.generate_validation_report(results)
    print(report)
    
    # Save report
    report_file = Path("agent_validation_report.txt")
    with open(report_file, 'w', encoding='utf-8') as f:
        f.write(report)
    print(f"Validation report saved to {report_file}")
    
    # Test LLM generation for a sample of agents
    print("\nTesting LLM generation for sample agents...")
    sample_agents = [r for r in results if r.is_valid][:5]  # Test first 5 valid agents
    
    if sample_agents:
        # Load agent data for LLM testing
        agent_data = []
        for result in sample_agents:
            agent_file = agent_dir / f"{result.agent_id}.yaml"
            try:
                with open(agent_file, 'r', encoding='utf-8') as f:
                    agent = yaml.safe_load(f)
                    agent_data.append(agent)
            except Exception as e:
                print(f"Failed to load {result.agent_id}: {e}")
        
        if agent_data:
            llm_test_results = asyncio.run(validator.test_agent_batch_llm(agent_data))
            print(f"LLM Test Results:")
            print(f"- Total agents tested: {llm_test_results['total_agents']}")
            print(f"- Successful tests: {llm_test_results['successful_tests']}")
            print(f"- Success rate: {llm_test_results['success_rate']:.1%}")


if __name__ == "__main__":
    main()
