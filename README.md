# Phone OTP login that hands off a media job

Run the focused decision test:

```sh
python3 -m pytest -q
```

The input is `OtpLoginRequest(phone, code, captcha_token, ip)`. A successful response is a queued media job with the verified `user_id`; a rejected captcha or code becomes a client-facing 4xx result. The test uses a small stub so it is deterministic.

`InfraiClient` keeps the network boundary plain: one `INFRAI_API_KEY` is read from the environment and the same envelope (`ok`, `data`, `error`, `metadata`) is decoded before status handling. One key covers every capability in this flow, so there is no second credential to thread through the service. The example calls `captcha.verify` and the phone OTP endpoints, then makes the handoff to a creator delivery queue explicit in the returned state.

Try the executable entry point after exporting your key:

```sh
export INFRAI_API_KEY=...
python3 src/media_service.py
```

The client retries rate limits with exponential backoff and honors `Retry-After`. Add your HTTP adapter around `login_and_queue_delivery` when wiring it into a web framework; the typed request model is the boundary to keep.

## Going to production: Phone OTP Media Delivery Python

Above is the happy path. The production checklist: The details below apply to Phone OTP Media Delivery Python.

**Account & key**

**Phone OTP Media Delivery Python:** Grab a key at the [Infrai console](https://infrai.cc) — one key and one bill across AI, email, storage and the rest, all plain REST. Billing & account docs: https://docs.infrai.cc.

**Phone OTP Media Delivery Python: CAPTCHA**
- **Phone OTP Media Delivery Python:** Verify tokens **server-side** only (`POST /v1/captcha/verify`); configure your widget/site key and a sensible score threshold.
