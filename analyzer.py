import ast
import re
from typing import Dict, Any, List

BUILTIN_NAMES = {"list", "dict", "set", "str", "int", "float", "type", "id", "input", "print", "len"}

def review_code(code_text: str) -> Dict[str, Any]:
    issues: List[Dict[str, Any]] = []
    lines = code_text.splitlines()

    # --- Phase 1: Line & Pattern Scans ---
    for idx, line in enumerate(lines, start=1):
        clean_line = line.strip()

        # Rule 1: Dynamic Execution
        if re.search(r'\b(eval|exec)\s*\(', clean_line):
            issues.append({
                "line": idx,
                "type": "Security",
                "severity": "Critical",
                "message": "Dynamic code execution (`eval` / `exec`) allows arbitrary code injection.",
                "fix": "Use safe parsers like `ast.literal_eval` or `json.loads`."
            })

        # Rule 2: Hardcoded Secrets / Tokens
        if re.search(r'(api[_-]?key|secret|token|password|passwd|auth)\s*=\s*["\'][A-Za-z0-9_\-\.]{8,}["\']', clean_line, re.IGNORECASE):
            issues.append({
                "line": idx,
                "type": "Security",
                "severity": "Critical",
                "message": "Hardcoded secret or authentication token detected in source.",
                "fix": "Load secrets securely from environment variables using `os.getenv()`."
            })

        # Rule 3: Bare except
        if re.search(r'except\s*:', clean_line):
            issues.append({
                "line": idx,
                "type": "Bug Risk",
                "severity": "High",
                "message": "Bare `except:` catches system signals and interrupts unexpectedly.",
                "fix": "Specify the exact exception type (e.g., `except ValueError:` or `except Exception:`)."
            })

        # Rule 4: Mutable default arguments
        if re.search(r'def\s+\w+\([^)]*=\s*(\[\]|\{\})', clean_line):
            issues.append({
                "line": idx,
                "type": "Bug Risk",
                "severity": "High",
                "message": "Mutable default argument persists state across multiple function calls.",
                "fix": "Use `default=None` and initialize the container inside the function body."
            })

        # Rule 5: Comparison to None using ==
        if re.search(r'==\s*None|!=\s*None', clean_line):
            issues.append({
                "line": idx,
                "type": "Style",
                "severity": "Low",
                "message": "Equality operator used against `None`.",
                "fix": "Use identity checks: `is None` or `is not None` (PEP 8)."
            })

        # Rule 6: Leftover debugging print statements
        if re.search(r'^\s*print\s*\(', clean_line):
            issues.append({
                "line": idx,
                "type": "Maintainability",
                "severity": "Low",
                "message": "Standard `print()` statement detected.",
                "fix": "Replace standard print calls with configured Python `logging`."
            })

    # --- Phase 2: AST Analysis (Deep Syntax & Structure) ---
    try:
        tree = ast.parse(code_text)
        
        imported_modules = {}
        used_names = set()

        for node in ast.walk(tree):
            # Track imports
            if isinstance(node, ast.Import):
                for alias in node.names:
                    imported_modules[alias.name] = node.lineno
            elif isinstance(node, ast.ImportFrom):
                for alias in node.names:
                    imported_modules[alias.name] = node.lineno

            # Track variable names loaded
            if isinstance(node, ast.Name) and isinstance(node.ctx, ast.Load):
                used_names.add(node.id)

            # Rule 7: Builtin shadowing
            if isinstance(node, ast.Assign):
                for target in node.targets:
                    if isinstance(target, ast.Name) and target.id in BUILTIN_NAMES:
                        issues.append({
                            "line": target.lineno,
                            "type": "Bug Risk",
                            "severity": "Medium",
                            "message": f"Variable name '{target.id}' shadows a Python built-in function/type.",
                            "fix": f"Rename '{target.id}' to avoid overriding Python built-ins."
                        })

        # Rule 8: Unused imports
        for mod_name, line_no in imported_modules.items():
            if mod_name not in used_names:
                issues.append({
                    "line": line_no,
                    "type": "Code Quality",
                    "severity": "Low",
                    "message": f"Imported module/name '{mod_name}' is never referenced.",
                    "fix": f"Remove `import {mod_name}` to keep namespace clean."
                })

    except SyntaxError as err:
        issues.append({
            "line": err.lineno or 1,
            "type": "Syntax Error",
            "severity": "Critical",
            "message": f"Syntax Error: {err.msg}",
            "fix": "Fix punctuation, colons, or matching brackets around this line."
        })

    # Sort issues by line number
    issues.sort(key=lambda x: x["line"])

    return {
        "total_lines": len(lines),
        "total_issues": len(issues),
        "issues": issues
    }
