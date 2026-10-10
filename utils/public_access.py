"""Bound public, user-funded analysis requests."""

from collections import defaultdict, deque
from contextlib import contextmanager
from threading import BoundedSemaphore, Lock
from time import monotonic


# URLs and models are selected by the server; visitors cannot supply an endpoint.
PROVIDERS = {
    "siliconflow": ("硅基流动", "deepseek-ai/DeepSeek-V3", "https://api.siliconflow.cn/v1"),
    "openai": ("OpenAI", "gpt-4o-mini", None),
    "anthropic": ("Anthropic", "claude-haiku-4-5-20251001", None),
}

_lock = Lock()
_requests = defaultdict(deque)
_global_requests = deque()
_active = BoundedSemaphore(3)
WINDOW_SECONDS = 3600
PER_USER_LIMIT = 6
GLOBAL_LIMIT = 60
MAX_BIRTH_INFO = 700
MAX_QUESTION = 300


def validate_request(provider: str, api_key: str, birth_info: str, question: str = ""):
    if provider not in PROVIDERS:
        raise ValueError("不支持该模型服务商")
    if not api_key or not api_key.strip() or len(api_key) > 512:
        raise ValueError("请输入有效的 API Key")
    if not birth_info or len(birth_info) > MAX_BIRTH_INFO:
        raise ValueError("出生信息过长或为空")
    if len(question) > MAX_QUESTION:
        raise ValueError("自定义问题不能超过 300 字")


@contextmanager
def analysis_slot(user_id: str):
    """Limit requests per account and process, plus simultaneous analyses."""
    if not user_id:
        raise ValueError("请先登录")
    if not _active.acquire(blocking=False):
        raise ValueError("当前分析人数较多，请稍后重试")
    try:
        now = monotonic()
        with _lock:
            recent = _requests[user_id]
            for bucket in (recent, _global_requests):
                while bucket and bucket[0] <= now - WINDOW_SECONDS:
                    bucket.popleft()
            if len(recent) >= PER_USER_LIMIT or len(_global_requests) >= GLOBAL_LIMIT:
                raise ValueError("请求过于频繁，请一小时后再试")
            recent.append(now)
            _global_requests.append(now)
        yield
    finally:
        _active.release()
