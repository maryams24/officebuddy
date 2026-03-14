# flows.py
from dataclasses import dataclass
from typing import List

@dataclass
class Step:
    field: str
    prompt: str
    required: bool = True

@dataclass
class Flow:
    name: str
    steps: List[Step]

FLOWS = {
    "ticket": Flow(
        "Raise a Ticket",
        [
            Step("category", "Ticket category? (IT/HR/Facilities/Payroll/Other)"),
            Step("summary", "Short summary (one line)"),
            Step("business_impact", "Business impact (what is blocked?)"),
            Step("urgency", "Urgency (Low/Medium/High/Critical)")
        ]
    ),
    "leave": Flow(
        "Leave Request",
        [
            Step("leave_type", "Leave type? (PTO/Sick/Personal/Other)"),
            Step("dates", "Leave dates (start - end)"),
            Step("coverage_plan", "Who will cover your work?"),
            Step("manager", "Manager name")
        ]
    ),
    "email": Flow(
        "Email Draft",
        [
            Step("subject", "Email subject"),
            Step("recipient", "Recipient name or email"),
            Step("body", "Email body / request details")
        ]
    )
}
