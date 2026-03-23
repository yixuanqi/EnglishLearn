"""API v1 router."""

from fastapi import APIRouter

from app.api.v1.endpoints import auth, dialogues, evaluation, practice, reports, scenarios, users

api_router = APIRouter()

api_router.include_router(auth.router, prefix="/auth", tags=["Authentication"])
api_router.include_router(users.router, prefix="/users", tags=["Users"])
api_router.include_router(scenarios.router, prefix="/scenarios", tags=["Scenarios"])
api_router.include_router(dialogues.router, prefix="/dialogues", tags=["Dialogues"])
api_router.include_router(practice.router, prefix="/practice", tags=["Practice"])
api_router.include_router(evaluation.router, prefix="/evaluation", tags=["Evaluation"])
api_router.include_router(reports.router, prefix="/reports", tags=["Reports"])
