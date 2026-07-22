from dataclasses import asdict
import json

from app.llm.base_generator import BaseGenerator
from app.llm.llm_schemas import GenerationRequest

from evaluation.judges.base_judge import BaseJudge
from evaluation.models import (
    AgentCase,
    EvaluationContext,
    JudgeResult,
)


SYSTEM_PROMPT = """
You are an expert evaluator for AI assistants.

Your task is to evaluate whether the generated response correctly answers the user's request.

Scoring criteria:
- Correctness
- Relevance
- Completeness
- Faithfulness

Use the expected answer and expected facts as guidance.

Return ONLY valid JSON in this format:

{
    "passed": true,
    "score": 4.5,
    "reason": "Brief explanation."
}

Rules:
- score must be between 0.0 and 5.0
- passed is true if score >= 4.0
- Do not include markdown.
- Do not include additional text.
"""


class FaithfulnessJudge(BaseJudge):
    """
    Evaluates generated agent responses using an LLM.
    """

    def __init__(
        self,
        generator: BaseGenerator,
    ) -> None:
        self._generator = generator

    async def evaluate(
        self,
        case: AgentCase,
        context: EvaluationContext,
    ) -> JudgeResult:

        prompt = f"""
User Query:
{case.request.message}

Expected:
{json.dumps(asdict(case.expected), indent=2)}

Generated Response:
{context.generated_response}
"""

        response = await self._generator.generate(
            GenerationRequest(
                messages=[
                    {
                        "role": "system",
                        "content": SYSTEM_PROMPT,
                    },
                    {
                        "role": "user",
                        "content": prompt,
                    },
                ],
                tool_definitions=[],
            )
        )

        try:
            result = json.loads(response.response)

            return JudgeResult(
                passed=result["passed"],
                score=float(result["score"]),
                reason=result["reason"],
            )

        except Exception:
            return JudgeResult(
                passed=False,
                score=0.0,
                reason="Judge failed to return valid JSON.",
            )