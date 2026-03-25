from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session, joinedload

from app.core.database import get_db
from app.models.entities import Scan
from app.schemas.common import (
    DiffScanRequest,
    ReportOut,
    RepoScanRequest,
    ScanOut,
    ScanSummaryOut,
    WebhookSimulationRequest,
)
from app.services.pr_service import PRReviewService
from app.services.report_service import ReportService
from app.services.scan_service import ScanService
from app.services.webhook_service import WebhookService

router = APIRouter(prefix="/api", tags=["scan"])
scan_service = ScanService()
report_service = ReportService()
pr_service = PRReviewService()
webhook_service = WebhookService()


@router.get("/health")
def health() -> dict:
    return {"status": "ok"}


@router.post("/scans/repository", response_model=ScanSummaryOut)
def scan_repository(req: RepoScanRequest, db: Session = Depends(get_db)):
    scan = scan_service.scan_repository(db, req.repo_path)
    scan = db.query(Scan).options(joinedload(Scan.findings)).get(scan.id)
    summary, comments = pr_service.summarize(scan)
    return {"scan": scan, "pr_summary": summary, "comments": comments}


@router.post("/scans/diff", response_model=ScanSummaryOut)
def scan_diff(req: DiffScanRequest, db: Session = Depends(get_db)):
    scan = scan_service.scan_diff(db, req.diff_text, req.source)
    scan = db.query(Scan).options(joinedload(Scan.findings)).get(scan.id)
    summary, comments = pr_service.summarize(scan)
    return {"scan": scan, "pr_summary": summary, "comments": comments}


@router.get("/scans", response_model=list[ScanOut])
def list_scans(db: Session = Depends(get_db)):
    scans = db.query(Scan).options(joinedload(Scan.findings)).order_by(Scan.id.desc()).all()
    return scans


@router.get("/scans/{scan_id}", response_model=ScanOut)
def get_scan(scan_id: int, db: Session = Depends(get_db)):
    scan = db.query(Scan).options(joinedload(Scan.findings)).get(scan_id)
    if not scan:
        raise HTTPException(status_code=404, detail="Scan not found")
    return scan


@router.get("/scans/{scan_id}/report", response_model=ReportOut)
def get_report(scan_id: int, db: Session = Depends(get_db)):
    scan = db.query(Scan).options(joinedload(Scan.findings)).get(scan_id)
    if not scan:
        raise HTTPException(status_code=404, detail="Scan not found")
    json_report = report_service.build_json_report(scan)
    markdown_report = report_service.build_markdown_report(scan)
    return {"scan_id": scan_id, "json_report": json_report, "markdown_report": markdown_report}


@router.post("/webhooks/github", response_model=ScanSummaryOut)
def simulate_webhook(req: WebhookSimulationRequest, db: Session = Depends(get_db)):
    _, scan = webhook_service.process(db, req.payload)
    scan = db.query(Scan).options(joinedload(Scan.findings)).get(scan.id)
    summary, comments = pr_service.summarize(scan)
    return {"scan": scan, "pr_summary": summary, "comments": comments}
