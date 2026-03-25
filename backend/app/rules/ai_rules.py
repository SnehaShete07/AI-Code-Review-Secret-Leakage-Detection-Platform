from app.rules.base import BaseRule, RuleMatch


class AIAgentSecurityRule(BaseRule):
    id = "ai.agent.security"
    title = "AI/Agent security misconfiguration"
    category = "agent_security"

    def match(self, file_path: str, content: str) -> list[RuleMatch]:
        matches: list[RuleMatch] = []
        for i, line in enumerate(content.splitlines(), start=1):
            low = line.lower()
            if "ignore previous instructions" in low:
                matches.append(
                    RuleMatch(
                        title="Prompt injection phrase propagated",
                        category="prompt_security",
                        rule_id="ai.prompt.injection_phrase",
                        file_path=file_path,
                        line_number=i,
                        snippet=line.strip(),
                        confidence=0.86,
                        cwe="CWE-74",
                    )
                )
            if "prompt = \"" in line and "user_input" in line:
                matches.append(
                    RuleMatch(
                        title="Direct prompt concatenation with user input",
                        category="prompt_security",
                        rule_id="ai.prompt.concat_user_input",
                        file_path=file_path,
                        line_number=i,
                        snippet=line.strip(),
                        confidence=0.9,
                        cwe="CWE-20",
                    )
                )
            if "allow_shell: true" in low or "allow_network: true" in low:
                matches.append(
                    RuleMatch(
                        title="Over-permissioned AI agent tool access",
                        category="agent_security",
                        rule_id="ai.agent.over_permissioned",
                        file_path=file_path,
                        line_number=i,
                        snippet=line.strip(),
                        confidence=0.91,
                        cwe="CWE-250",
                    )
                )
            if "model_output_to_tool: direct" in low:
                matches.append(
                    RuleMatch(
                        title="Direct model-to-tool path without approval",
                        category="agent_security",
                        rule_id="ai.agent.direct_tool_path",
                        file_path=file_path,
                        line_number=i,
                        snippet=line.strip(),
                        confidence=0.89,
                        cwe="CWE-285",
                    )
                )
        return matches
