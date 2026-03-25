from datetime import datetime

from pydantic import BaseModel, Field


class FindingOut(BaseModel):
    id: int
    title: str
    category: str
    severity: str
    confidence: float
    rule_id: str
    file_path: str
    line_number: int
    snippet: str
    explanation: str
    remediation: str
    cwe: str | None
    policy_rationale: str

    class Config:
        from_attributes = True


class ScanOut(BaseModel):
    id: int
    scan_type: str
    source: str
    status: str
    recommendation: str
    summary: dict
    created_at: datetime
    findings: list[FindingOut] = Field(default_factory=list)

    class Config:
        from_attributes = True


class RepoScanRequest(BaseModel):
    repo_path: str


class DiffScanRequest(BaseModel):
    diff_text: str
    source: str = "manual-diff"


class WebhookSimulationRequest(BaseModel):
    payload: dict


class ScanSummaryOut(BaseModel):
    scan: ScanOut
    pr_summary: str
    comments: list[str]


class ReportOut(BaseModel):
    scan_id: int
    json_report: dict
    markdown_report: str
