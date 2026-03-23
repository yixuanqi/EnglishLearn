"""Report schemas following api_spec.yaml."""

from datetime import date, datetime
from typing import Optional

from pydantic import BaseModel, Field

from app.schemas.base import BaseSchema


class DailyBreakdown(BaseModel):
    """Daily practice breakdown."""

    practice_date: date = Field(..., description="Date")
    sessions: int = Field(..., description="Number of sessions")
    duration_minutes: int = Field(..., description="Duration in minutes")
    average_score: float = Field(..., description="Average score")


class WeeklyReport(BaseSchema):
    """Weekly report schema."""

    week_start: date = Field(..., description="Week start date")
    week_end: date = Field(..., description="Week end date")
    total_sessions: int = Field(..., description="Total sessions")
    total_duration_minutes: int = Field(..., description="Total duration")
    average_score: float = Field(..., description="Average score")
    scenarios_practiced: int = Field(..., description="Scenarios practiced")
    improvement_percentage: float = Field(..., description="Improvement percentage")
    daily_breakdown: list[DailyBreakdown] = Field(
        default_factory=list,
        description="Daily breakdown",
    )


class TopScenario(BaseModel):
    """Top practiced scenario."""

    scenario_title: str = Field(..., description="Scenario title")
    sessions: int = Field(..., description="Number of sessions")
    average_score: float = Field(..., description="Average score")


class ScoreTrend(BaseModel):
    """Score trend data point."""

    week: int = Field(..., description="Week number")
    score: float = Field(..., description="Score")


class MonthlyReport(BaseSchema):
    """Monthly report schema."""

    month: str = Field(..., description="Month in YYYY-MM format")
    total_sessions: int = Field(..., description="Total sessions")
    total_duration_minutes: int = Field(..., description="Total duration")
    average_score: float = Field(..., description="Average score")
    scenarios_practiced: int = Field(..., description="Scenarios practiced")
    weekly_progress: list[WeeklyReport] = Field(
        default_factory=list,
        description="Weekly progress",
    )
    top_scenarios: list[TopScenario] = Field(
        default_factory=list,
        description="Top scenarios",
    )
    score_trend: list[ScoreTrend] = Field(
        default_factory=list,
        description="Score trend",
    )


class LearningStats(BaseSchema):
    """Overall learning statistics."""

    total_sessions: int = Field(..., description="Total sessions")
    total_duration_hours: float = Field(..., description="Total duration in hours")
    overall_average_score: float = Field(..., description="Overall average score")
    best_score: float = Field(..., description="Best score achieved")
    scenarios_completed: int = Field(..., description="Scenarios completed")
    current_streak: int = Field(..., description="Current streak in days")
    longest_streak: int = Field(..., description="Longest streak in days")
    member_since: date = Field(..., description="Member since date")


class PracticeReport(BaseSchema):
    """Practice session report."""

    id: str = Field(..., description="Report UUID")
    scenario_id: Optional[str] = Field(None, description="Scenario UUID")
    overall_score: float = Field(..., ge=0, le=100, description="Overall score")
    average_accuracy: float = Field(..., description="Average accuracy")
    average_fluency: float = Field(..., description="Average fluency")
    average_completeness: float = Field(..., description="Average completeness")
    strengths: list[str] = Field(default_factory=list, description="Strengths")
    improvements: list[str] = Field(default_factory=list, description="Areas to improve")
    started_at: datetime = Field(..., description="Start timestamp")
    ended_at: Optional[datetime] = Field(None, description="End timestamp")
    duration_minutes: int = Field(..., description="Duration in minutes")


class PaginatedReportResponse(BaseModel):
    """Paginated report response."""

    items: list[PracticeReport] = Field(..., description="Report list")
    total: int = Field(..., description="Total count")
    page: int = Field(..., description="Current page")
    limit: int = Field(..., description="Items per page")
    pages: int = Field(..., description="Total pages")
