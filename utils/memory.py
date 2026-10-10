import json
from pathlib import Path
from typing import Any, Dict, List, Optional
from datetime import datetime

try:
    from env_loader import load_env_file
except Exception:
    load_env_file = None

from .memory_retrievers import (
    EmbeddingRetriever,
    KeywordRetriever,
    StructuredRetriever,
    as_float,
    clamp,
    get_config_value,
    has_quality_risk,
    normalize_features,
    text_hash,
)


DEFAULT_QUALITY_SCORE = 0.6
SCHEMA_VERSION = 2


class BaziAnalysisMemory:
    """Case memory system for Bazi analysis agents."""

    def __init__(
        self,
        memory_name: str,
        config: Dict[str, Any],
        embedding_client: Any = None,
    ):
        """Initialize the memory system.

        Args:
            memory_name: Name of the memory (e.g., "traditional_memory")
            config: Configuration dictionary
            embedding_client: Optional test/client adapter for embeddings
        """
        if load_env_file is not None:
            load_env_file()

        self.memory_name = memory_name
        self.config = config or {}
        self.min_quality_score = clamp(
            as_float(
                get_config_value(
                    self.config,
                    "memory_min_quality_score",
                    0.4,
                ),
                0.4,
            )
        )

        self.memory_dir = Path(self.config.get("memory_dir", "./memory")) / memory_name
        self.memory_dir.mkdir(parents=True, exist_ok=True)
        self.memory_file = self.memory_dir / f"{memory_name}.json"

        self.embedding_retriever = EmbeddingRetriever(self.config, client=embedding_client)
        self.retriever = StructuredRetriever(
            keyword_retriever=KeywordRetriever(),
            embedding_retriever=self.embedding_retriever,
        )
        self.memories = self._load_memories()

    def _load_memories(self) -> List[Dict[str, Any]]:
        """Load memories from file and normalize old records."""
        if not self.memory_file.exists():
            return []
        try:
            with open(self.memory_file, "r", encoding="utf-8") as f:
                payload = json.load(f)
        except Exception as e:
            print(f"Error loading memories: {e}")
            return []

        if isinstance(payload, dict):
            raw_memories = payload.get("memories", [])
        elif isinstance(payload, list):
            raw_memories = payload
        else:
            raw_memories = []

        normalized = []
        for memory in raw_memories:
            if isinstance(memory, dict):
                normalized.append(self._normalize_memory(memory))
        return normalized

    def _save_memories(self):
        """Save memories to file."""
        try:
            with open(self.memory_file, "w", encoding="utf-8") as f:
                json.dump(self.memories, f, indent=2, ensure_ascii=False)
        except Exception as e:
            print(f"Error saving memories: {e}")

    def add_memory(
        self,
        situation: str,
        recommendation: str,
        outcome: str = None,
        metadata: Dict[str, Any] = None,
        birth_features: Dict[str, Any] = None,
        agent_type: str = None,
        quality_score: float = None,
        outcome_score: float = None,
        tags: List[str] = None,
    ) -> Dict[str, Any]:
        """Add a new case memory.

        Existing callers can still pass only situation and recommendation.
        """
        metadata = metadata or {}
        feature_source = dict(metadata)
        if birth_features:
            feature_source["birth_features"] = birth_features
        if agent_type:
            feature_source["agent_type"] = agent_type
        if tags:
            feature_source["tags"] = tags

        memory = {
            "schema_version": SCHEMA_VERSION,
            "timestamp": datetime.now().isoformat(),
            "situation": situation,
            "recommendation": recommendation,
            "outcome": outcome,
            "metadata": metadata,
            "birth_features": self.retriever.extract_features(situation, feature_source),
            "agent_type": agent_type or feature_source.get("agent_type", ""),
            "quality_score": clamp(as_float(quality_score, DEFAULT_QUALITY_SCORE)),
            "outcome_score": (
                clamp(as_float(outcome_score, DEFAULT_QUALITY_SCORE))
                if outcome_score is not None
                else None
            ),
            "tags": tags or feature_source.get("tags", []),
            "embedding": None,
            "embedding_text_hash": None,
        }
        memory["birth_features"]["agent_type"] = memory["agent_type"]
        memory["birth_features"]["tags"] = memory["tags"]

        self._ensure_embedding(memory)
        self.memories.append(memory)
        self._save_memories()
        return memory

    def get_memories(
        self,
        situation: str,
        n_matches: int = 3,
        birth_features: Dict[str, Any] = None,
        agent_type: str = None,
        min_quality_score: float = None,
    ) -> List[Dict[str, Any]]:
        """Get relevant memories using structured case retrieval."""
        threshold = self.min_quality_score if min_quality_score is None else min_quality_score
        query_features = self.retriever.extract_features(
            situation,
            {
                "birth_features": birth_features or {},
                "agent_type": agent_type or "",
            },
        )
        query_embedding = self._embed_query(situation)

        embeddings_changed = False
        scored_memories = []
        for memory in self.memories:
            if self._should_filter(memory, threshold):
                continue
            embeddings_changed = self._ensure_embedding(memory) or embeddings_changed
            score, details = self.retriever.score_memory(
                situation,
                query_features,
                memory,
                query_embedding=query_embedding,
            )
            scored_memories.append((score, details, memory))

        if embeddings_changed:
            self._save_memories()

        scored_memories.sort(key=lambda item: item[0], reverse=True)
        results = []
        for score, details, memory in scored_memories[:n_matches]:
            result = dict(memory)
            result["retrieval_score"] = score
            result["retrieval_details"] = details
            results.append(result)
        return results

    def update_outcome(
        self,
        memory_index: int,
        outcome: str,
        outcome_score: float = None,
    ):
        """Update the outcome and optional outcome score of a memory."""
        if 0 <= memory_index < len(self.memories):
            self.memories[memory_index]["outcome"] = outcome
            if outcome_score is not None:
                self.memories[memory_index]["outcome_score"] = clamp(
                    as_float(outcome_score, DEFAULT_QUALITY_SCORE)
                )
            self._save_memories()

    def clear_old_memories(self, days: int = 30):
        """Clear memories older than specified days."""
        from datetime import timedelta

        cutoff_date = datetime.now() - timedelta(days=days)
        cutoff_iso = cutoff_date.isoformat()

        self.memories = [
            m for m in self.memories if m["timestamp"] >= cutoff_iso
        ]
        self._save_memories()

    def get_memory_count(self) -> int:
        """Get the total number of memories."""
        return len(self.memories)

    def _normalize_memory(self, memory: Dict[str, Any]) -> Dict[str, Any]:
        metadata = memory.get("metadata")
        if not isinstance(metadata, dict):
            metadata = {}

        feature_source = dict(metadata)
        feature_source["birth_features"] = memory.get("birth_features") or metadata.get("birth_features") or {}
        if memory.get("agent_type"):
            feature_source["agent_type"] = memory.get("agent_type")
        if memory.get("tags"):
            feature_source["tags"] = memory.get("tags")

        normalized = {
            "schema_version": SCHEMA_VERSION,
            "timestamp": memory.get("timestamp") or datetime.now().isoformat(),
            "situation": str(memory.get("situation") or ""),
            "recommendation": str(memory.get("recommendation") or ""),
            "outcome": memory.get("outcome"),
            "metadata": metadata,
            "birth_features": self.retriever.extract_features(
                str(memory.get("situation") or ""),
                feature_source,
            ),
            "agent_type": str(memory.get("agent_type") or feature_source.get("agent_type") or ""),
            "quality_score": clamp(as_float(memory.get("quality_score"), DEFAULT_QUALITY_SCORE)),
            "outcome_score": (
                clamp(as_float(memory.get("outcome_score"), DEFAULT_QUALITY_SCORE))
                if memory.get("outcome_score") is not None
                else None
            ),
            "tags": memory.get("tags") or feature_source.get("tags") or [],
            "embedding": memory.get("embedding"),
            "embedding_text_hash": memory.get("embedding_text_hash"),
        }
        normalized["birth_features"] = normalize_features(normalized["birth_features"])
        normalized["birth_features"]["agent_type"] = normalized["agent_type"]
        normalized["birth_features"]["tags"] = normalized["tags"]
        return normalized

    def _should_filter(self, memory: Dict[str, Any], min_quality_score: float) -> bool:
        if clamp(as_float(memory.get("quality_score"), DEFAULT_QUALITY_SCORE)) < min_quality_score:
            return True
        combined_text = f"{memory.get('situation', '')}\n{memory.get('recommendation', '')}"
        return has_quality_risk(combined_text)

    def _embedding_text(self, memory: Dict[str, Any]) -> str:
        return f"{memory.get('situation', '')}\n{memory.get('recommendation', '')}".strip()

    def _ensure_embedding(self, memory: Dict[str, Any]) -> bool:
        if not self.embedding_retriever.is_available():
            return False
        text = self._embedding_text(memory)
        if not text:
            return False
        current_hash = text_hash(text)
        if memory.get("embedding") and memory.get("embedding_text_hash") == current_hash:
            return False

        embedding = self.embedding_retriever.embed(text)
        if not embedding:
            return False
        memory["embedding"] = embedding
        memory["embedding_text_hash"] = current_hash
        return True

    def _embed_query(self, situation: str) -> Optional[List[float]]:
        if not self.embedding_retriever.is_available():
            return None
        return self.embedding_retriever.embed(situation)
