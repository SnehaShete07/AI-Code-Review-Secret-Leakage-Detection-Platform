from app.rules.ai_rules import AIAgentSecurityRule
from app.rules.base import BaseRule
from app.rules.config_rules import ConfigSecurityRule
from app.rules.js_rules import JavaScriptRiskyPatternRule
from app.rules.python_rules import PythonAstDangerousExecRule


def default_rules() -> list[BaseRule]:
    return [
        PythonAstDangerousExecRule(),
        JavaScriptRiskyPatternRule(),
        ConfigSecurityRule(),
        AIAgentSecurityRule(),
    ]
