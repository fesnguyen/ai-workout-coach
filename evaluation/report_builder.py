from collections import defaultdict
from pathlib import Path

from evaluation.models import EvaluationResult


class ReportBuilder:
    """
    Builds a Markdown evaluation report.
    """

    def build(
        self,
        results: list[EvaluationResult],
        output: Path,
    ) -> None:
        lines: list[str] = []

        # Title
        lines.append("# Evaluation Report")
        lines.append("")

        # Summary
        total = len(results)
        passed = sum(result.passed for result in results)
        failed = total - passed

        average_score = (
            sum(result.score for result in results) / total
            if total
            else 0.0
        )

        lines.append("## Summary")
        lines.append("")
        lines.append(f"- Total Evaluations: {total}")
        lines.append(f"- Passed: {passed}")
        lines.append(f"- Failed: {failed}")
        lines.append(f"- Average Score: {average_score:.2f}/5.0")
        lines.append("")

        # Group by evaluation category
        grouped: dict[str, list[EvaluationResult]] = defaultdict(list)

        for result in results:
            grouped[result.category].append(result)

        for category, category_results in grouped.items():
            lines.append(f"## {category}")
            lines.append("")
            lines.append("| Case | Judge | Score | Passed |")
            lines.append("|------|-------|------:|:------:|")

            for result in category_results:
                status = "✅" if result.passed else "❌"

                lines.append(
                    f"| {result.case_id} "
                    f"| {result.judge} "
                    f"| {result.score:.1f} "
                    f"| {status} |"
                )

            lines.append("")

        # Failure details
        failures = [
            result
            for result in results
            if not result.passed
        ]

        if failures:
            lines.append("## Failure Analysis")
            lines.append("")

            for result in failures:
                lines.append(f"### {result.case_id}")
                lines.append("")
                lines.append(f"**Category:** {result.category}")
                lines.append("")
                lines.append(f"**Judge:** {result.judge}")
                lines.append("")
                lines.append(f"**Question:**")
                lines.append("")
                lines.append(result.question)
                lines.append("")
                lines.append(f"**Score:** {result.score:.1f}/5.0")
                lines.append("")
                lines.append("**Reason:**")
                lines.append("")
                lines.append(result.reason)
                lines.append("")
                lines.append("**Generated Answer:**")
                lines.append("")
                lines.append("```text")
                lines.append(result.answer)
                lines.append("```")
                lines.append("")

        output.write_text(
            "\n".join(lines),
            encoding="utf-8",
        )