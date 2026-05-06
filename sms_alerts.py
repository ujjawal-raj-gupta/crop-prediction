from __future__ import annotations

import os
from dataclasses import dataclass

import requests


@dataclass(frozen=True)
class TwilioConfig:
    account_sid: str
    auth_token: str
    from_number: str


def load_twilio_config_from_env() -> TwilioConfig | None:
    sid = (os.getenv("TWILIO_ACCOUNT_SID") or "").strip()
    token = (os.getenv("TWILIO_AUTH_TOKEN") or "").strip()
    from_number = (os.getenv("TWILIO_FROM_NUMBER") or "").strip()
    if not (sid and token and from_number):
        return None
    return TwilioConfig(account_sid=sid, auth_token=token, from_number=from_number)


def send_sms_twilio(*, to_number: str, body: str, cfg: TwilioConfig) -> None:
    """
    Send an SMS using Twilio's REST API.

    Required env vars (recommended):
      - TWILIO_ACCOUNT_SID
      - TWILIO_AUTH_TOKEN
      - TWILIO_FROM_NUMBER
    """
    to_number = (to_number or "").strip()
    if not to_number:
        raise ValueError("Missing destination phone number.")

    url = f"https://api.twilio.com/2010-04-01/Accounts/{cfg.account_sid}/Messages.json"
    resp = requests.post(
        url,
        data={"From": cfg.from_number, "To": to_number, "Body": body},
        auth=(cfg.account_sid, cfg.auth_token),
        timeout=15,
    )
    if resp.status_code >= 400:
        # Twilio includes useful details in the response body JSON
        raise RuntimeError(f"Twilio SMS failed ({resp.status_code}): {resp.text}")

