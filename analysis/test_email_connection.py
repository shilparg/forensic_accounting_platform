import os
import smtplib
from email.message import EmailMessage
from sendgrid import SendGridAPIClient
from sendgrid.helpers.mail import Mail
from dotenv import load_dotenv, find_dotenv

# Load environment variables
load_dotenv(find_dotenv(), override=True)

def get_recipients():
    """Helper to convert comma-separated string to a clean list for testing."""
    raw = os.getenv("AUDIT_EMAIL_RECIPIENT", "")
    return [email.strip() for email in raw.split(",") if email.strip()]

def test_gmail_diagnostic():
    print("--- 🔍 GMAIL DIAGNOSTIC TEST ---")
    user = os.getenv("GMAIL_USER")
    pwd = os.getenv("GMAIL_APP_PASSWORD")
    recipient_list = get_recipients()
    
    print(f"👤 Sending From: {user}")
    print(f"👥 Sending To: {', '.join(recipient_list)}")
    print(f"🔑 Password Length: {len(pwd) if pwd else 0} chars (Should be 16)")

    msg = EmailMessage()
    msg.set_content("Success! The Forensic Pipeline multi-recipient logic is working.")
    msg['Subject'] = "🧪 DIAGNOSTIC: Multi-Recipient Test"
    msg['From'] = f"{os.getenv('SMTP_NAME', 'Forensic Bot')} <{user}>"
    msg['To'] = ", ".join(recipient_list)

    try:
        print("⏳ Connecting to smtp.gmail.com:587...")
        server = smtplib.SMTP("smtp.gmail.com", 587, timeout=15)
        server.starttls()
        
        print("🔐 TLS Handshake successful. Logging in...")
        server.login(user, pwd)
        
        print("📧 Sending test message to all recipients...")
        server.send_message(msg, to_addrs=recipient_list)
        
        print("✅ GMAIL SUCCESS: Check all inboxes!")
        server.quit()
    except Exception as e:
        print(f"❌ GMAIL FAILED: {e}")
        print("\n💡 TIP: If 'Username and Password not accepted', double-check your new 16-char App Password.")

def test_sendgrid_diagnostic():
    print("--- 🚀 SENDGRID DIAGNOSTIC TEST ---")
    recipient_list = get_recipients()
    print(f"👥 Sending To: {', '.join(recipient_list)}")

    message = Mail(
        from_email=os.getenv("SENDGRID_FROM_EMAIL"),
        to_emails=recipient_list,
        subject="🧪 DIAGNOSTIC: SendGrid Multi-Recipient Test",
        plain_text_content="Success! SendGrid API is delivering to the full audit team."
    )
    try:
        sg = SendGridAPIClient(os.getenv('SENDGRID_API_KEY'))
        sg.send(message)
        print("✅ SENDGRID SUCCESS: Check all inboxes!")
    except Exception as e:
        print(f"❌ SENDGRID FAILED: {e}")

if __name__ == "__main__":
    provider = os.getenv("EMAIL_PROVIDER", "gmail").lower()
    
    if provider == "sendgrid":
        test_sendgrid_diagnostic()
    else:
        test_gmail_diagnostic()