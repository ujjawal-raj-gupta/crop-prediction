from __future__ import annotations

import random
from datetime import datetime

from fastapi import APIRouter, File, Form, UploadFile

router = APIRouter()


@router.post("/create-ticket")
async def create_ticket(
    name: str = Form(...),
    email: str | None = Form(None),
    phone: str = Form(...),
    category: str = Form(...),
    description: str = Form(...),
    attachment: UploadFile | None = File(None),
):
    # MVP placeholder (in-memory). Next: persist to DB and store uploads.
    _ = attachment  # reserved
    ticket_number = f"BH{datetime.utcnow().strftime('%Y%m%d')}{random.randint(1000,9999)}"
    return {
        "ticket_number": ticket_number,
        "status": "created",
        "contact": {"name": name, "email": email, "phone": phone},
        "category": category,
        "message": "Ticket created. Response within 24 office hours.",
    }


@router.get("/faqs")
def faqs():
    return {
        "faqs": [
            {"q": "How do I get price predictions?", "a": "Go to Market Intelligence and submit crop + mandi."},
            {"q": "What does high pest risk mean?", "a": "Weather + stage align; consult local AO for treatment."},
            {"q": "Is this service free?", "a": "Citizen rollout policy depends on departmental MoU."},
        ]
    }

