import imaplib
import email
from email.header import decode_header
import os
from dotenv import load_dotenv

load_dotenv()

class GmailClient:
    def __init__(self):
        self.server = os.getenv("IMAP_SERVER", "imap.gmail.com")
        self.email_address = os.getenv("EMAIL_ADDRESS")
        self.password = os.getenv("EMAIL_PASSWORD")
        self.mail = None

    def connect(self):
        if not self.email_address or not self.password:
            raise ValueError("Email credentials not found. Please check your .env file.")
        
        # Connect to server via SSL on port 993
        self.mail = imaplib.IMAP4_SSL(self.server, 993)
        self.mail.login(self.email_address, self.password)
        self.mail.select("INBOX")

    def disconnect(self):
        if self.mail:
            try:
                self.mail.close()
                self.mail.logout()
            except Exception:
                pass

    def fetch_job_emails(self, max_emails=20):
        """
        Fetches unread job-related emails from Gmail.
        Uses X-GM-RAW for advanced Gmail search query syntax.
        """
        if not self.mail:
            self.connect()

        # Search query for job-related unread emails
        # This will match subjects containing job keywords that are unread
        search_query = 'subject:(job OR career OR hiring OR role OR position OR opening OR recruit OR opportunity OR application) is:unread'
        
        status, data = self.mail.search(None, 'X-GM-RAW', f'"{search_query}"')
        
        if status != 'OK':
            print("Error searching emails.")
            return []

        email_ids = data[0].split()
        if not email_ids:
            return []

        # Get the most recent email IDs up to max_emails
        email_ids = email_ids[-max_emails:]
        email_ids.reverse() # Process newest first

        job_emails = []

        for e_id in email_ids:
            status, msg_data = self.mail.fetch(e_id, '(RFC822)')
            if status != 'OK':
                continue

            for response_part in msg_data:
                if isinstance(response_part, tuple):
                    raw_email = response_part[1]
                    msg = email.message_from_bytes(raw_email)
                    
                    # Extract headers
                    subject = self._decode_header_value(msg["Subject"])
                    sender = self._decode_header_value(msg["From"])
                    date = msg["Date"]
                    message_id = msg["Message-ID"] or f"fallback_{e_id.decode()}"
                    
                    # Extract body
                    body = self._extract_body(msg)
                    
                    job_emails.append({
                        "id": e_id.decode(),
                        "message_id": message_id,
                        "subject": subject,
                        "sender": sender,
                        "date": date,
                        "body": body
                    })
                    
        return job_emails

    def _decode_header_value(self, value):
        if not value:
            return ""
        decoded_parts = decode_header(value)
        header_str = ""
        for part, encoding in decoded_parts:
            if isinstance(part, bytes):
                try:
                    header_str += part.decode(encoding or "utf-8", errors="ignore")
                except Exception:
                    header_str += part.decode("utf-8", errors="ignore")
            else:
                header_str += part
        return header_str

    def _extract_body(self, msg):
        body = ""
        if msg.is_multipart():
            # Walk parts to find text/html or text/plain
            html_body = ""
            plain_body = ""
            for part in msg.walk():
                content_type = part.get_content_type()
                content_disposition = str(part.get("Content-Disposition"))

                if "attachment" in content_disposition:
                    continue

                if content_type == "text/plain":
                    try:
                        plain_body += part.get_payload(decode=True).decode(part.get_content_charset() or "utf-8", errors="ignore")
                    except Exception:
                        pass
                elif content_type == "text/html":
                    try:
                        html_body += part.get_payload(decode=True).decode(part.get_content_charset() or "utf-8", errors="ignore")
                    except Exception:
                        pass

            # Prefer HTML because job boards (LinkedIn, Indeed) have formatted lists
            body = html_body if html_body else plain_body
        else:
            try:
                body = msg.get_payload(decode=True).decode(msg.get_content_charset() or "utf-8", errors="ignore")
            except Exception:
                pass
                
        return body
