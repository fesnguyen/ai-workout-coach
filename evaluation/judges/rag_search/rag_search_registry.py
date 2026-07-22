from app.application_container import ApplicationContainer

from .faithfulness_judge import FaithfulnessJudge
from .fact_coverage_judge import FactCoverageJudge
from .source_judge import SourceJudge


def build_rag_judges(
    container: ApplicationContainer,
):
    return [
        FaithfulnessJudge(container.generator),
        SourceJudge(),
        FactCoverageJudge(),
    ]