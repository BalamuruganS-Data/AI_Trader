import smtplib
import ssl
from email.message import EmailMessage
from typing import Any, Dict, List


class EmailClient:
    def __init__(self, smtp_server: str, smtp_port: int, username: str, password: str, recipients: List[str]):
        self.smtp_server = smtp_server
        self.smtp_port = smtp_port
        self.username = username
        self.password = password
        self.recipients = recipients

    def send(self, subject: str, body: str):
        if not self.username or not self.password:
            raise ValueError("Email username or password is not configured.")

        msg = EmailMessage()
        msg["Subject"] = subject
        msg["From"] = self.username
        msg["To"] = ", ".join(self.recipients)
        msg.set_content(body)

        context = ssl.create_default_context()
        try:
            with smtplib.SMTP(self.smtp_server, self.smtp_port) as server:
                server.starttls(context=context)
                server.login(self.username, self.password)
                server.send_message(msg)
        except smtplib.SMTPAuthenticationError as exc:
            raise ValueError(
                "SMTP authentication failed. Check your email credentials and if you are using Gmail, use an app password or allow less secure apps. "
                f"Original error: {exc}"
            ) from exc
        except smtplib.SMTPException as exc:
            raise ValueError(f"SMTP error sending email: {exc}") from exc

    def build_summary(self, trades: List[Dict[str, Any]]) -> str:
        lines = ["Intraday trade alert summary:\n"]
        for trade in trades:
            lines.append(
                f"{trade['ticker']} | {trade['side']} | qty={trade['quantity']} | entry={trade['entry_price']:.2f} | "
                f"sl={trade['stop_loss']:.2f} | target={trade['target']:.2f}"
            )
        return "\n".join(lines)
