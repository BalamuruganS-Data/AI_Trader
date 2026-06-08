import smtplib
import ssl
import logging
import threading
from email.message import EmailMessage
from typing import Any, Dict, List

logging.basicConfig(level=logging.INFO, format="%(asctime)s %(levelname)s %(message)s")


class EmailClient:
    def __init__(self, smtp_server: str, smtp_port: int, username: str, password: str, recipients: List[str]):
        self.smtp_server = smtp_server
        self.smtp_port = smtp_port
        self.username = username
        self.password = password
        self.recipients = recipients

    def send(self, subject: str, body: str, background: bool = False):
        """Send email synchronously or in background thread."""
        if not self.username or not self.password:
            raise ValueError("Email username or password is not configured.")

        if background:
            # Send in background thread to avoid blocking request
            thread = threading.Thread(target=self._send_email, args=(subject, body), daemon=True)
            thread.start()
            logging.info(f"Email sent to background thread: {subject}")
        else:
            # Send synchronously (blocks)
            self._send_email(subject, body)

    def _send_email(self, subject: str, body: str):
        """Internal method to actually send the email."""
        try:
            msg = EmailMessage()
            msg["Subject"] = subject
            msg["From"] = self.username
            msg["To"] = ", ".join(self.recipients)
            msg.set_content(body)

            context = ssl.create_default_context()
            with smtplib.SMTP(self.smtp_server, self.smtp_port) as server:
                server.starttls(context=context)
                server.login(self.username, self.password)
                server.send_message(msg)
            logging.info(f"Email sent successfully: {subject}")
        except smtplib.SMTPAuthenticationError as exc:
            logging.error(
                f"SMTP authentication failed. Check your email credentials. Error: {exc}"
            )
        except smtplib.SMTPException as exc:
            logging.error(f"SMTP error sending email: {exc}")
        except Exception as exc:
            logging.error(f"Unexpected error sending email: {exc}")

    def build_summary(self, trades: List[Dict[str, Any]]) -> str:
        lines = ["Intraday trade alert summary:\n"]
        for trade in trades:
            lines.append(
                f"{trade['ticker']} | {trade['side']} | qty={trade['quantity']} | entry={trade['entry_price']:.2f} | "
                f"sl={trade['stop_loss']:.2f} | target={trade['target']:.2f}"
            )
        return "\n".join(lines)
