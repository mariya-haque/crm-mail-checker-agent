# Mail Checker Agent

A FastAPI service that answers natural-language questions about a CRM mailbox, such as "How many emails did I get from Cursor?" or "How many unread emails do I have?". An OpenAI Agents SDK agent uses two tools that fetch inbox messages from the CRM mail API and count them by sender or unread status. It replies in Roman Urdu when the question is written that way. A single-page chat UI (`chat.html`) talks to the API.

## Files

| File | Purpose |
|------|---------|
| `API.py` | FastAPI app with `POST /ask` and `GET /health`, CORS open to all origins. |
| `agent.py` | The `Mail Checker Agent` and its tools `check_emails_from_sender` and `check_total_emails`. |
| `mail.py` | CRM mail API client: paginated message fetch, filtering and de-duplication. Can be run on its own as a connectivity test. |
| `chat.html` | Browser chat UI that posts to `http://localhost:5000/ask`. |

## Tech stack

Python 3.10+, FastAPI, Uvicorn, `openai-agents`, `requests`, vanilla HTML/JS.

## Setup

```bash
python -m venv .venv
source .venv/bin/activate        # Windows: .venv\Scripts\activate
pip install -r requirements.txt
cp .env.example .env             # then fill in the values
```

| Variable | Description | Where to get it |
|----------|-------------|-----------------|
| `OPENAI_API_KEY` | OpenAI API key, read automatically by the SDK | https://platform.openai.com/api-keys |
| `CRM_API_BASE` | Base URL of the CRM mail API, e.g. `https://api.your-crm.com/api/v1/mail` | Your CRM deployment |
| `CRM_ACCOUNT_ID` | ID of the mail account to read | The `accountId` query parameter the CRM web app sends (browser dev tools, Network tab) |
| `CRM_INBOX_FOLDER_ID` | ID of the inbox folder | The `folderId` query parameter, found the same way |
| `CRM_SESSION_TOKEN` | Value of the `better-auth.session_token` cookie | Browser dev tools, Application > Cookies, after logging in to the CRM. It expires, so refresh it when requests start returning 401. |
| `CRM_REFERER` | Optional. Referer header sent with each request, e.g. `https://your-crm.com/mail` | Your CRM web app URL |

`API.py` and `mail.py` both load `.env` on startup.

## Running

`chat.html` expects the API on port 5000:

```bash
uvicorn API:app --port 5000
```

Then open `chat.html` in a browser.

To test the CRM connection alone:

```bash
python mail.py
```

## Endpoints

| Method | Path | Description |
|--------|------|-------------|
| POST | `/ask` | Body `{"question": "..."}`; returns `{"answer": "..."}` |
| GET | `/health` | Returns `{"status": "ok"}` |
