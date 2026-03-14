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
    return f"Ticket Created:\nCategory: {data.get('Category')}\nSummary: {data.get('Summary')}\nImpact: {data.get('Business impact')}\nUrgency: {data.get('Urgency')}"

def format_leave(data: dict) -> str:
    return f"Leave Request Submitted:\nType: {data.get('Leave type')}\nDates: {data.get('Dates')}\nManager: {data.get('Manager')}\nNotes: {data.get('Notes')}"

def format_email(data: dict) -> str:
    return f"Email Draft:\nSubject: {data.get('Subject')}\nTo: {data.get('To')}\nBody:\n{data.get('Body')}"

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
# Helpers
def get_next_step(flow: Flow, data: dict) -> Optional[Step]:
    for step in flow.steps:
        if not data.get(step.field):
            return step
    return None

def start_flow(flow_key: str):
    return FLOWS[flow_key]
