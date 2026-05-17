from __future__ import annotations

import logging
import re
from dataclasses import dataclass, field
from pathlib import Path

from novel_analyzer.services.project_shell_service import ProjectShellService

logger = logging.getLogger(__name__)


@dataclass
class Violation:
    assertion: str
    evidence_excerpt: str
    severity: str = "high"


@dataclass
class LockContractReport:
    violations: list[Violation] = field(default_factory=list)

    @property
    def verdict(self) -> str:
        return "fail" if self.violations else "pass"


class LockContractChecker:
    def __init__(
        self,
        base_dir: Path = Path("output/projects"),
        shell: ProjectShellService | None = None,
    ) -> None:
        self._shell = shell or ProjectShellService(base_dir=base_dir)

    def check(self, slug: str, text: str) -> LockContractReport:
        assertions = self._shell.list_locked_assertions(slug)
        violations: list[Violation] = []
        for assertion in assertions:
            violation = self._check_assertion(assertion, text)
            if violation:
                violations.append(violation)
        return LockContractReport(violations=violations)

    def _check_assertion(self, assertion: str, text: str) -> Violation | None:
        # Pattern: "主角不能/不应/禁止 + action" — negation heuristic for Chinese constraints
        negation_pattern = re.compile(r"不能|不应|禁止|严禁|不得")
        if negation_pattern.search(assertion):
            # Extract the forbidden action (text after negation word)
            parts = negation_pattern.split(assertion, maxsplit=1)
            if len(parts) > 1:
                forbidden = parts[1].strip()[:20]
                if forbidden and re.search(re.escape(forbidden[:5]), text):
                    match = re.search(re.escape(forbidden[:5]), text)
                    if match:
                        start = max(0, match.start() - 20)
                        end = min(len(text), match.end() + 50)
                        return Violation(
                            assertion=assertion,
                            evidence_excerpt=text[start:end],
                        )
        return None
