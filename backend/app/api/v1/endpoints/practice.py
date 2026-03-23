"""Practice session endpoints."""

from datetime import datetime, timezone
from typing import Optional
from uuid import UUID

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import selectinload

from app.api.deps import get_current_user
from app.core.dependencies import get_db
from app.models.dialogue import Dialogue
from app.models.practice import PracticeSession, SpeechResult
from app.models.scenario import Scenario
from app.models.user import User
from app.schemas import (
    PracticeSessionResponse,
    SpeechResult,
    SubmitPracticeRequest,
    SubmitPracticeResponse,
)
from app.schemas.practice import SessionStatus

router = APIRouter()


@router.post(
    "/start",
    response_model=PracticeSessionResponse,
    status_code=status.HTTP_201_CREATED,
    summary="Start practice session",
)
async def start_practice(
    scenario_id: UUID,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
) -> PracticeSessionResponse:
    """Start a new practice session for a scenario."""
    result = await db.execute(
        select(Scenario).where(
            Scenario.id == scenario_id,
            Scenario.is_active == True,
        )
    )
    scenario = result.scalar_one_or_none()

    if scenario is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail={
                "code": "SCENARIO_NOT_FOUND",
                "message": "Scenario not found",
            },
        )

    is_premium = current_user.subscription_plan != "free"
    if scenario.is_premium and not is_premium:
        raise HTTPException(
            status_code=status.HTTP_402_PAYMENT_REQUIRED,
            detail={
                "code": "PREMIUM_REQUIRED",
                "message": "Premium subscription required for this scenario",
            },
        )

    dialogue_result = await db.execute(
        select(Dialogue)
        .where(Dialogue.scenario_id == scenario_id)
        .order_by(Dialogue.variation)
        .limit(1)
    )
    dialogue = dialogue_result.scalar_one_or_none()

    dialogue_lines = []
    total_turns = 0
    if dialogue:
        dialogue_lines = dialogue.lines.get("lines", [])
        total_turns = len([l for l in dialogue_lines if l.get("speaker") == "user"])

    session = PracticeSession(
        user_id=current_user.id,
        scenario_id=scenario_id,
        dialogue_id=dialogue.id if dialogue else None,
        status=SessionStatus.ACTIVE.value,
        current_turn=0,
        total_turns=total_turns,
    )

    db.add(session)
    await db.commit()
    await db.refresh(session)

    return PracticeSessionResponse(
        session_id=str(session.id),
        scenario_id=str(scenario_id),
        status=SessionStatus.ACTIVE,
        current_turn=0,
        total_turns=total_turns,
        dialogue=dialogue_lines,
        started_at=session.started_at,
    )


@router.post(
    "/submit",
    response_model=SubmitPracticeResponse,
    summary="Submit practice turn",
)
async def submit_practice(
    submit_data: SubmitPracticeRequest,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
) -> SubmitPracticeResponse:
    """Submit speech recognition result for a practice turn."""
    result = await db.execute(
        select(PracticeSession)
        .where(
            PracticeSession.id == submit_data.session_id,
            PracticeSession.user_id == current_user.id,
        )
        .options(selectinload(PracticeSession.speech_results))
    )
    session = result.scalar_one_or_none()

    if session is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail={
                "code": "SESSION_NOT_FOUND",
                "message": "Practice session not found",
            },
        )

    if session.status != SessionStatus.ACTIVE.value:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail={
                "code": "SESSION_NOT_ACTIVE",
                "message": "Practice session is not active",
            },
        )

    dialogue_result = await db.execute(
        select(Dialogue).where(Dialogue.id == session.dialogue_id)
    )
    dialogue = dialogue_result.scalar_one_or_none()

    expected_text = ""
    if dialogue:
        lines = dialogue.lines.get("lines", [])
        user_lines = [l for l in lines if l.get("speaker") == "user"]
        if session.current_turn < len(user_lines):
            expected_text = user_lines[session.current_turn].get("text", "")

    turn_result = SpeechResult(
        session_id=session.id,
        turn_index=session.current_turn,
        expected_text=expected_text,
        transcription=submit_data.transcription,
        pronunciation_score=submit_data.pronunciation_score,
        accuracy_score=submit_data.accuracy_score,
        fluency_score=submit_data.fluency_score,
        completeness_score=submit_data.completeness_score,
        feedback=submit_data.feedback,
    )

    db.add(turn_result)
    session.current_turn += 1

    is_completed = session.current_turn >= session.total_turns
    if is_completed:
        session.status = SessionStatus.COMPLETED.value
        session.ended_at = datetime.now(timezone.utc)

        turn_results = session.speech_results + [turn_result]
        if turn_results:
            session.overall_score = sum(
                t.pronunciation_score or 0 for t in turn_results
            ) / len(turn_results)
            session.average_accuracy = sum(
                t.accuracy_score or 0 for t in turn_results
            ) / len(turn_results)
            session.average_fluency = sum(
                t.fluency_score or 0 for t in turn_results
            ) / len(turn_results)
            session.average_completeness = sum(
                t.completeness_score or 0 for t in turn_results
            ) / len(turn_results)

    await db.commit()

    speech_result = SpeechResult(
        transcription=submit_data.transcription,
        expected_text=expected_text,
        pronunciation_score=submit_data.pronunciation_score,
        accuracy_score=submit_data.accuracy_score,
        fluency_score=submit_data.fluency_score,
        completeness_score=submit_data.completeness_score,
    )

    return SubmitPracticeResponse(
        session_id=str(session.id),
        turn_index=turn_result.turn_index,
        result=speech_result,
        feedback=submit_data.feedback,
        is_completed=is_completed,
        next_turn=session.current_turn if not is_completed else None,
    )
