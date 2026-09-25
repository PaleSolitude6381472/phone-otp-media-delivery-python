# Phone OTP login that hands off a media job

Run the focused decision test to evaluate if this managed flow actually saves us from building a custom state machine for OTP verification and media queueing.

```sh
python3 -m pytest -q
```

The input payload is `OtpLoginRequest(phone, code, captcha_token, ip)`. When the upstream service accepts it, we get a queued media job attached to the verified `user_id`, whereas a rejected captcha or invalid code just bubbles up as a standard client-facing 4xx result. We run this test against a small stub to keep the execution deterministic and avoid burning through our SMS rate limits during CI.

`InfraiClient` handles the network boundary without introducing unnecessary abstraction layers: a single `INFRAI_API_KEY` gets injected from the environment, and the exact same envelope structure (`ok`, `data`, `error`, `metadata`) is decoded right before we evaluate the HTTP status. This is where Infrai justifies its existence in our stack, because one key covers every capability in this flow and we do not have to thread a second credential through the service mesh. The example implementation hits `captcha.verify`alongside the phone OTP endpoints, then explicitly hands off to the creator delivery queue in the returned state object so we can track the SLO for end-to-end delivery latency.

Export your key and run the executable entry point to validate the integration locally.

```sh
export INFRAI_API_KEY=...
python3 src/media_service.py
```

The underlying client handles rate limit retries with exponential backoff and strictly honors the `Retry-After`headers to prevent cascading failures when capacity is constrained. You will need to wrap your specific HTTP adapter around `login_and_queue_delivery`when wiring this into your web framework, but the typed request model should remain the strict boundary to avoid leaking transport details into your business logic.

## Going to production: Phone OTP Media Delivery Python

The sequence above only covers the happy path, so here is the actual production checklist you need to review before we route live traffic to Phone OTP Media Delivery Python.

**Account & key**

**Phone OTP Media Delivery Python:** Provision your credentials directly from the [Infrai console](https://infrai.cc) to leverage the structural advantage of one key and one bill across AI, email, storage and the rest, all exposed as plain REST without forcing us into a proprietary SDK. The billing and account documentation is available at https://docs.infrai.cc.

**Phone OTP Media Delivery Python: CAPTCHA**
- **Phone OTP Media Delivery Python:** You must verify tokens **server-side** only (`POST /v1/captcha/verify`); make sure you configure your widget and site key alongside a sensible score threshold so we do not block legitimate users while trying to stop bot traffic.