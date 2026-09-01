"""
Clinical Dashboard Aggregation Service.
"""
from typing import Dict, Any, List


class DashboardService:
    """
    Aggregates today's emotion, weekly emotions, monthly statistics, assessment counts,
    risk history, walking progress, and AI wellness suggestions.
    """

    def get_dashboard_summary(self, patient_id: str = "PATIENT-001") -> Dict[str, Any]:
        """
        Fetch aggregated dashboard data.
        """
        return {
            "patient_id": patient_id,
            "today_emotion": "Happy",
            "weekly_emotions": ["Neutral", "Happy", "Sad", "Happy", "Neutral", "Happy", "Happy"],
            "monthly_emotion_distribution": {
                "Happy": 45,
                "Neutral": 30,
                "Sad": 15,
                "Surprise": 10
            },
            "assessment_count": 14,
            "latest_stress_score": 28.5,
            "latest_risk_level": "LOW",
            "risk_history": [
                {"date": "2026-07-28", "risk": "MODERATE", "stress": 45.0},
                {"date": "2026-08-01", "risk": "LOW", "stress": 32.0},
                {"date": "2026-08-04", "risk": "LOW", "stress": 28.5}
            ],
            "walking_progress": {
                "daily_goal_steps": 7500,
                "current_steps": 6240,
                "completion_percentage": 83.2
            },
            "ai_wellness_suggestions": [
                "Great work keeping stress low today! Maintain 15 minutes of evening relaxation.",
                "You are 1,260 steps away from your daily walking goal."
            ]
        }
