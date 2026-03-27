from app.models.entities import Scan


class ReportService:
    def build_json_report(self, scan: Scan) -> dict:
        return {
            "scan_id": scan.id,
            "scan_type": scan.scan_type,
            "source": scan.source,
            "recommendation": scan.recommendation,
            "summary": scan.summary,
            "findings": [
                {
                    "id": f.id,
                    "title": f.title,
                    "category": f.category,
                    "severity": f.severity,
                    "confidence": f.confidence,
                    "rule_id": f.rule_id,
                    "file_path": f.file_path,
                    "line_number": f.line_number,
                    "snippet": f.snippet,
                    "remediation": f.remediation,
                    "cwe": f.cwe,
                    "cwe_name": f.cwe_name,
                    "cvss_score": f.cvss_score,
                    "cvss_severity": f.cvss_severity,
                }
                for f in scan.findings
            ],
        }

    def build_markdown_report(self, scan: Scan) -> str:
        lines = [
            f"# Scan Report #{scan.id}",
            f"- Type: `{scan.scan_type}`",
            f"- Source: `{scan.source}`",
            f"- Recommendation: **{scan.recommendation}**",
            f"- Total Findings: **{scan.summary.get('total', 0)}**",
            "",
            "## Severity Breakdown",
        ]
        for sev, count in scan.summary.get("severity", {}).items():
            lines.append(f"- {sev.title()}: {count}")
        lines.append("\n## Findings")
        for f in scan.findings:
            lines.extend(
                [
                    f"### [{f.severity.upper()}] {f.title}",
                    f"- File: `{f.file_path}:{f.line_number}`",
                    f"- Rule: `{f.rule_id}`",
                    f"- Category: `{f.category}`",
                    f"- CWE: `{f.cwe or 'N/A'}` ({f.cwe_name or 'Unknown'})",
                    f"- CVSS-like score: `{f.cvss_score}` ({f.cvss_severity})",
                    f"- Snippet: `{f.snippet}`",
                    f"- Remediation: {f.remediation}",
                    "",
                ]
            )
        return "\n".join(lines)
