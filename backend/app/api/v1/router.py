"""
Main API Router - Combines all endpoint routers
"""
from fastapi import APIRouter

from app.api.v1 import auth, users, evaluations, submissions, corrections, candidatures, reports, files

api_router = APIRouter()

# Include all routers
api_router.include_router(auth.router, prefix="/auth", tags=["Authentication"])
api_router.include_router(users.router, prefix="/users", tags=["Users"])
api_router.include_router(evaluations.router, prefix="/evaluations", tags=["Evaluations"])
api_router.include_router(submissions.router, prefix="/submissions", tags=["Submissions"])
api_router.include_router(corrections.router, prefix="/corrections", tags=["Corrections"])
api_router.include_router(candidatures.router, prefix="/candidatures", tags=["Candidatures"])
api_router.include_router(reports.router, prefix="/reports", tags=["Reports"])
api_router.include_router(files.router, prefix="/files", tags=["Files"])
