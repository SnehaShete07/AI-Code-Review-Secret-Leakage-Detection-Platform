from __future__ import annotations

from dataclasses import asdict
from pathlib import Path

from sqlalchemy.orm import Session

from app.llm.factory import get_llm_provider
from app.models.entities import Finding, Repository, Scan
from app.policies.engine import PolicyEngine
from app.scanners.dependency_scanner import DependencyScanner
from app.scanners.rule_scanner import RuleScanner
from app.scanners.secret_scanner import SecretScanner
from app.utils.cwe import cwe_name
from app.utils.diff import parse_unified_diff
from app.utils.files import iter_files


class ScanService:
    def __init__(self) -> None:
        self.secret_scanner = SecretScanner()
        self.rule_scanner = RuleScanner()
        self.dep_scanner = DependencyScanner()
        self.policy = PolicyEngine()
        self.llm = get_llm_provider()

    def _persist_findings(self, db: Session, scan: Scan, matches: list[dict]) -> list[Finding]:
        created: list[Finding] = []
        for m in matches:
            policy = self.policy.classify(m["category"], m["confidence"])
            llm = self.llm.explain_finding(m["title"], m["category"], m["snippet"])
            finding = Finding(
                scan_id=scan.id,
                title=m["title"],
                category=m["category"],
                severity=policy.severity,
                confidence=m["confidence"],
                rule_id=m["rule_id"],
                file_path=m["file_path"],
                line_number=m["line_number"],
                snippet=m["snippet"],
                explanation=llm.explanation,
                remediation=llm.remediation,
                cwe=m.get("cwe"),
                cwe_name=cwe_name(m.get("cwe")),
                policy_rationale=policy.rationale,
                cvss_score=policy.cvss_score,
                cvss_severity=policy.cvss_severity,
            )
            db.add(finding)
            created.append(finding)
        db.flush()
        scan.recommendation = self.policy.merge_recommendation([f.severity for f in created])
        scan.summary = self._build_summary(created)
        return created

    def _build_summary(self, findings: list[Finding]) -> dict:
        buckets = {"critical": 0, "high": 0, "medium": 0, "low": 0}
        categories: dict[str, int] = {}
        cvss_values: list[float] = []
        for f in findings:
            buckets[f.severity] = buckets.get(f.severity, 0) + 1
            categories[f.category] = categories.get(f.category, 0) + 1
            cvss_values.append(f.cvss_score)
        avg_cvss = round(sum(cvss_values) / len(cvss_values), 2) if cvss_values else 0.0
        exposure_index = round((buckets["critical"] * 5 + buckets["high"] * 3 + buckets["medium"] * 2 + buckets["low"]) / max(len(findings), 1), 2)
        return {
            "total": len(findings),
            "severity": buckets,
            "categories": categories,
            "avg_cvss": avg_cvss,
            "exposure_index": exposure_index,
        }

    def scan_repository(self, db: Session, repo_path: str) -> Scan:
        repo = Repository(name=Path(repo_path).name, path=repo_path)
        db.add(repo)
        db.flush()
        scan = Scan(scan_type="repository", source=repo_path, repository_id=repo.id)
        db.add(scan)
        db.flush()
        matches: list[dict] = []
        for fpath in iter_files(repo_path):
            text = fpath.read_text(encoding="utf-8", errors="ignore")
            rel = str(fpath.relative_to(repo_path))
            matches.extend(asdict(x) for x in self.secret_scanner.scan_text(rel, text))
            matches.extend(asdict(x) for x in self.rule_scanner.scan_text(rel, text))
            matches.extend(asdict(x) for x in self.dep_scanner.scan(rel, text))
        self._persist_findings(db, scan, matches)
        db.commit()
        db.refresh(scan)
        return scan

    def scan_diff(self, db: Session, diff_text: str, source: str) -> Scan:
        scan = Scan(scan_type="diff", source=source)
        db.add(scan)
        db.flush()
        matches: list[dict] = []
        for dl in parse_unified_diff(diff_text):
            text = dl.content
            fp = dl.file_path
            for sm in self.secret_scanner.scan_text(fp, text):
                sm.line_number = dl.line_number
                matches.append(asdict(sm))
            for rm in self.rule_scanner.scan_text(fp, text):
                rm.line_number = dl.line_number
                matches.append(asdict(rm))
        self._persist_findings(db, scan, matches)
        db.commit()
        db.refresh(scan)
        return scan
