"""Learning feedback generation service."""

from typing import Any, Optional

from app.ai.exceptions import LLMServiceError
from app.ai.services.dialogue import DialogueService


class FeedbackResult:
    """Learning feedback result."""

    def __init__(
        self,
        overall_feedback: str,
        strengths: list[str],
        areas_for_improvement: list[str],
        practice_suggestions: list[str],
        next_steps: str,
    ) -> None:
        self.overall_feedback = overall_feedback
        self.strengths = strengths
        self.areas_for_improvement = areas_for_improvement
        self.practice_suggestions = practice_suggestions
        self.next_steps = next_steps


class LearningFeedbackService:
    """Service for generating personalized learning feedback."""

    def __init__(self) -> None:
        self.dialogue_service = DialogueService()

    async def generate_session_feedback(
        self,
        scenario_title: str,
        difficulty: str,
        total_turns: int,
        overall_score: float,
        accuracy_score: float,
        fluency_score: float,
        completeness_score: float,
        word_issues: Optional[list[dict[str, Any]]] = None,
    ) -> FeedbackResult:
        """Generate comprehensive feedback for a practice session."""
        try:
            feedback_data = await self.dialogue_service.generate_learning_feedback(
                scenario_title=scenario_title,
                difficulty=difficulty,
                total_turns=total_turns,
                overall_score=overall_score,
                accuracy_score=accuracy_score,
                fluency_score=fluency_score,
                completeness_score=completeness_score,
                word_issues=word_issues,
            )

            return FeedbackResult(
                overall_feedback=feedback_data.get(
                    "overall_feedback",
                    self._default_overall_feedback(overall_score),
                ),
                strengths=feedback_data.get("strengths", []),
                areas_for_improvement=feedback_data.get("areas_for_improvement", []),
                practice_suggestions=feedback_data.get("practice_suggestions", []),
                next_steps=feedback_data.get(
                    "next_steps",
                    "Continue practicing to improve your skills.",
                ),
            )
        except LLMServiceError:
            return self._generate_fallback_feedback(
                overall_score=overall_score,
                accuracy_score=accuracy_score,
                fluency_score=fluency_score,
                completeness_score=completeness_score,
            )

    async def generate_quick_feedback(
        self,
        score: float,
        transcription: str,
        reference_text: str,
    ) -> str:
        """Generate quick feedback for a single turn."""
        if score >= 90:
            return "Excellent! Your pronunciation was nearly perfect."
        elif score >= 80:
            return "Great job! Minor improvements possible."
        elif score >= 70:
            return "Good effort! Keep practicing for better clarity."
        elif score >= 60:
            return "Keep trying! Focus on the highlighted words."
        else:
            return "Don't give up! Listen to the reference and try again."

    async def generate_improvement_plan(
        self,
        user_level: str,
        weak_areas: list[str],
        practice_history: list[dict[str, Any]],
    ) -> dict[str, Any]:
        """Generate a personalized improvement plan."""
        plan = {
            "current_level": user_level,
            "focus_areas": weak_areas[:3],
            "recommended_scenarios": self._recommend_scenarios(user_level, weak_areas),
            "daily_practice_goals": self._generate_daily_goals(user_level),
            "weekly_targets": self._generate_weekly_targets(user_level),
            "estimated_improvement_time": self._estimate_improvement_time(user_level, weak_areas),
        }

        return plan

    def _generate_fallback_feedback(
        self,
        overall_score: float,
        accuracy_score: float,
        fluency_score: float,
        completeness_score: float,
    ) -> FeedbackResult:
        """Generate fallback feedback when LLM is unavailable."""
        strengths = []
        improvements = []

        if accuracy_score >= 80:
            strengths.append("Good pronunciation accuracy")
        else:
            improvements.append("Focus on pronouncing words correctly")

        if fluency_score >= 80:
            strengths.append("Natural speech rhythm")
        else:
            improvements.append("Practice speaking more smoothly")

        if completeness_score >= 90:
            strengths.append("Complete sentences without omissions")
        else:
            improvements.append("Try to complete all words")

        return FeedbackResult(
            overall_feedback=self._default_overall_feedback(overall_score),
            strengths=strengths if strengths else ["Keep practicing to build strengths"],
            areas_for_improvement=improvements if improvements else ["Continue practicing"],
            practice_suggestions=[
                "Practice with easier scenarios",
                "Listen to native speaker audio",
                "Record and compare your speech",
            ],
            next_steps="Try another practice session to continue improving.",
        )

    def _default_overall_feedback(self, score: float) -> str:
        """Generate default overall feedback based on score."""
        if score >= 90:
            return "Outstanding performance! You're speaking like a native."
        elif score >= 80:
            return "Great session! You're making excellent progress."
        elif score >= 70:
            return "Good practice! Focus on the areas highlighted for improvement."
        elif score >= 60:
            return "Keep working at it! Regular practice will help you improve."
        else:
            return "Don't be discouraged! Every practice session helps you learn."

    def _recommend_scenarios(
        self,
        level: str,
        weak_areas: list[str],
    ) -> list[dict[str, str]]:
        """Recommend scenarios based on level and weak areas."""
        recommendations = []

        if "pronunciation" in " ".join(weak_areas).lower():
            recommendations.append({
                "category": "daily_life",
                "difficulty": level,
                "reason": "Practice everyday conversations for natural pronunciation",
            })

        if "fluency" in " ".join(weak_areas).lower():
            recommendations.append({
                "category": "business",
                "difficulty": level,
                "reason": "Business scenarios help with formal speech patterns",
            })

        if not recommendations:
            recommendations.append({
                "category": "exhibition",
                "difficulty": level,
                "reason": "Good for practicing technical vocabulary",
            })

        return recommendations

    def _generate_daily_goals(self, level: str) -> list[str]:
        """Generate daily practice goals."""
        base_goals = [
            "Complete at least 1 practice session",
            "Practice for at least 10 minutes",
        ]

        if level == "beginner":
            base_goals.append("Focus on basic vocabulary scenarios")
        elif level == "intermediate":
            base_goals.append("Try one advanced scenario")
        else:
            base_goals.append("Challenge yourself with technical scenarios")

        return base_goals

    def _generate_weekly_targets(self, level: str) -> list[str]:
        """Generate weekly practice targets."""
        return [
            f"Complete 5-7 practice sessions",
            "Achieve average score above 75%",
            "Practice all scenario categories",
            "Focus on improving weak areas",
        ]

    def _estimate_improvement_time(
        self,
        level: str,
        weak_areas: list[str],
    ) -> str:
        """Estimate time to see improvement."""
        if level == "beginner":
            return "2-4 weeks of regular practice"
        elif level == "intermediate":
            return "4-6 weeks of focused practice"
        else:
            return "6-8 weeks of intensive practice"
