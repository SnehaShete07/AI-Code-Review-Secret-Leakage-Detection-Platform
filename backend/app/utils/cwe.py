CWE_TITLES: dict[str, str] = {
    "CWE-20": "Improper Input Validation",
    "CWE-74": "Improper Neutralization of Special Elements",
    "CWE-78": "OS Command Injection",
    "CWE-79": "Cross-site Scripting",
    "CWE-89": "SQL Injection",
    "CWE-94": "Code Injection",
    "CWE-95": "Eval Injection",
    "CWE-1104": "Use of Unmaintained Third Party Components",
    "CWE-250": "Execution with Unnecessary Privileges",
    "CWE-285": "Improper Authorization",
    "CWE-295": "Improper Certificate Validation",
    "CWE-502": "Deserialization of Untrusted Data",
    "CWE-798": "Use of Hard-coded Credentials",
    "CWE-942": "Permissive Cross-domain Policy with Untrusted Domains",
}


def cwe_name(cwe_id: str | None) -> str | None:
    if not cwe_id:
        return None
    return CWE_TITLES.get(cwe_id, "CWE reference")
