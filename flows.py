# flows.py
from dataclasses import dataclass
from typing import List, Callable, Optional

@dataclass
class Step:
    field: str
    prompt: str
    required: bool = True

@dataclass
class Flow:
    name: str
    steps: List[Step]
    formatter: Callable[[dict], str]

# =========================
# Flow formatters
def format_ticket(data: dict) -> str:
    return (
        f"Ticket Created:\n"
        f"Category: {data.get('Category')}\n"
        f"Summary: {data.get('Summary')}\n"
        f"Business Impact: {data.get('Business impact')}\n"
        f"Urgency: {data.get('Urgency')}"
    )

def format_leave(data: dict) -> str:
    return (
        f"Leave Request Submitted:\n"
        f"Type: {data.get('Leave type')}\n"
        f"Dates: {data.get('Dates')}\n"
        f"Manager: {data.get('Manager')}\n"
        f"Notes: {data.get('Notes')}"
    )

def format_email(data: dict) -> str:
    return (
        f"Email Draft:\n"
        f"Subject: {data.get('Subject')}\n"
        f"To: {data.get('To')}\n"
        f"Body:\n{data.get('Body')}"
    )

# =========================
# Define flows
FLOWS = {
    "ticket": Flow(
        "ticket",
        [
            Step("Category", "Ticket category? (IT/HR/Facilities/Payroll/Other)"),
            Step("Summary", "Short summary (one line)"),
            Step("Business impact", "Who/what is blocked?"),
            Step("Urgency", "Urgency level (Low/Medium/High/Critical)")
        ],
        format_ticket
    ),
    "leave": Flow(
        "leave",
        [
            Step("Leave type", "Leave type? (PTO/Sick/Personal/Other)"),
            Step("Dates", "Leave dates (start - end)"),
            Step("Manager", "Manager name"),
            Step("Notes", "Any notes (optional)")
        ],
        format_leave
    ),
    "email": Flow(
        "email",
        [
            Step("Subject", "Email subject"),
            Step("To", "Recipient(s)"),
            Step("Body", "Email body")
        ],
        format_email
    )
}

# =========================
# Helper to get the next unanswered step
def get_next_step(flow: Flow, data: dict):
    for step in flow.steps:
        if not data.get(step.field):
            return step
    return None
