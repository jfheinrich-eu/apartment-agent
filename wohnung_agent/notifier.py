from __future__ import annotations

import logging
import smtplib
import ssl
from email.message import EmailMessage
from typing import Any
import requests
from wohnung_agent.i18n import tr
from wohnung_agent.models import ApartmentMatch

LOGGER = logging.getLogger(__name__)


def format_match(apartment_match: ApartmentMatch, language: str) -> str:
    apartment = apartment_match.apartment
    unknown = tr(language, "notifier.unknown")
    rent = unknown if apartment.warm_rent_eur is None else f"{apartment.warm_rent_eur:.0f} EUR"
    rooms = unknown if apartment.rooms is None else str(apartment.rooms)
    reasons = "\n".join(f"- {reason}" for reason in apartment_match.reasons)

    return (
        f"{tr(language, 'notifier.new_match', city=apartment.city, title=apartment.title)}\n"
        f"{tr(language, 'notifier.rent', rent=rent)}\n"
        f"{tr(language, 'notifier.rooms', rooms=rooms)}\n"
        f"{tr(language, 'notifier.score', score=apartment_match.score)}\n"
        f"{tr(language, 'notifier.link', url=apartment.url)}\n\n"
        f"{tr(language, 'notifier.evaluation', reasons=reasons)}"
    )


class Notifier:
    """Send apartment matches to the configured notification channels."""

    def __init__(self, config: dict[str, Any], language: str = "en") -> None:
        """Store notification configuration for Telegram and email delivery."""
        self.config = config
        self.language = language

    def send(self, apartment_match: ApartmentMatch) -> None:
        message = format_match(apartment_match, self.language)
        LOGGER.info("Notification prepared for %s", apartment_match.apartment.title)
        LOGGER.debug("Notification body:\n%s", message)
        self._send_telegram(message)
        self._send_email(message)

    def _send_telegram(self, message: str) -> None:
        telegram_config = self.config.get("telegram", {})
        if not telegram_config.get("enabled"):
            return

        bot_token = telegram_config.get("bot_token", "")
        chat_id = telegram_config.get("chat_id", "")
        if not bot_token or not chat_id:
            LOGGER.error("Telegram notification enabled but bot_token or chat_id is missing.")
            return

        LOGGER.info("Sending Telegram notification")
        try:
            response = requests.post(
                f"https://api.telegram.org/bot{bot_token}/sendMessage",
                json={"chat_id": chat_id, "text": message},
                timeout=20,
            )
            response.raise_for_status()
        except requests.RequestException:
            LOGGER.exception("Telegram notification failed")

    def _send_email(self, message: str) -> None:
        email_config = self.config.get("email", {})
        if not email_config.get("enabled"):
            return

        smtp_host = email_config.get("smtp_host", "")
        smtp_port = email_config.get("smtp_port", 587)
        username = email_config.get("username", "")
        password = email_config.get("password", "")
        recipient = email_config.get("recipient", "")

        if not smtp_host or not username or not password or not recipient:
            LOGGER.error("Email notification enabled but required fields (smtp_host, username, password, recipient) are missing.")
            return

        email_message = EmailMessage()
        email_message["From"] = username
        email_message["To"] = recipient
        email_message["Subject"] = "Neuer Wohnungstreffer"
        email_message.set_content(message)

        tls_context = ssl.create_default_context()
        LOGGER.info("Sending email notification to %s via %s", recipient, smtp_host)
        try:
            with smtplib.SMTP(smtp_host, smtp_port) as smtp:
                smtp.starttls(context=tls_context)
                smtp.login(username, password)
                smtp.send_message(email_message)
        except (OSError, smtplib.SMTPException):
            LOGGER.exception("Email notification failed for %s via %s", recipient, smtp_host)
