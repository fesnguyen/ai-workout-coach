from __future__ import annotations
import json

from app.agent.tools.base_tool import BaseTool
from app.workout_analysis.workout_service import WorkoutService


class WorkoutAnalyzerTool(BaseTool):
    """
    Answers questions about a user's workout history using the
    previously generated workout analysis.

    The analysis is produced by the Workout Analysis feature and stored
    on disk. This tool loads the user's analysis and generates an answer
    without recomputing workout metrics.
    """

    def __init__(
        self,
        workout_service: WorkoutService,
    ) -> None:
        self._workout_service = workout_service

    @property
    def name(self) -> str:
        return "analyze_workout_history"

    @property
    def openai_definition(self) -> dict:
        return {
            "type": "function",
            "name": self.name,
            "description": (
                "Answer questions about a user's workout history using "
                "their previously generated workout analysis."
            ),
            "parameters": {
                "type": "object",
                "properties": {
                    "user_id": {
                        "type": "string",
                        "description": (
                            "The identifier of the user whose workout "
                            "analysis should be used."
                        ),
                    },
                },
                "required": [
                    "user_id",
                ],
                "additionalProperties": False,
            },
            "strict": True,
        }

    async def invoke(
        self,
        arguments: dict[str, object],
    ) -> str:
        # Extract the tool arguments.
        user_id = str(arguments["user_id"])

        analysis_json = await self._workout_service.load_analysis(user_id=user_id)

        # Answer the question using the stored workout analysis.
        return analysis_json