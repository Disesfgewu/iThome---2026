"""
UniMock AI - Day 27 Fallback Service Unit Tests
Verifies graceful degradation matrix for LLM timeouts, network errors, and API quota limits.
"""

import pytest
from app.services.fallback_service import fallback_service


def test_fallback_question_generation_business():
    question = fallback_service.get_fallback_question("輔仁大學 金融與國際企業學研究所 EMBA 在職碩士專班", turn_index=1)
    assert isinstance(question, str)
    assert len(question) > 5
    assert "動機" in question or "成就" in question or "背景" in question


def test_fallback_question_generation_tech():
    question = fallback_service.get_fallback_question("國立臺灣大學 資訊工程學系", turn_index=2)
    assert isinstance(question, str)
    assert "系統" in question or "演算法" in question or "Trade-off" in question or "優化" in question


def test_fallback_evaluation_report_generation():
    turns = [
        {"turn": 1, "question": "請進行自我介紹與說明報考動機？", "answer": "教授好，我是風控主管，希望能結合貴所EMBA知識。"},
        {"turn": 2, "question": "您如何進行外匯避險與壓力測試？", "answer": "我主持了外匯避險專案，建立敏感度分析模型。"},
        {"turn": 3, "question": "關於未來ESG與綠色金融規劃？", "answer": "我將聚焦於綠色金融與AI風控審查。"}
    ]

    report = fallback_service.get_fallback_evaluation_report(
        target_school="輔仁大學",
        target_major="金融與國際企業學研究所 EMBA 在職碩士專班",
        transcript_turns=turns
    )

    assert "overall_score" in report
    assert report["overall_score"] >= 70.0
    assert "radar_scores" in report
    assert "strengths" in report
    assert "improvements" in report
    assert len(report["question_diagnoses"]) == 3
    assert "【Situation】" not in report["question_diagnoses"][0]["improved_sample"]
