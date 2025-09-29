"""LLM client for content generation using multiple providers (Groq, Anthropic)."""

import asyncio
import logging
import os
from typing import Dict, Optional

from openai import OpenAI
import backoff

# Import Anthropic with fallback
try:
    import anthropic
    ANTHROPIC_AVAILABLE = True
except ImportError:
    ANTHROPIC_AVAILABLE = False

from models.config import LLMConfig


class LLMClient:
    """Client for LLM content generation via multiple providers (Groq, Anthropic)"""

    def __init__(self, config: LLMConfig):
        self.config = config
        self.logger = logging.getLogger(__name__)
        
        # Initialize provider clients
        self.groq_client = None
        self.anthropic_client = None
        self._init_clients()

    def _init_clients(self):
        """Initialize provider clients"""
        # Initialize Groq client
        groq_api_key = self.config.api_key or os.getenv('GROQ_API_KEY')
        if groq_api_key:
            self.groq_client = OpenAI(
                base_url=self.config.base_url,
                api_key=groq_api_key.strip()
            )
        
        # Initialize Anthropic client
        if ANTHROPIC_AVAILABLE:
            anthropic_api_key = os.getenv('ANTHROPIC_API_KEY')
            if anthropic_api_key:
                self.anthropic_client = anthropic.Anthropic(
                    api_key=anthropic_api_key.strip()
                )

    def _get_provider_from_agent(self, agent: Dict) -> str:
        """Determine which provider to use for the agent"""
        agent_llm = agent.get('llm', {})
        provider = agent_llm.get('provider', 'groq').lower()
        
        # Validate provider availability
        if provider == 'anthropic' and not self.anthropic_client:
            self.logger.warning(f"Anthropic requested but not available, falling back to Groq")
            provider = 'groq'
        elif provider == 'groq' and not self.groq_client:
            self.logger.warning(f"Groq requested but not available, falling back to Anthropic")
            provider = 'anthropic'
            
        return provider

    @backoff.on_exception(backoff.expo, Exception, max_tries=3)
    def _generate_with_groq(self, agent: Dict, prompt: str) -> str:
        """Generate content using Groq API via OpenAI SDK"""
        # Get configuration
        agent_llm = agent.get('llm', {})
        model = agent_llm.get('model', self.config.default_model)
        temperature = agent_llm.get('temperature', self.config.default_temperature)
        max_tokens = agent_llm.get('max_tokens', self.config.default_max_tokens)

        # Get API key
        api_key = self.config.api_key or os.getenv('GROQ_API_KEY')
        if not api_key:
            raise ValueError("Groq API key not found")

        api_key = api_key.strip()

        try:
            if not self.groq_client:
                raise ValueError("Groq client not initialized")

            # Make the completion request
            completion = self.groq_client.chat.completions.create(
                model=model,
                messages=[{"role": "user", "content": prompt}],
                temperature=temperature,
                max_tokens=max_tokens
            )

            # Extract and format content
            content = completion.choices[0].message.content.strip()
            max_length = agent.get('constraints', {}).get('max_tweet_length', 280)
            return content[:max_length] if len(content) > max_length else content

        except Exception as e:
            error_message = str(e)
            self.logger.error(f"Groq API error: {error_message}")

            if "401" in error_message:
                raise ValueError(f"Groq authentication failed: {error_message}")
            raise

    @backoff.on_exception(backoff.expo, Exception, max_tries=3)
    def _generate_with_anthropic(self, agent: Dict, prompt: str) -> str:
        """Generate content using Anthropic API"""
        if not self.anthropic_client:
            raise ValueError("Anthropic client not initialized")
            
        # Get configuration
        agent_llm = agent.get('llm', {})
        model = agent_llm.get('model', 'claude-3-haiku-20240307')
        temperature = agent_llm.get('temperature', self.config.default_temperature)
        max_tokens = agent_llm.get('max_tokens', self.config.default_max_tokens)

        try:
            # Make the completion request
            message = self.anthropic_client.messages.create(
                model=model,
                max_tokens=max_tokens,
                temperature=temperature,
                messages=[{"role": "user", "content": prompt}]
            )

            # Extract and format content
            content = message.content[0].text.strip()
            max_length = agent.get('constraints', {}).get('max_tweet_length', 280)
            return content[:max_length] if len(content) > max_length else content

        except Exception as e:
            error_message = str(e)
            self.logger.error(f"Anthropic API error: {error_message}")

            if "401" in error_message or "authentication" in error_message.lower():
                raise ValueError(f"Anthropic authentication failed: {error_message}")
            raise

    async def generate_content_async(self, agent: Dict, prompt: str) -> str:
        """Generate content asynchronously using the appropriate provider"""
        agent_id = agent.get('id', 'unknown')
        provider = self._get_provider_from_agent(agent)

        try:
            # Run in executor to avoid blocking
            loop = asyncio.get_event_loop()
            
            if provider == 'anthropic':
                content = await loop.run_in_executor(
                    None,
                    self._generate_with_anthropic,
                    agent,
                    prompt
                )
            else:  # Default to Groq
                content = await loop.run_in_executor(
                    None,
                    self._generate_with_groq,
                    agent,
                    prompt
                )
            
            self.logger.info(f"[{agent_id}] Generated content using {provider} provider")
            return content
        except Exception as e:
            self.logger.error(f"[{agent_id}] Failed to generate content with {provider}: {e}")
            raise Exception(f"Content generation failed for {agent_id}: {e}")

    def validate_api_key(self) -> bool:
        """Validate that at least one provider API key is working"""
        groq_valid = False
        anthropic_valid = False
        
        # Test Groq
        if self.groq_client:
            try:
                completion = self.groq_client.chat.completions.create(
                    model=self.config.default_model,
                    messages=[{"role": "user", "content": "test"}],
                    max_tokens=1
                )
                groq_valid = completion.choices[0].message.content is not None
                self.logger.info("Groq API key validation: SUCCESS")
            except Exception as e:
                self.logger.warning(f"Groq API key validation failed: {e}")
        
        # Test Anthropic
        if self.anthropic_client:
            try:
                message = self.anthropic_client.messages.create(
                    model="claude-3-haiku-20240307",
                    max_tokens=1,
                    messages=[{"role": "user", "content": "test"}]
                )
                anthropic_valid = message.content[0].text is not None
                self.logger.info("Anthropic API key validation: SUCCESS")
            except Exception as e:
                self.logger.warning(f"Anthropic API key validation failed: {e}")
        
        if not groq_valid and not anthropic_valid:
            self.logger.error("No valid API keys found for any provider!")
            return False
            
        return True