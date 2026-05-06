from __future__ import annotations

import time

from db import fetch_due_pending_jobs, init_db, mark_job_failed, mark_job_sent
from sms_alerts import load_twilio_config_from_env, send_sms_twilio


def main() -> None:
    init_db()
    cfg = load_twilio_config_from_env()
    if cfg is None:
        raise RuntimeError(
            "Twilio is not configured. Set TWILIO_ACCOUNT_SID, TWILIO_AUTH_TOKEN, TWILIO_FROM_NUMBER."
        )

    # Simple polling loop (cloud-friendly). Run this as a separate worker process.
    while True:
        due = fetch_due_pending_jobs(limit=25)
        for job in due:
            try:
                send_sms_twilio(to_number=str(job["to_number"]), body=str(job["body"]), cfg=cfg)
                mark_job_sent(job_id=int(job["id"]))
            except Exception as e:
                mark_job_failed(job_id=int(job["id"]), error=str(e))
        time.sleep(20)


if __name__ == "__main__":
    main()

