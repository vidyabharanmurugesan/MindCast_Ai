"""
Longitudinal Report Analysis Service for Comparing Reports and Generating Trends.
"""
from typing import Dict, Any, List


class ReportAnalysisService:
    """
    Parses PDF/JSON/CSV clinical reports, compares historical records,
    and generates weekly/monthly stress trends, emotion progressions, and AI summaries.
    """

    def analyze_report_trends(self, report_history: List[Dict[str, Any]]) -> Dict[str, Any]:
        """
        Compute longitudinal mental wellness trends over time.
        """
        if not report_history:
            return {
                "trend_status": "NO_DATA",
                "stress_trend": [],
                "dominant_emotion": "Neutral",
                "ai_summary": "Insufficient report history to generate longitudinal trend analysis."
            }

        stress_points = []
        emotions = []

        for r in report_history:
            fused = r.get("fused_clinical_result", {})
            stress_points.append(fused.get("stress_score", 50.0))
            emotions.append(fused.get("overall_emotion", "Neutral"))

        avg_stress = round(sum(stress_points) / len(stress_points), 2)
        initial_stress = stress_points[0]
        latest_stress = stress_points[-1]

        diff = latest_stress - initial_stress
        if diff < -5.0:
            trend_direction = "IMPROVING (Decreasing Stress)"
        elif diff > 5.0:
            trend_direction = "REGRESSING (Increasing Stress)"
        else:
            trend_direction = "STABLE"

        ai_summary = (
            f"Longitudinal evaluation across {len(report_history)} clinical sessions shows a '{trend_direction}' trajectory. "
            f"Average overall stress index is {avg_stress}/100. Latest recorded stress level is {latest_stress}/100."
        )

        return {
            "total_reports_analyzed": len(report_history),
            "trend_direction": trend_direction,
            "average_stress_score": avg_stress,
            "initial_stress_score": initial_stress,
            "latest_stress_score": latest_stress,
            "stress_timeline": stress_points,
            "emotion_history": emotions,
            "ai_generated_summary": ai_summary
        }
