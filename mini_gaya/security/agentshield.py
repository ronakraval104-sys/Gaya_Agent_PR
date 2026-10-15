import re
from dataclasses import dataclass
from typing import List, Dict, Any

@dataclass
class SecurityFinding:
    severity: str  # LOW, MEDIUM, HIGH, CRITICAL
    category: str  # SECRET, UNSAFE_EXEC, MCP_RISK
    description: str
    snippet: str

SECRET_PATTERNS = [
    (r"sk-ant-api[a-zA-Z0-9_\-]{30,}", "Anthropic API Key", "HIGH"),
    (r"ghp_[a-zA-Z0-9]{36,}", "GitHub Personal Access Token", "HIGH"),
    (r"AIza[0-9A-Za-z-_]{35}", "Google Gemini/Cloud API Key", "HIGH"),
    (r"sk-[a-zA-Z0-9]{48,}", "OpenAI Secret Key", "HIGH"),
    (r"-----BEGIN (RSA|EC|DSA|OPENSSH) PRIVATE KEY-----", "Private Key Block", "CRITICAL"),
    (r"password\s*[:=]\s*['\"][^\s'\"]{6,}['\"]", "Plaintext Password Assignment", "MEDIUM"),
]

UNSAFE_COMMAND_PATTERNS = [
    (r"(curl|wget)[^|\n]+\|\s*(sh|bash|powershell|cmd)", "Remote script piped directly to shell", "HIGH"),
    (r"rm\s+-rf\s+[\/~]", "Destructive root recursive deletion", "CRITICAL"),
    (r":\(\)\s*\{\s*:\s*\|\s*:\s*&\s*\}\s*;", "Fork bomb pattern", "CRITICAL"),
]

def scan_text(content: str) -> List[SecurityFinding]:
    findings = []
    if not content:
        return findings

    for pattern, desc, sev in SECRET_PATTERNS:
        for match in re.finditer(pattern, content, re.IGNORECASE):
            findings.append(SecurityFinding(
                severity=sev,
                category="SECRET",
                description=desc,
                snippet=match.group(0)[:16] + "..."
            ))

    for pattern, desc, sev in UNSAFE_COMMAND_PATTERNS:
        for match in re.finditer(pattern, content, re.IGNORECASE):
            findings.append(SecurityFinding(
                severity=sev,
                category="UNSAFE_EXEC",
                description=desc,
                snippet=match.group(0)[:32]
            ))
    return findings

def scan_mcp_config(config: Dict[str, Any]) -> List[SecurityFinding]:
    findings = []
    if not isinstance(config, dict):
        return findings

    servers = config.get("mcpServers", {})
    if not isinstance(servers, dict):
        return findings

    for s_name, s_def in servers.items():
        if not isinstance(s_def, dict):
            continue
        cmd = str(s_def.get("command", ""))
        args = " ".join(str(a) for a in s_def.get("args", []))
        full = f"{cmd} {args}"
        for f in scan_text(full):
            findings.append(SecurityFinding(
                severity=f.severity,
                category="MCP_RISK",
                description=f"MCP Server [{s_name}]: {f.description}",
                snippet=f.snippet
            ))
    return findings
