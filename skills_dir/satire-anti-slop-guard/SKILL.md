# satire-anti-slop-guard

Checks generated prose for AI slop patterns specific to satirical Chinese web fiction.

## Input Schema
See schemas/check_input.json

## Output Schema
See schemas/check_output.json

## Patterns Detected

1. **meta_commentary** (blocker): Narrator explains the satire ("这其实是在讽刺...")
2. **happy_ending** (blocker): Chapter ends with 圆满/终于幸福/一切都好/从此无忧/皆大欢喜
3. **expletive_abuse** (fail): Single paragraph has ≥3 "特么的/他么的/妈的" OR chapter has ≥6
4. **early_deflate** (warn): Reversal appears in first 30% of chapter
5. **internet_slang_abuse** (warn): Single paragraph has ≥2 of yyds/内卷/躺平/摆烂/破防/绝绝子/栓Q/emo
6. **character_emotional_outburst** (warn): Protagonist name + 怒吼/暴怒/拍桌/吼道/咆哮 when character card has "克制" constraint

## Usage
```python
from novel_analyzer.services.satire_anti_slop_service import SatireAntiSlopChecker
checker = SatireAntiSlopChecker()
report = checker.check_text(chapter_text, protagonist_names=["主角名"])
# report.verdict: "pass" | "warn" | "fail"
# report.findings: list of Finding(severity, type, evidence)
```
