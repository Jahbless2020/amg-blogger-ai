This document explains how to securely provide your sensitive files (credentials.json and token.json) and environment variables to the bot without committing secrets to the repository.

Recommended approaches (pick one):

A) Use your hosting provider's environment/secret manager (Render, Railway, Heroku, etc.)
- Base64-encode your credentials.json and token.json and paste the single-line base64 strings as environment variables.
- Set TELEGRAM_TOKEN, GEMINI_API_KEY, BLOG_ID as normal environment variables in the host UI.

B) Use GitHub Actions / Secrets (for CI/CD deployments)
- Add secrets to the repository or organization secrets (NOT in code).
- Use workflow to pass secrets to the deployment target.

C) Local development (safe local files)
- Keep credentials.json and token.json on your local machine only.
- Do NOT commit them. Use .gitignore to ensure they are not added.

How to base64-encode the JSON files (Linux / macOS)

1. Base64-encode credentials.json:
   cat credentials.json | base64 | tr -d '\n' > credentials.b64

2. Base64-encode token.json:
   cat token.json | base64 | tr -d '\n' > token.b64

3. Copy the single-line contents of credentials.b64 and token.b64 into your host's secret fields for B64_CREDENTIALS_JSON and B64_TOKEN_JSON respectively.

PowerShell (Windows)

1. Base64-encode credentials.json:
   [Convert]::ToBase64String([IO.File]::ReadAllBytes("credentials.json")) > credentials.b64

2. Base64-encode token.json:
   [Convert]::ToBase64String([IO.File]::ReadAllBytes("token.json")) > token.b64

Security notes
- Never paste credentials.json or token.json directly into chat or commit them to the repository.
- If you accidentally commit a secret, rotate it immediately and remove it from history (BFG or git filter-repo).
- The repository includes write_secrets.py which will decode and write credentials.json and token.json from the B64_* environment variables at startup. This avoids storing the raw files in the repository.

Using the repository on a host
1. Set environment variables in the host (B64_CREDENTIALS_JSON, B64_TOKEN_JSON, TELEGRAM_TOKEN, GEMINI_API_KEY, BLOG_ID).
2. Deploy or start the app — the startup code will write credentials.json and token.json if the base64 envs are present.

If you want, I can also add example commands for specific hosts (Render / Railway / Heroku). Tell me which host you plan to use.