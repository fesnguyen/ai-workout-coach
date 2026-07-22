from evaluation.judges.base_judge import BaseJudge
from evaluation.models import EvaluationContext, JudgeResult, SearchCase

from app.rag.rag_schemas import RAGResponse


class SourceJudge(BaseJudge):
    """
    Verifies that the RAG response includes supporting sources.
    """

    async def evaluate(
        self,
        case: SearchCase,
        context: EvaluationContext,
    ) -> JudgeResult:
        source_count = len(context.response.sources)

        if source_count == 0:
            return JudgeResult(
                passed=False,
                score=0.0,
                reason="No supporting sources were returned.",
            )

        return JudgeResult(
            passed=True,
            score=5.0,
            reason=f"{source_count} supporting source(s) returned.",
        )