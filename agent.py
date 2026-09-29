from agents import Agent, function_tool
import mail

ACCOUNT_ID = mail.ACCOUNT_ID
INBOX_FOLDER_ID = mail.INBOX_FOLDER_ID


@function_tool
def check_emails_from_sender(sender_name_or_address: str) -> str:
    """
    Checks how many emails were received from a specific sender (by name or
    email address, partial match ok).
    """
    messages = mail.fetch_messages_in_range(ACCOUNT_ID, INBOX_FOLDER_ID)
    count, filtered = mail.aggregate(messages, sender_contains=sender_name_or_address)

    if count == 0:
        return f"No emails found from '{sender_name_or_address}'."

    subjects = "\n".join(f"- [{m['receivedAt']}] {m['subject']}" for m in filtered[:15])
    more_note = f"\n(+{count - 15} more not shown)" if count > 15 else ""
    return f"Found {count} emails from '{sender_name_or_address}'.\n{subjects}{more_note}"


@function_tool
def check_total_emails(unread_only: bool = False) -> str:
    """
    Checks the total number of emails in the inbox, optionally filtered to
    only unread messages.
    """
    messages = mail.fetch_messages_in_range(ACCOUNT_ID, INBOX_FOLDER_ID)
    count, filtered = mail.aggregate(messages, unread_only=unread_only)
    label = "unread emails" if unread_only else "emails"
    return f"There are {count} {label} in the inbox."


mail_agent = Agent(
    name="Mail Checker Agent",
    instructions=(
        "You are a helpful assistant that answers questions about the user's "
        "CRM inbox. Use check_emails_from_sender when a specific person/address "
        "is mentioned. Use check_total_emails for general counts (all mail or "
        "unread mail) when no sender is specified. Always answer in a short, "
        "clear sentence with the count. If the user writes in Roman Urdu or "
        "mixed Urdu-English, respond in the same style."
    ),
    tools=[check_emails_from_sender, check_total_emails],
)