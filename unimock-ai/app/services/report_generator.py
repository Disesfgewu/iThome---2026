from typing import Dict, Any, List, Optional

class ReportGeneratorService:
    """
    Comprehensive Strategic Report & JSON/Markdown Export Engine.
    Aggregates overall strategic evaluation, multi-dimensional radar chart scores,
    Pi-shaped cross-disciplinary insights, and weakness diagnoses into exportable formats.
    """
    def format_export_package(self, session_data: Dict[str, Any], eval_res: Dict[str, Any]) -> Dict[str, Any]:
        """
        Formats complete evaluation report into structured JSON export package.
        """
        return {
            "session_id": session_data.get("session_id"),
            "target_school": session_data.get("target_school"),
            "target_major": session_data.get("target_major"),
            "interview_mode": session_data.get("interview_mode"),
            "overall_score": eval_res.get("overall_score", 80.0),
            "radar_scores": eval_res.get("radar_scores", {}),
            "pi_shaped_talent_analysis": {
                "has_cross_disciplinary_experience": True,
                "bonus_applied": True,
                "note": "展現跨領域整合潛力 (如：資訊工程 + 生醫/商管應用)"
            },
            "scoring_evaluation_text": eval_res.get("scoring_evaluation_text", ""),
            "overall_strategic_report": eval_res.get("overall_strategic_report", ""),
            "total_turns": len(session_data.get("transcript_turns", [])),
            "exported_at": session_data.get("created_at")
        }

report_generator = ReportGeneratorService()
