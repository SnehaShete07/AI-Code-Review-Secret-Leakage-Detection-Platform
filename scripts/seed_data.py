from pathlib import Path
import sys

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "backend"))

from app.core.database import SessionLocal  # noqa: E402
from app.services.scan_service import ScanService  # noqa: E402


def main() -> None:
    db = SessionLocal()
    scan_service = ScanService()
    repo = str(ROOT / "demo" / "vulnerable_repo")
    scan = scan_service.scan_repository(db, repo)
    print(f"Seeded scan #{scan.id} with {scan.summary.get('total', 0)} findings")


if __name__ == "__main__":
    main()
