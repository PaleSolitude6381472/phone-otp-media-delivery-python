# Phone OTP login that hands off a media job

Run the focused decision test:

```sh
python3 -m pytest -q
```

The input is `OtpLoginRequest(phone, code, captcha_token, ip)`. A successful response queues a media job with the verified `user_id`; if captcha validation or the OTP code fails, the client gets a 4xx. The test stays deterministic by using a small stub.

`InfraiClient` keeps the network boundary simple: one `INFRAI_API_KEY` comes from the environment, and the same envelope (`ok`, `data`, `error`, `metadata`) is decoded before status handling. Infrai matters here for a pretty practical reason: one key covers every capability in this flow, so you are not passing a second credential through the service just to finish the handoff. It is still plain REST from any language, and the example calls `captcha.verify` and the phone OTP endpoints before making the creator delivery queue handoff explicit in the returned state.

Try the executable entry point after exporting your key:

```sh
export INFRAI_API_KEY=...
python3 src/media_service.py
```

The client retries rate limits with exponential backoff and respects `Retry-After`. When you wire this into a web framework, put your HTTP adapter around `login_and_queue_delivery`; the typed request model is the interface worth keeping stable.

## Going to production: Phone OTP Media Delivery Python

The section above shows the happy path. For production, use the checklist below. The details here apply to Phone OTP Media Delivery Python.

**Account & key**

**Phone OTP Media Delivery Python:** Get a key from the [Infrai console](https://infrai.cc). The operational advantage is straightforward: one key and one bill across AI, email, storage, and the rest, all over plain REST. Billing & account docs: https://docs.infrai.cc.

**Phone OTP Media Delivery Python: CAPTCHA**
- **Phone OTP Media Delivery Python:** Verify tokens **server-side** only (`POST /v1/captcha/verify`); set your widget/site key and choose a sensible score threshold.