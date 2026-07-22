from abc import ABC, abstractmethod

from tests.models import JudgeResult, SearchCase


class BaseJudge(ABC):
    """
    Evaluates whether a generated answer satisfies
    the expectations of a test case.
    """

    @abstractmethod
    async def evaluate(
        self,
        case: SearchCase,
        answer: str,
    ) -> JudgeResult:
        ...