"""Report endpoints."""

from datetime import date, datetime, timedelta, timezone
from typing import Optional
from uuid import UUID

from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy import func, select
from sqlalchemy.ext.asyncio import AsyncSession

from app.api.deps import get_current_user
from app.core.dependencies import get_db
from app.models.practice import PracticeSession
from app.models.user import User
from app.schemas import DailyBreakdown, PaginatedReportResponse, WeeklyReport
from app.schemas.report import PracticeReport

router = APIRouter()


@router.get(
    "/history",
    response_model=PaginatedReportResponse,
    summary="Get practice history",
)
async def get_practice_history(
    page: int = Query(default=1, ge=1, description="Page number"),
    limit: int = Query(default=10, ge=1, le=50, description="Items per page"),
    start_date: Optional[date] = Query(default=None, description="Start date filter"),
    end_date: Optional[date] = Query(default=None, description="End date filter"),
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
) -> PaginatedReportResponse:
    """Retrieve paginated practice session history."""
    query = select(PracticeSession).where(
        PracticeSession.user_id == current_user.id,
        PracticeSession.status == "completed",
    )

    if start_date:
        start_datetime = datetime.combine(start_date, datetime.min.time()).replace(
            tzinfo=timezone.utc
        )
        query = query.where(PracticeSession.started_at >= start_datetime)

    if end_date:
        end_datetime = datetime.combine(end_date, datetime.max.time()).replace(
            tzinfo=timezone.utc
        )
        query = query.where(PracticeSession.started_at <= end_datetime)

    count_query = select(func.count()).select_from(query.subquery())
    total_result = await db.execute(count_query)
    total = total_result.scalar() or 0

    offset = (page - 1) * limit
    query = query.order_by(PracticeSession.started_at.desc()).offset(offset).limit(limit)

    result = await db.execute(query)
    sessions = result.scalars().all()

    items = [
        PracticeReport(
            id=str(s.id),
            scenario_id=str(s.scenario_id) if s.scenario_id else None,
            overall_score=s.overall_score or 0.0,
            average_accuracy=s.average_accuracy or 0.0,
            average_fluency=s.average_fluency or 0.0,
            average_completeness=s.average_completeness or 0.0,
            strengths=s.strengths or [],
            improvements=s.improvements or [],
            started_at=s.started_at,
            ended_at=s.ended_at,
            duration_minutes=int((s.ended_at - s.started_at).total_seconds() / 60)
            if s.ended_at
            else 0,
        )
        for s in sessions
    ]

    return PaginatedReportResponse(
        items=items,
        total=total,
        page=page,
        limit=limit,
        pages=(total + limit - 1) // limit,
    )


@router.get(
    "/{report_id}",
    response_model=PracticeReport,
    summary="Get practice report",
)
async def get_practice_report(
    report_id: UUID,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
) -> PracticeReport:
    """Retrieve detailed report for a specific practice session."""
    result = await db.execute(
        select(PracticeSession).where(
            PracticeSession.id == report_id,
            PracticeSession.user_id == current_user.id,
        )
    )
    session = result.scalar_one_or_none()

    if session is None:
        raise HTTPException(
            status_code=404,
            detail={
                "code": "REPORT_NOT_FOUND",
                "message": "Practice report not found",
            },
        )

    duration_minutes = 0
    if session.ended_at and session.started_at:
        duration_minutes = int((session.ended_at - session.started_at).total_seconds() / 60)

    return PracticeReport(
        id=str(session.id),
        scenario_id=str(session.scenario_id) if session.scenario_id else None,
        overall_score=session.overall_score or 0.0,
        average_accuracy=session.average_accuracy or 0.0,
        average_fluency=session.average_fluency or 0.0,
        average_completeness=session.average_completeness or 0.0,
        strengths=session.strengths or [],
        improvements=session.improvements or [],
        started_at=session.started_at,
        ended_at=session.ended_at,
        duration_minutes=duration_minutes,
    )


@router.get(
    "/weekly",
    response_model=WeeklyReport,
    summary="Get weekly report",
)
async def get_weekly_report(
    week_start: Optional[date] = Query(default=None, description="Week start date"),
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
) -> WeeklyReport:
    """Retrieve weekly learning progress summary."""
    if week_start is None:
        today = date.today()
        week_start = today - timedelta(days=today.weekday())

    week_end = week_start + timedelta(days=6)

    start_datetime = datetime.combine(week_start, datetime.min.time()).replace(
        tzinfo=timezone.utc
    )
    end_datetime = datetime.combine(week_end, datetime.max.time()).replace(
        tzinfo=timezone.utc
    )

    result = await db.execute(
        select(PracticeSession).where(
            PracticeSession.user_id == current_user.id,
            PracticeSession.status == "completed",
            PracticeSession.started_at >= start_datetime,
            PracticeSession.started_at <= end_datetime,
        )
    )
    sessions = result.scalars().all()

    total_sessions = len(sessions)
    total_duration_minutes = sum(
        int((s.ended_at - s.started_at).total_seconds() / 60)
        for s in sessions
        if s.ended_at and s.started_at
    )
    average_score = (
        sum(s.overall_score or 0 for s in sessions) / total_sessions
        if total_sessions > 0
        else 0.0
    )
    scenarios_practiced = len(set(s.scenario_id for s in sessions if s.scenario_id))

    daily_data = {}
    for s in sessions:
        if s.started_at:
            day = s.started_at.date()
            if day not in daily_data:
                daily_data[day] = {
                    "sessions": 0,
                    "duration": 0,
                    "scores": [],
                }
            daily_data[day]["sessions"] += 1
            if s.ended_at and s.started_at:
                daily_data[day]["duration"] += int(
                    (s.ended_at - s.started_at).total_seconds() / 60
                )
            if s.overall_score:
                daily_data[day]["scores"].append(s.overall_score)

    daily_breakdown = [
        DailyBreakdown(
            date=day,
            sessions=data["sessions"],
            duration_minutes=data["duration"],
            average_score=sum(data["scores"]) / len(data["scores"])
            if data["scores"]
            else 0.0,
        )
        for day, data in sorted(daily_data.items())
    ]

    prev_week_start = week_start - timedelta(days=7)
    prev_week_end = week_start - timedelta(days=1)
    prev_start_datetime = datetime.combine(
        prev_week_start, datetime.min.time()
    ).replace(tzinfo=timezone.utc)
    prev_end_datetime = datetime.combine(
        prev_week_end, datetime.max.time()
    ).replace(tzinfo=timezone.utc)

    prev_result = await db.execute(
        select(func.count()).where(
            PracticeSession.user_id == current_user.id,
            PracticeSession.status == "completed",
            PracticeSession.started_at >= prev_start_datetime,
            PracticeSession.started_at <= prev_end_datetime,
        )
    )
    prev_total = prev_result.scalar() or 0

    improvement_percentage = 0.0
    if prev_total > 0:
        improvement_percentage = ((total_sessions - prev_total) / prev_total) * 100

    return WeeklyReport(
        week_start=week_start,
        week_end=week_end,
        total_sessions=total_sessions,
        total_duration_minutes=total_duration_minutes,
        average_score=average_score,
        scenarios_practiced=scenarios_practiced,
        improvement_percentage=improvement_percentage,
        daily_breakdown=daily_breakdown,
    )
