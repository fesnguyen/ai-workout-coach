from abc import ABC, abstractmethod

from evaluation.models import (
    EvaluationContext,
    JudgeResult,
    SearchCase,
)


class BaseJudge(ABC):
    """
    Base class for all evaluation judges.
    """

    @abstractmethod
    async def evaluate(
        self,
        case: SearchCase,
        context: EvaluationContext,
    ) -> JudgeResult:
        """
        Evaluate one test case.
        """
        ...