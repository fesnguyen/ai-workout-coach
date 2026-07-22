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

Evaluate whether the generated response correctly reflects the expected workout analysis.

Evaluation Criteria:

1. Correctness
- Does the generated response correctly answer the user's question?

2. Findings Coverage
- Does it include the important findings?
- Exact wording is NOT required.
- Semantic equivalence is sufficient.

3. Recommendation Coverage
- Does it include the important recommendations?
- Similar advice should be considered correct.

4. Faithfulness
- Does the response avoid contradicting the expected analysis?
- Does it avoid inventing unsupported conclusions?

Return ONLY valid JSON:

{
    "passed": true,
    "score": 5,
    "reason": "..."
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

Expected Findings:
{json.dumps(case.expected.findings, indent=2)}

Expected Recommendations:
{json.dumps(case.expected.recommendations, indent=2)}

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