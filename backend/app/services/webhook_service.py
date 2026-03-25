from sqlalchemy.orm import Session

from app.models.entities import WebhookEvent
from app.services.scan_service import ScanService


class WebhookService:
    def __init__(self) -> None:
        self.scan_service = ScanService()

    def process(self, db: Session, payload: dict):
        event = WebhookEvent(event_type=payload.get("action", "unknown"), payload=payload)
        db.add(event)
        db.flush()
        diff_text = payload.get("pull_request", {}).get("diff_text", "")
        source = payload.get("pull_request", {}).get("html_url", "webhook")
        scan = self.scan_service.scan_diff(db, diff_text, source)
        return event, scan
