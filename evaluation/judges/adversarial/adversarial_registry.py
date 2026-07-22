from app.application_container import ApplicationContainer
from evaluation.judges.adversarial.guardrail_judge import GuardrailJudge


def build_adversarial_judges(
    container: ApplicationContainer,
):
    return [
        GuardrailJudge(container.generator),
    ]