import re
from typing import Dict, Any, List

def review_code(code_text: str) -> Dict[str, Any]:
    issues: List[Dict[str, Any]] = []
    lines = code_text.splitlines()

    for idx, line in enumerate(lines, start=1):
        clean_line = line.strip()

        # Rule 1: Dangerous execution
        if re.search(r'\b(eval|exec)\s*\(', clean_line):
            issues.append({
                "line": idx,
                "type": "Security",
                "severity": "High",
                "message": "Dynamic code execution (`eval` or `exec`) detected.",
                "fix": "Use safe parsing libraries like `ast.literal_eval` or `json.loads`."
            })

        # Rule 2: Hardcoded credentials
        if re.search(r'(api[_-]?key|secret|password|auth_token)\s*=\s*["\'][A-Za-z0-9_\-\.]{8,}["\']', clean_line, re.IGNORECASE):
            issues.append({
                "line": idx,
                "type": "Security",
                "severity": "Critical",
                "message": "Hardcoded secret or credential detected.",
                "fix": "Store sensitive values in environment variables."
            })

        # Rule 3: Bare except
        if re.search(r'except\s*:', clean_line):
            issues.append({
                "line": idx,
                "type": "Code Quality",
                "severity": "Medium",
                "message": "Bare `except:` clause used.",
                "fix": "Catch explicit exceptions like `except ValueError:` or `except Exception:`."
            })

        # Rule 4: Mutable default arg
        if re.search(r'def\s+\w+\(.*=\s*(\[\]\vert{}\{\})\)', clean_line):
            issues.append({
                "line": idx,
                "type": "Bug Risk",
                "severity": "Medium",
                "message": "Mutable default argument in function definition.",
                "fix": "Use `None` as default and initialize inside the function."
            })

    return {
        "total_lines": len(lines),
        "total_issues": len(issues),
        "issues": issues
    }
