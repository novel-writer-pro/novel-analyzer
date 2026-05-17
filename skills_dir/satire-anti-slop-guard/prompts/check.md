# satire-anti-slop-guard check prompt

You are reviewing a chapter of satirical Chinese web fiction for AI slop patterns.

Check for these 6 patterns:
1. meta_commentary: narrator explains the satire ("这其实是在讽刺...")
2. happy_ending: chapter ends with 圆满/终于幸福/一切都好/从此无忧/皆大欢喜
3. expletive_abuse: single paragraph has ≥3 "特么的/他么的/妈的" OR chapter has ≥6
4. early_deflate: reversal appears in first 30% of chapter
5. internet_slang_abuse: single paragraph has ≥2 of yyds/内卷/躺平/摆烂/破防/绝绝子/栓Q/emo
6. character_emotional_outburst: protagonist name + 怒吼/暴怒/拍桌/吼道/咆哮

Return JSON: {"verdict": "pass|warn|fail", "findings": [{"severity": "blocker|fail|warn", "type": "...", "evidence": "..."}]}
