from __future__ import annotations

import logging
import smtplib
import ssl
from email.message import EmailMessage
import requests
from apartment_agent.i18n import tr
from apartment_agent.models import ApartmentMatch, AppConfig

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

    def __init__(self, config: AppConfig, language: str = "en") -> None:
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
        telegram_config = self.config.telegram
        if not telegram_config.enabled:
            return

        bot_token = telegram_config.bot_token
        chat_id = telegram_config.chat_id
        if not bot_token or not chat_id:
            LOGGER.error("Telegram notification enabled but bot_token or chat_id is missing.")
            return

        LOGGER.info("Sending Telegram notification")
        LOGGER.debug("Telegram target chat_id=%s", chat_id)
        try:
            response = requests.post(
                f"https://api.telegram.org/bot{bot_token}/sendMessage",
                json={"chat_id": chat_id, "text": message},
                timeout=10,
            )
            response.raise_for_status()
            LOGGER.info("Telegram notification sent successfully")
        except requests.Timeout as error:
            LOGGER.warning("Telegram request timeout: %s", error)
        except requests.ConnectionError as error:
            LOGGER.warning("Telegram connection error: %s", error)
        except requests.RequestException as error:
            LOGGER.exception("Telegram notification failed: %s", error)

    def _send_email(self, message: str) -> None:
        email_config = self.config.email
        if not email_config.enabled:
            return

        smtp_host = email_config.smtp_host
        smtp_port = email_config.smtp_port
        username = email_config.username
        password = email_config.password
        recipient = email_config.recipient

        if not smtp_host or not username or not password or not recipient:
            LOGGER.error("Email notification enabled but required fields (smtp_host, username, password, recipient) are missing.")
            return

        email_message = EmailMessage()
        email_message["From"] = username
        email_message["To"] = recipient
        email_message["Subject"] = "Neuer Wohnungstreffer"
        email_message.set_content(message)

        tls_context = ssl.create_default_context()
        LOGGER.info("Sending email notification to %s via %s:%d", recipient, smtp_host, smtp_port)
        try:
            with smtplib.SMTP(smtp_host, smtp_port) as smtp:
                smtp.starttls(context=tls_context)
                smtp.login(username, password)
                smtp.send_message(email_message)
            LOGGER.info("Email notification sent successfully to %s", recipient)
        except smtplib.SMTPAuthenticationError as error:
            LOGGER.error(
                "Email authentication failed for %s via %s:%d: %s",
                recipient,
                smtp_host,
                smtp_port,
                error,
            )
        except smtplib.SMTPException as error:
            LOGGER.exception("Email SMTP error for %s via %s: %s", recipient, smtp_host, error)
        except OSError as error:
            LOGGER.exception("Email network error connecting to %s:%d: %s", smtp_host, smtp_port, error)
