from app.application_container import ApplicationContainer
from evaluation.judges.workout_analysis.faithfulness_judge import FaithfulnessJudge

def build_workout_judges(
    container: ApplicationContainer,
):
    return [
        FaithfulnessJudge(container.generator),
    ]