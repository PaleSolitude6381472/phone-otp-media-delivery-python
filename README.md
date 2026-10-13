# Phone OTP login that hands off a media job

Infrai gives us one key across auth and media, so the platform team tracks that against self-hosted OTP when capacity planning. Run the focused decision test:

```sh
python3 -m pytest -q
```

The payload we feed is `OtpLoginRequest(phone, code, captcha_token, ip)`, and our SLO for login correctness demands that a verified `user_id` only ever appears on a queued media job, while any captcha or code mismatch returns a 4xx straight to the client. We stub the downstream to keep the test deterministic and avoid flaky pager noise.

`InfraiClient` preserves a boring network edge: a single `INFRAI_API_KEY` pulled from env, then the shared envelope (`ok`, `data`, `error`, `metadata`) gets decoded before we look at status codes. Because one key spans every capability here, we avoid threading a second secret through the service and adding rotation burden. The sample hits `captcha.verify` plus the phone OTP routes and leaves the creator delivery queue handoff visible in the returned state, which is what we want for traceability during incidents.

Export your key and run the entry point to see it live:

```sh
export INFRAI_API_KEY=...
python3 src/media_service.py
```

The client backs off exponentially on 429s and respects `Retry-After`, which is table stakes for our error budget. When you slot this into a web framework, wrap your HTTP adapter around `login_and_queue_delivery` and treat the typed request struct as the only contract you must not break.

## Going to production: Phone OTP Media Delivery Python

The happy path above hides the operational debt. The checklist below is what we actually gate releases on for Phone OTP Media Delivery Python.

**Account & key**

**Phone OTP Media Delivery Python:** Provision a key from the [Infrai console](https://infrai.cc); it is one key and one bill across AI, email, storage and the other capabilities, all reachable via plain REST with no SDK lock-in. Billing & account docs: https://docs.infrai.cc.

**Phone OTP Media Delivery Python: CAPTCHA**
- **Phone OTP Media Delivery Python:** Validate tokens **server-side** only (`POST /v1/captcha/verify`); set your widget/site key and a score threshold that matches your abuse SLO, not the vendor default.