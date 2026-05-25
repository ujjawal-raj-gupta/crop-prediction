from __future__ import annotations

import os
import random
from datetime import datetime

from fastapi import APIRouter, File, Form, UploadFile

from src.db.models import SupportTicket
from src.db.session import session_scope

router = APIRouter()

_UPLOAD_DIR_ENV = os.getenv("SUPPORT_UPLOAD_DIR", "data/support_uploads")


@router.post("/create-ticket")
async def create_ticket(
    name: str = Form(...),
    phone: str = Form(...),
    category: str = Form(...),
    message: str = Form(...),
    email: str | None = Form(None),
    screenshot: UploadFile | None = File(None),
):
    ticket_number = f"BH{datetime.utcnow().strftime('%Y%m%d')}{random.randint(1000, 9999)}"
    screenshot_name: str | None = None
    if screenshot and screenshot.filename:
        dest_root = os.path.abspath(_UPLOAD_DIR_ENV)
        os.makedirs(dest_root, exist_ok=True)
        safe_base = "".join(c for c in screenshot.filename if c.isalnum() or c in "._-")[:120] or "upload"
        screenshot_name = f"{ticket_number}_{safe_base}"
        path = os.path.join(dest_root, screenshot_name)
        data = await screenshot.read()
        if data:
            with open(path, "wb") as f:
                f.write(data)

    with session_scope() as s:
        row = SupportTicket(
            ticket_number=ticket_number,
            name=name.strip()[:100],
            phone=phone.strip()[:20],
            email=(email or "").strip()[:100] or None,
            category=category.strip()[:50],
            message=message.strip()[:4000],
            screenshot_filename=screenshot_name,
            status="open",
        )
        s.add(row)

    return {
        "ticket_number": ticket_number,
        "status": "created",
        "message": "Ticket logged. Agriculture Department support will respond within 24 office hours.",
    }


@router.get("/recent-alerts-summary")
def recent_activity_teaser(limit: int = 8):
    """Lightweight teaser rows for homepage ticker (reads pest alerts table)."""
    from sqlalchemy import desc, select

    from src.db.models import PestAlert

    lim = max(1, min(limit, 50))
    rows: list[dict] = []
    with session_scope() as s:
        q = s.execute(select(PestAlert).order_by(desc(PestAlert.created_at)).limit(lim)).scalars().all()
        for a in q:
            rows.append(
                {
                    "type": "pest_alert",
                    "severity": ("high" if a.risk_score >= 61 else "medium" if a.risk_score >= 31 else "low"),
                    "title": f"{a.crop}: {a.pest_name}",
                    "risk_score": a.risk_score,
                    "created_at": a.created_at.isoformat() if a.created_at else "",
                }
            )
    return {"items": rows}
