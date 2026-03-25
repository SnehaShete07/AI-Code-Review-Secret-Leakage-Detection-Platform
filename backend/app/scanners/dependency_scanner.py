import json

from app.rules.base import RuleMatch


class DependencyScanner:
    RISKY_PACKAGES = {
        "python": {"pycrypto": "Unmaintained crypto library"},
        "node": {"serialize-javascript": "Historically associated with injection risks"},
    }

    def scan(self, file_path: str, content: str) -> list[RuleMatch]:
        findings: list[RuleMatch] = []
        if file_path.endswith("requirements.txt"):
            for idx, line in enumerate(content.splitlines(), start=1):
                pkg = line.split("==")[0].strip().lower()
                if pkg in self.RISKY_PACKAGES["python"]:
                    findings.append(
                        RuleMatch(
                            title=f"Dependency risk indicator: {pkg}",
                            category="dependency_hygiene",
                            rule_id="dep.python.risky",
                            file_path=file_path,
                            line_number=idx,
                            snippet=line,
                            confidence=0.72,
                            cwe="CWE-1104",
                        )
                    )
        if file_path.endswith("package.json"):
            try:
                parsed = json.loads(content)
            except json.JSONDecodeError:
                return findings
            deps = {**parsed.get("dependencies", {}), **parsed.get("devDependencies", {})}
            for pkg, version in deps.items():
                if pkg in self.RISKY_PACKAGES["node"]:
                    findings.append(
                        RuleMatch(
                            title=f"Dependency risk indicator: {pkg}",
                            category="dependency_hygiene",
                            rule_id="dep.node.risky",
                            file_path=file_path,
                            line_number=1,
                            snippet=f'{pkg}: {version}',
                            confidence=0.7,
                            cwe="CWE-1104",
                        )
                    )
        return findings
