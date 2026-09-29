import os
from datetime import datetime, timezone

import requests
from dotenv import load_dotenv

load_dotenv()

# CRM connection details live in .env (see .env.example), never in source.
BASE = os.environ["CRM_API_BASE"].rstrip("/")
ACCOUNT_ID = os.environ["CRM_ACCOUNT_ID"]
INBOX_FOLDER_ID = os.environ["CRM_INBOX_FOLDER_ID"]
SESSION_TOKEN = os.environ["CRM_SESSION_TOKEN"]
REFERER = os.environ.get("CRM_REFERER", "")

session = requests.Session()
session.headers.update({
    "Cookie": f"better-auth.session_token={SESSION_TOKEN}",
    "Referer": REFERER,
})


def fetch_messages_in_range(account_id, folder_id, date_from=None, date_to=None, limit=50):
    results = []
    cursor = None
    while True:
        params = {"accountId": account_id, "folderId": folder_id, "limit": limit}
        if cursor:
            params["cursor"] = cursor

        resp = session.get(f"{BASE}/messages", params=params)
        resp.raise_for_status()
        data = resp.json()
        items = data["items"]

        for msg in items:
            received = datetime.fromisoformat(msg["receivedAt"].replace("Z", "+00:00"))
            if date_from and received < date_from:
                return results
            if date_to and received > date_to:
                continue
            results.append({
                "subject": msg["subject"],
                "fromAddress": msg["fromAddress"],
                "fromName": msg["fromName"],
                "receivedAt": msg["receivedAt"],
                "isUnread": msg["isUnread"],
                "bodyTextPreview": msg.get("bodyTextPreview", ""),
            })

        cursor = data.get("nextCursor")
        if not cursor:
            break
    return results


def aggregate(messages, sender_contains=None, unread_only=False):
    filtered = messages
    if sender_contains:
        s = sender_contains.lower()
        filtered = [m for m in filtered if s in m["fromAddress"].lower() or s in m["fromName"].lower()]
    if unread_only:
        filtered = [m for m in filtered if m["isUnread"]]
    return len(filtered), filtered


def dedupe_for_summary(messages):
    """Collapse true near-duplicates (same sender, subject, AND similar preview text).
    No cap here anymore — batching in agent.py handles arbitrarily large unique counts."""
    seen = {}
    for m in messages:
        preview_key = m.get("bodyTextPreview", "")[:60].strip().lower()
        key = (m["fromAddress"], m["subject"], preview_key)
        if key not in seen:
            seen[key] = {**m, "count": 1}
        else:
            seen[key]["count"] += 1
    deduped = sorted(seen.values(), key=lambda m: m["receivedAt"], reverse=True)
    return deduped  # full list, no truncation

if __name__ == "__main__":
    print("Fetching messages from inbox...\n")
    messages = fetch_messages_in_range(ACCOUNT_ID, INBOX_FOLDER_ID)

    print(f"Total messages fetched: {len(messages)}\n")

    if not messages:
        print("No messages returned — check auth/cookie or account/folder IDs.")
    else:
        print("First 5 raw messages:")
        for m in messages[:5]:
            print(f"  - [{m['receivedAt']}] {m['fromName']} <{m['fromAddress']}>: {m['subject']}")
            print(f"    preview: {m['bodyTextPreview'][:80]}...")
            print(f"    unread: {m['isUnread']}\n")

        # test aggregate()
        count, matched = aggregate(messages, sender_contains="cursor")
        print(f"Aggregate test — from 'cursor': {count} matches\n")

        # test dedupe_for_summary()
        deduped = dedupe_for_summary(messages)
        print(f"Dedupe test — {len(messages)} raw messages collapsed to {len(deduped)} unique entries\n")
        print("Deduped entries:")
        for d in deduped[:10]:
            tag = f" (x{d['count']})" if d["count"] > 1 else ""
            print(f"  - {d['fromName']}: {d['subject']}{tag}")
            