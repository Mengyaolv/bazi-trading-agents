"""Retrievers and scoring helpers for Bazi case memories."""

import hashlib
import math
import os
import re
from datetime import datetime
from typing import Any, Dict, Iterable, List, Optional, Sequence, Tuple


ELEMENTS = {"木", "火", "土", "金", "水"}
STEMS = {"甲", "乙", "丙", "丁", "戊", "己", "庚", "辛", "壬", "癸"}
ENGLISH_STEMS = {
    "jia": "甲",
    "yi": "乙",
    "bing": "丙",
    "ding": "丁",
    "wu": "戊",
    "ji": "己",
    "geng": "庚",
    "xin": "辛",
    "ren": "壬",
    "gui": "癸",
}
ENGLISH_ELEMENTS = {
    "wood": "木",
    "fire": "火",
    "earth": "土",
    "metal": "金",
    "water": "水",
}
MOJIBAKE_MARKERS = ("锛", "鈫", "鍏", "鐢", "涓", "闆", "鏃", "熸", "€", "�")
ABSOLUTE_RISK_PATTERNS = (
    "必然发生",
    "注定失败",
    "注定离婚",
    "一定离婚",
    "必有灾祸",
    "绝对会",
    "必死",
    "必破产",
)


def text_hash(text: str) -> str:
    return hashlib.sha256(text.encode("utf-8")).hexdigest()


def as_float(value: Any, default: float) -> float:
    try:
        return float(value)
    except (TypeError, ValueError):
        return default


def clamp(value: float, minimum: float = 0.0, maximum: float = 1.0) -> float:
    return max(minimum, min(maximum, value))


def truthy(value: Any) -> bool:
    return str(value).strip().lower() in {"1", "true", "yes", "on"}


def get_config_value(config: Dict[str, Any], key: str, default: Any = None) -> Any:
    return config.get(key) if key in config else os.environ.get(key.upper(), default)


def jaccard(left: Iterable[str], right: Iterable[str]) -> float:
    left_set = {item for item in left if item}
    right_set = {item for item in right if item}
    if not left_set and not right_set:
        return 0.0
    if not left_set or not right_set:
        return 0.0
    return len(left_set & right_set) / len(left_set | right_set)


def cosine_similarity(left: Sequence[float], right: Sequence[float]) -> float:
    if not left or not right or len(left) != len(right):
        return 0.0
    dot = sum(a * b for a, b in zip(left, right))
    left_norm = math.sqrt(sum(a * a for a in left))
    right_norm = math.sqrt(sum(b * b for b in right))
    if left_norm == 0 or right_norm == 0:
        return 0.0
    return clamp((dot / (left_norm * right_norm) + 1.0) / 2.0)


def has_quality_risk(text: str) -> bool:
    marker_count = sum(text.count(marker) for marker in MOJIBAKE_MARKERS)
    if marker_count >= 2:
        return True
    if any(pattern in text for pattern in ABSOLUTE_RISK_PATTERNS):
        return True
    if "%" in text and any(keyword in text for keyword in ("研究表明", "数据显示", "实验显示")):
        return True
    return False


class KeywordRetriever:
    """Chinese-friendly keyword retriever with optional jieba segmentation."""

    def __init__(self) -> None:
        try:
            import jieba  # type: ignore
        except Exception:
            self._jieba = None
        else:
            self._jieba = jieba

    def tokens(self, text: str) -> List[str]:
        text = (text or "").lower()
        if self._jieba is not None:
            return [
                token.strip()
                for token in self._jieba.cut(text)
                if token.strip() and not token.isspace()
            ]

        tokens = re.findall(r"[a-z0-9]+", text)
        chinese_chars = re.findall(r"[\u4e00-\u9fff]", text)
        tokens.extend(chinese_chars)
        tokens.extend(
            "".join(pair)
            for pair in zip(chinese_chars, chinese_chars[1:])
        )
        return tokens

    def score(self, query: str, candidate: str) -> float:
        return jaccard(self.tokens(query), self.tokens(candidate))


class EmbeddingRetriever:
    """Optional SiliconFlow embedding adapter. Disabled unless configured."""

    def __init__(self, config: Dict[str, Any], client: Any = None) -> None:
        self.config = config
        self.client = client
        self.enabled = truthy(get_config_value(config, "embedding_enabled", "false"))
        self.provider = str(get_config_value(config, "embedding_provider", "siliconflow")).lower()
        self.model = get_config_value(config, "embedding_model", "")
        self.base_url = get_config_value(
            config,
            "embedding_base_url",
            "https://api.siliconflow.cn/v1/embeddings",
        )
        self.api_key = (
            config.get("embedding_api_key")
            or os.environ.get("SILICONFLOW_API_KEY")
        )

    def is_available(self) -> bool:
        if not self.enabled:
            return False
        if self.client is not None:
            return True
        return self.provider == "siliconflow" and bool(self.model and self.api_key and self.base_url)

    def embed(self, text: str) -> Optional[List[float]]:
        if not self.is_available() or not text:
            return None
        try:
            if self.client is not None:
                return self.client.embed(text)

            import requests

            response = requests.post(
                self.base_url,
                headers={
                    "Authorization": f"Bearer {self.api_key}",
                    "Content-Type": "application/json",
                },
                json={"model": self.model, "input": text},
                timeout=20,
            )
            response.raise_for_status()
            payload = response.json()
            data = payload.get("data") or []
            if not data:
                return None
            embedding = data[0].get("embedding")
            if not isinstance(embedding, list):
                return None
            return [float(value) for value in embedding]
        except Exception:
            return None


class StructuredRetriever:
    """Scores memories using text, Bazi features, quality, and recency."""

    def __init__(
        self,
        keyword_retriever: Optional[KeywordRetriever] = None,
        embedding_retriever: Optional[EmbeddingRetriever] = None,
    ) -> None:
        self.keyword_retriever = keyword_retriever or KeywordRetriever()
        self.embedding_retriever = embedding_retriever

    def extract_features(self, text: str, metadata: Optional[Dict[str, Any]] = None) -> Dict[str, Any]:
        metadata = metadata or {}
        features = dict(metadata.get("birth_features") or {})
        features.update({
            key: value
            for key, value in metadata.items()
            if key in {
                "day_master",
                "dominant_elements",
                "useful_gods",
                "pattern",
                "luck_cycle",
                "agent_type",
                "tags",
            }
            and value
        })

        if not features.get("day_master"):
            features["day_master"] = self._extract_day_master(text)
        if not features.get("dominant_elements"):
            features["dominant_elements"] = self._extract_dominant_elements(text)
        if not features.get("useful_gods"):
            features["useful_gods"] = self._extract_useful_gods(text)
        if not features.get("pattern"):
            features["pattern"] = self._extract_line_value(text, ("格局", "Pattern"))
        if not features.get("luck_cycle"):
            features["luck_cycle"] = self._extract_line_value(text, ("大运", "Luck Cycle", "当前阶段"))
        if not features.get("tags"):
            features["tags"] = []
        return normalize_features(features)

    def score_memory(
        self,
        query: str,
        query_features: Dict[str, Any],
        memory: Dict[str, Any],
        query_embedding: Optional[List[float]] = None,
    ) -> Tuple[float, Dict[str, float]]:
        keyword_score = self.keyword_retriever.score(query, memory.get("situation", ""))
        embedding_score = 0.0
        if query_embedding and memory.get("embedding"):
            embedding_score = cosine_similarity(query_embedding, memory["embedding"])
        text_score = (keyword_score * 0.5 + embedding_score * 0.5) if embedding_score else keyword_score

        memory_features = memory.get("birth_features") or {}
        structure_score = self._structure_score(query_features, memory_features)
        luck_score = self._luck_score(query_features, memory_features)
        quality_score = clamp(as_float(memory.get("quality_score"), 0.6))
        recency_score = self._recency_score(memory.get("timestamp"))

        total = (
            0.20 * text_score
            + 0.40 * structure_score
            + 0.15 * luck_score
            + 0.15 * quality_score
            + 0.10 * recency_score
        )
        return total, {
            "keyword_score": keyword_score,
            "embedding_score": embedding_score,
            "text_score": text_score,
            "structure_score": structure_score,
            "luck_score": luck_score,
            "quality_score": quality_score,
            "recency_score": recency_score,
            "total_score": total,
        }

    def _extract_day_master(self, text: str) -> str:
        match = re.search(r"日主\s*[:：]?\s*([甲乙丙丁戊己庚辛壬癸])", text)
        if match:
            return match.group(1)
        match = re.search(r"Day Master\s*[:：]?\s*([A-Za-z]+)", text, re.I)
        if match:
            return ENGLISH_STEMS.get(match.group(1).lower(), "")
        return ""

    def _extract_dominant_elements(self, text: str) -> List[str]:
        counts = {element: text.count(element) for element in ELEMENTS}
        lowered = text.lower()
        for word, element in ENGLISH_ELEMENTS.items():
            counts[element] += lowered.count(word)
        ordered = sorted(counts.items(), key=lambda item: item[1], reverse=True)
        return [element for element, count in ordered if count > 0][:3]

    def _extract_useful_gods(self, text: str) -> List[str]:
        useful: List[str] = []
        for match in re.finditer(r"(?:用神|喜用|Useful God|Primary Useful God)[^\n。；;:：]*[:：]?\s*([甲乙丙丁戊己庚辛壬癸木火土金水A-Za-z /、,，]+)", text, re.I):
            useful.extend(extract_elements_and_stems(match.group(1)))
        return unique_list(useful)

    def _extract_line_value(self, text: str, labels: Sequence[str]) -> str:
        for label in labels:
            pattern = re.compile(rf"{re.escape(label)}\s*[:：]?\s*([^\n\r]+)", re.I)
            match = pattern.search(text)
            if match:
                return match.group(1).strip()[:80]
        return ""

    def _structure_score(self, left: Dict[str, Any], right: Dict[str, Any]) -> float:
        parts = []
        parts.append(1.0 if left.get("day_master") and left.get("day_master") == right.get("day_master") else 0.0)
        parts.append(jaccard(as_list(left.get("dominant_elements")), as_list(right.get("dominant_elements"))))
        parts.append(jaccard(as_list(left.get("useful_gods")), as_list(right.get("useful_gods"))))
        parts.append(substring_score(left.get("pattern", ""), right.get("pattern", "")))
        parts.append(1.0 if left.get("agent_type") and left.get("agent_type") == right.get("agent_type") else 0.0)
        return sum(parts) / len(parts)

    def _luck_score(self, left: Dict[str, Any], right: Dict[str, Any]) -> float:
        return substring_score(left.get("luck_cycle", ""), right.get("luck_cycle", ""))

    def _recency_score(self, timestamp: Any) -> float:
        if not timestamp:
            return 0.6
        try:
            created_at = datetime.fromisoformat(str(timestamp))
        except ValueError:
            return 0.6
        age_days = max((datetime.now() - created_at).days, 0)
        if age_days <= 30:
            return 1.0
        if age_days >= 365:
            return 0.3
        return 1.0 - (age_days - 30) / 335 * 0.7


def normalize_features(features: Optional[Dict[str, Any]]) -> Dict[str, Any]:
    features = dict(features or {})
    return {
        "day_master": str(features.get("day_master") or "").strip(),
        "dominant_elements": unique_list(extract_elements_and_stems(features.get("dominant_elements"))),
        "useful_gods": unique_list(extract_elements_and_stems(features.get("useful_gods"))),
        "pattern": str(features.get("pattern") or "").strip(),
        "luck_cycle": str(features.get("luck_cycle") or "").strip(),
        "agent_type": str(features.get("agent_type") or "").strip(),
        "tags": unique_list(as_list(features.get("tags"))),
    }


def extract_elements_and_stems(value: Any) -> List[str]:
    if isinstance(value, list):
        text = " ".join(str(item) for item in value)
    else:
        text = str(value or "")
    items = [char for char in text if char in ELEMENTS or char in STEMS]
    lowered = text.lower()
    for word, element in ENGLISH_ELEMENTS.items():
        if word in lowered:
            items.append(element)
    for word, stem in ENGLISH_STEMS.items():
        if word in lowered:
            items.append(stem)
    return items


def as_list(value: Any) -> List[str]:
    if value is None:
        return []
    if isinstance(value, list):
        return [str(item) for item in value if str(item)]
    if isinstance(value, tuple) or isinstance(value, set):
        return [str(item) for item in value if str(item)]
    return [str(value)] if str(value) else []


def unique_list(values: Iterable[str]) -> List[str]:
    seen = set()
    result = []
    for value in values:
        item = str(value).strip()
        if item and item not in seen:
            seen.add(item)
            result.append(item)
    return result


def substring_score(left: str, right: str) -> float:
    left = str(left or "").strip()
    right = str(right or "").strip()
    if not left or not right:
        return 0.0
    if left == right:
        return 1.0
    if left in right or right in left:
        return 0.8
    return jaccard(KeywordRetriever().tokens(left), KeywordRetriever().tokens(right))
