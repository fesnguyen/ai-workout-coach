from __future__ import annotations

import json

from app.llm.llm_schemas import Message
from app.prompts.system_prompt_builder import SystemPromptBuilder
from app.workout_analysis.workout_schemas import AnalysisResult


ANALYZER_RESPONSE_RULE = """
Strictly follow these rules:

- Answer the user's question directly.
- Base your answer only on the provided analysis.
- Do not invent statistics or workouts.
- Explain your reasoning using the provided metrics.
- If there is insufficient information, clearly say so.
- Keep your answer practical, encouraging and concise.
""".strip()


class WorkoutPromptBuilder:

    def __init__(
        self,
        system_prompt_builder: SystemPromptBuilder,
    ) -> None:
        self.system_prompt_builder = system_prompt_builder

    def build(
        self,
        query: str,
        analysis: AnalysisResult,
    ) -> list[Message]:
        return [
            *self.system_prompt_builder.build_workout_analysis_prompt(),
            Message(
                role="system",
                content=ANALYZER_RESPONSE_RULE,
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