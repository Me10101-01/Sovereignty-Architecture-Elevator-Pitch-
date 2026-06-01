from abc import ABC, abstractmethod
from src.models.pipeline_state import PipelineState


class BasePass(ABC):
    @property
    def name(self) -> str:
        return self.__class__.__name__

    @abstractmethod
    def execute(self, state: PipelineState) -> PipelineState:
        """Read state, compute this pass's layer, mutate state, return it."""

    def __call__(self, state: PipelineState) -> PipelineState:
        result = self.execute(state)
        state.pass_log.append(f"[{self.name}] complete")
        return result
