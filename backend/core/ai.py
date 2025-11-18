from .config import openai_client, MODEL_ID
from .models import EmailRequest, MeetingRequest, TaskRequest, EmailAnalysisResponse  # Import EmailAnalysisResponse from models.py
import json
from typing import Dict, Any, List
from datetime import datetime
import asyncio
import logging

logger = logging.getLogger(__name__)

async def analyze_email(email_text: str) -> Dict[str, Any]:
    """
    Analyze email content using the fine-tuned GPT model to determine required actions.
    
    Args:
        email_text: The full email text to analyze
        
    Returns:
        Dictionary containing analysis and suggested actions
    """
    try:
        # Create the prompt for email analysis
        system_prompt = """You are an AI assistant that analyzes emails and determines what actions need to be taken. 
        You can identify if an email requires:
        1. Meeting scheduling
        2. Task creation
        3. Simple response
        4. No action needed
        
        Respond with a JSON object containing:
        {
            "analysis": "Brief analysis of the email content",
            "action_type": "meeting|task|response|none",
            "confidence": 0.95,
            "extracted_data": {
                "organizer": "name or email",
                "attendees": ["list", "of", "attendees"],
                "proposed_dates": ["YYYY-MM-DD"],
                "duration": "1 hour",
                "task_description": "task description if applicable",
                "assigned_to": "person name",
                "deadline": "YYYY-MM-DD",
                "priority": "Low|Medium|High|Urgent"
            }
        }"""
        
        response = await asyncio.to_thread(
            openai_client.chat.completions.create,
            model=MODEL_ID,
            messages=[
                {"role": "system", "content": system_prompt},
                {"role": "user", "content": f"Analyze this email:\n\n{email_text}"}
            ],
            temperature=0.1,
            max_tokens=1000
        )
        
        # Parse the response
        content = response.choices[0].message.content
        try:
            result = json.loads(content)
        except json.JSONDecodeError:
            # Fallback if JSON parsing fails
            result = {
                "analysis": content,
                "action_type": "none",
                "confidence": 0.5,
                "extracted_data": {}
            }
        
        # Determine actions based on analysis
        actions = []
        if result.get("action_type") == "meeting":
            actions.append({
                "type": "schedule_meeting",
                "data": result.get("extracted_data", {})
            })
        elif result.get("action_type") == "task":
            actions.append({
                "type": "create_task",
                "data": result.get("extracted_data", {})
            })
        
        return {
            "analysis": result.get("analysis", "Analysis completed"),
            "actions": actions,
            "confidence": result.get("confidence", 0.5)
        }
        
    except Exception as e:
        logger.error(f"Error in email analysis: {str(e)}")
        return {
            "analysis": f"Error analyzing email: {str(e)}",
            "actions": [],
            "confidence": 0.0
        }

async def create_task(task_request: TaskRequest) -> Dict[str, Any]:
    """
    Create a task using the AI model to enhance the task description.
    
    Args:
        task_request: TaskRequest object with task details
        
    Returns:
        Dictionary containing the created task information
    """
    try:
        # Enhance task description using AI
        enhancement_prompt = f"""Enhance this task description to be more specific and actionable:
        
        Original: {task_request.description}
        Assigned to: {task_request.assigned_to}
        Deadline: {task_request.deadline}
        Priority: {task_request.priority}
        
        Provide an enhanced description that includes:
        1. Clear objectives
        2. Specific deliverables
        3. Success criteria
        4. Any dependencies or prerequisites
        
        Return only the enhanced description."""
        
        response = await asyncio.to_thread(
            openai_client.chat.completions.create,
            model=MODEL_ID,
            messages=[
                {"role": "user", "content": enhancement_prompt}
            ],
            temperature=0.3,
            max_tokens=500
        )
        
        enhanced_description = response.choices[0].message.content.strip()
        
        # Create task response
        import uuid
        from datetime import datetime
        
        task_id = str(uuid.uuid4())
        current_time = datetime.now().isoformat()
        
        return {
            "id": task_id,
            "description": enhanced_description,
            "assigned_to": task_request.assigned_to,
            "deadline": task_request.deadline,
            "priority": task_request.priority.value,
            "status": "To Do",
            "created_at": current_time,
            "updated_at": current_time
        }
        
    except Exception as e:
        logger.error(f"Error creating task: {str(e)}")
        raise Exception(f"Failed to create task: {str(e)}")

async def schedule_meeting(meeting_request: MeetingRequest) -> Dict[str, Any]:
    """
    Schedule a meeting using the AI model to optimize timing and provide recommendations.
    
    Args:
        meeting_request: MeetingRequest object with meeting details
        
    Returns:
        Dictionary containing meeting scheduling results
    """
    try:
        # Analyze meeting request and provide recommendations
        analysis_prompt = f"""Analyze this meeting request and provide scheduling recommendations:
        
        Organizer: {meeting_request.organizer}
        Attendees: {', '.join(meeting_request.attendees)}
        Proposed dates: {', '.join(meeting_request.proposed_dates)}
        Duration: {meeting_request.duration}
        
        Provide recommendations for:
        1. Best meeting time from the proposed dates
        2. Meeting agenda suggestions
        3. Preparation requirements
        4. Follow-up actions
        
        Return as JSON:
        {{
            "recommendation": "analysis text",
            "best_date": "YYYY-MM-DD",
            "suggested_time": "HH:MM",
            "agenda": ["item1", "item2"],
            "preparation": ["prep1", "prep2"],
            "follow_up": ["action1", "action2"]
        }}"""
        
        response = await asyncio.to_thread(
            openai_client.chat.completions.create,
            model=MODEL_ID,
            messages=[
                {"role": "user", "content": analysis_prompt}
            ],
            temperature=0.2,
            max_tokens=800
        )
        
        content = response.choices[0].message.content
        try:
            analysis = json.loads(content)
        except json.JSONDecodeError:
            analysis = {
                "recommendation": content,
                "best_date": meeting_request.proposed_dates[0] if meeting_request.proposed_dates else "",
                "suggested_time": "09:00",
                "agenda": [],
                "preparation": [],
                "follow_up": []
            }
        
        # Simulate calendar event creation
        event_details = {
            "summary": f"Meeting with {meeting_request.organizer}",
            "description": analysis.get("recommendation", "Meeting scheduled"),
            "start_time": f"{analysis.get('best_date', '')}T{analysis.get('suggested_time', '09:00')}:00",
            "end_time": f"{analysis.get('best_date', '')}T{analysis.get('suggested_time', '09:00')}:00",
            "attendees": meeting_request.attendees,
            "organizer": meeting_request.organizer
        }
        
        return {
            "recommendation": analysis.get("recommendation", "Meeting analysis completed"),
            "event_created": True,
            "event_details": event_details,
            "scheduled_time": {
                "date": analysis.get("best_date", ""),
                "time": analysis.get("suggested_time", "09:00")
            }
        }
        
    except Exception as e:
        logger.error(f"Error scheduling meeting: {str(e)}")
        raise Exception(f"Failed to schedule meeting: {str(e)}")

def categorize_email(email_text: str):
    """Categorize an email using the fine-tuned model."""
    response = openai_client.chat.completions.create(
        model=MODEL_ID,
        messages=[
            {"role": "system", "content": "You are an email categorization assistant."},
            {"role": "user", "content": f"Categorize this email: {email_text}"}
        ]
    )
    return response.choices[0].message.content.strip()

def prioritize_task(task_data: TaskRequest):
    """Analyze and prioritize a task using the fine-tuned model."""
    task_info = (
        f"Description: {task_data.description}\n"
        f"Assigned To: {task_data.assigned_to}\n"
        f"Deadline: {task_data.deadline}\n"
        f"Priority: {task_data.priority}"
    )
    
    response = openai_client.chat.completions.create(
        model=MODEL_ID,
        messages=[
            {"role": "system", "content": "You are a task prioritization assistant."},
            {"role": "user", "content": f"Analyze this task and suggest optimal handling: {task_info}"}
        ]
    )
    return response.choices[0].message.content.strip()