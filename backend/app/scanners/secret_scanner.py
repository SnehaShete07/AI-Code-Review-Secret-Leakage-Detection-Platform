import re
from dataclasses import dataclass

from app.utils.security import mask_secret, shannon_entropy


@dataclass
class SecretMatch:
    title: str
    category: str
    rule_id: str
    file_path: str
    line_number: int
    snippet: str
    confidence: float
    cwe: str | None = "CWE-798"


class SecretScanner:
    ALLOWLIST = ["example", "changeme", "fake", "sample"]
    PATTERNS: list[tuple[re.Pattern[str], str]] = [
        (re.compile(r"AKIA[0-9A-Z]{16}"), "Possible AWS Access Key"),
        (re.compile(r"ghp_[A-Za-z0-9]{20,}"), "Possible GitHub Token"),
        (re.compile(r"sk-[A-Za-z0-9]{20,}"), "Possible OpenAI-style API Key"),
        (re.compile(r"xox[baprs]-[A-Za-z0-9-]{10,}"), "Possible Slack Token"),
        (re.compile(r"sk_live_[A-Za-z0-9]{16,}"), "Possible Stripe Live Key"),
        (re.compile(r"-----BEGIN (RSA |EC )?PRIVATE KEY-----"), "Private key material"),
        (re.compile(r"eyJ[A-Za-z0-9_-]{8,}\.[A-Za-z0-9_-]{8,}\.[A-Za-z0-9_-]{8,}"), "JWT-like token"),
        (re.compile(r"Bearer\s+[A-Za-z0-9._-]{16,}"), "Bearer token exposure"),
        (re.compile(r"(?i)(api[_-]?key|token|password)\s*[:=]\s*['\"]?[A-Za-z0-9_\-/.+=]{8,}"), "Generic secret assignment"),
    ]

    def scan_text(self, file_path: str, text: str) -> list[SecretMatch]:
        matches: list[SecretMatch] = []
        for i, line in enumerate(text.splitlines(), start=1):
            low = line.lower()
            if any(allow in low for allow in self.ALLOWLIST):
                continue
            for pattern, title in self.PATTERNS:
                found = pattern.search(line)
                if found:
                    token = found.group(0)
                    entropy = shannon_entropy(token)
                    confidence = 0.7 if entropy < 3.2 else 0.92
                    masked = line.replace(token, mask_secret(token))
                    matches.append(
                        SecretMatch(
                            title=title,
                            category="secret",
                            rule_id="secret.regex",
                            file_path=file_path,
                            line_number=i,
                            snippet=masked,
                            confidence=confidence,
                        )
                    )
        return matches
