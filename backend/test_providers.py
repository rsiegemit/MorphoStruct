#!/usr/bin/env python3
"""
Quick test script to verify multi-provider LLM abstraction.

Usage:
    python test_providers.py
"""

import asyncio
import sys
from pathlib import Path

# Add backend to path
sys.path.insert(0, str(Path(__file__).parent))

from app.llm.providers import (
    LLMClientFactory,
    LLMProvider,
    LLMMessage,
)
from app.config import get_settings


async def test_provider(provider: LLMProvider):
    """Test a specific provider."""
    settings = get_settings()

    # Get API key for provider
    if provider == LLMProvider.ANTHROPIC:
        api_key = settings.anthropic_api_key
        if not api_key:
            print(f"❌ Skipping {provider.value}: No API key configured")
            return False
    elif provider == LLMProvider.OPENAI:
        api_key = settings.openai_api_key
        if not api_key:
            print(f"❌ Skipping {provider.value}: No API key configured")
            return False
    else:
        print(f"❌ Unknown provider: {provider}")
        return False

    print(f"\n🧪 Testing {provider.value.upper()} provider...")

    try:
        # Create client
        client = LLMClientFactory.create(provider, api_key)
        print(f"  ✓ Client created successfully")

        # Test simple chat
        messages = [
            LLMMessage(role="user", content="Say 'Hello from SHED!' and nothing else.")
        ]

        response = await client.chat_async(
            messages=messages,
            system="You are a helpful assistant. Be concise.",
            max_tokens=50,
        )

        print(f"  ✓ Response received: {response.text[:50]}...")
        print(f"  ✓ Tool calls: {len(response.tool_calls)}")

        return True

    except ImportError as e:
        print(f"  ❌ Import error: {e}")
        print(f"     Install required package for {provider.value}")
        return False
    except Exception as e:
        print(f"  ❌ Error: {e}")
        return False


async def main():
    """Run provider tests."""
    print("=" * 60)
    print("Multi-Provider LLM Abstraction Test")
    print("=" * 60)

    settings = get_settings()
    print(f"\nConfigured provider: {settings.llm_provider}")
    print(f"Configured model: {settings.llm_model or '(default)'}")

    # Test Anthropic
    anthropic_ok = await test_provider(LLMProvider.ANTHROPIC)

    # Test OpenAI
    openai_ok = await test_provider(LLMProvider.OPENAI)

    # Summary
    print("\n" + "=" * 60)
    print("Summary:")
    print(f"  Anthropic: {'✓ PASS' if anthropic_ok else '✗ SKIP/FAIL'}")
    print(f"  OpenAI:    {'✓ PASS' if openai_ok else '✗ SKIP/FAIL'}")
    print("=" * 60)

    if not (anthropic_ok or openai_ok):
        print("\n⚠️  No providers available!")
        print("   Add API keys to .env file:")
        print("   - ANTHROPIC_API_KEY=sk-ant-...")
        print("   - OPENAI_API_KEY=sk-...")
        sys.exit(1)


if __name__ == "__main__":
    asyncio.run(main())
