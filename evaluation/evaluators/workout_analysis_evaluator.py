from app.application_container import ApplicationContainer
from evaluation.models import EvaluationContext, EvaluationResult, WorkoutAnalysisCase
from pathlib import Path
import json
from app.api.api_schemas import UserProfile, WorkoutAnalyzeRequest
from evaluation.models import ExpectedWorkoutAnalysis

def load_workout_analysis_cases(
    filename: str,
) -> list[WorkoutAnalysisCase]:
    """
    Load workout analysis evaluation cases.

    The evaluation dataset references workout history files instead of
    embedding them directly. Each referenced fixture is loaded and used
    to construct a complete WorkoutAnalyzeRequest.
    """

    dataset_dir = Path(__file__).parent.parent / "datasets"

    # Load the evaluation dataset.
    with (dataset_dir / filename).open(
        "r",
        encoding="utf-8",
    ) as f:
        raw_cases = json.load(f)

    cases: list[WorkoutAnalysisCase] = []

    for case in raw_cases:

        # Resolve the workout history fixture path.
        workout_file = (
            dataset_dir
            / case["request"]["user_profile"]["workouts"]
        )

        # Load the user's workout history.
        with workout_file.open(
            "r",
            encoding="utf-8",
        ) as f:
            workout_data = json.load(f)

        # Build the request that will be passed to the analyzer.
        request = WorkoutAnalyzeRequest(
            query=case["request"]["query"],
            user_profile=UserProfile(**workout_data),
        )

        cases.append(
            WorkoutAnalysisCase(
                id=case["id"],
                request=request,
                expected=ExpectedWorkoutAnalysis(
                    **case["expected"]
                ),
            )
        )

    return cases


async def evaluate_workout_analysis(
    container: ApplicationContainer,
    judges: list,
) -> list[EvaluationResult]:

    workout_service = container.workout_service

    results: list[EvaluationResult] = []

    for case in load_workout_analysis_cases(
        "workout_analysis_cases.json",
    ):
        print(f"Evaluating {case.id}...")

        response = await workout_service.analyze(
            case.request,
        )

        context = EvaluationContext(
            generated_response=response.response,
        )

        for judge in judges:
            judge_result = await judge.evaluate(
                case=case,
                context=context,
            )

            results.append(
                EvaluationResult(
                    category="Workout Analysis",
                    case_id=case.id,
                    question=case.request.query,
                    judge=judge.__class__.__name__,
                    passed=judge_result.passed,
                    score=judge_result.score,
                    reason=judge_result.reason,
                    answer=response.response,
                )
            )

            status = (
                "PASS"
                if judge_result.passed
                else "FAIL"
            )

            print(
                f"  [{status}] "
                f"{judge.__class__.__name__} "
                f"({judge_result.score:.1f}/5)"
            )

    return results