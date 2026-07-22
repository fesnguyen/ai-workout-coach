from dataclasses import asdict
import json

from app.llm.base_generator import BaseGenerator
from app.llm.llm_schemas import GenerationRequest
from evaluation.models import (
    EvaluationContext,
    JudgeResult,
    WorkoutAnalysisCase,
)


SYSTEM_PROMPT = """
You are an expert evaluator for AI workout coaching systems.

Your task is to evaluate whether the generated response faithfully reflects
the workout analysis produced by the system.

Evaluate the response based on:

- Correctness
- Completeness
- Relevance
- Faithfulness to the analysis

The expected findings and recommendations are provided only as additional
guidance.

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


class FaithfulnessJudge:
    """
    Evaluates workout analysis responses using an LLM.
    """

    def __init__(
        self,
        generator: BaseGenerator,
    ) -> None:
        self._generator = generator

    async def evaluate(
        self,
        case: WorkoutAnalysisCase,
        context: EvaluationContext,
    ) -> JudgeResult:

        prompt = f"""
User Query:
{case.request.query}

Workout Analysis:
{json.dumps(context.analysis.model_dump(mode="json"), indent=2)}

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