from __future__ import annotations

import json

from app.llm.llm_schemas import Message
from app.workout_analysis.workout_schemas import AnalysisResult


SYSTEM_PROMPT = """
You are an experienced fitness coach.

Your task is to analyze a user's workout history based ONLY on the provided workout analysis.

Guidelines:

- Answer the user's question directly.
- Base your answer only on the provided analysis.
- Do not invent statistics or workouts.
- Explain your reasoning using the provided metrics.
- If there is insufficient information, clearly say so.
- Keep your answer practical, encouraging and concise.
""".strip()


class WorkoutPromptBuilder:

    def build(
        self,
        query: str,
        analysis: AnalysisResult,
    ) -> list:
        return [
            Message(
                role="system",
                content=SYSTEM_PROMPT,
            ),
            Message(
                role="user",
                content=(
                    f"User Question:\n"
                    f"{query}\n\n"
                    f"Workout Analysis:\n"
                    f"{json.dumps(analysis.model_dump(), indent=2)}"
                ),
            ),
        ]