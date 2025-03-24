from email_connector import fetch_emails_with_attachments
from llm_connector import analyze_text, determine_request_type


def main():
    emails = fetch_emails_with_attachments()

    if not emails:
        print("No emails found.")
        return

    request_type, sub_request_types = determine_request_type(emails)

    for email in emails:
        print(f"\n📩 Processing Email: {email['subject']}")

        analysis = analyze_text(email['bodyPreview'], request_type, sub_request_types)
        print(f"🔍 Pattern: {analysis['pattern']}")
        print(f"📌 Request Type: {analysis['request_type']}")
        print(f"📑 Sub-Request Type: {analysis['sub_request_type']}")
        print(f"📜 Summary: {analysis['summary']}")
        print("-" * 50)


if __name__ == "__main__":
    main()