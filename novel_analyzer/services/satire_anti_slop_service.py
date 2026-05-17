from __future__ import annotations

import re
from dataclasses import dataclass, field
from typing import Literal

Severity = Literal["blocker", "fail", "warn", "info"]
Verdict = Literal["pass", "warn", "fail"]


@dataclass
class Finding:
    severity: Severity
    type: str
    evidence: str


@dataclass
class SatireAntiSlopReport:
    verdict: Verdict
    findings: list[Finding] = field(default_factory=list)


class SatireAntiSlopChecker:
    """Detects AI slop patterns specific to satirical Chinese web fiction."""

    _META_COMMENTARY = re.compile(
        r"这其实是在|说白了就是|讽刺的是|暗示着|寓意是|象征着|表达了"
    )
    _HAPPY_ENDING = re.compile(
        r"圆满|终于幸福|一切都好|从此无忧|皆大欢喜|阖家欢乐|破镜重圆"
    )
    _EXPLETIVE = re.compile(r"特么的|他么的|妈的")
    _REVERSAL_MARKERS = re.compile(r"原来是假的|结果竟然|没想到只是")
    _INTERNET_SLANG = re.compile(r"yyds|内卷|躺平|摆烂|破防|绝绝子|栓Q|emo")
    _OUTBURST = re.compile(r"怒吼|暴怒|拍桌|吼道|咆哮")

    def check_text(
        self,
        text: str,
        protagonist_names: list[str] | None = None,
        fast_mode: bool = False,
    ) -> SatireAntiSlopReport:
        findings: list[Finding] = []
        paragraphs = [p.strip() for p in text.split("\n") if p.strip()]

        # 1. Meta-commentary (blocker)
        for para in paragraphs:
            if self._META_COMMENTARY.search(para):
                findings.append(Finding(
                    severity="blocker",
                    type="meta_commentary",
                    evidence=para[:100],
                ))
                break

        # 2. Happy ending (blocker) — check last 200 chars
        tail = text[-200:] if len(text) > 200 else text
        if self._HAPPY_ENDING.search(tail):
            findings.append(Finding(
                severity="blocker",
                type="happy_ending",
                evidence=tail[:100],
            ))

        # 3. Expletive abuse (fail)
        chapter_expletive_count = len(self._EXPLETIVE.findall(text))
        for para in paragraphs:
            para_count = len(self._EXPLETIVE.findall(para))
            if para_count >= 3:
                findings.append(Finding(
                    severity="fail",
                    type="expletive_abuse",
                    evidence=f"Paragraph has {para_count} expletives: {para[:80]}",
                ))
                break
        if chapter_expletive_count >= 6:
            findings.append(Finding(
                severity="fail",
                type="expletive_abuse",
                evidence=f"Chapter has {chapter_expletive_count} total expletives",
            ))

        # 4. Early deflate (warn) — reversal in first 30%
        cutoff = int(len(text) * 0.3)
        early_text = text[:cutoff]
        if self._REVERSAL_MARKERS.search(early_text):
            findings.append(Finding(
                severity="warn",
                type="early_deflate",
                evidence="Reversal marker found in first 30% of chapter",
            ))

        # 5. Internet slang abuse (warn)
        for para in paragraphs:
            slang_matches = self._INTERNET_SLANG.findall(para)
            if len(slang_matches) >= 2:
                findings.append(Finding(
                    severity="warn",
                    type="internet_slang_abuse",
                    evidence=f"Paragraph has {len(slang_matches)} slang terms: {para[:80]}",
                ))
                break

        # 6. Character emotional outburst (warn)
        if protagonist_names:
            for name in protagonist_names:
                pattern = re.compile(re.escape(name) + r".{0,30}(?:怒吼|暴怒|拍桌|吼道|咆哮)")
                for para in paragraphs:
                    if pattern.search(para):
                        findings.append(Finding(
                            severity="warn",
                            type="character_emotional_outburst",
                            evidence=para[:100],
                        ))
                        break

        # Determine verdict
        verdict: Verdict
        if any(f.severity in ("blocker", "fail") for f in findings):
            verdict = "fail"
        elif any(f.severity == "warn" for f in findings):
            verdict = "warn"
        else:
            verdict = "pass"

        # In fast_mode, downgrade blockers to warn
        if fast_mode:
            for f in findings:
                if f.severity == "blocker":
                    f.severity = "warn"
            if all(f.severity in ("warn", "info") for f in findings):
                verdict = "warn" if findings else "pass"

        return SatireAntiSlopReport(verdict=verdict, findings=findings)
