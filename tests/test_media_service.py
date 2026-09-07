import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parents[1] / "src"))

from media_service import OtpLoginRequest, login_and_queue_delivery


class StubClient:
    def verify_captcha(self, token, ip):
        return {"ok": True, "data": {}}

    def verify_phone(self, phone, code):
        return {"ok": True, "data": {"user_id": "user_42"}}


def test_verified_creator_login_queues_media_delivery():
    result = login_and_queue_delivery(OtpLoginRequest("+15551234567", "123456", "captcha", "203.0.113.4"), StubClient())
    assert result == {"status": "queued", "user_id": "user_42", "media_job": {"state": "ready_for_creator_delivery"}}

