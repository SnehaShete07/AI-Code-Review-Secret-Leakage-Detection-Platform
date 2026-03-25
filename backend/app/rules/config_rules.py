from app.rules.base import BaseRule, RuleMatch


class ConfigSecurityRule(BaseRule):
    id = "config.security"
    title = "Insecure configuration"
    category = "auth"

    def match(self, file_path: str, content: str) -> list[RuleMatch]:
        matches: list[RuleMatch] = []
        for i, line in enumerate(content.splitlines(), start=1):
            low = line.lower()
            if "yaml.load(" in low and "safe_load" not in low:
                matches.append(
                    RuleMatch(
                        title="Unsafe YAML deserialization",
                        category="injection",
                        rule_id="config.yaml.unsafe_load",
                        file_path=file_path,
                        line_number=i,
                        snippet=line.strip(),
                        confidence=0.89,
                        cwe="CWE-502",
                    )
                )
            if "allow_origins=['*']" in low or 'allow_origins=["*"]' in low:
                matches.append(
                    RuleMatch(
                        title="Overly broad CORS policy",
                        category="auth",
                        rule_id="config.cors.broad",
                        file_path=file_path,
                        line_number=i,
                        snippet=line.strip(),
                        confidence=0.73,
                        cwe="CWE-942",
                    )
                )
            if "password=" in low and "example" not in low:
                matches.append(
                    RuleMatch(
                        title="Hardcoded password in config",
                        category="secret",
                        rule_id="config.hardcoded.password",
                        file_path=file_path,
                        line_number=i,
                        snippet=line.strip(),
                        confidence=0.8,
                        cwe="CWE-798",
                    )
                )
        return matches
