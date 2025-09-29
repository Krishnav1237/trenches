#!/usr/bin/env python3
"""
Agent System Tester - Comprehensive testing and validation of the Trenches agent system.
"""

import asyncio
import yaml
import json
import time
import logging
from pathlib import Path
from typing import Dict, List, Any, Optional, Tuple
from dataclasses import dataclass
from agent_generator import TrenchesAgentGenerator
from specialized_agent_generator import SpecializedAgentGenerator
from agent_validator import AgentValidator
from core.enhanced_prompt_engine import EnhancedPromptEngine
from core.simulation import TrenchesSimulation
from models.entities import SimulationContext, Tweet


@dataclass
class TestResult:
    """Result of a system test"""
    test_name: str
    success: bool
    duration: float
    details: Dict[str, Any]
    errors: List[str]
    warnings: List[str]


class AgentSystemTester:
    """Comprehensive testing system for Trenches agents"""
    
    def __init__(self, config_path: Path = None):
        if config_path is None:
            config_path = Path("config")
        self.config_path = config_path
        self.test_results = []
        
        # Initialize components
        self.agent_generator = TrenchesAgentGenerator()
        self.specialized_generator = SpecializedAgentGenerator()
        self.validator = AgentValidator(config_path)
        self.enhanced_prompt_engine = EnhancedPromptEngine(config_path)
        
        # Test configuration
        self.test_config = {
            "max_test_agents": 10,
            "test_duration": 30,  # seconds
            "min_quality_threshold": 0.7,
            "max_error_rate": 0.1
        }

    async def run_comprehensive_tests(self) -> List[TestResult]:
        """Run comprehensive tests on the agent system"""
        print("🧪 Starting comprehensive agent system tests...")
        
        tests = [
            ("agent_generation", self.test_agent_generation),
            ("agent_validation", self.test_agent_validation),
            ("prompt_engine", self.test_prompt_engine),
            ("memory_system", self.test_memory_system),
            ("simulation_integration", self.test_simulation_integration),
            ("performance_test", self.test_performance),
            ("stress_test", self.test_stress_test),
            ("ecosystem_health", self.test_ecosystem_health)
        ]
        
        for test_name, test_func in tests:
            print(f"\n🔍 Running {test_name} test...")
            try:
                result = await test_func()
                self.test_results.append(result)
                status = "✅ PASSED" if result.success else "❌ FAILED"
                print(f"{status} {test_name} ({result.duration:.2f}s)")
            except Exception as e:
                error_result = TestResult(
                    test_name=test_name,
                    success=False,
                    duration=0.0,
                    details={"error": str(e)},
                    errors=[str(e)],
                    warnings=[]
                )
                self.test_results.append(error_result)
                print(f"❌ FAILED {test_name} - Exception: {e}")
        
        return self.test_results

    async def test_agent_generation(self) -> TestResult:
        """Test agent generation functionality"""
        start_time = time.time()
        errors = []
        warnings = []
        details = {}
        
        try:
            # Test basic agent generation
            agent = self.agent_generator.generate_agent("crypto_degen")
            details["basic_generation"] = {
                "agent_id": agent.id,
                "alias": agent.alias,
                "classification": agent.classification,
                "domain": agent.domain.value,
                "temperament": agent.temperament.value,
                "tone": agent.tone.value
            }
            
            # Test batch generation
            batch_agents = self.agent_generator.generate_agent_batch(5)
            details["batch_generation"] = {
                "count": len(batch_agents),
                "unique_ids": len(set(a.id for a in batch_agents)),
                "archetype_distribution": {}
            }
            
            # Calculate archetype distribution
            for agent in batch_agents:
                archetype = agent.id.split("_")[1] if "_" in agent.id else "unknown"
                details["batch_generation"]["archetype_distribution"][archetype] = \
                    details["batch_generation"]["archetype_distribution"].get(archetype, 0) + 1
            
            # Test specialized generation
            specialized_agents = self.specialized_generator.generate_cluster_agents("solana_ecosystem", 3)
            details["specialized_generation"] = {
                "count": len(specialized_agents),
                "cluster": "solana_ecosystem",
                "target_assets": specialized_agents[0].target_assets if specialized_agents else []
            }
            
            success = True
            
        except Exception as e:
            errors.append(f"Agent generation failed: {e}")
            success = False
        
        duration = time.time() - start_time
        return TestResult(
            test_name="agent_generation",
            success=success,
            duration=duration,
            details=details,
            errors=errors,
            warnings=warnings
        )

    async def test_agent_validation(self) -> TestResult:
        """Test agent validation functionality"""
        start_time = time.time()
        errors = []
        warnings = []
        details = {}
        
        try:
            # Generate test agents
            test_agents = self.agent_generator.generate_agent_batch(5)
            agent_dicts = [self._agent_persona_to_dict(agent) for agent in test_agents]
            
            # Test validation
            validation_results = self.validator.validate_agent_batch(agent_dicts)
            
            details["validation_results"] = {
                "total_agents": len(validation_results),
                "valid_agents": sum(1 for r in validation_results if r.is_valid),
                "average_quality": sum(r.quality_score for r in validation_results) / len(validation_results),
                "error_count": sum(len(r.errors) for r in validation_results),
                "warning_count": sum(len(r.warnings) for r in validation_results)
            }
            
            # Check quality threshold
            low_quality_agents = [r for r in validation_results if r.quality_score < self.test_config["min_quality_threshold"]]
            if low_quality_agents:
                warnings.append(f"Found {len(low_quality_agents)} low-quality agents")
            
            success = len(validation_results) > 0 and all(r.is_valid for r in validation_results)
            
        except Exception as e:
            errors.append(f"Agent validation failed: {e}")
            success = False
        
        duration = time.time() - start_time
        return TestResult(
            test_name="agent_validation",
            success=success,
            duration=duration,
            details=details,
            errors=errors,
            warnings=warnings
        )

    async def test_prompt_engine(self) -> TestResult:
        """Test enhanced prompt engine functionality"""
        start_time = time.time()
        errors = []
        warnings = []
        details = {}
        
        try:
            # Create test agent
            test_agent = {
                "id": "test_prompt_agent",
                "alias": "Test Agent",
                "classification": "Test Agent",
                "threat_level": "Gamma",
                "domain": "crypto",
                "posting_style": "analytical",
                "social_behavior": "educator",
                "target_assets": ["BTC", "ETH"],
                "skills": [{"name": "Analysis", "description": "Test skill"}],
                "weaknesses": ["Test weakness"],
                "biases": ["Test bias"],
                "catchphrase": "Test catchphrase",
                "origin_story": "Test origin story",
                "personality": {
                    "temperament": "analytical",
                    "tone": "technical",
                    "decision_bias": "logical",
                    "emotionality": "low",
                    "description": "Test description"
                }
            }
            
            # Test context
            test_context = SimulationContext(
                trending_topics=["BTC", "ETH"],
                activity_level="high",
                sentiment="positive",
                time_context="afternoon"
            )
            
            # Test prompt generation
            prompt = self.enhanced_prompt_engine.build_enhanced_prompt(
                test_agent, "tweet", test_context
            )
            
            details["prompt_generation"] = {
                "prompt_length": len(prompt),
                "contains_personality": "personality" in prompt.lower(),
                "contains_memory": "memory" in prompt.lower(),
                "contains_context": "context" in prompt.lower()
            }
            
            # Test memory update
            interaction = {
                "type": "tweet",
                "content": "BTC is looking bullish today!",
                "likes": 10,
                "retweets": 5
            }
            
            self.enhanced_prompt_engine.update_agent_memory("test_prompt_agent", interaction)
            
            # Test memory retrieval
            memory_summary = self.enhanced_prompt_engine.get_agent_memory_summary("test_prompt_agent")
            details["memory_system"] = memory_summary
            
            success = len(prompt) > 100 and "personality" in prompt.lower()
            
        except Exception as e:
            errors.append(f"Prompt engine test failed: {e}")
            success = False
        
        duration = time.time() - start_time
        return TestResult(
            test_name="prompt_engine",
            success=success,
            duration=duration,
            details=details,
            errors=errors,
            warnings=warnings
        )

    async def test_memory_system(self) -> TestResult:
        """Test agent memory system"""
        start_time = time.time()
        errors = []
        warnings = []
        details = {}
        
        try:
            # Test memory creation and updates
            agent_id = "test_memory_agent"
            
            # Simulate multiple interactions
            interactions = [
                {"type": "tweet", "content": "First tweet about BTC", "likes": 5},
                {"type": "reply", "content": "Great analysis!", "likes": 2},
                {"type": "retweet", "content": "Retweeting this", "likes": 8},
                {"type": "tweet", "content": "ETH looking strong", "likes": 12},
                {"type": "reply", "content": "I agree with this", "likes": 3}
            ]
            
            for interaction in interactions:
                self.enhanced_prompt_engine.update_agent_memory(agent_id, interaction)
            
            # Test memory retrieval
            memory_summary = self.enhanced_prompt_engine.get_agent_memory_summary(agent_id)
            
            details["memory_test"] = {
                "interactions_processed": len(interactions),
                "short_term_memory_size": memory_summary.get("short_term_memory_size", 0),
                "long_term_memory_size": memory_summary.get("long_term_memory_size", 0),
                "behavioral_patterns": memory_summary.get("behavioral_patterns", {}),
                "memory_health": memory_summary.get("memory_health", "unknown")
            }
            
            # Test memory persistence
            memory_dir = Path("test_memories")
            self.enhanced_prompt_engine.save_agent_memories(memory_dir)
            
            # Check if files were created
            memory_files = list(memory_dir.glob("*_memory.yaml"))
            details["memory_persistence"] = {
                "memory_files_created": len(memory_files),
                "memory_dir": str(memory_dir)
            }
            
            success = memory_summary.get("short_term_memory_size", 0) > 0
            
        except Exception as e:
            errors.append(f"Memory system test failed: {e}")
            success = False
        
        duration = time.time() - start_time
        return TestResult(
            test_name="memory_system",
            success=success,
            duration=duration,
            details=details,
            errors=errors,
            warnings=warnings
        )

    async def test_simulation_integration(self) -> TestResult:
        """Test simulation integration"""
        start_time = time.time()
        errors = []
        warnings = []
        details = {}
        
        try:
            # Test simulation initialization
            simulation = TrenchesSimulation(self.config_path)
            
            # Test agent loading
            agents = simulation.agent_manager.load_all_agents()
            details["simulation_integration"] = {
                "agents_loaded": len(agents),
                "agent_types": list(set(agent.get("classification", "Unknown") for agent in agents.values())),
                "simulation_initialized": True
            }
            
            # Test context analysis
            context = simulation.analyze_current_context()
            details["context_analysis"] = {
                "context_analyzed": True,
                "trending_topics": getattr(context, 'trending_topics', []),
                "activity_level": getattr(context, 'activity_level', 'unknown'),
                "sentiment": getattr(context, 'sentiment', 'unknown')
            }
            
            success = len(agents) > 0
            
        except Exception as e:
            errors.append(f"Simulation integration test failed: {e}")
            success = False
        
        duration = time.time() - start_time
        return TestResult(
            test_name="simulation_integration",
            success=success,
            duration=duration,
            details=details,
            errors=errors,
            warnings=warnings
        )

    async def test_performance(self) -> TestResult:
        """Test system performance"""
        start_time = time.time()
        errors = []
        warnings = []
        details = {}
        
        try:
            # Test agent generation performance
            gen_start = time.time()
            agents = self.agent_generator.generate_agent_batch(10)
            gen_duration = time.time() - gen_start
            
            # Test validation performance
            val_start = time.time()
            agent_dicts = [self._agent_persona_to_dict(agent) for agent in agents]
            validation_results = self.validator.validate_agent_batch(agent_dicts)
            val_duration = time.time() - val_start
            
            # Test prompt generation performance
            prompt_start = time.time()
            test_agent = agent_dicts[0]
            test_context = SimulationContext()
            prompt = self.enhanced_prompt_engine.build_enhanced_prompt(
                test_agent, "tweet", test_context
            )
            prompt_duration = time.time() - prompt_start
            
            details["performance_metrics"] = {
                "agent_generation_time": gen_duration,
                "validation_time": val_duration,
                "prompt_generation_time": prompt_duration,
                "agents_per_second": len(agents) / gen_duration,
                "validations_per_second": len(validation_results) / val_duration,
                "prompts_per_second": 1 / prompt_duration
            }
            
            # Check performance thresholds
            if gen_duration > 5.0:
                warnings.append(f"Agent generation slow: {gen_duration:.2f}s")
            if val_duration > 2.0:
                warnings.append(f"Validation slow: {val_duration:.2f}s")
            if prompt_duration > 1.0:
                warnings.append(f"Prompt generation slow: {prompt_duration:.2f}s")
            
            success = gen_duration < 10.0 and val_duration < 5.0 and prompt_duration < 2.0
            
        except Exception as e:
            errors.append(f"Performance test failed: {e}")
            success = False
        
        duration = time.time() - start_time
        return TestResult(
            test_name="performance",
            success=success,
            duration=duration,
            details=details,
            errors=errors,
            warnings=warnings
        )

    async def test_stress_test(self) -> TestResult:
        """Test system under stress"""
        start_time = time.time()
        errors = []
        warnings = []
        details = {}
        
        try:
            # Generate many agents quickly
            stress_agents = self.agent_generator.generate_agent_batch(50)
            details["stress_generation"] = {
                "agents_generated": len(stress_agents),
                "unique_ids": len(set(a.id for a in stress_agents))
            }
            
            # Test memory system under load
            memory_start = time.time()
            for i, agent in enumerate(stress_agents[:10]):  # Test with first 10
                interaction = {
                    "type": "tweet",
                    "content": f"Stress test tweet {i}",
                    "likes": i * 2
                }
                self.enhanced_prompt_engine.update_agent_memory(agent.id, interaction)
            memory_duration = time.time() - memory_start
            
            # Test prompt generation under load
            prompt_start = time.time()
            agent_dicts = [self._agent_persona_to_dict(agent) for agent in stress_agents[:5]]
            for agent_dict in agent_dicts:
                prompt = self.enhanced_prompt_engine.build_enhanced_prompt(
                    agent_dict, "tweet", SimulationContext()
                )
            prompt_duration = time.time() - prompt_start
            
            details["stress_metrics"] = {
                "memory_update_time": memory_duration,
                "prompt_generation_time": prompt_duration,
                "memory_updates_per_second": 10 / memory_duration,
                "prompts_per_second": 5 / prompt_duration
            }
            
            success = memory_duration < 5.0 and prompt_duration < 10.0
            
        except Exception as e:
            errors.append(f"Stress test failed: {e}")
            success = False
        
        duration = time.time() - start_time
        return TestResult(
            test_name="stress_test",
            success=success,
            duration=duration,
            details=details,
            errors=errors,
            warnings=warnings
        )

    async def test_ecosystem_health(self) -> TestResult:
        """Test overall ecosystem health"""
        start_time = time.time()
        errors = []
        warnings = []
        details = {}
        
        try:
            # Load existing agents
            agent_dir = Path("agent_spec")
            if agent_dir.exists():
                validation_results = self.validator.validate_agent_files(agent_dir)
                
                details["ecosystem_health"] = {
                    "total_agents": len(validation_results),
                    "valid_agents": sum(1 for r in validation_results if r.is_valid),
                    "average_quality": sum(r.quality_score for r in validation_results) / len(validation_results),
                    "error_rate": sum(len(r.errors) for r in validation_results) / len(validation_results),
                    "warning_rate": sum(len(r.warnings) for r in validation_results) / len(validation_results)
                }
                
                # Check health thresholds
                error_rate = details["ecosystem_health"]["error_rate"]
                if error_rate > self.test_config["max_error_rate"]:
                    warnings.append(f"High error rate: {error_rate:.2%}")
                
                avg_quality = details["ecosystem_health"]["average_quality"]
                if avg_quality < self.test_config["min_quality_threshold"]:
                    warnings.append(f"Low average quality: {avg_quality:.2f}")
                
                success = error_rate <= self.test_config["max_error_rate"] and avg_quality >= self.test_config["min_quality_threshold"]
            else:
                warnings.append("No existing agent directory found")
                success = False
            
        except Exception as e:
            errors.append(f"Ecosystem health test failed: {e}")
            success = False
        
        duration = time.time() - start_time
        return TestResult(
            test_name="ecosystem_health",
            success=success,
            duration=duration,
            details=details,
            errors=errors,
            warnings=warnings
        )

    def _agent_persona_to_dict(self, agent) -> Dict:
        """Convert AgentPersona to dictionary"""
        return {
            "id": agent.id,
            "personality": {
                "temperament": agent.temperament.value,
                "tone": agent.tone.value,
                "decision_bias": "logical",
                "emotionality": "medium",
                "description": agent.description
            },
            "alias": agent.alias,
            "classification": agent.classification,
            "threat_level": agent.threat_level,
            "skills": agent.skills,
            "weaknesses": agent.weaknesses,
            "catchphrase": agent.catchphrase,
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

    def generate_test_report(self) -> str:
        """Generate comprehensive test report"""
        total_tests = len(self.test_results)
        passed_tests = sum(1 for r in self.test_results if r.success)
        failed_tests = total_tests - passed_tests
        
        total_duration = sum(r.duration for r in self.test_results)
        avg_duration = total_duration / total_tests if total_tests > 0 else 0
        
        report = f"""
🧪 Trenches Agent System Test Report
====================================

📊 Test Summary:
- Total Tests: {total_tests}
- Passed: {passed_tests} ({passed_tests/total_tests*100:.1f}%)
- Failed: {failed_tests} ({failed_tests/total_tests*100:.1f}%)
- Total Duration: {total_duration:.2f}s
- Average Duration: {avg_duration:.2f}s

📋 Test Results:
"""
        
        for result in self.test_results:
            status = "✅ PASS" if result.success else "❌ FAIL"
            report += f"{status} {result.test_name} ({result.duration:.2f}s)\n"
            
            if result.errors:
                report += f"  Errors: {', '.join(result.errors)}\n"
            if result.warnings:
                report += f"  Warnings: {', '.join(result.warnings)}\n"
        
        # Performance summary
        performance_tests = [r for r in self.test_results if r.test_name in ["performance", "stress_test"]]
        if performance_tests:
            report += "\n⚡ Performance Summary:\n"
            for test in performance_tests:
                if "performance_metrics" in test.details:
                    metrics = test.details["performance_metrics"]
                    report += f"- {test.test_name}: {metrics.get('agents_per_second', 0):.1f} agents/s, {metrics.get('validations_per_second', 0):.1f} validations/s\n"
        
        # Recommendations
        report += "\n💡 Recommendations:\n"
        if failed_tests > 0:
            report += f"- {failed_tests} tests failed, review and fix issues\n"
        
        slow_tests = [r for r in self.test_results if r.duration > 10.0]
        if slow_tests:
            report += f"- {len(slow_tests)} tests are slow (>10s), consider optimization\n"
        
        warning_tests = [r for r in self.test_results if r.warnings]
        if warning_tests:
            report += f"- {len(warning_tests)} tests have warnings, review for improvements\n"
        
        return report

    def save_test_report(self, output_file: Path = None):
        """Save test report to file"""
        if output_file is None:
            output_file = Path("agent_system_test_report.txt")
        
        report = self.generate_test_report()
        with open(output_file, 'w', encoding='utf-8') as f:
            f.write(report)
        
        print(f"📄 Test report saved to {output_file}")


async def main():
    """Main function to run comprehensive tests"""
    tester = AgentSystemTester()
    
    print("🚀 Starting comprehensive agent system testing...")
    
    # Run all tests
    test_results = await tester.run_comprehensive_tests()
    
    # Generate and save report
    tester.save_test_report()
    
    # Print summary
    total_tests = len(test_results)
    passed_tests = sum(1 for r in test_results if r.success)
    
    print(f"\n🎉 Testing complete!")
    print(f"📊 Results: {passed_tests}/{total_tests} tests passed")
    
    if passed_tests == total_tests:
        print("🎊 All tests passed! System is ready for production.")
    else:
        print("⚠️  Some tests failed. Review the report for details.")


if __name__ == "__main__":
    asyncio.run(main())
