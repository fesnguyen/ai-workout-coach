"""
RAG guardrails.

Responsibilities
----------------
- Determine whether a query is allowed.
- Detect out-of-domain questions.
- Detect medical advice requests.
- Produce a standardized guardrail decision.

The guardrail intentionally performs NO:

- retrieval
- embedding
- generation

Pipeline
--------

User Query
      │
      ▼
RAGGuardrail
      │
      ├── Allow
      │
      └── Refuse
"""

from __future__ import annotations

from enum import Enum

from pydantic import BaseModel

from app.llm.base_generator import BaseGenerator
from app.llm.llm_schemas import GenerationRequest, Message


class GuardrailAction(str, Enum):
    """
    Guardrail decision.
    """

    ALLOW = "allow"

    OUT_OF_SCOPE = "out_of_scope"

    MEDICAL = "medical"

    UNSAFE = "unsafe"


class GuardrailDecision(BaseModel):
    """
    Result returned by the guardrail.
    """

    action: GuardrailAction

    reason: str


SYSTEM_PROMPT = """
You are a query safety classifier.

Classify the user's request into ONE category.

allow
- General fitness
- Exercise technique
- Strength training
- Nutrition education
- Recovery
- Programming
- Workout advice

out_of_scope
- Weather
- Politics
- Programming
- Movies
- General knowledge unrelated to fitness

medical
- Medical diagnosis
- Injury diagnosis
- Rehabilitation without professional assessment
- Eating disorder advice
- Prescription drugs
- Medical treatment

unsafe
- Self-harm
- Illegal activities

Return ONLY one JSON object.

{
    "action": "...",
    "reason": "..."
}
"""


class RAGGuardrail:
    """
    Query guardrail for the RAG pipeline.
    """

    def __init__(
        self,
        generator: BaseGenerator,
    ) -> None:
        self._generator = generator

    async def validate(
        self,
        query: str,
    ) -> GuardrailDecision:
        """
        Validate a user query.

        Returns
        -------
        GuardrailDecision
        """

        response = await self._generator.generate(
            GenerationRequest(
                input=[
                    Message(
                        role="system",
                        content=SYSTEM_PROMPT,
                    ),
                    Message(
                        role="user",
                        content=query,
                    ),
                ],
            )
        )

        return GuardrailDecision.model_validate_json(
            response.content,
        )

    @staticmethod
    def refusal_message(
        action: GuardrailAction,
    ) -> str:
        """
        Convert a guardrail decision into a user-facing response.
        """

        if action == GuardrailAction.OUT_OF_SCOPE:
            return (
                "I'm designed to answer fitness-related questions. "
                "Please ask about training, exercise, recovery, or nutrition."
            )

        if action == GuardrailAction.MEDICAL:
            return (
                "I can't provide medical advice or diagnose injuries. "
                "Please consult a qualified healthcare professional."
            )

        if action == GuardrailAction.UNSAFE:
            return (
                "I'm not able to assist with that request."
            )

        return ""