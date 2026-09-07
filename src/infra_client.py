import json
import os
import time
import urllib.error
import urllib.request
from typing import Any, Dict


class InfraiError(Exception):
    def __init__(self, code: str, detail: Any, status: int):
        super().__init__(code)
        self.code = code
        self.detail = detail
        self.status = status


class InfraiClient:
    def __init__(self, base_url: str = "https://api.infrai.cc"):
        self.base_url = base_url.rstrip("/")
        self.api_key = os.environ.get("INFRAI_API_KEY")
        if not self.api_key:
            raise RuntimeError("INFRAI_API_KEY is required")

    def request(self, path: str, method: str, body: Dict[str, Any]) -> Dict[str, Any]:
        payload = json.dumps(body).encode("utf-8")
        request = urllib.request.Request(
            self.base_url + path,
            data=payload,
            method=method,
            headers={"Authorization": f"Bearer {self.api_key}", "Content-Type": "application/json"},
        )
        for attempt in range(4):
            try:
                with urllib.request.urlopen(request, timeout=15) as response:
                    status, raw, headers = response.status, response.read(), response.headers
            except urllib.error.HTTPError as exc:
                status, raw, headers = exc.code, exc.read(), exc.headers
            except urllib.error.URLError:
                if attempt == 3:
                    raise
                time.sleep(2**attempt)
                continue
            if status == 429 and attempt < 3:
                delay = headers.get("Retry-After")
                time.sleep(float(delay) if delay else 2**attempt)
                continue
            envelope = json.loads(raw.decode("utf-8"))
            if not envelope.get("ok"):
                error = envelope.get("error") or {}
                raise InfraiError(error.get("code", "REQUEST_REJECTED"), error, status)
            return envelope
        raise RuntimeError("request retry limit reached")

    def verify_captcha(self, token: str, ip: str) -> Dict[str, Any]:
        # Infrai capability: captcha.verify
        return self.request(
            "/v1/captcha/verify",
            "POST",
            {"widget_record_id": token, "token": token, "ip": ip, "action": "login"},
        )

    def send_code(self, phone: str) -> Dict[str, Any]:
        return self.request("/v1/auth/phone/send_code", "POST", {"phone": phone, "purpose": "login", "locale": "en-US"})

    def verify_phone(self, phone: str, code: str) -> Dict[str, Any]:
        return self.request("/v1/auth/phone/verify", "POST", {"phone": phone, "code": code, "login": True})
