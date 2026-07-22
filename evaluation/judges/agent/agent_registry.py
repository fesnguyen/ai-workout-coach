from app.application_container import ApplicationContainer
from evaluation.judges.agent.faithfulness_judge import FaithfulnessJudge
from evaluation.judges.agent.fact_coverage_judge import FactCoverageJudge


def build_agent_judges(
    container: ApplicationContainer,
):
    return [
        FaithfulnessJudge(container.generator),
        FactCoverageJudge(),
    ]