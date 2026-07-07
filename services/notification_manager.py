"""
notification_manager.py
------------------------------------------------------------
TrendForge Notification Manager

Features
--------
- Discord Notifications
- Email Notifications
- Console Notifications
- Risk Alerts
- Scanner Alerts
- Trade Alerts
- Error Notifications
- Extensible Architecture
"""

from dataclasses import dataclass
from datetime import datetime
from typing import Optional
import requests
import smtplib
from email.mime.text import MIMEText


# ==========================================================
# Notification
# ==========================================================

@dataclass
class Notification:

    title: str

    message: str

    level: str = "INFO"

    timestamp: datetime = datetime.now()


# ==========================================================
# Notification Manager
# ==========================================================

class NotificationManager:

    def __init__(
        self,
        discord_webhook: Optional[str] = None,
        email_enabled: bool = False,
        smtp_server: str = "",
        smtp_port: int = 587,
        sender_email: str = "",
        sender_password: str = "",
        receiver_email: str = ""
    ):

        self.discord_webhook = discord_webhook

        self.email_enabled = email_enabled

        self.smtp_server = smtp_server

        self.smtp_port = smtp_port

        self.sender_email = sender_email

        self.sender_password = sender_password

        self.receiver_email = receiver_email

    # ------------------------------------------------------

    def send(self, notification: Notification):

        self.console(notification)

        if self.discord_webhook:

            self.discord(notification)

        if self.email_enabled:

            self.email(notification)

    # ------------------------------------------------------

    def console(self, notification):

        print(
            f"[{notification.level}] "
            f"{notification.timestamp.strftime('%H:%M:%S')} | "
            f"{notification.title} : {notification.message}"
        )

    # ------------------------------------------------------

    def discord(self, notification):

        payload = {

            "embeds": [

                {

                    "title": notification.title,

                    "description": notification.message,

                    "color": self._color(notification.level)

                }

            ]

        }

        try:

            requests.post(
                self.discord_webhook,
                json=payload,
                timeout=10
            )

        except Exception as e:

            print("Discord Error:", e)

    # ------------------------------------------------------

    def email(self, notification):

        try:

            msg = MIMEText(notification.message)

            msg["Subject"] = notification.title

            msg["From"] = self.sender_email

            msg["To"] = self.receiver_email

            with smtplib.SMTP(
                self.smtp_server,
                self.smtp_port
            ) as server:

                server.starttls()

                server.login(
                    self.sender_email,
                    self.sender_password
                )

                server.send_message(msg)

        except Exception as e:

            print("Email Error:", e)

    # ------------------------------------------------------

    def trade_alert(
        self,
        symbol,
        action,
        quantity,
        price
    ):

        self.send(

            Notification(

                title="Trade Executed",

                message=(
                    f"{action} "
                    f"{quantity} "
                    f"{symbol} @ ₹{price:.2f}"
                ),

                level="SUCCESS"

            )

        )

    # ------------------------------------------------------

    def scanner_alert(
        self,
        symbol,
        strategy,
        score
    ):

        self.send(

            Notification(

                title="Scanner Alert",

                message=(
                    f"{symbol}\n"
                    f"Strategy : {strategy}\n"
                    f"Score : {score}"
                ),

                level="INFO"

            )

        )

    # ------------------------------------------------------

    def risk_alert(self, reason):

        self.send(

            Notification(

                title="Risk Manager",

                message=reason,

                level="WARNING"

            )

        )

    # ------------------------------------------------------

    def error_alert(self, error):

        self.send(

            Notification(

                title="Application Error",

                message=str(error),

                level="ERROR"

            )

        )

    # ------------------------------------------------------

    def system_alert(self, message):

        self.send(

            Notification(

                title="System",

                message=message,

                level="INFO"

            )

        )

    # ------------------------------------------------------

    @staticmethod
    def _color(level):

        colors = {

            "SUCCESS": 5763719,

            "INFO": 3447003,

            "WARNING": 16776960,

            "ERROR": 15158332

        }

        return colors.get(level, 3447003)