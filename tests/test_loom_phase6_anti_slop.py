from __future__ import annotations
import pytest
from unittest.mock import MagicMock
from novel_analyzer.services.satire_anti_slop_service import SatireAntiSlopChecker
from novel_analyzer.services.lock_contract_checker_service import LockContractChecker


@pytest.fixture
def checker() -> SatireAntiSlopChecker:
    return SatireAntiSlopChecker()


def test_meta_commentary_blocker(checker: SatireAntiSlopChecker) -> None:
    text = "他站在台上侃侃而谈。这其实是在讽刺那些官员的虚伪。众人鼓掌。"
    report = checker.check_text(text)
    assert report.verdict == "fail"
    assert any(f.type == "meta_commentary" for f in report.findings)


def test_happy_ending_blocker(checker: SatireAntiSlopChecker) -> None:
    text = "经历了种种磨难，他终于明白了人生的真谛。" + "x" * 300 + "从此两人终于幸福地生活在一起。"
    report = checker.check_text(text)
    assert report.verdict == "fail"
    assert any(f.type == "happy_ending" for f in report.findings)


def test_expletive_abuse_paragraph(checker: SatireAntiSlopChecker) -> None:
    text = "他特么的真是太过分了，特么的这种人，特么的居然还有脸说话。"
    report = checker.check_text(text)
    assert report.verdict == "fail"
    assert any(f.type == "expletive_abuse" for f in report.findings)


def test_expletive_abuse_chapter(checker: SatireAntiSlopChecker) -> None:
    text = "\n".join([
        "第一段，妈的真烦。",
        "第二段，妈的又来了。",
        "第三段，妈的没完没了。",
        "第四段，妈的这什么情况。",
        "第五段，妈的算了。",
        "第六段，妈的随便吧。",
    ])
    report = checker.check_text(text)
    assert report.verdict == "fail"
    assert any(f.type == "expletive_abuse" for f in report.findings)


def test_early_deflate_warn(checker: SatireAntiSlopChecker) -> None:
    early = "原来是假的，一切都是骗局。"
    padding = "后来发生了很多事情。" * 20
    text = early + padding
    report = checker.check_text(text)
    assert report.verdict == "warn"
    assert any(f.type == "early_deflate" for f in report.findings)


def test_internet_slang_warn(checker: SatireAntiSlopChecker) -> None:
    text = "这个操作真的yyds，完全就是内卷的典型案例，大家都懂的。"
    report = checker.check_text(text)
    assert report.verdict == "warn"
    assert any(f.type == "internet_slang_abuse" for f in report.findings)


def test_character_outburst_warn(checker: SatireAntiSlopChecker) -> None:
    text = "张羽看着眼前的一切，终于忍不住怒吼道：你们这些人！"
    report = checker.check_text(text, protagonist_names=["张羽"])
    assert report.verdict == "warn"
    assert any(f.type == "character_emotional_outburst" for f in report.findings)


def test_clean_text_passes(checker: SatireAntiSlopChecker) -> None:
    text = (
        "李处长端着茶杯，微微一笑，将文件推到桌角。\n"
        "下属们心领神会，各自散去。\n"
        "走廊里的灯光昏黄，照出一排排相同的背影。\n"
        "没有人说话，也没有人需要说话。"
    )
    report = checker.check_text(text, protagonist_names=["李处长"])
    assert report.verdict == "pass"
    assert report.findings == []


def test_fast_mode_downgrades_blocker(checker: SatireAntiSlopChecker) -> None:
    text = "他站在台上侃侃而谈。这其实是在讽刺那些官员的虚伪。众人鼓掌。"
    report = checker.check_text(text, fast_mode=True)
    assert report.verdict == "warn"
    assert all(f.severity != "blocker" for f in report.findings)


def test_lock_contract_checker_violation() -> None:
    mock_shell = MagicMock()
    mock_shell.list_locked_assertions.return_value = ["主角不能怒吼"]
    lcc = LockContractChecker(shell=mock_shell)
    text = "张羽怒吼道：我不服！"
    report = lcc.check("test-slug", text)
    assert report.verdict == "fail"
    assert len(report.violations) == 1
    assert "怒吼" in report.violations[0].assertion or "不能" in report.violations[0].assertion


def test_source_novel_no_false_positive(checker: SatireAntiSlopChecker) -> None:
    text = (
        "王科长推开办公室的门，看见桌上摆着一份新的报告。\n"
        "他拿起来翻了翻，放回原处，若无其事地坐下。\n"
        "窗外的梧桐树叶子黄了又绿，绿了又黄。\n"
        "他在这个位置上已经坐了十七年。\n"
        "每一份报告都长得差不多，每一个下属的眼神也都差不多。\n"
        "他喝了口茶，拿起笔，在报告的右上角写下两个字：已阅。"
    )
    report = checker.check_text(text, protagonist_names=["王科长"])
    assert report.verdict == "pass"
