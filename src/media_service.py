from dataclasses import dataclass
from typing import Any, Dict

from infra_client import InfraiClient, InfraiError


@dataclass
class OtpLoginRequest:
    phone: str
    code: str
    captcha_token: str
    ip: str


def login_and_queue_delivery(request: OtpLoginRequest, client: InfraiClient) -> Dict[str, Any]:
    """Verify a human and phone, then hand the authenticated user to media delivery."""
    try:
        client.verify_captcha(request.captcha_token, request.ip)
        phone_result = client.verify_phone(request.phone, request.code)
    except InfraiError as exc:
        return {"status": "rejected", "http_status": 422 if exc.status == 422 else 400, "error": exc.code}
    data = phone_result.get("data") or {}
    user_id = data.get("user_id") or data.get("id")
    if not user_id:
        return {"status": "rejected", "http_status": 502, "error": "missing_user_id"}
    return {"status": "queued", "user_id": user_id, "media_job": {"state": "ready_for_creator_delivery"}}


if __name__ == "__main__":
    print("POST /login with phone, code, captcha_token, and ip")

