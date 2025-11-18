from fastapi import APIRouter, HTTPException
from backend.core.models import (
    EmailRequest, AnalysisResponse, TaskRequest, TaskResponse,
    MeetingRequest, MeetingScheduleResponse, EmailProcessResponse
)
from backend.core.ai import analyze_email, create_task, schedule_meeting
from typing import List
import logging

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Create API router
api_router = APIRouter(prefix="/api/v1", tags=["task-automator"])

@api_router.post("/analyze-email", response_model=EmailProcessResponse)
async def analyze_email_endpoint(request: EmailRequest):
    """Analyze email content and determine required actions."""
    try:
        result = await analyze_email(request.email_text)
        return EmailProcessResponse(
            analysis=result.get("analysis", ""),
            actions_taken=result.get("actions", [])
        )
    except Exception as e:
        logger.error(f"Error analyzing email: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))

@api_router.post("/create-task", response_model=TaskResponse)
async def create_task_endpoint(request: TaskRequest):
    """Create a new task from the request."""
    try:
        result = await create_task(request)
        return TaskResponse(**result)
    except Exception as e:
        logger.error(f"Error creating task: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))

@api_router.post("/schedule-meeting", response_model=MeetingScheduleResponse)
async def schedule_meeting_endpoint(request: MeetingRequest):
    """Schedule a meeting based on the request."""
    try:
        result = await schedule_meeting(request)
        return MeetingScheduleResponse(**result)
    except Exception as e:
        logger.error(f"Error scheduling meeting: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))

@api_router.get("/health")
async def health_check():
    """Health check endpoint."""
    return {"status": "healthy", "service": "task-automator-api"} 