# Utils

from .memory import BaziAnalysisMemory

__all__ = ["BaziAnalysisMemory", "BaziAnalysisState", "BaziDebateState"]


def __getattr__(name):
    if name in {"BaziAnalysisState", "BaziDebateState"}:
        from .bazi_states import BaziAnalysisState, BaziDebateState

        return {
            "BaziAnalysisState": BaziAnalysisState,
            "BaziDebateState": BaziDebateState,
        }[name]
    raise AttributeError(f"module 'utils' has no attribute {name!r}")
