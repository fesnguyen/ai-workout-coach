from app.application_container import ApplicationContainer
from evaluation.judges.workout_analysis.faithfulness_judge import FaithfulnessJudge
from evaluation.judges.workout_analysis.analysis_coverage import AnalysisCoverageJudge
from evaluation.judges.workout_analysis.recommendation_judge import RecommendationJudge
def build_workout_judges(
    container: ApplicationContainer,
):
    return [
        # FaithfulnessJudge(container.generator),
        AnalysisCoverageJudge(),
        RecommendationJudge(),
    ]