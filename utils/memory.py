import json
import os
from pathlib import Path
from typing import List, Dict, Any
from datetime import datetime


class BaziAnalysisMemory:
    """Memory system for Bazi analysis agents."""

    def __init__(self, memory_name: str, config: Dict[str, Any]):
        """Initialize the memory system.

        Args:
            memory_name: Name of the memory (e.g., "traditional_memory", "psychology_memory")
            config: Configuration dictionary
        """
        self.memory_name = memory_name
        self.config = config

        # Create memory directory
        self.memory_dir = Path(config.get("memory_dir", "./memory")) / memory_name
        self.memory_dir.mkdir(parents=True, exist_ok=True)

        # Memory file
        self.memory_file = self.memory_dir / f"{memory_name}.json"

        # Load existing memories
        self.memories = self._load_memories()

    def _load_memories(self) -> List[Dict[str, Any]]:
        """Load memories from file."""
        if self.memory_file.exists():
            try:
                with open(self.memory_file, "r", encoding="utf-8") as f:
                    return json.load(f)
            except Exception as e:
                print(f"Error loading memories: {e}")
                return []
        return []

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
    ):
        """Add a new memory.

        Args:
            situation: The situation/context
            recommendation: The recommendation made
            outcome: The outcome (optional, for learning)
            metadata: Additional metadata
        """
        memory = {
            "timestamp": datetime.now().isoformat(),
            "situation": situation,
            "recommendation": recommendation,
            "outcome": outcome,
            "metadata": metadata or {},
        }

        self.memories.append(memory)
        self._save_memories()

    def get_memories(
        self, situation: str, n_matches: int = 3
    ) -> List[Dict[str, Any]]:
        """Get relevant memories based on situation.

        Args:
            situation: The current situation
            n_matches: Number of memories to return

        Returns:
            List of relevant memories
        """
        # Simple keyword matching (can be improved with embeddings)
        situation_words = set(situation.lower().split())

        scored_memories = []
        for memory in self.memories:
            memory_words = set(memory["situation"].lower().split())
            overlap = len(situation_words & memory_words)
            scored_memories.append((overlap, memory))

        # Sort by overlap score and return top n_matches
        scored_memories.sort(key=lambda x: x[0], reverse=True)
        return [memory for score, memory in scored_memories[:n_matches]]

    def update_outcome(self, memory_index: int, outcome: str):
        """Update the outcome of a memory.

        Args:
            memory_index: Index of the memory to update
            outcome: The outcome to set
        """
        if 0 <= memory_index < len(self.memories):
            self.memories[memory_index]["outcome"] = outcome
            self._save_memories()

    def clear_old_memories(self, days: int = 30):
        """Clear memories older than specified days.

        Args:
            days: Number of days to keep
        """
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
