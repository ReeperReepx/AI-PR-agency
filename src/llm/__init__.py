"""
LLM-assisted reasoning module (Phase 5).

LLMs advise, they never decide. All AI outputs are supplementary
to the deterministic matching logic.
"""

from src.llm.provider import LLMProvider
from src.llm.mock import MockLLMProvider
from src.llm.service import get_llm_provider

__all__ = ["LLMProvider", "MockLLMProvider", "get_llm_provider"]
