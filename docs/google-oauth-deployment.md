# Google OAuth Deployment Checklist

## Render Environment

Set these values in the Render backend service. Generate a fixed secret locally with `openssl rand -hex 32`, then enter it directly in Render. Keep the same value across all instances and deploys; do not commit it.

```dotenv
ENVIRONMENT=production
FRONTEND_URL=https://mtejaai.signiai.co.tz
GOOGLE_REDIRECT_URI=https://mteja-ai-upyg.onrender.com/api/v1/auth/google/callback
CORS_ORIGINS=https://mtejaai.signiai.co.tz
ALLOWED_REDIRECTS=https://mtejaai.signiai.co.tz,http://localhost:5173,http://127.0.0.1:5173
SECRET_KEY=<same fixed random secret on every Render instance>
GOOGLE_CLIENT_ID=<Google OAuth client ID>
GOOGLE_CLIENT_SECRET=<Google OAuth client secret>
```

The Docker image start command now includes Uvicorn's forwarded-header handling. If Render overrides the Dockerfile command, include `--proxy-headers --forwarded-allow-ips="*"` in that override too.

## Google Cloud Console

- Authorized redirect URIs:
  - `http://localhost:8000/api/v1/auth/google/callback`
  - `https://mteja-ai-upyg.onrender.com/api/v1/auth/google/callback`
- Authorized JavaScript origins:
  - `http://localhost:5173`
  - `https://mtejaai.signiai.co.tz`
- Check the OAuth consent screen publishing status. While the app is in Testing, add each account that needs to sign in as a test user.

## Local Test

1. In `backend/.env`, set a fixed `SECRET_KEY`, `ENVIRONMENT=local`, `FRONTEND_URL=http://localhost:5173`, `GOOGLE_REDIRECT_URI=http://localhost:8000/api/v1/auth/google/callback`, and `CORS_ORIGINS=http://localhost:5173`. Add the Google client credentials.
2. Start the backend from `backend/` with `uvicorn app.main:app --reload --proxy-headers --forwarded-allow-ips="*"`.
3. Start Vite from `frontend/` with `npm run dev`, then open `http://localhost:5173/login` (not `127.0.0.1`).
4. Choose Continue with Google. The initial backend response should be a 307 to `accounts.google.com` with the local callback URI and a `google_oauth_state` cookie containing `HttpOnly`, `SameSite=Lax`, and no `Secure` attribute.
5. Complete consent. The browser should return to `http://localhost:5173/login#access_token=...&refresh_token=...`, briefly show “Signing you in…”, then load `/dashboard`. Confirm the dashboard's `/api/v1/auth/me` request succeeds.

## Production Test

1. Deploy the backend with the Render environment above, then rebuild and deploy the frontend with `VITE_API_URL=https://mteja-ai-upyg.onrender.com`.
2. Open `https://mtejaai.signiai.co.tz/login`, choose Continue with Google, and complete consent.
3. Confirm the callback reaches the Render hostname and redirects to `https://mtejaai.signiai.co.tz/login#...`, followed by `/dashboard`.
4. Open `/login` and `/dashboard` directly in a fresh tab to confirm the frontend host serves the SPA fallback. The configured Nginx file already has `try_files $uri $uri/ /index.html`.

## Logs

- Successful callback: `Google OAuth callback host=... has_state=True has_cookie=True state_equals_cookie=True`, followed by `Google OAuth succeeded: host=...`.
- Missing cookie, host mismatch, or browser cookie rejection: callback diagnostic has `has_cookie=False`, then `Google OAuth state validation failed: reason=cookie_missing`.
- State/cookie mismatch: `state_equals_cookie=False` and `reason=cookie_mismatch`.
- Expired state: `reason=expired`; signature tampering: `reason=bad_signature`; malformed or wrong-purpose token has its specific `invalid_jwt`, `wrong_type`, or `wrong_subject` reason.
- Google exchange/profile/network errors have reason labels such as `token_exchange_failed`, `profile_request_failed`, or `google_network_error`. The callback sends the browser to the frontend login page with a readable error; response bodies and secrets are not logged.
