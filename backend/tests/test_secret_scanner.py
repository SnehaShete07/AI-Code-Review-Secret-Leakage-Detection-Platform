from app.scanners.secret_scanner import SecretScanner
from app.utils.security import shannon_entropy


def test_secret_regex_detection():
    scanner = SecretScanner()
    text = 'TOKEN="ghp_abcdefghijklmnopqrstuvwxyz1234"'
    findings = scanner.scan_text(".env", text)
    assert findings
    assert findings[0].category == "secret"


def test_entropy_helper():
    low = shannon_entropy("aaaaaaaaaa")
    high = shannon_entropy("A1b2C3d4E5f6")
    assert high > low
