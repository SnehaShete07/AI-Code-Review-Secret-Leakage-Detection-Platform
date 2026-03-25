from app.models.entities import Scan


class PRReviewService:
    def summarize(self, scan: Scan) -> tuple[str, list[str]]:
        sev = scan.summary.get("severity", {})
        summary = (
            f"PR Security Summary: {scan.summary.get('total', 0)} findings "
            f"(Critical={sev.get('critical',0)}, High={sev.get('high',0)}, "
            f"Medium={sev.get('medium',0)}, Low={sev.get('low',0)}). "
            f"Recommendation: {scan.recommendation}."
        )
        comments = []
        for f in scan.findings[:10]:
            comments.append(
                f"[{f.severity.upper()}] {f.title} in {f.file_path}:{f.line_number} — {f.remediation}"
            )
        return summary, comments
